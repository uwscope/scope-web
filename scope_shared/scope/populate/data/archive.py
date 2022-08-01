import contextlib
import copy
import json
from pathlib import Path
import pyzipper
from typing import Dict, Optional, Tuple, Union


class Archive(contextlib.AbstractContextManager):
    _archive_path: Path
    _password: str

    _zipfile: Optional[pyzipper.AESZipFile]

    _documents: Optional[Dict[Path, dict]]

    def __init__(
        self,
        archive_path: Path,
        password: str,
    ):
        self._archive_path = archive_path
        self._password = password
        self._zipfile = None
        self._documents = None

    def __enter__(self):
        # Open the archive
        self._zipfile = pyzipper.AESZipFile(
            self._archive_path,
            mode="r",
            compression=pyzipper.ZIP_LZMA,
            encryption=pyzipper.WZ_AES,
        )
        self._zipfile.setpassword(self._password.encode("utf-8"))

        # Confirm the archive is valid
        if self._zipfile.testzip():
            raise ValueError("Invalid archive or password")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close the archive
        self._zipfile.close()

    @staticmethod
    def collapse_revisions(
        *,
        documents: Dict[Path, dict]
    ) -> Dict[Path, dict]:
        """
        Remove all documents that have been replaced by a more recent revision.
        """
        grouped_documents = Archive.group_revisions(documents=documents)

        # Each group contains all versions of a specific document, keep only the most recent version
        collapsed_documents: Dict[Path, dict] = {}
        for (group_key_current, group_current) in grouped_documents.items():
            key_most_recent = None
            document_most_recent = None
            for (key_current, document_current) in group_current.items():
                if document_most_recent is None:
                    key_most_recent = key_current
                    document_most_recent = document_current
                else:
                    if document_current["_rev"] > document_most_recent["_rev"]:
                        key_most_recent = key_current
                        document_most_recent = document_current

            collapsed_documents[key_most_recent] = document_most_recent

        return collapsed_documents

    @staticmethod
    def group_revisions(
        *,
        documents: Dict[Path, dict]
    ) -> Dict[Union[Tuple[str], Tuple[str, str]], Dict[Path, dict]]:
        """
        Group documents according to a tuple created from
        - document "_type"
        - any document "_set_id"
        """
        grouped_documents: Dict[Union[Tuple[str], Tuple[str, str]], Dict[Path, dict]] = {}
        for (key_current, document_current) in documents.items():
            if "_set_id" in document_current:
                group_key_current = (document_current["_type"], document_current["_set_id"])
            else:
                group_key_current = (document_current["_type"])

            if group_key_current not in grouped_documents:
                grouped_documents[group_key_current] = {}
            grouped_documents[group_key_current][key_current] = document_current

        return grouped_documents

    @property
    def documents(self) -> Dict[Path, dict]:
        """
        All documents in the archive.
        """

        if self._documents is None:
            self._documents = {}

            # Each file is a document
            for info_current in self._zipfile.infolist():
                document_bytes = self._zipfile.read(info_current)
                document_string = document_bytes.decode("utf-8")
                document_current = json.loads(document_string)

                self._documents[Path(info_current.filename)] = document_current

        return copy.deepcopy(self._documents)

    def documents_in_collection(
        self,
        *,
        collection: str,
        ignore_sentinel: bool,
        collapsed: bool,
    ) -> Dict[Path, dict]:
        """
        All documents in a specific collection.
        """

        # Obtain all documents in the archive
        documents = self.documents

        # Filter to those in this collection
        documents_in_collection = {}
        for (key_current, document_current) in documents.items():
            parents_current = [
                str(parent_current)
                for parent_current
                in key_current.parents
                if str(parent_current) not in ["."]
            ]

            if collection in parents_current:
                documents_in_collection[key_current] = document_current

        # If there is a sentinel to ignore, do that
        if ignore_sentinel:
            documents_in_collection = {
                key_current: document_current
                for (key_current, document_current)
                in documents_in_collection.items()
                if document_current["_type"] != "sentinel"
            }

        # If documents are to be collapsed, do that
        if collapsed:
            return self.collapse_revisions(documents=documents_in_collection)
        else:
            return documents_in_collection

    def patients_documents(
        self,
        *,
        ignore_sentinel: bool,
        collapsed: bool,
    ) -> Dict[Path, dict]:
        return self.documents_in_collection(
            collection="patients",
            ignore_sentinel=ignore_sentinel,
            collapsed=collapsed,
        )

    def providers_documents(
        self,
        *,
        ignore_sentinel: bool,
        collapsed: bool,
    ) -> Dict[Path, dict]:
        return self.documents_in_collection(
            collection="providers",
            ignore_sentinel=ignore_sentinel,
            collapsed=collapsed,
        )
