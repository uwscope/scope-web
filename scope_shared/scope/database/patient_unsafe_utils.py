import copy
import pymongo.collection

import scope.database.collection_utils
import scope.database.patient.assessments


def unsafe_update_assessment(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
    assessment: dict,
) -> scope.database.collection_utils.SetPutResult:
    """
    Update an assessment document.
    """

    current_document = scope.database.collection_utils.get_set_element(
        collection=collection,
        document_type=scope.database.patient.assessments.DOCUMENT_TYPE,
        set_id=set_id,
    )

    if current_document:
        updated_document = copy.deepcopy(current_document)
        updated_document.update(copy.deepcopy(assessment))
        del updated_document["_id"]
    else:
        updated_document = assessment

    return scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=scope.database.patient.assessments.DOCUMENT_TYPE,
        semantic_set_id=scope.database.patient.assessments.SEMANTIC_SET_ID,
        set_id=set_id,
        document=updated_document,
    )
