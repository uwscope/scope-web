# Allow typing to forward reference
# TODO: Not necessary with Python 3.11
from __future__ import annotations

import scope.populate.data.archive
import scope.schema
import scope.schema_utils


def validate_archive(archive: scope.populate.data.archive.Archive):
    _validate_expected_collections(archive=archive)

    # Validate every document matches the document schema
    for document_current in archive.entries.values():
        # Assert the document schema
        scope.schema_utils.assert_schema(
            data=document_current,
            schema=scope.schema.document_schema,
        )


def _validate_expected_collections(archive: scope.populate.data.archive.Archive):
    """
    Validate existence of expected collections.
    """

    # We expect every collection to be referenced
    unreferenced_collections = archive.collections()
    assert "patients" in unreferenced_collections
    unreferenced_collections.remove("patients")
    assert "providers" in unreferenced_collections
    unreferenced_collections.remove("providers")

    # Ensure every referenced patient collection exists
    patients_documents = archive.collection_documents(collection="patients")
    patients_documents = patients_documents.remove_sentinel()
    patients_documents = patients_documents.remove_revisions()

    for patients_document_current in patients_documents:
        # Ensure these documents cannot be deleted
        # TODO: This is also implied by the schema.
        #       If we had a cleaner hierarchy of schemas, it could be more explicit and this could be removed.
        assert "_deleted" not in patients_document_current

        # Track that each referenced collection exists and is referenced exactly once
        referenced_collection_current = patients_document_current["collection"]
        assert referenced_collection_current in unreferenced_collections
        unreferenced_collections.remove(referenced_collection_current)

    # Every collection should now have been referenced
    assert len(unreferenced_collections) == 0

