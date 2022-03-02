import pymongo.database


def populate_from_config(
    *,
    database: pymongo.database.Database,
    populate_config: dict
) -> dict:
    """
    Populate from a provided config.

    Return a new state of the populate config.
    """

    return populate_config
