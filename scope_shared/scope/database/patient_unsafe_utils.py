import copy

import pymongo.collection
from typing import Callable, List, Optional

import scope.database.collection_utils
import scope.database.patient
import scope.database.patient.activities
import scope.database.patient.assessments


def _unsafe_update_set_element(
    *,
    database_get_function: Callable[[...], Optional[dict]],
    database_put_function: Callable[
        [...], scope.database.collection_utils.SetPutResult
    ],
    database_put_document_parameter: str,
    collection: pymongo.collection.Collection,
    set_id: str,
    new_document_complete: dict,
    preserve_keys: List[str],
) -> scope.database.collection_utils.SetPutResult:
    """
    Update a set element.

    Unsafe because it gets and updates the current document,
    effectively ignoring use of _rev to prevent race conflicts in modifications.
    """

    preserve_keys = ["_type", "_set_id", "_rev"] + preserve_keys

    current_document = database_get_function(
        **{
            "collection": collection,
            "set_id": set_id,
        }
    )

    if current_document:
        updated_document = {}
        for preserve_key_current in preserve_keys:
            if preserve_key_current in current_document:
                updated_document[preserve_key_current] = current_document[
                    preserve_key_current
                ]

        updated_document.update(copy.deepcopy(new_document_complete))
    else:
        updated_document = new_document_complete

    return database_put_function(
        **{
            "collection": collection,
            "set_id": set_id,
            database_put_document_parameter: updated_document,
        }
    )


def _unsafe_update_singleton(
    *,
    database_get_function: Callable[[...], Optional[dict]],
    database_put_function: Callable[[...], scope.database.collection_utils.PutResult],
    database_put_document_parameter: str,
    collection: pymongo.collection.Collection,
    new_document: dict,
) -> scope.database.collection_utils.PutResult:
    """
    Update a singleton.

    Unsafe because it gets and updates the current document,
    effectively ignoring use of _rev to prevent race conflicts in modifications.
    """

    current_document = database_get_function(
        **{
            "collection": collection,
        }
    )

    if current_document:
        updated_document = copy.deepcopy(current_document)
        updated_document.update(copy.deepcopy(new_document))
        del updated_document["_id"]
    else:
        updated_document = new_document

    return database_put_function(
        **{
            "collection": collection,
            database_put_document_parameter: updated_document,
        }
    )


#
# Unsafe set updates
#


def unsafe_update_assessment(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
    assessment_complete: dict,
) -> scope.database.collection_utils.SetPutResult:
    return _unsafe_update_set_element(
        database_get_function=scope.database.patient.assessments.get_assessment,
        database_put_function=scope.database.patient.assessments.put_assessment,
        database_put_document_parameter="assessment",
        collection=collection,
        set_id=set_id,
        preserve_keys=[scope.database.patient.assessments.SEMANTIC_SET_ID],
        new_document_complete=assessment_complete,
    )


def unsafe_update_activity(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
    activity_complete: dict,
) -> scope.database.collection_utils.SetPutResult:
    return _unsafe_update_set_element(
        database_get_function=scope.database.patient.activities.get_activity,
        database_put_function=scope.database.patient.activities.put_activity,
        database_put_document_parameter="activity",
        collection=collection,
        set_id=set_id,
        preserve_keys=[scope.database.patient.activities.SEMANTIC_SET_ID],
        new_document_complete=activity_complete,
    )


#
# Unsafe singleton updates
#


def unsafe_update_clinical_history(
    *,
    collection: pymongo.collection.Collection,
    clinical_history: dict,
) -> scope.database.collection_utils.PutResult:
    return _unsafe_update_singleton(
        database_get_function=scope.database.patient.get_clinical_history,
        database_put_function=scope.database.patient.put_clinical_history,
        database_put_document_parameter="clinical_history",
        collection=collection,
        new_document=clinical_history,
    )


def unsafe_update_patient_profile(
    *,
    collection: pymongo.collection.Collection,
    patient_profile: dict,
) -> scope.database.collection_utils.PutResult:
    return _unsafe_update_singleton(
        database_get_function=scope.database.patient.get_patient_profile,
        database_put_function=scope.database.patient.put_patient_profile,
        database_put_document_parameter="patient_profile",
        collection=collection,
        new_document=patient_profile,
    )


def unsafe_update_safety_plan(
    *,
    collection: pymongo.collection.Collection,
    safety_plan: dict,
) -> scope.database.collection_utils.PutResult:
    return _unsafe_update_singleton(
        database_get_function=scope.database.patient.get_safety_plan,
        database_put_function=scope.database.patient.put_safety_plan,
        database_put_document_parameter="safety_plan",
        collection=collection,
        new_document=safety_plan,
    )


def unsafe_update_values_inventory(
    *,
    collection: pymongo.collection.Collection,
    values_inventory: dict,
) -> scope.database.collection_utils.PutResult:
    return _unsafe_update_singleton(
        database_get_function=scope.database.patient.get_values_inventory,
        database_put_function=scope.database.patient.put_values_inventory,
        database_put_document_parameter="values_inventory",
        collection=collection,
        new_document=values_inventory,
    )
