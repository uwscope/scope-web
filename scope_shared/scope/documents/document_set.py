# Allow typing to forward reference
# TODO: Not necessary with Python 3.11
from __future__ import annotations

from typing import Dict, Iterable, List, NewType, Optional, Tuple, Union


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

    def contains_all(
        self,
        *,
        documents: DocumentSet,
    ):
        """
        Return whether the set of documents contains all of the provided documents.
        """

        for document_current in documents:
            if document_current not in self.documents:
                return False

        return True

    def contains_any(
            self,
            *,
            documents: DocumentSet,
    ):
        """
        Return whether the set of documents contains any of the provided documents.
        """

        for document_current in documents:
            if document_current in self.documents:
                return True

        return False

    @property
    def documents(self) -> List[dict]:
        """
        Access the contained set of documents.
        """
        return self._documents

    @staticmethod
    def _match_document(
        document: dict,
        match_type: Optional[str],
        match_values: Optional[Dict[str, str]] = None,
    ) -> bool:
        tested: bool = False
        matches: bool = True

        if matches and match_type:
            tested = True
            matches = matches and document["_type"] == match_type

        if matches and match_values:
            tested = True
            for key_current, value_current in match_values.items():
                matches = matches and key_current in document
                matches = matches and document[key_current] == value_current

        if not tested:
            raise ValueError('At least one match parameter must be provided')

        return matches

    def filter_match(
        self,
        match_type: Optional[str] = None,
        match_values: Optional[Dict[str, str]] = None,
    ) -> DocumentSet:
        """
        Keep only documents that match all provided parameters.
        """

        retained_documents = []
        for document_current in self:
            matches: bool = DocumentSet._match_document(
                document=document_current,
                match_type=match_type,
                match_values=match_values,
            )

            if matches:
                retained_documents.append(document_current)

        return DocumentSet(documents=retained_documents)

    def remove_match(
        self,
        match_type: Optional[str] = None,
        match_values: Optional[Dict[str, str]] = None,
    ) -> DocumentSet:
        """
        Remove any documents that match all provided parameters.
        """

        retained_documents = []
        for document_current in self:
            matches: bool = DocumentSet._match_document(
                document=document_current,
                match_type=match_type,
                match_values=match_values,
            )

            if not matches:
                retained_documents.append(document_current)

        return DocumentSet(documents=retained_documents)

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

    def union(
        self,
        *,
        documents: DocumentSet,
    ):
        """
        Union this set with the provided documents.
        """

        retained_documents = list(self.documents)
        for document_current in documents:
            if document_current not in retained_documents:
                retained_documents.append(document_current)

        return DocumentSet(documents=retained_documents)
