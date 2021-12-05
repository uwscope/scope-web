import scope.config

FLASK_CONFIGS = {
    "development_local": scope.config.FlaskConfig(
        baseurl="http://127.0.0.1:4000",
    ),
}
