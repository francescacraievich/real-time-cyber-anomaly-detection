"""
Prometheus metrics registry for Cyber Anomaly Detection system.
Centralizes all metric definitions for ML model monitoring.
"""

from prometheus_client import REGISTRY, Counter, Gauge, Histogram, Info, generate_latest

# Track which metrics have been created to avoid duplicates
_metrics_cache = {}


def _get_or_create_gauge(name, description, labelnames=None):
    """Get existing gauge or create new one."""
    if name in _metrics_cache:
        return _metrics_cache[name]
    try:
        if labelnames:
            metric = Gauge(name, description, labelnames)
        else:
            metric = Gauge(name, description)
        _metrics_cache[name] = metric
        return metric
    except ValueError:
        # Already registered - find it in cache or registry
        for collector in REGISTRY._names_to_collectors.values():
            if hasattr(collector, "_name") and collector._name == name:
                _metrics_cache[name] = collector
                return collector
        raise


def _get_or_create_counter(name, description, labelnames=None):
    """Get existing counter or create new one."""
    if name in _metrics_cache:
        return _metrics_cache[name]
    try:
        if labelnames:
            metric = Counter(name, description, labelnames)
        else:
            metric = Counter(name, description)
        _metrics_cache[name] = metric
        return metric
    except ValueError:
        for collector in REGISTRY._names_to_collectors.values():
            if hasattr(collector, "_name") and collector._name == name:
                _metrics_cache[name] = collector
                return collector
        raise


def _get_or_create_histogram(name, description, labelnames=None, buckets=None):
    """Get existing histogram or create new one."""
    if name in _metrics_cache:
        return _metrics_cache[name]
    try:
        kwargs = {}
        if labelnames:
            kwargs["labelnames"] = labelnames
        if buckets:
            kwargs["buckets"] = buckets
        metric = Histogram(name, description, **kwargs)
        _metrics_cache[name] = metric
        return metric
    except ValueError:
        for collector in REGISTRY._names_to_collectors.values():
            if hasattr(collector, "_name") and collector._name == name:
                _metrics_cache[name] = collector
                return collector
        raise


def _get_or_create_info(name, description):
    """Get existing info or create new one."""
    if name in _metrics_cache:
        return _metrics_cache[name]
    try:
        metric = Info(name, description)
        _metrics_cache[name] = metric
        return metric
    except ValueError:
        for collector in REGISTRY._names_to_collectors.values():
            if hasattr(collector, "_name") and collector._name == name:
                _metrics_cache[name] = collector
                return collector
        raise


# ============ MODEL PERFORMANCE METRICS ============

model_precision = _get_or_create_gauge(
    "anomaly_detection_precision", "Current model precision score (0-1)"
)

model_recall = _get_or_create_gauge(
    "anomaly_detection_recall", "Current model recall score (0-1)"
)

model_f1_score = _get_or_create_gauge(
    "anomaly_detection_f1_score", "Current model F1-score (0-1)"
)

detection_rate = _get_or_create_gauge(
    "anomaly_detection_detection_rate", "Attack detection rate TP / (TP + FN)"
)

false_alarm_rate = _get_or_create_gauge(
    "anomaly_detection_false_alarm_rate", "False alarm rate FP / (FP + TN)"
)

confusion_matrix = _get_or_create_gauge(
    "anomaly_detection_confusion_matrix",
    "Confusion matrix values",
    ["actual", "predicted"],
)

decision_score_histogram = _get_or_create_histogram(
    "anomaly_detection_decision_score",
    "Distribution of model decision scores",
    buckets=[-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 3, 5],
)

threshold_boundary = _get_or_create_gauge(
    "anomaly_detection_threshold_boundary", "Current decision threshold boundary"
)

# ============ DRIFT DETECTION METRICS ============

anomaly_rate_gauge = _get_or_create_gauge(
    "anomaly_detection_anomaly_rate", "Current anomaly rate in sliding window (0-1)"
)

drift_detected_total = _get_or_create_counter(
    "anomaly_detection_drift_detected_total", "Total number of drift events detected"
)

drift_detected_flag = _get_or_create_gauge(
    "anomaly_detection_drift_status",
    "Binary flag: 1 if drift currently detected, 0 otherwise",
)

samples_since_drift = _get_or_create_gauge(
    "anomaly_detection_samples_since_drift",
    "Number of samples processed since last drift reset",
)

model_retrain_total = _get_or_create_counter(
    "anomaly_detection_model_retrain_total", "Total number of model retraining events"
)

retrain_buffer_size = _get_or_create_gauge(
    "anomaly_detection_retrain_buffer_size",
    "Current retrain buffer occupancy (max 5000)",
)

# ============ PREDICTION METRICS ============

predictions_total = _get_or_create_counter(
    "anomaly_detection_predictions_total",
    "Total predictions by severity level",
    ["severity"],
)

samples_processed_total = _get_or_create_counter(
    "anomaly_detection_samples_processed_total", "Total samples processed by the model"
)

anomalies_detected_total = _get_or_create_counter(
    "anomaly_detection_anomalies_detected_total",
    "Total anomalies detected (ORANGE + RED)",
)

severity_distribution = _get_or_create_gauge(
    "anomaly_detection_severity_distribution",
    "Current severity distribution percentage",
    ["severity"],
)

attack_detection_rate_by_type = _get_or_create_gauge(
    "anomaly_detection_attack_detection_rate_by_type",
    "Detection rate per attack type",
    ["attack_type"],
)

# ============ SYSTEM/API METRICS ============

prediction_latency = _get_or_create_histogram(
    "anomaly_detection_prediction_latency_seconds",
    "Time to predict a batch of samples",
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5],
)

api_request_duration = _get_or_create_histogram(
    "anomaly_detection_api_request_duration_seconds",
    "API request duration in seconds",
    labelnames=["endpoint", "method"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

api_requests_total = _get_or_create_counter(
    "anomaly_detection_api_requests_total", "Total API requests", ["endpoint", "status"]
)

model_loaded_gauge = _get_or_create_gauge(
    "anomaly_detection_model_loaded", "Binary: 1 if model is loaded, 0 otherwise"
)

dataset_size_gauge = _get_or_create_gauge(
    "anomaly_detection_dataset_size", "Number of records in the loaded dataset"
)

# ============ MODEL INFO ============

model_info = _get_or_create_info(
    "anomaly_detection_model", "Model configuration information"
)


def get_metrics():
    """Generate Prometheus metrics output"""
    return generate_latest(REGISTRY)
