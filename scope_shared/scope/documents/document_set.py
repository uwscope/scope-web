# Allow typing to forward reference
# TODO: Not necessary with Python 3.11
from __future__ import annotations

from typing import Dict, Iterable, List, NewType, Tuple, Union


DocumentType = NewType('DocumentType', str)
SetId = NewType('SetId', str)
DocumentKey = Union[Tuple[DocumentType], Tuple[DocumentType, SetId]]

class DocumentSet:
    """
    A set of documents that are all from the same collection.
    """

    _documents: List[dict]

    def __init__(
        self,
        *,
        documents: Iterable[dict] = None,
    ):
        """
        Create a set containing a shallow copy of the provided documents.
        """
        if not documents:
            documents = []

        self._documents = list(documents)

    def __iter__(self) -> Iterable[dict]:
        """
        Iterate over contained documents.
        """
        return iter(self.documents)

    @property
    def documents(self) -> List[dict]:
        """
        Access the contained set of documents.
        """
        return self._documents

    def remove_revisions(self) -> DocumentSet:
        """
        Remove any prior revisions of documents.
        """

        current_revisions: Dict[DocumentKey, dict] = {}
        for document_current in self:
            # Singletons have only a _type, while set elements also have a _set_id
            key_current = document_current["_type"]
            if "_set_id" in document_current:
                key_current = (
                    document_current["_type"],
                    document_current["_set_id"],
                )

            # Keep one document for each key
            document_existing = current_revisions.get(key_current, None)
            if document_existing:
                # If we already have a document for this key, keep only the greatest revision
                if int(document_current["_rev"]) > int(document_existing["_rev"]):
                    current_revisions[key_current] = document_current
            else:
                current_revisions[key_current] = document_current

        return DocumentSet(
            documents=current_revisions.values()
        )

    def remove_sentinel(self) -> DocumentSet:
        """
        If the DocumentSet includes a sentinel document, remove it.
        """

        return DocumentSet(
            documents=(
                document_current
                for document_current in self
                if document_current["_type"] != "sentinel"
            )
        )
