import faker
import pymongo.collection
import pymongo.database

import scope.database.patient.patient_profile
# import scope.database.patient.values_inventory
import scope.database.patients
import scope.testing.fake_data.fixtures_fake_patient_profile
# import scope.testing.fake_data.fixtures_fake_values_inventory


def populate_database(
    *,
    database: pymongo.database.Database,
    populate_patients: int,
):
    faker_factory = faker.Faker()

    for patient_count in range(populate_patients):
        patient_current = scope.database.patients.create_patient(database=database)
        patient_collection = database.get_collection(patient_current["collection"])

        _populate_patient(
            faker_factory=faker_factory,
            patient_collection=patient_collection,
        )


def _populate_patient(
    *,
    faker_factory: faker.Faker,
    patient_collection: pymongo.collection.Collection,
):
    # Not ready yet
    #
    # fake_values_collection = scope.testing.fake_data.fixtures_fake_values_inventory.fake_values_inventory_factory()
    # scope.database.patient.values_inventory.put_values_inventory(
    #     collection=patient_collection,
    #     values_collection=fake_values_collection,
    # )

    fake_patient_profile_factory = scope.testing.fake_data.fixtures_fake_patient_profile.fake_patient_profile_factory(
        faker_factory=faker_factory,
    )
    scope.database.patient.patient_profile.put_patient_profile(
        collection=patient_collection,
        patient_profile=fake_patient_profile_factory(),
    )
