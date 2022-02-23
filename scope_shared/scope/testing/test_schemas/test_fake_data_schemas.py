import bson.objectid
import copy
from dataclasses import dataclass
import faker
import jschon
import pytest
from typing import Optional

import scope.database.patient.activities
import scope.database.patient.assessments
import scope.database.patient.case_reviews
import scope.database.patient.mood_logs
import scope.database.patient.scheduled_assessments
import scope.database.patient.sessions
import scope.database.providers
import scope.database.collection_utils as collection_utils
import scope.database.document_utils as document_utils
import scope.schema
import scope.testing.fake_data.fixtures_fake_activity
import scope.testing.fake_data.fixtures_fake_activities
import scope.testing.fake_data.fixtures_fake_assessment_contents
import scope.testing.fake_data.fixtures_fake_assessments
import scope.testing.fake_data.fixtures_fake_case_review
import scope.testing.fake_data.fixtures_fake_case_reviews
import scope.testing.fake_data.fixtures_fake_clinical_history
import scope.testing.fake_data.fixtures_fake_contact
import scope.testing.fake_data.fixtures_fake_life_area_contents
import scope.testing.fake_data.fixtures_fake_mood_log
import scope.testing.fake_data.fixtures_fake_mood_logs
import scope.testing.fake_data.fixtures_fake_patient_profile
import scope.testing.fake_data.fixtures_fake_provider_identity
import scope.testing.fake_data.fixtures_fake_referral_status
import scope.testing.fake_data.fixtures_fake_safety_plan
import scope.testing.fake_data.fixtures_fake_session
import scope.testing.fake_data.fixtures_fake_sessions
import scope.testing.fake_data.fixtures_fake_scheduled_assessments
import scope.testing.fake_data.fixtures_fake_values_inventory
import scope.testing.schema


@dataclass(frozen=True)
class ConfigTestFakeDataSchema:
    name: str
    schema: jschon.JSONSchema
    data_factory_fixture: str

    expected_document: bool
    expected_singleton: bool
    expected_set_element: bool
    expected_semantic_set_id: Optional[str]

    # Used to indicate test is not resolved
    # because it has an issue in data or schema
    XFAIL_TEST_HAS_TODO: bool = False


TEST_ITERATIONS = 100
faker_factory = faker.Faker()

TEST_CONFIGS = [
    # TODO: @James; activity and activites could fail because of empty/null values in values inventory
    ConfigTestFakeDataSchema(
        name="activity",
        schema=scope.schema.activity_schema,
        data_factory_fixture="data_fake_activity_factory",
        expected_document=True,
        expected_singleton=False,
        expected_set_element=True,
        expected_semantic_set_id=scope.database.patient.activities.SEMANTIC_SET_ID,
    ),
    ConfigTestFakeDataSchema(
        name="activities",
        schema=scope.schema.activities_schema,
        data_factory_fixture="data_fake_activities_factory",
        expected_document=False,
        expected_singleton=False,
        expected_set_element=False,
        expected_semantic_set_id=None,
    ),
    ConfigTestFakeDataSchema(
        name="assessment",
        schema=scope.schema.assessment_schema,
        data_factory_fixture="data_fake_assessment_factory",
        expected_document=True,  # TODO: @James, are these boolean configurations correct? Tests are passing.
        expected_singleton=False,
        expected_set_element=True,
        expected_semantic_set_id=None,  # TODO: @James, assert config.expected_semantic_set_id not in document_singleton will fail if we send semantic_set_id here
    ),
    ConfigTestFakeDataSchema(
        name="assessments",
        schema=scope.schema.assessments_schema,
        data_factory_fixture="data_fake_assessments_factory",
        expected_document=False,  # TODO: @James, are these boolean configurations correct? Tests are passing.
        expected_singleton=False,
        expected_set_element=False,
        expected_semantic_set_id=None,
    ),
    ConfigTestFakeDataSchema(
        name="assessment-contents",
        schema=scope.schema.assessment_contents_schema,
        data_factory_fixture="data_fake_assessment_contents_factory",
        expected_document=False,
        expected_singleton=False,
        expected_set_element=False,
        expected_semantic_set_id=None,
    ),
    ConfigTestFakeDataSchema(
        name="case-review",
        schema=scope.schema.case_review_schema,
        data_factory_fixture="data_fake_case_review_factory",
        expected_document=True,
        expected_singleton=False,
        expected_set_element=True,
        expected_semantic_set_id=scope.database.patient.case_reviews.SEMANTIC_SET_ID,
    ),
    ConfigTestFakeDataSchema(
        name="case-reviews",
        schema=scope.schema.case_reviews_schema,
        data_factory_fixture="data_fake_case_reviews_factory",
        expected_document=False,
        expected_singleton=False,
        expected_set_element=False,
        expected_semantic_set_id=None,
    ),
    ConfigTestFakeDataSchema(
        name="clinical-history",
        schema=scope.schema.clinical_history_schema,
        data_factory_fixture="data_fake_clinical_history_factory",
        expected_document=True,
        expected_singleton=True,
        expected_set_element=False,
        expected_semantic_set_id=None,
    ),
    ConfigTestFakeDataSchema(
        name="contact",
        schema=scope.schema.contact_schema,
        data_factory_fixture="data_fake_contact_factory",
        expected_document=True,
        expected_singleton=False,
        expected_set_element=False,
        expected_semantic_set_id=None,
    ),
    ConfigTestFakeDataSchema(
        name="life-areas",
        schema=scope.schema.life_areas_schema,
        data_factory_fixture="data_fake_life_area_contents_factory",
        expected_document=False,
        expected_singleton=False,
        expected_set_element=False,
        expected_semantic_set_id=None,
    ),
    ConfigTestFakeDataSchema(
        name="mood-log",
        schema=scope.schema.mood_log_schema,
        data_factory_fixture="data_fake_mood_log_factory",
        expected_document=True,
        expected_singleton=False,
        expected_set_element=True,
        expected_semantic_set_id=scope.database.patient.mood_logs.SEMANTIC_SET_ID,
    ),
    ConfigTestFakeDataSchema(
        name="mood-logs",
        schema=scope.schema.mood_logs_schema,
        data_factory_fixture="data_fake_mood_logs_factory",
        expected_document=False,
        expected_singleton=False,
        expected_set_element=False,
        expected_semantic_set_id=None,
    ),
    # patient-identity is not faked because there would be no patient backing that identity.
    # Fake patient identities are instead obtained by generating entire fake patients.
    # ConfigTestFakeDataSchema(
    #     name="patient-identity",
    #     schema=scope.schema.patient_identity_schema,
    # ),
    ConfigTestFakeDataSchema(
        name="patient-profile",
        schema=scope.schema.patient_profile_schema,
        data_factory_fixture="data_fake_patient_profile_factory",
        expected_document=True,
        expected_singleton=True,
        expected_set_element=False,
        expected_semantic_set_id=None,
    ),
    ConfigTestFakeDataSchema(
        name="provider-identity",
        schema=scope.schema.provider_identity_schema,
        data_factory_fixture="data_fake_provider_identity_factory",
        expected_document=True,
        expected_singleton=False,
        expected_set_element=True,
        expected_semantic_set_id=scope.database.providers.PROVIDER_IDENTITY_SEMANTIC_SET_ID,
    ),
    ConfigTestFakeDataSchema(
        name="referral-status",
        schema=scope.schema.referral_status_schema,
        data_factory_fixture="data_fake_referral_status_factory",
        expected_document=True,
        expected_singleton=False,
        expected_set_element=False,
        expected_semantic_set_id=None,
    ),
    ConfigTestFakeDataSchema(
        name="safety-plan",
        schema=scope.schema.safety_plan_schema,
        data_factory_fixture="data_fake_safety_plan_factory",
        expected_document=True,
        expected_singleton=True,
        expected_set_element=False,
        expected_semantic_set_id=None,
    ),
    ConfigTestFakeDataSchema(
        name="session",
        schema=scope.schema.session_schema,
        data_factory_fixture="data_fake_session_factory",
        expected_document=True,
        expected_singleton=False,
        expected_set_element=True,
        expected_semantic_set_id=scope.database.patient.sessions.SEMANTIC_SET_ID,
    ),
    ConfigTestFakeDataSchema(
        name="sessions",
        schema=scope.schema.sessions_schema,
        data_factory_fixture="data_fake_sessions_factory",
        expected_document=False,
        expected_singleton=False,
        expected_set_element=False,
        expected_semantic_set_id=None,
    ),
    ConfigTestFakeDataSchema(
        name="scheduled-assessment",
        schema=scope.schema.scheduled_assessment_schema,
        data_factory_fixture="data_fake_scheduled_assessment_factory",
        expected_document=True,
        expected_singleton=False,
        expected_set_element=True,
        expected_semantic_set_id=scope.database.patient.scheduled_assessments.SEMANTIC_SET_ID,
    ),
    ConfigTestFakeDataSchema(
        name="scheduled-assessments",
        schema=scope.schema.scheduled_assessments_schema,
        data_factory_fixture="data_fake_scheduled_assessments_factory",
        expected_document=False,
        expected_singleton=False,
        expected_set_element=False,
        expected_semantic_set_id=None,
    ),
    ConfigTestFakeDataSchema(
        name="values-inventory",
        schema=scope.schema.values_inventory_schema,
        data_factory_fixture="data_fake_values_inventory_factory",
        expected_document=True,
        expected_singleton=True,
        expected_set_element=False,
        expected_semantic_set_id=None,
    ),
]


@pytest.mark.parametrize(
    ["config"],
    [[config] for config in TEST_CONFIGS],
    ids=[config.name for config in TEST_CONFIGS],
)
def test_fake_data_schema(
    request: pytest.FixtureRequest,
    config: ConfigTestFakeDataSchema,
):
    if config.XFAIL_TEST_HAS_TODO:
        pytest.xfail("Test has TODO in data or schema.")

    if config.schema is None:
        pytest.xfail("Schema failed to parse")

    # Ensure valid configuration of expectations
    if config.expected_document:
        # May be a singleton, may be a set, or may be neither
        # Ensure not testing both singleton and set
        assert not (config.expected_singleton and config.expected_set_element)

        # Only set elements can have a semantic set id
        if not config.expected_set_element:
            assert config.expected_semantic_set_id is None
    else:
        # Fake data is expected to be a List[dict]
        # Assume those documents will be tested elsewhere
        assert not config.expected_singleton
        assert not config.expected_set_element
        assert config.expected_semantic_set_id is None

    for count in range(TEST_ITERATIONS):
        # Obtain fake data
        data_factory = request.getfixturevalue(config.data_factory_fixture)
        data = data_factory()

        # Test against the schema
        scope.testing.schema.assert_schema(
            data=data,
            schema=config.schema,
            expected_valid=True,
        )

        # Fake data factories generate data with fields corresponding to
        # data that has not been stored and retrieved from the database.
        # For schemas that are intended for database storage,
        # we also test they support the additional associated fields.

        if config.expected_document:
            # A document can be normalized
            document_normalized = document_utils.normalize_document(document=data)

            # Test against the schema
            scope.testing.schema.assert_schema(
                data=document_normalized,
                schema=config.schema,
                expected_valid=True,
            )

            # A document can have schema fields added or removed.
            # It should accept or reject those fields based on expectations.

            # These fields are expected by both singletons and set elements
            # Ensure they were not already present, as that's a fake_data error
            document_singleton = copy.deepcopy(document_normalized)
            assert "_id" not in document_singleton
            document_singleton["_id"] = str(bson.objectid.ObjectId())
            assert "_rev" not in document_singleton
            document_singleton["_rev"] = 1
            document_singleton = document_utils.normalize_document(
                document=document_singleton
            )

            scope.testing.schema.assert_schema(
                data=document_singleton,
                schema=config.schema,
                expected_valid=config.expected_singleton or config.expected_set_element,
            )

            # These fields are expected by only set elements
            # Ensure they were not already present, as that's a fake_data error
            document_set_element = copy.deepcopy(document_singleton)
            document_set_element["_set_id"] = collection_utils.generate_set_id()
            assert "_set_id" not in document_singleton
            if config.expected_semantic_set_id:
                assert config.expected_semantic_set_id not in document_singleton
                document_set_element[
                    config.expected_semantic_set_id
                ] = document_set_element["_set_id"]
            document_set_element = document_utils.normalize_document(
                document=document_set_element
            )

            scope.testing.schema.assert_schema(
                data=document_set_element,
                schema=config.schema,
                expected_valid=config.expected_set_element,
            )
