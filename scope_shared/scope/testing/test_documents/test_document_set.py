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


def test_document_set_remove_revisions():
    original_documents=[
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
