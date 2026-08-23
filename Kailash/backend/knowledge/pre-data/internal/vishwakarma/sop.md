# VISHWAKARMA Department - Standard Operating Procedures

## Daily Development Operations

### Morning Standup (10:00 UTC)
1. Review yesterday's work
2. Share today's plan
3. Identify blockers
4. Discuss technical challenges
5. Review incident reports
6. Check CI/CD pipeline health

### Code Development SOP

#### Starting New Feature
1. Create feature branch from main
2. Write failing tests first (TDD)
3. Implement feature code
4. Make tests pass
5. Refactor for clean code
6. Run linter and type checker
7. Commit with descriptive message
8. Push to remote branch
9. Create pull request
10. Request code review

#### Code Review Process
1. Reviewer assigned within 2 hours
2. Check code quality and standards
3. Verify test coverage
4. Test functionality locally
5. Provide constructive feedback
6. Approve or request changes
7. Author addresses feedback
8. Final approval and merge
9. CI/CD pipeline runs
10. Monitor deployment

## Deployment SOP

### Pre-Deployment Checklist
- [ ] All tests passing
- [ ] Code review approved
- [ ] Database migrations ready (if any)
- [ ] Environment variables configured
- [ ] Monitoring alerts set up
- [ ] Rollback plan documented
- [ ] Stakeholders notified
- [ ] Off-peak deployment time scheduled

### Deployment Steps

#### Staging Deployment
1. Merge feature branch to staging
2. CI/CD triggers build
3. Run test suite
4. Build Docker images
5. Push to container registry
6. Deploy to staging cluster
7. Run smoke tests
8. Manual QA verification
9. Performance check
10. Security scan

#### Production Deployment
1. Tag release version
2. Create deployment ticket
3. Deploy to canary (10% traffic)
4. Monitor for 15 minutes
5. Check error rates and latency
6. If healthy, roll out to 50%
7. Monitor for 15 minutes
8. If healthy, roll out to 100%
9. Monitor for 1 hour
10. Update documentation
11. Close deployment ticket

### Rollback Procedure
1. Identify issue requiring rollback
2. Notify team immediately
3. Trigger rollback via CI/CD
4. Deploy previous stable version
5. Verify rollback successful
6. Monitor system health
7. Investigate root cause
8. Document incident
9. Plan fix
10. Schedule redeployment

## Database Operations SOP

### Running Migrations
1. Review migration script
2. Test on local database
3. Backup production database
4. Run migration on staging
5. Verify data integrity
6. Schedule production migration
7. Enable maintenance mode (if needed)
8. Run migration on production
9. Verify success
10. Disable maintenance mode
11. Monitor for issues

### Database Performance Optimization
1. Identify slow queries from logs
2. Use MongoDB explain() to analyze
3. Check if indexes exist
4. Create missing indexes
5. Test query performance
6. Deploy index creation
7. Monitor query times
8. Document optimization

### Database Backup & Restore

#### Daily Backup
1. Automated backup runs at 02:00 UTC
2. Backup stored in S3 with encryption
3. Verify backup integrity
4. Test restore monthly
5. Retain 30 days of backups
6. Archive monthly backups for 1 year

#### Restore Procedure
1. Identify backup to restore
2. Create new database instance
3. Download backup from S3
4. Restore to new instance
5. Verify data integrity
6. Run data validation scripts
7. Point application to new database
8. Monitor for issues
9. Keep old database for 24 hours
10. Delete old database if stable

## Incident Response SOP

### P0 Incident (System Down)
1. **00:00**: Alert triggered
2. **00:02**: On-call engineer acknowledges
3. **00:05**: Initial assessment complete
4. **00:10**: Incident commander assigned
5. **00:15**: War room created
6. **00:20**: Status page updated
7. **00:30**: Mitigation in progress
8. **01:00**: Service restored (target)
9. **01:30**: Monitoring for stability
10. **24:00**: Post-mortem scheduled

### Investigation Process
1. Check monitoring dashboards
2. Review error logs
3. Check recent deployments
4. Verify external dependencies
5. Check database health
6. Review auto-rectification attempts
7. Test API endpoints manually
8. Check network connectivity
9. Review resource utilization
10. Identify root cause

### Communication During Incident
- Update status page every 15 minutes
- Post in Slack incident channel
- Notify affected customers
- Escalate to management if > 1 hour
- Document all actions taken
- Record timeline of events

## Performance Optimization SOP

### Weekly Performance Review
1. Review monitoring dashboards
2. Identify performance bottlenecks
3. Analyze slow API endpoints
4. Check database query performance
5. Review AI model response times
6. Check resource utilization
7. Prioritize optimization tasks
8. Create tickets for improvements

### Optimization Actions

#### API Optimization
- Add caching for frequently accessed data
- Implement response compression
- Optimize database queries
- Use connection pooling
- Implement pagination
- Add CDN for static assets

#### Database Optimization
- Add indexes for slow queries
- Denormalize for read-heavy operations
- Implement caching layer (Redis)
- Archive old data
- Optimize document structure
- Use projections to limit fields

#### AI Model Optimization
- Optimize prompt length
- Use cheaper models where appropriate
- Implement response streaming
- Cache common queries
- Batch API calls
- Use model-specific optimizations

## Security SOP

### Monthly Security Audit
1. Run automated security scan
2. Review dependency vulnerabilities
3. Check for exposed secrets
4. Verify SSL/TLS certificates
5. Review API authentication logs
6. Check for suspicious activity
7. Update security patches
8. Review access controls
9. Document findings
10. Create remediation tickets

### Secret Rotation
1. Generate new secret
2. Update in secret manager
3. Deploy to staging
4. Test functionality
5. Deploy to production
6. Verify old secret still works
7. Monitor for 24 hours
8. Revoke old secret
9. Document rotation
10. Update runbooks

### Vulnerability Response
1. **Detection**: Security scan or report
2. **Assessment**: Evaluate severity
3. **Prioritization**: Based on CVSS score
4. **Mitigation**: Patch or workaround
5. **Testing**: Verify fix
6. **Deployment**: Emergency patch if critical
7. **Verification**: Confirm vulnerability closed
8. **Documentation**: Update security log
