"""Anomaly detection using Isolation Forest."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from sklearn.ensemble import IsolationForest

from backend.shared import ValidationError


@dataclass
class AnomalyResult:
    n: int
    n_anomalies: int
    scores: list[float]
    labels: list[int]  # 1 = inlier, -1 = anomaly
    threshold: float


def detect(points: Sequence[Sequence[float]], contamination: float = 0.05) -> AnomalyResult:
    if not points:
        raise ValidationError("empty dataset")
    if not 0.0 < contamination < 0.5:
        raise ValidationError("contamination must be in (0, 0.5)")
    X = np.asarray(points, dtype=float)
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    if X.shape[0] < 8:
        raise ValidationError("need at least 8 samples for robust detection")

    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=42,
    )
    model.fit(X)
    scores = model.decision_function(X)
    labels = model.predict(X)
    threshold = float(np.quantile(scores, contamination))
    return AnomalyResult(
        n=int(X.shape[0]),
        n_anomalies=int(np.sum(labels == -1)),
        scores=scores.astype(float).tolist(),
        labels=labels.astype(int).tolist(),
        threshold=threshold,
    )
