from pathlib import Path
from typing import Union

import scope.config
from config.base import Config


class ProductionConfig(Config):
    def __init__(self, *, instance_dir: Union[Path, str]):
        flask_config_path = Path(instance_dir, "flask_config.yaml")
        flask_config = scope.config.FlaskConfig.load(flask_config_path)

        Config.__init__(
            self=self,
            secret_key=flask_config.secret_key,
            cognito_poolid=flask_config.cognito_poolid,
            cognito_clientid=flask_config.cognito_clientid,
            documentdb_host=flask_config.documentdb_host,
            documentdb_port=flask_config.documentdb_port,
            documentdb_directconnection=flask_config.documentdb_directconnection,
            documentdb_tlsinsecure=flask_config.documentdb_tlsinsecure,
            database_name=flask_config.database_name,
            database_user=flask_config.database_user,
            database_password=flask_config.database_password,
        )
