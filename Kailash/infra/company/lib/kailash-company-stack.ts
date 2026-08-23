/**
 * KailashCompanyStack — the Company segment on AWS, per
 * company-segment/docs/aws/Company_Segment_Backend_Architecture_AWS.md.
 *
 * L0  API Gateway (+WAF) / SQS buffer -> ingestion Lambda -> S3 vault +
 *     DynamoDB idempotency/error queue
 * L1  Aurora Serverless v2 (PostgreSQL, `company` schema) behind RDS Proxy,
 *     posting via the same engine code as local dev
 * L2  Step Functions period-end close (lock -> GSTR-1 -> 3B -> statements
 *     -> recon -> publish); EventBridge Scheduler compliance calendar
 * L3  reconciliation runs inside the close flow (same engine)
 * L4  read APIs on the co_v_* views through the API Lambda
 * Bus EventBridge "center-lake" bus — JournalPosted / ReturnGenerated /
 *     ReconciliationCompleted / FinancialFactsPublished / ComplianceDue
 */
import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as rds from "aws-cdk-lib/aws-rds";
import * as kms from "aws-cdk-lib/aws-kms";
import * as s3 from "aws-cdk-lib/aws-s3";
import * as dynamodb from "aws-cdk-lib/aws-dynamodb";
import * as sqs from "aws-cdk-lib/aws-sqs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as lambdaEventSources from "aws-cdk-lib/aws-lambda-event-sources";
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import * as events from "aws-cdk-lib/aws-events";
import * as targets from "aws-cdk-lib/aws-events-targets";
import * as sfn from "aws-cdk-lib/aws-stepfunctions";
import * as sfnTasks from "aws-cdk-lib/aws-stepfunctions-tasks";
import * as secretsmanager from "aws-cdk-lib/aws-secretsmanager";
import * as wafv2 from "aws-cdk-lib/aws-wafv2";
import * as logs from "aws-cdk-lib/aws-logs";
import * as path from "path";

export class KailashCompanyStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // ------------------------------------------------------------------ KMS
    const key = new kms.Key(this, "CompanyKey", {
      alias: "kailash/company",
      description: "Company segment — ledger, vault and PII encryption",
      enableKeyRotation: true,
    });

    // ------------------------------------------------------------------ VPC
    const vpc = new ec2.Vpc(this, "CompanyVpc", {
      maxAzs: 2,
      natGateways: 1,
      subnetConfiguration: [
        { name: "public", subnetType: ec2.SubnetType.PUBLIC, cidrMask: 24 },
        {
          name: "ledger",
          subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
          cidrMask: 24,
        },
      ],
    });

    // -------------------------------------------- L1 · Aurora Serverless v2
    const dbSecret = new rds.DatabaseSecret(this, "LedgerSecret", {
      username: "kailash",
      dbname: "kailash",
    });

    const cluster = new rds.DatabaseCluster(this, "Ledger", {
      engine: rds.DatabaseClusterEngine.auroraPostgres({
        version: rds.AuroraPostgresEngineVersion.VER_16_4,
      }),
      credentials: rds.Credentials.fromSecret(dbSecret),
      defaultDatabaseName: "kailash",
      serverlessV2MinCapacity: 0.5,
      serverlessV2MaxCapacity: 4,
      writer: rds.ClusterInstance.serverlessV2("writer"),
      vpc,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
      storageEncryptionKey: key,
      backup: { retention: cdk.Duration.days(35) }, // PITR window for the SoR
      deletionProtection: true,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    // RDS Proxy — survives Lambda connection storms.
    const proxy = cluster.addProxy("LedgerProxy", {
      secrets: [dbSecret],
      vpc,
      requireTLS: true,
    });

    // ------------------------------------------------------- L0 · S3 vault
    const vault = new s3.Bucket(this, "DocumentVault", {
      bucketName: undefined, // let CFN name it; exported below
      encryption: s3.BucketEncryption.KMS,
      encryptionKey: key,
      versioned: true, // statutory artefacts are versioned facts
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      enforceSSL: true,
      lifecycleRules: [
        {
          id: "statutory-retention",
          transitions: [
            {
              storageClass: s3.StorageClass.INFREQUENT_ACCESS,
              transitionAfter: cdk.Duration.days(365),
            },
            {
              storageClass: s3.StorageClass.GLACIER,
              transitionAfter: cdk.Duration.days(3 * 365),
            },
          ],
          // Companies Act §128(5): books preserved 8 years — never expire
          // before that; deletion stays a manual, audited decision.
        },
      ],
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    // ---------------------------------------- L0 · DynamoDB fast-path state
    const idempotency = new dynamodb.Table(this, "Idempotency", {
      partitionKey: { name: "source_hash", type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.CUSTOMER_MANAGED,
      encryptionKey: key,
      pointInTimeRecoverySpecification: { pointInTimeRecoveryEnabled: true },
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    // ------------------------------------------------- L0 · SQS buffer + DLQ
    const ingestDlq = new sqs.Queue(this, "IngestDlq", {
      retentionPeriod: cdk.Duration.days(14),
    });
    const ingestQueue = new sqs.Queue(this, "IngestQueue", {
      visibilityTimeout: cdk.Duration.minutes(5),
      deadLetterQueue: { queue: ingestDlq, maxReceiveCount: 5 },
    });

    // -------------------------------------------------- Center Lake bus
    const bus = new events.EventBus(this, "CenterLakeBus", {
      eventBusName: "kailash-center-lake",
    });

    // -------------------------------------------------- GSTN/IRP secret
    const gstnSecret = new secretsmanager.Secret(this, "GstnCredentials", {
      secretName: "kailash/company/gstn",  // secret-scan: allow a Secrets Manager secret name, not a secret value
      description:
        "GSTN API / e-invoice IRP credentials (populate before enabling filing)",
      encryptionKey: key,
    });

    // -------------------------------------------------- Lambda common
    const bundle = lambda.Code.fromAsset(
      path.join(__dirname, "..", "lambda-dist")
    );
    const commonEnv: Record<string, string> = {
      COMPANY_DB_SECRET_ARN: dbSecret.secretArn,
      COMPANY_DB_HOST: proxy.endpoint,
      COMPANY_SCAFFOLD_DIR: "/var/task/company-segment",
      EVENT_BUS_NAME: bus.eventBusName,
      IDEMPOTENCY_TABLE: idempotency.tableName,
      DOCUMENT_VAULT_BUCKET: vault.bucketName,
      ENV: "prod",
      LOG_JSON: "true",
    };

    const mkFn = (
      name: string,
      handler: string,
      opts: Partial<lambda.FunctionProps> = {}
    ) =>
      new lambda.Function(this, name, {
        runtime: lambda.Runtime.PYTHON_3_11,
        code: bundle,
        handler,
        memorySize: 512,
        timeout: cdk.Duration.seconds(60),
        vpc,
        vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
        environment: commonEnv,
        logRetention: logs.RetentionDays.ONE_YEAR,
        ...opts,
      });

    const apiFn = mkFn("ApiFn", "handlers.api_handler.handler", {
      memorySize: 1024,
      timeout: cdk.Duration.seconds(30),
      description: "Company segment API (FastAPI via Mangum)",
    });
    const ingestFn = mkFn("IngestWorkerFn", "handlers.ingest_worker.handler", {
      description: "SQS-buffered L0 ingestion worker",
    });
    const closeFn = mkFn("CloseStepFn", "handlers.close_steps.handler", {
      timeout: cdk.Duration.minutes(5),
      description: "Period-end close steps (GSTR-1/3B, statements, recon, publish)",
    });
    const tallyFn = mkFn("TallyMigrationFn", "handlers.tally_migration.handler", {
      timeout: cdk.Duration.minutes(10),
      description: "Tally migration: stage -> post opening -> verify",
    });
    const calendarFn = mkFn("CalendarAlertFn", "handlers.calendar_alert.handler", {
      description: "Daily compliance-calendar alerts onto the bus",
    });

    const allFns = [apiFn, ingestFn, closeFn, tallyFn, calendarFn];
    for (const fn of allFns) {
      dbSecret.grantRead(fn);
      proxy.grantConnect(fn, "kailash");
      bus.grantPutEventsTo(fn);
      idempotency.grantReadWriteData(fn);
      vault.grantReadWrite(fn);
      key.grantEncryptDecrypt(fn);
    }
    gstnSecret.grantRead(closeFn); // filing path only

    ingestFn.addEventSource(
      new lambdaEventSources.SqsEventSource(ingestQueue, {
        batchSize: 10,
        reportBatchItemFailures: true,
      })
    );

    // -------------------------------------------------- Edge: REST API + WAF
    const api = new apigateway.LambdaRestApi(this, "CompanyApi", {
      handler: apiFn,
      proxy: true,
      restApiName: "kailash-company",
      description: "Company segment — master operational ledger API",
      deployOptions: {
        stageName: "prod",
        throttlingRateLimit: 50,
        throttlingBurstLimit: 100,
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        metricsEnabled: true,
      },
    });

    const waf = new wafv2.CfnWebACL(this, "CompanyWaf", {
      scope: "REGIONAL",
      defaultAction: { allow: {} },
      visibilityConfig: {
        cloudWatchMetricsEnabled: true,
        metricName: "kailash-company-waf",
        sampledRequestsEnabled: true,
      },
      rules: [
        {
          name: "AWSManagedCommonRules",
          priority: 0,
          overrideAction: { none: {} },
          statement: {
            managedRuleGroupStatement: {
              vendorName: "AWS",
              name: "AWSManagedRulesCommonRuleSet",
            },
          },
          visibilityConfig: {
            cloudWatchMetricsEnabled: true,
            metricName: "common-rules",
            sampledRequestsEnabled: true,
          },
        },
        {
          name: "RateLimitPerIp",
          priority: 1,
          action: { block: {} },
          statement: {
            rateBasedStatement: { limit: 2000, aggregateKeyType: "IP" },
          },
          visibilityConfig: {
            cloudWatchMetricsEnabled: true,
            metricName: "rate-limit",
            sampledRequestsEnabled: true,
          },
        },
      ],
    });
    new wafv2.CfnWebACLAssociation(this, "CompanyWafAssoc", {
      resourceArn: api.deploymentStage.stageArn,
      webAclArn: waf.attrArn,
    });

    // ------------------------------------- L2 · Step Functions: period close
    const closeStep = (step: string) =>
      new sfnTasks.LambdaInvoke(this, `Close_${step}`, {
        lambdaFunction: closeFn,
        payload: sfn.TaskInput.fromObject({
          step,
          "fy.$": "$.fy",
          "gstin.$": "$.gstin",
          "period.$": "$.period",
          "externals.$": "$.externals",
        }),
        outputPath: "$.Payload",
        retryOnServiceExceptions: true,
      });

    const closeDefinition = closeStep("lock_period")
      .next(closeStep("build_gstr1"))
      .next(closeStep("build_gstr3b"))
      .next(closeStep("build_statements"))
      .next(closeStep("run_recon"))
      .next(closeStep("publish_facts"));

    const closeSm = new sfn.StateMachine(this, "PeriodEndClose", {
      stateMachineName: "kailash-company-period-end-close",
      definitionBody: sfn.DefinitionBody.fromChainable(closeDefinition),
      timeout: cdk.Duration.hours(1),
      tracingEnabled: true,
    });

    // --------------------------------- L0 · Step Functions: Tally migration
    const tallyStep = (step: string) =>
      new sfnTasks.LambdaInvoke(this, `Tally_${step}`, {
        lambdaFunction: tallyFn,
        payload: sfn.TaskInput.fromObject({
          step,
          "bucket.$": "$.bucket",
          "key.$": "$.key",
          "gstin.$": "$.gstin",
          "as_of.$": "$.as_of",
          "maker.$": "$.maker",
          "checker.$": "$.checker",
        }),
        outputPath: "$.Payload",
        retryOnServiceExceptions: true,
      });

    const tallyDefinition = tallyStep("stage")
      .next(
        new sfn.Choice(this, "StagedBalanced")
          .when(
            sfn.Condition.booleanEquals("$.result.balanced", false),
            new sfn.Fail(this, "TallyUnbalanced", {
              cause: "Staged Tally export does not balance",
              error: "TallyExportUnbalanced",
            })
          )
          .otherwise(
            tallyStep("post_opening").next(
              tallyStep("verify").next(
                new sfn.Succeed(this, "TallyMigrated")
              )
            )
          )
      );

    const tallySm = new sfn.StateMachine(this, "TallyMigration", {
      stateMachineName: "kailash-company-tally-migration",
      definitionBody: sfn.DefinitionBody.fromChainable(tallyDefinition),
      timeout: cdk.Duration.hours(2),
      tracingEnabled: true,
    });

    // -------------------------------- Compliance calendar (daily, 03:30 UTC
    // = 09:00 IST) + monthly close reminder on the bus
    new events.Rule(this, "DailyComplianceCheck", {
      schedule: events.Schedule.cron({ minute: "30", hour: "3" }),
      targets: [new targets.LambdaFunction(calendarFn)],
      description: "Daily compliance-calendar sweep (09:00 IST)",
    });

    // -------------------------------------------------------------- Outputs
    new cdk.CfnOutput(this, "ApiUrl", { value: api.url });
    new cdk.CfnOutput(this, "EventBusName", { value: bus.eventBusName });
    new cdk.CfnOutput(this, "DocumentVaultBucket", { value: vault.bucketName });
    new cdk.CfnOutput(this, "LedgerProxyEndpoint", { value: proxy.endpoint });
    new cdk.CfnOutput(this, "LedgerSecretArn", { value: dbSecret.secretArn });
    new cdk.CfnOutput(this, "IngestQueueUrl", { value: ingestQueue.queueUrl });
    new cdk.CfnOutput(this, "PeriodEndCloseArn", { value: closeSm.stateMachineArn });
    new cdk.CfnOutput(this, "TallyMigrationArn", { value: tallySm.stateMachineArn });
    new cdk.CfnOutput(this, "GstnSecretArn", { value: gstnSecret.secretArn });
  }
}
