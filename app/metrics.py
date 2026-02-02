from prometheus_client import Counter, Gauge

# Coffee metrics
COFFEE_LOGGED_TOTAL = Counter(
    'coffee_logged_total',
    'Total number of coffee logs',
    ['user_id']
)

CAFFEINE_MG_TOTAL = Counter(
    'caffeine_mg_total',
    'Total caffeine in mg consumed'
)

COFFEE_LAST_TIMESTAMP_SECONDS = Gauge(
    'coffee_last_timestamp_seconds',
    'Timestamp of last coffee log'
)

CAFFEINE_LAST_MG = Gauge(
    'caffeine_last_mg',
    'Caffeine amount in mg of last coffee'
)

