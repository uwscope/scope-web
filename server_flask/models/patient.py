import datetime

from database import DocumentDB


class Patient(object):
    def __init__(self, name):
        self.name = name
        self.created_at = datetime.datetime.utcnow()

    def insert(self):
        # Check if patient doesn't exist already.
        if not DocumentDB.find_one("patient", {"name": self.name}):
            DocumentDB.insert(collection="patient", data=self.json())

    def json(self):
        return {"name": self.name, "created_at": self.created_at}
