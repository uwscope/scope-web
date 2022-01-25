import pymongo.collection
import pymongo.database

import scope.database.patient.values_inventory
import scope.database.patients
import scope.testing.fake_data.fixtures_fake_values_inventory


def populate_database(
    *,
    database: pymongo.database.Database,
    populate_patients: int,
):
    for patient_count in range(populate_patients):
        patient_current = scope.database.patients.create_patient(database=database)

        _populate_patient(
            patient_current=patient_current,
            patient_collection=database.get_collection(patient_current["collection"])
        )


def _populate_patient(
    *,
    patient_current: dict,
    patient_collection: pymongo.collection.Collection,
):
    pass

    # Not ready yet
    #
    # fake_values_collection = scope.testing.fake_data.fixtures_fake_values_inventory.fake_values_inventory_factory()
    # scope.database.patient.values_inventory.put_values_inventory(
    #     collection=patient_collection,
    #     values_collection=fake_values_collection,
    # )
