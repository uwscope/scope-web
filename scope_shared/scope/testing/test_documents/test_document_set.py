from scope.documents.document_set import DocumentSet


def test_document_set_constructor_shallow_copies_documents():
    """
    DocumentSet should shallow copy the provided documents.
    """

    original_documents = [
        {
            "key": "value",
        },
        {
            "key": "value",
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


def test_document_set_contains():
    document_set = DocumentSet(
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
        documents=DocumentSet(
            documents=[
                {
                    "key": "value"
                },
                {
                    "key": "other value"
                },
            ]
        )
    )

    assert not document_set.contains_all(
        documents=DocumentSet(
            documents=[
                {
                    "key": "value"
                },
                {
                    "key": "missing value"
                },
            ]
        )
    )

    assert document_set.contains_any(
        documents=DocumentSet(
            documents=[
                {
                    "key": "value"
                },
            ]
        )
    )

    assert not document_set.contains_any(
        documents=DocumentSet(
            documents=[
                {
                    "key": "missing value"
                },
            ]
        )
    )


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
    document_set_removed = document_set_combined.remove_match(**match_args)

    assert document_set_filtered.contains_all(documents=document_set_matching)
    assert not document_set_filtered.contains_any(documents=document_set_not_matching)

    assert document_set_removed.contains_all(documents=document_set_not_matching)
    assert not document_set_removed.contains_any(documents=document_set_matching)


def test_document_set_remove_revisions():
    original_documents = [
        {
            "_type": "type",
            "_rev": "3",
        },
        {
            "_type": "type",
            "_rev": "20",
        },
        {
            "_type": "set type",
            "_set_id": "set id",
            "_rev": "3",
        },
        {
            "_type": "set type",
            "_set_id": "set id",
            "_rev": "20",
        },
        {
            "_type": "set type",
            "_set_id": "other set id",
            "_rev": "30",
        },
        {
            "_type": "set type",
            "_set_id": "other set id",
            "_rev": "4",
        },
    ]

    document_set = DocumentSet(documents=original_documents)
    document_set = document_set.remove_revisions()
    document_set = DocumentSet(
        documents=sorted(
            document_set.documents,
            key=lambda document: original_documents.index(document),
        )
    )

    assert document_set.documents == [
        {
            "_type": "type",
            "_rev": "20",
        },
        {
            "_type": "set type",
            "_set_id": "set id",
            "_rev": "20",
        },
        {
            "_type": "set type",
            "_set_id": "other set id",
            "_rev": "30",
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
