import copy
import pymongo.database


def populate_account_from_config(
    *,
    database: pymongo.database.Database,
    populate_config_account: dict,
) -> dict:
    populate_config_account = copy.deepcopy(populate_config_account)

    return populate_config_account
