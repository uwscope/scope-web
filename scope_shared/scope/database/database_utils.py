import pymongo.collection
import pymongo.database

from typing import List, Optional

import scope.database.date_utils as date_utils
import scope.database.collection_utils
import scope.database.patient.assessments
import scope.database.patient.clinical_history
import scope.database.patient.patient_profile
import scope.database.patient.safety_plan
import scope.database.patient.values_inventory
import scope.enums
import scope.schema
import scope.schema_utils as schema_utils


def get_patient_collections(
    *,
    database: pymongo.database.Database,
) -> Optional[List[pymongo.collection.Collection]]:
    """
    Retrieve all patient collections documents.
    """

    collection_names = database.list_collection_names()

    patient_collection_names = list(
        filter(lambda cn: "patient_" in cn, collection_names)
    )

    patient_collections: List[pymongo.collection.Collection] = []
    for patient_collection_name in patient_collection_names:
        patient_collections.append(database.get_collection(patient_collection_name))

    return patient_collections
