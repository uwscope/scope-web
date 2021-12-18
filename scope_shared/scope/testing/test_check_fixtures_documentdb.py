import pymongo


def test_documentdb_client_admin(
    documentdb_client_admin: pymongo.MongoClient,
):
    """
    Test for documentdb_client_admin.
    """

    assert documentdb_client_admin
