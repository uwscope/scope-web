import flask
import pymongo.collection
import pymongo.database
from typing import cast

import request_utils
import scope.database.patients


class RequestContext:
    @property
    def database(self) -> pymongo.database.Database:
        # noinspection PyUnresolvedReferences
        return cast(pymongo.database.Database, flask.current_app.database)

    def patient_collection(self, *, patient_id: str) -> pymongo.collection.Collection:
        # Use patient ID to confirm validity and obtain collection
        # TODO: As part of authentication, determine if we can cache this.
        #       Otherwise, maybe an annotation or enhance context to reduce code repetition.
        patient_document = scope.database.patients.get_patient(
            database=self.database,
            patient_id=patient_id,
        )
        if patient_document is None:
            request_utils.abort_patient_not_found()

        # Obtain patient collection
        patient_collection = self.database.get_collection(
            patient_document["collection"]
        )

        return patient_collection


def request_context() -> RequestContext:
    return RequestContext()
