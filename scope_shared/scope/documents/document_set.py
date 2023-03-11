# Allow typing to forward reference
# TODO: Not necessary with Python 3.11
from __future__ import annotations

import bson.objectid
from datetime import datetime
import pytz
import secrets
from typing import Dict, Iterable, List, NewType, Optional, Tuple, Union

# This will allow either until we actually have a Document type
Document = Union[NewType("Document", dict), dict]

DocumentType = NewType('DocumentType', str)
SetId = NewType('SetId', str)
DocumentKey = Union[Tuple[DocumentType], Tuple[DocumentType, SetId]]


def datetime_from_document(
    *,
    document: dict,
) -> datetime:
    return bson.objectid.ObjectId(document["_id"]).generation_time.astimezone(pytz.utc)


def document_id_from_datetime(
    generation_time: datetime,
) -> str:
    hex_datetime = str(bson.objectid.ObjectId.from_datetime(
        generation_time=generation_time
    ))[0:8]

    hex_random = secrets.token_hex(8)

    return hex_datetime + hex_random


def document_key(
    *,
    document: Document
) -> DocumentKey:
    """
    Obtain a key for the provided document.
    """

    key = (
        document["_type"],
    )
    if "_set_id" in document:
        key = (
            document["_type"],
            document["_set_id"],
        )

    return key


class DocumentSet:
    """
    A set of documents that are all from the same collection.
    """

    _documents: List[dict]
    _revisions: Optional[Dict[DocumentKey, DocumentSet]]

    def __init__(
        self,
        *,
        documents: Iterable[dict] = None,
    ):
        """
        Create a set containing a shallow copy of the provided documents.

        Ensures the provided documents are unique.
        """
        if not documents:
            documents = []

        retained_documents = []
        for document_current in documents:
            if document_current in retained_documents:
                raise ValueError

            retained_documents.append(document_current)

        self._documents = retained_documents
        self._revisions = None

    def contains_all(
        self,
        *,
        documents: Iterable[dict] = None,
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
        documents: Iterable[dict] = None,
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

    def __eq__(self, other) -> bool:
        """
        Equal to any iterable containing equivalent objects in any order.
        """

        # Obtain a list of items
        try:
            other_items: List = list(iter(other))
        except TypeError:
            return False

        # If the lists are not the same length, we cannot be equal
        if len(self) != len(other_items):
            return False

        # Every item in our set must appear exactly once in the other items
        for item_current in self:
            try:
                other_items.remove(item_current)
            except ValueError:
                return False

        return True

    def __len__(self) -> int:
        """
        Number of documents in the set.
        """
        return len(self.documents)

    def filter_match(
        self,
        match_type: Optional[str] = None,
        match_deleted: Optional[bool] = None,
        match_datetime_at: Optional[datetime] = None,
        match_values: Optional[Dict[str, str]] = None,
    ) -> DocumentSet:
        """
        Keep only documents that match all provided parameters.
        """

        retained_documents = []
        for document_current in self:
            matches: bool = self._match_document(
                document=document_current,
                match_type=match_type,
                match_deleted=match_deleted,
                match_datetime_at=match_datetime_at,
                match_values=match_values,
            )

            if matches:
                retained_documents.append(document_current)

        return DocumentSet(documents=retained_documents)

    def is_unique(self) -> bool:
        """
        Whether this set contains exactly one document.
        """
        return len(self) == 1

    def __iter__(self) -> Iterable[dict]:
        """
        Iterate over contained documents.
        """
        return iter(self.documents)

    def _match_document(
        self,
        document: dict,
        match_type: Optional[str],
        match_deleted: Optional[bool],
        match_datetime_at: Optional[datetime],
        match_values: Optional[Dict[str, str]],
    ) -> bool:
        tested: bool = False
        matches: bool = True

        if matches and match_type:
            tested = True
            matches = matches and document["_type"] == match_type

        if matches and match_deleted is not None:
            tested = True
            matches = matches and match_deleted == document.get("_deleted", False)

        if matches and match_datetime_at is not None:
            tested = True

            if match_datetime_at < datetime_from_document(document=document):
                # A document created after our match time cannot match
                matches = matches and False
            else:
                # A document created at or before our match time
                # matches if no revision replaces it before the match time
                revisions = self.revisions[document_key(document=document)]
                revision_index = revisions.documents.index(document)
                if revision_index + 1 == len(revisions):
                    # The current document is the final revision
                    matches = matches and True
                else:
                    # There is a document after this
                    datetime_next_revision = datetime_from_document(
                        document=revisions.documents[revision_index + 1],
                    )
                    matches = matches and match_datetime_at < datetime_next_revision

        if matches and match_values:
            tested = True
            for key_current, value_current in match_values.items():
                matches = matches and key_current in document
                matches = matches and document[key_current] == value_current

        if not tested:
            raise ValueError('At least one match parameter must be provided.')

        return matches

    def remove_all(
        self,
        *,
        documents: Iterable[dict] = None,
    ) -> DocumentSet:
        """
        Remove all of the provided documents from the set.

        Raise ValueError if a provided document was not in the set.
        """

        remove_documents = list(documents)

        retained_documents = list(self)
        for document_current in remove_documents:
            try:
                retained_documents.remove(document_current)
            except ValueError:
                # Re-raise the ValueError
                raise

        return DocumentSet(documents=retained_documents)

    def remove_any(
        self,
        *,
        documents: Iterable[dict] = None,
    ) -> DocumentSet:
        """
        Remove any of the provided documents that occur in set.
        """

        remove_documents = list(documents)

        return DocumentSet(documents=[
            document_current
            for document_current in self
            if document_current not in remove_documents
        ])

    def remove_match(
        self,
        match_type: Optional[str] = None,
        match_deleted: Optional[bool] = None,
        match_datetime_at: Optional[datetime] = None,
        match_values: Optional[Dict[str, str]] = None,
    ) -> DocumentSet:
        """
        Remove any documents that match all provided parameters.
        """

        retained_documents = []
        for document_current in self:
            matches: bool = self._match_document(
                document=document_current,
                match_type=match_type,
                match_deleted=match_deleted,
                match_datetime_at=match_datetime_at,
                match_values=match_values,
            )

            if not matches:
                retained_documents.append(document_current)

        return DocumentSet(documents=retained_documents)

    def remove_revisions(self) -> DocumentSet:
        """
        Remove any prior revisions of documents.
        """

        return DocumentSet(
            documents=[
                document_revisions.documents[-1]
                for document_revisions in self.revisions.values()
            ]
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

    def __repr__(self) -> str:
        """
        String representation is the same as our documents.
        """
        return repr(self.documents)

    def __str__(self) -> str:
        """
        String representation is the same as our documents.
        """
        return str(self.documents)

    def union(
        self,
        *,
        documents: Iterable[dict],
    ):
        """
        Union this set with the provided documents.
        """

        retained_documents = list(self.documents)
        for document_current in documents:
            if document_current not in retained_documents:
                retained_documents.append(document_current)

        return DocumentSet(documents=retained_documents)

    @property
    def revisions(self) -> Dict[DocumentKey, DocumentSet]:
        """
        Group documents that are revisions of each underlying DocumentKey.
        - Each DocumentKey will correspond to a set of all revisions of a document.
        - The documents property of that set will be sorted in increasing order (i.e., the latest revision at the end).
        """

        if self._revisions is None:
            revisions: Dict[DocumentKey, List[dict]] = {}
            for document_current in self:
                # Singletons have only a _type, while set elements also have a _set_id
                key_current = document_key(document=document_current)

                revisions_existing = revisions.get(key_current, [])
                revisions_existing.append(document_current)
                revisions_existing = sorted(revisions_existing, key=lambda document: int(document["_rev"]))

                revisions[key_current] = revisions_existing

            self._revisions = {
                key_current: DocumentSet(documents=revisions[key_current])
                for key_current in revisions.keys()
            }

        return self._revisions

    def unique(self) -> Dict:
        """
        Obtain the single document in this set.
        """

        if len(self) != 1:
            raise ValueError

        return self.documents[0]
