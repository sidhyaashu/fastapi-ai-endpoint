import structlog

def get_logger():
    """Configures and returns a structlog logger."""
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(min_level=structlog.INFO),
        cache_logger_on_first_use=True,
    )
    return structlog.get_logger()

logger = get_logger()
