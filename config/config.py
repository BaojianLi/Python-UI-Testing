
from environs import Env
env = Env()
env.read_env()


environments = {
    "local": {
        "weather_url": "https://www.accuweather.com/",
        "booking_url": "https://www.booking.com/",
        "todo_url": "https://demo.playwright.dev/todomvc/#/",
    },
    "staging": {
        "weather_url": "https://www.accuweather.com/",
        "booking_url": "https://www.booking.com/",
        "todo_url": "https://demo.playwright.dev/todomvc/#/",
    },
    "integration": {
        "weather_url": "https://www.accuweather.com/",
        "booking_url": "https://www.booking.com/",
        "todo_url": "https://demo.playwright.dev/todomvc/#/",
    },
    "production": {
        "weather_url": "https://www.accuweather.com/",
        "booking_url": "https://www.booking.com/",
        "todo_url": "https://demo.playwright.dev/todomvc",
    },
}


def get_environment():
    """Always use the 'local' environment configuration."""
    app_env_name = env("APP_ENV", default="local")
    app_env = environments.get(app_env_name)
    print(f"Tests will be run against '{app_env_name}' environment: {app_env}")
    return app_env
