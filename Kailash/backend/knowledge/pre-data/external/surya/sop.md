# SURYA Department - URGAA Standard Operating Procedures

## Daily Operations

### Morning Startup (06:00 UTC)
1. Review overnight charging sessions
2. Check all charger status (online/offline)
3. Review auto-rectification actions
4. Check energy consumption vs. forecast
5. Review dynamic pricing performance
6. Identify chargers needing attention
7. Update dashboard metrics

### Continuous Monitoring
1. Real-time charger health monitoring
2. OCPP message stream analysis
3. Energy grid load tracking
4. User session monitoring
5. Revenue tracking
6. Alert response and action

### End of Day (22:00 UTC)
1. Generate daily operations report
2. Archive charging session data
3. Update predictive models with new data
4. Schedule next day maintenance
5. Review and close resolved incidents

## Charger Incident Response SOP

### Charger Offline Alert
1. **00:00**: Alert received - charger offline
2. **00:01**: SURYA AI analyzes last known state
3. **00:02**: Check network connectivity
4. **00:03**: Attempt remote restart
5. **00:05**: If successful, monitor for 15 minutes
6. **00:20**: If failed, escalate to field technician
7. **00:30**: Field technician dispatched
8. **02:00**: Issue resolved (target)
9. Document root cause and prevention

### Charging Session Failure
1. Detect session failure
2. Check charger hardware status
3. Check vehicle compatibility
4. Review OCPP message logs
5. Identify failure point (charger/vehicle/network)
6. Attempt auto-rectification
7. If unsuccessful, guide user to alternative charger
8. Log incident for analysis
9. Update failure pattern database

### Performance Degradation
1. Detect slow charging speed
2. Check power supply stability
3. Verify cable and connector health
4. Check grid voltage levels
5. Analyze historical performance
6. If hardware issue, schedule maintenance
7. If grid issue, notify DISCOM
8. Provide user with estimated time

## Predictive Maintenance SOP

### Daily Health Scoring
1. Collect charger telemetry data
2. Run AI health assessment model
3. Generate health score (0-100) for each charger
4. Categorize:
   - 90-100: Excellent (green)
   - 70-89: Good (yellow)
   - 50-69: Fair (orange)
   - <50: Poor (red)
5. Schedule maintenance for scores < 70

### Maintenance Scheduling
1. Identify chargers with health score < 70
2. Predict failure probability
3. Estimate time to failure
4. Prioritize based on usage and criticality
5. Schedule during low-demand periods
6. Assign to field technician
7. Provide technician with diagnosis
8. Parts pre-ordered if needed
9. Execute maintenance
10. Verify health score improves post-maintenance

## Dynamic Pricing SOP

### Real-time Price Adjustment
1. Monitor grid load every 15 minutes
2. Check DISCOM tariff updates
3. Calculate demand on network
4. Determine pricing multiplier:
   - Low demand (<40%): 0.8x base price
   - Normal (40-70%): 1.0x base price
   - High (70-85%): 1.2x base price
   - Peak (>85%): 1.3x base price
5. Update pricing in real-time
6. Notify users of price changes
7. Log pricing decisions for analysis

### Price Optimization
1. Analyze historical demand patterns
2. Identify optimal pricing strategies
3. A/B test pricing models
4. Measure impact on:
   - Revenue
   - User satisfaction
   - Grid load distribution
   - Charger utilization
5. Refine pricing model monthly

## Energy Management SOP

### Load Balancing
1. Monitor total power consumption
2. Track individual charger load
3. When approaching 80% capacity:
   - Limit power to non-critical chargers
   - Prioritize critical vehicles
   - Queue new session requests
   - Notify users of wait time
4. Dynamically redistribute load
5. Log load balancing events

### Grid Integration
1. Receive real-time grid status from DISCOM
2. Adjust charging rates based on grid health
3. Support grid stabilization (V2G if available)
4. Shift non-urgent charging to off-peak
5. Coordinate with renewable energy availability
