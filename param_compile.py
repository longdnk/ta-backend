import argparse


def param_compile():
    parser = argparse.ArgumentParser(description="Backend compile flags")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host of backend default is 127.0.0.1, deploy mode is 0.0.0.0",
    )
    parser.add_argument(
        "--port", type=int, default=9999, help="Port of api backend, default is 9999"
    )
    parser.add_argument(
        "--reload",
        type=int,
        default=1,
        help="Reload item default is true (1), false in deploy (set 0)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Multi process core running, use in production",
    )
    parser.add_argument(
        "--log_level",
        type=str,
        default="info",
        help="Default log level running, critical, error, warning, info, debug, trace",
    )
    parser.add_argument(
        "--use_colors",
        type=bool,
        default=True,
        help="Enable or disable color log in console",
    )
    parser.add_argument(
        "--limit_concurrency",
        type=int,
        default=10_000,
        help="Maximum number of concurrent connections or tasks to allow, before issuing HTTP 503 responses.",
    )
    parser.add_argument(
        "--limit_max_requests",
        type=int,
        default=1_000,
        help="Maximum number of requests to service before terminating the process.",
    )
    parser.add_argument(
        "--backlog",
        type=int,
        default=5000,
        help="Maximum number of connections to hold in backlog",
    )
    parser.add_argument(
        "--ssl_keyfile",
        type=str,
        default="",
        help="SSL key file, use when deploy in production",
    )
    parser.add_argument(
        "--ssl_certfile",
        type=str,
        default="",
        help="SSL certificate file, use when deploy in production",
    )
    parser.add_argument(
        "--web_socket_time",
        type=float,
        default=0.1,
        help="Web socket chat reload time"
    )
    parser.add_argument(
        "--model_temp",
        type=float,
        default=0.05,
        help="Model temparature"
    )
    parser.add_argument(
        "--prod",
        type=bool,
        default=False,
        help="Model temparature"
    )
    return parser.parse_args()


params = param_compile()