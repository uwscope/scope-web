from pprint import pprint
import pymongo.database
import pytest
import random
import string
from typing import Callable


@pytest.mark.parametrize(
    ["size"],
    [
        [1 * 1024],
        [30 * 1024],
        # Previously observed a failure near 32k due to SSH issues
        [35 * 1024],
        [64 * 1024],
        [1024 * 1024],
    ],
    ids=[
        "1k",
        "< 32k",
        "> 32k",
        "64k",
        "1M",
    ],
)
def test_database_put_size(
    database_temp_collection_factory: Callable[[], pymongo.collection.Collection],
    size: int,
):
    """
    Test insertion of a document of a specific size.
    """

    collection = database_temp_collection_factory()
    content = "".join(random.choice(string.ascii_letters) for _ in range(size))

    collection.insert_one(
        document={
            "content": content,
        },
    )
