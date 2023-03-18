from datetime import datetime, timedelta
import pytest
import pytz

from scope.documents.document_set import document_id_from_datetime, DocumentSet


def test_document_set_constructor_enforces_unique():
    """
    DocumentSet should shallow copy the provided documents.
    """

    original_documents = [
        {
            "key": "value",
        },
        {
            "key": "other value",
        },
        {
            "key": "duplicate value",
        },
        {
            "key": "duplicate value",
        },
    ]

    with pytest.raises(ValueError):
        DocumentSet(documents=original_documents)


def test_document_set_constructor_shallow_copies_documents():
    """
    DocumentSet should shallow copy the provided documents.
    """

    original_documents = [
        {
            "key": "value",
        },
        {
            "key": "other value",
        },
    ]

    document_set = DocumentSet(documents=original_documents)
    assert original_documents == document_set.documents

    # Modifying a key within a document should change both
    original_documents[0]["key"] = "different value"
    assert original_documents == document_set.documents

    # Deleting a document should only change one
    del original_documents[0]
    assert original_documents != document_set.documents


def test_document_set_group_revisions():
    original_documents = [
        {
            "_type": "type",
            "_rev": 3,
        },
        {
            "_type": "type",
            "_rev": 20,
        },
        {
            "_type": "set type",
            "_set_id": "set id",
            "_rev": 3,
        },
        {
            "_type": "set type",
            "_set_id": "set id",
            "_rev": 20,
        },
        {
            "_type": "set type",
            "_set_id": "other set id",
            "_rev": 30,
        },
        {
            "_type": "set type",
            "_set_id": "other set id",
            "_rev": 4,
        },
    ]

    assert DocumentSet(documents=original_documents).group_revisions() == {
        ("type", ): [
            {
                "_type": "type",
                "_rev": 3,
            },
            {
                "_type": "type",
                "_rev": 20,
            },
        ],
        ("set type", "set id"): [
            {
                "_type": "set type",
                "_set_id": "set id",
                "_rev": 3,
            },
            {
                "_type": "set type",
                "_set_id": "set id",
                "_rev": 20,
            },
        ],
        ("set type", "other set id"): [
            {
                "_type": "set type",
                "_set_id": "other set id",
                "_rev": 4,
            },
            {
                "_type": "set type",
                "_set_id": "other set id",
                "_rev": 30,
            },
        ],
    }


def test_document_set_contains():
    document_set = DocumentSet(
        documents=[
            {
                "key": "value"
            },
            {
                "key": "other value"
            },
            {
                "key": "another value"
            },
        ]
    )

    assert document_set.contains_all(
        documents=[
            {
                "key": "value"
            },
            {
                "key": "other value"
            },
        ]
    )

    assert document_set.contains_all(
        documents=[
            {
                "key": "value"
            },
            {
                "key": "other value"
            },
            {
                "key": "another value"
            },
        ]
    )

    assert not document_set.contains_all(
        documents=[
            {
                "key": "value"
            },
            {
                "key": "missing value"
            },
        ]
    )

    assert document_set.contains_any(
        documents=[
            {
                "key": "value"
            },
        ]
    )

    assert not document_set.contains_any(
        documents=[
            {
                "key": "missing value"
            },
        ]
    )


def test_document_set_eq():
    document_set = DocumentSet(
        documents=[
            {
                "key": "first value"
            },
            {
                "key": "second value"
            },
        ]
    )

    # Non-iterable comparison
    assert document_set != 0

    # Another document set
    assert document_set == DocumentSet(
        documents=[
            {
                "key": "first value"
            },
            {
                "key": "second value"
            },
        ]
    )

    # A list
    assert document_set == [
        {
            "key": "first value"
        },
        {
            "key": "second value"
        },
    ]

    # Order is not considered
    assert document_set == [
        {
            "key": "second value"
        },
        {
            "key": "first value"
        },
    ]

    # Missing item
    assert document_set != [
        {
            "key": "first value"
        },
    ]

    # Different item
    assert document_set != [
        {
            "key": "first value"
        },
        {
            "key": "different value"
        },
    ]


def test_document_set_match():
    document_set_matching = DocumentSet(documents=[
        {
            "_type": "matching",
            "match_value_key": "matching",
        },
    ])

    document_set_not_matching = DocumentSet(documents=[
        {
            "_type": "not matching",
            "match_value_key": "matching",
        },
        {
            "_type": "matching",
            "match_value_key": "not matching",
        },
    ])

    match_args = {
        "match_type": "matching",
        "match_values": {
            "match_value_key": "matching",
        }
    }

    document_set_combined = document_set_matching.union(documents=document_set_not_matching)

    document_set_filtered = document_set_combined.filter_match(**match_args)
    assert document_set_filtered.contains_all(documents=document_set_matching)
    assert not document_set_filtered.contains_any(documents=document_set_not_matching)

    document_set_removed = document_set_combined.remove_match(**match_args)
    assert document_set_removed.contains_all(documents=document_set_not_matching)
    assert not document_set_removed.contains_any(documents=document_set_matching)


def test_document_set_match_deleted():
    document_set = DocumentSet(documents=[
        {
            "_type": "test",
        },
        {
            "_type": "test",
            "_deleted": True,
        },
    ])

    assert document_set.filter_match(
        match_type="test",
    ) == [
        {
            "_type": "test",
        },
        {
            "_type": "test",
            "_deleted": True,
        },
    ]

    assert document_set.filter_match(
        match_type="test",
        match_deleted=False,
    ) == [
        {
            "_type": "test",
        },
    ]

    assert document_set.filter_match(
        match_type="test",
        match_deleted=True,
    ) == [
        {
            "_type": "test",
            "_deleted": True,
        },
    ]

    assert document_set.remove_match(
        match_type="test",
    ) == [
    ]

    assert document_set.remove_match(
        match_type="test",
        match_deleted=False,
    ) == [
        {
            "_type": "test",
            "_deleted": True,
        },
    ]

    assert document_set.remove_match(
        match_type="test",
        match_deleted=True,
    ) == [
        {
            "_type": "test",
        },
    ]


def test_document_set_match_datetime_at():
    datetime_rev1 = pytz.utc.localize(datetime(
        year=2023,
        month=3,
        day=11,
        hour=7,
        minute=0,
        second=0,
        microsecond=0,
    ))
    document_rev1 = {
        "_id": document_id_from_datetime(
            generation_time=datetime_rev1
        ),
        "_type": "type",
        "_rev": 1,
    }

    datetime_rev2 = datetime_rev1 + timedelta(days=1)
    document_rev2 = {
        "_id": document_id_from_datetime(
            generation_time=datetime_rev2
        ),
        "_type": "type",
        "_rev": 2,
    }

    datetime_rev3 = datetime_rev2 + timedelta(hours=1)
    document_rev3 = {
        "_id": document_id_from_datetime(
            generation_time=datetime_rev3
        ),
        "_type": "type",
        "_rev": 3,
    }

    # The encoding within _id is only to the second.
    # This is effectively at the same time as rev3.
    datetime_rev4 = datetime_rev3 + timedelta(milliseconds=1)
    document_rev4 = {
        "_id": document_id_from_datetime(
            generation_time=datetime_rev4
        ),
        "_type": "type",
        "_rev": 4,
    }

    document_other_type = {
        "_id": document_id_from_datetime(
            generation_time=datetime_rev1
        ),
        "_type": "other type",
        "_rev": 1,
    }

    # The internal implementation of match_date_time_at is based on sorting by revision
    # Ensure documents are not already sorted by revision
    document_set = DocumentSet(documents=[
        document_other_type,
        document_rev4,
        document_rev3,
        document_rev2,
        document_rev1,
    ])

    # Before our initial documents should be an empty set
    assert document_set.filter_match(
        match_datetime_at=datetime_rev1 - timedelta(days=1),
    ) == [
    ]

    # Same time as our initial documents should be both of them
    assert document_set.filter_match(
        match_datetime_at=datetime_rev1,
    ) == [
        document_rev1,
        document_other_type
    ]

    # An additional filter for type
    assert document_set.filter_match(
        match_type="type",
        match_datetime_at=datetime_rev1,
    ) == [
        document_rev1,
    ]

    # Because rev3 and rev4 are effectively the same time, prefer the later revision
    assert document_set.filter_match(
        match_type="type",
        match_datetime_at=datetime_rev3,
    ) == [
        document_rev4,
    ]

    # Because rev3 and rev4 are effectively the same time, prefer the later revision
    assert document_set.filter_match(
        match_type="type",
        match_datetime_at=datetime_rev4,
    ) == [
        document_rev4,
    ]

    # In the future should still be rev4
    assert document_set.filter_match(
        match_datetime_at=datetime_rev4 + timedelta(days=1),
    ) == [
        document_rev4,
        document_other_type
    ]


def test_document_set_order_by_revisions():
    # This test purposefully uses strings for "_rev" to ensure that error gets handled correctly.
    # "_rev" should be an integer, and enforcing that elsewhere would allow simplifying this test
    # and the logic of DocumentSet.order_by_revisions that currently ensures robustness to string values.

    document_set = DocumentSet(documents=[
        {
            "_type": "type",
            "_rev": "20",
        },
        {
            "_type": "type",
            "_rev": "30",
        },
        {
            "_type": "type",
            "_rev": "4",
        },
        {
            "_type": "other type",
            "_rev": "1",
        },
    ])

    # A mixed set should error
    with pytest.raises(ValueError):
        document_set.order_by_revision()

    assert document_set.filter_match(
        match_type="type",
    ).order_by_revision() == [
        {
            "_type": "type",
            "_rev": "4",
        },
        {
            "_type": "type",
            "_rev": "20",
        },
        {
            "_type": "type",
            "_rev": "30",
        },
    ]


def test_document_set_remove_documents():
    document_set = DocumentSet(
        documents=[
            {
                "key": "first value"
            },
            {
                "key": "second value"
            },
            {
                "key": "third value"
            },
        ]
    )

    assert document_set.remove_any(
        documents=[
            {
                "key": "first value"
            },
            {
                "key": "first value"
            },
            {
                "key": "missing value"
            },
        ]
    ) == [
        {
            "key": "second value"
        },
        {
            "key": "third value"
        },
    ]

    assert document_set.remove_all(
        documents=[
            {
                "key": "first value"
            },
        ]
    ) == [
        {
            "key": "second value"
        },
        {
            "key": "third value"
        },
    ]

    with pytest.raises(ValueError):
        assert document_set.remove_all(
            documents=[
                {
                    "key": "first value"
                },
                {
                    "key": "first value"
                },
            ]
        )

    with pytest.raises(ValueError):
        assert document_set.remove_all(
            documents=[
                {
                    "key": "missing value"
                },
            ]
        )


def test_document_set_remove_revisions():
    original_documents = [
        {
            "_type": "type",
            "_rev": 3,
        },
        {
            "_type": "type",
            "_rev": 20,
        },
        {
            "_type": "set type",
            "_set_id": "set id",
            "_rev": 3,
        },
        {
            "_type": "set type",
            "_set_id": "set id",
            "_rev": 20,
        },
        {
            "_type": "set type",
            "_set_id": "other set id",
            "_rev": 30,
        },
        {
            "_type": "set type",
            "_set_id": "other set id",
            "_rev": 4,
        },
    ]

    document_set = DocumentSet(documents=original_documents)
    document_set = document_set.remove_revisions()

    assert document_set.documents == [
        {
            "_type": "type",
            "_rev": 20,
        },
        {
            "_type": "set type",
            "_set_id": "set id",
            "_rev": 20,
        },
        {
            "_type": "set type",
            "_set_id": "other set id",
            "_rev": 30,
        },
    ]


def test_document_set_remove_sentinel():
    document_set = DocumentSet(
        documents=[
            {
                "_type": "sentinel",
            },
            {
                "_type": "type",
            },
        ]
    )

    document_set = document_set.remove_sentinel()

    assert document_set.documents == [
        {
            "_type": "type",
        },
    ]
