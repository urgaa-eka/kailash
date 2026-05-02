# services/anomaly

Unsupervised anomaly detection (Isolation Forest).

```
POST /detect   { points: number[][], contamination?: number }
```

Returns per-sample `scores`, `labels` (1 inlier, -1 anomaly), `threshold`,
`n`, `n_anomalies`. Consumers: URGAA SLA, GSTSAAS fraud, Ignition charger
trust.
