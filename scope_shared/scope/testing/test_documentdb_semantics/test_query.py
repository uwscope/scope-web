# import pprint
# from typing import Callable
#
# import pymongo.database
# import pymongo.errors
# import pytest
# import scope.database.patients
#
# PP = pprint.PrettyPrinter(indent=4)
#
#
# # @pytest.mark.skip(reason="no way of currently testing this")
# def test_sessions_pymongo_tutorial_one(
#     database_client: pymongo.database.Database,
#     data_fake_patient_factory: Callable[[], dict],
# ):
#     # Generate a fake patient
#     data_fake_patient = data_fake_patient_factory()
#
#     patient_collection_name = scope.database.patients.create_patient(
#         database=database_client, patient=data_fake_patient
#     )
#
#     session_documents = data_fake_patient.get("sessions")
#
#     session_revised_document = session_documents[0]
#     session_revised_document.pop("_id")
#     session_revised_document["_rev"] += 1
#
#     database_client[patient_collection_name].insert_one(session_revised_document)
#
#     pipeline = [
#         {"$match": {"_type": "session"}},
#         {
#             "$group": {
#                 "_id": "$_session_id",
#                 # Count the number of revison sessions in the group:
#                 "session_count": {"$sum": 1},
#                 # Create a list of _rev value
#                 "session_revs": {"$push": "$_rev"},
#             }
#         },
#         {"$sort": {"_rev": pymongo.DESCENDING}},
#     ]
#
#     PP.pprint(list(database_client[patient_collection_name].aggregate(pipeline)))
#
#     database_client.drop_collection(patient_collection_name)
#
#
# def test_sessions_pymongo_tutorial_two(
#     database_client: pymongo.database.Database,
#     data_fake_patient_factory: Callable[[], dict],
# ):
#     # Generate a fake patient
#     data_fake_patient = data_fake_patient_factory()
#
#     patient_collection_name = scope.database.patients.create_patient(
#         database=database_client, patient=data_fake_patient
#     )
#
#     session_documents = data_fake_patient.get("sessions")
#
#     # Revise all documents in session_documents
#     for sd in session_documents:
#         sd.pop("_id", None)
#         sd["_rev"] += 1
#
#     database_client[patient_collection_name].insert_many(session_documents)
#
#     pipeline = [
#         {"$match": {"_type": "session"}},
#         {"$sort": {"_rev": pymongo.DESCENDING}},
#         {
#             "$group": {
#                 "_id": "$_session_id",
#                 "latest_session_document": {"$first": "$$ROOT"},
#             }
#         },
#         {"$replaceRoot": {"newRoot": "$latest_session_document"}},
#     ]
#
#     # PP.pprint(
#     #     list(database_client[patient_collection_name].aggregate(pipeline_option_one))
#     # )
#
#     found_sessions = list(database_client[patient_collection_name].aggregate(pipeline))
#
#     for fs in found_sessions:
#         assert fs["_rev"] == 2
#
#     # database_client.drop_collection(patient_collection_name)
