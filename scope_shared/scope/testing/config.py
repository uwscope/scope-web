import scope.config

FLASK_CONFIGS = {
    "development_local": scope.config.FlaskConfig(
        baseurl="http://localhost:4000",
    ),
}
