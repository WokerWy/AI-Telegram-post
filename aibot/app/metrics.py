from prometheus_client import Counter, Histogram

posts_sent = Counter(
    "telegram_posts_sent_total",
    "Total sent posts"
)

posts_failed = Counter(
    "telegram_posts_failed_total",
    "Total failed posts"
)

post_latency = Histogram(
    "telegram_post_send_latency_seconds",
    "Post send latency"
)
