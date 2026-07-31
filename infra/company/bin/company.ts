#!/usr/bin/env node
import * as cdk from "aws-cdk-lib";
import { KailashCompanyStack } from "../lib/kailash-company-stack";

const app = new cdk.App();
new KailashCompanyStack(app, "KailashCompanyStack", {
  description:
    "Kailash Company segment — master operational ledger (Aurora + Lambda + Step Functions + EventBridge)",
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || "ap-south-1", // India data residency
  },
  tags: {
    project: "kailash",
    segment: "company",
    "managed-by": "cdk",
  },
});
