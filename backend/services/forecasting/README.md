# services/forecasting

Univariate time-series forecasting for demand, uptime, breakdowns, energy.

**Endpoint**

```
POST /forecast   { series: number[], horizon: int, season?: int }
```

Returns `yhat`, `yhat_lower`, `yhat_upper`, `method`. Default is a
light-weight EMA + trend (+ optional seasonal) baseline. Swap in Prophet
/ NeuralProphet / XGBoost by adding an alternate provider in
`app/service.py`.
