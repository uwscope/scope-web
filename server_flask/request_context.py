import flask
import http
import pymongo.collection
import pymongo.database
from typing import cast, NoReturn

import scope.database.patients


class RequestContext:
    """
    James: I'm not sure about this as the proper location for some of this.
           But putting things here to consolidate / organize them for now.
    """

    @property
    def database(self) -> pymongo.database.Database:
        # noinspection PyUnresolvedReferences
        return cast(pymongo.database.Database, flask.current_app.database)

    @staticmethod
    def _abort(response: dict, status: int) -> NoReturn:
        flask.abort(flask.make_response(
            flask.jsonify(response), status,
        ))

    @staticmethod
    def abort_document_not_found() -> NoReturn:
        RequestContext._abort(
            {
                "message": "Document not found.",
            },
            http.HTTPStatus.NOT_FOUND,
        )

    @staticmethod
    def abort_patient_not_found() -> NoReturn:
        RequestContext._abort(
            {
                "message": "Patient not found.",
            },
            http.HTTPStatus.NOT_FOUND,
        )

    @staticmethod
    def abort_put_with_id() -> NoReturn:
        RequestContext._abort(
            {
                "message": "Put must not include \"_id\".",
            },
            http.HTTPStatus.BAD_REQUEST,
        )

    @staticmethod
    def abort_revision_conflict(*, document: dict) -> NoReturn:
        RequestContext._abort(
            document | {
                "message": "Revision conflict.",
            },
            http.HTTPStatus.CONFLICT,
        )

    def patient_collection(self, *, patient_id: str) -> pymongo.collection.Collection:
        # Use patient ID to confirm validity and obtain collection
        # TODO: As part of authentication, determine if we can cache this.
        #       Otherwise, maybe an annotation or enhance context to reduce code repetition.
        patient_document = scope.database.patients.get_patient(
            database=self.database,
            patient_id=patient_id,
        )
        if patient_document is None:
            RequestContext.abort_patient_not_found()

        # Obtain patient collection
        patient_collection = self.database.get_collection(patient_document["collection"])

        return patient_collection


def request_context() -> RequestContext:
    return RequestContext()
