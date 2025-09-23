from prometheus_client import Counter, Histogram, Gauge
import re

# HTTP request metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    buckets=(
        0.005,
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        1.0,
        2.5,
        5.0,
        10.0,
    ),
    labelnames=["method", "path"],
)

# Domain metrics
COFFEE_LOGGED_TOTAL = Counter(
    "coffee_logged_total", "Total coffee entries logged", ["type"]
)

CAFFEINE_MG_TOTAL = Counter(
    "caffeine_mg_total", "Total caffeine mg logged"
)

# Last coffee info
COFFEE_LAST_TIMESTAMP_SECONDS = Gauge(
    "coffee_last_timestamp_seconds", "Unix timestamp of the last coffee event"
)
CAFFEINE_LAST_MG = Gauge(
    "caffeine_last_mg", "Caffeine amount (mg) of the last coffee event"
)

HEARTRATE_LOGGED_TOTAL = Counter(
    "heartrate_logged_total", "Total heart rate readings logged", ["context"]
)

HEARTRATE_GAUGE = Gauge(
    "heartrate_bpm_current", "Most recent heart rate BPM"
)
HEARTRATE_LAST_TIMESTAMP_SECONDS = Gauge(
    "heartrate_last_timestamp_seconds", "Unix timestamp of the last heart rate reading"
)


def observe_request(method: str, path: str, status_code: int, duration_s: float) -> None:
    # Collapse numeric IDs to avoid high cardinality
    sanitized_path = re.sub(r"/(?:\d+)(?=/|$)", "/:id", path)
    REQUEST_COUNT.labels(method=method, path=sanitized_path,
                         status_code=str(status_code)).inc()
    REQUEST_LATENCY.labels(
        method=method, path=sanitized_path).observe(duration_s)
