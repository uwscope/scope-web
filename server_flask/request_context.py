import flask
import pymongo.database
from typing import cast


class RequestContext:
    @property
    def database(self) -> pymongo.database.Database:
        # noinspection PyUnresolvedReferences
        return cast(pymongo.database.Database, flask.current_app.database)


def request_context() -> RequestContext:
    return RequestContext()
