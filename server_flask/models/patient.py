import datetime

from database import Database


class Patient(object):
    def __init__(self, collection_name):
        # DocumentDB collection name for the model.
        self.collection_name = collection_name

    def create(self, patient_document):
        result = Database.insert(patient_document, self.collection_name)
        return {"inserted_id ": result}

    def find(self, query):
        return {"patients": Database.find(query, self.collection_name)}

    def find_by_id(self, patient_id):
        return Database.find_by_id(patient_id, self.collection_name)
