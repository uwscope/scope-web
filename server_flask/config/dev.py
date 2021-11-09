import ruamel.yaml

# Path is relative to server_flask
DOCUMENT_DB_CONFIG_PATH = "../secrets/server/dev/documentdb_config.yaml"


class Config:
    # TODO James: In production SECRET_KEY needs to be consistent across instances
    SECRET_KEY: str = "development"

    DB_USER: str
    DB_PASSWORD: str
    DATABASE: str

    def __init__(self):
        with open(DOCUMENT_DB_CONFIG_PATH) as file_document_db_config:
            document_db_client_config = ruamel.yaml.safe_load(file_document_db_config)

        self.DATABASE = document_db_client_config["database"]
        self.DB_USER = document_db_client_config["admin_user"]
        self.DB_PASSWORD = document_db_client_config["admin_password"]
