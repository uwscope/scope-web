import contextlib
import copy
import json
from pathlib import Path
import pyzipper
from typing import Dict, List, Optional


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

    @property
    def documents(self) -> Dict[Path, dict]:
        if self._documents is None:
            self._documents = {}

            # Each file is a document
            for info_current in self._zipfile.infolist():
                document_bytes = self._zipfile.read(info_current)
                document_string = document_bytes.decode("utf-8")
                document_current = json.loads(document_string)

                self._documents[Path(info_current.filename)] = document_current

        return copy.deepcopy(self._documents)
