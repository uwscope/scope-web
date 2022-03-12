import faker
import pytest
import random
from typing import Callable, List

import scope.database.collection_utils as collection_utils
import scope.database.patient.assessments
import scope.database.patient.assessment_logs
import scope.database.patient.scheduled_assessments
import scope.enums
import scope.schema
import scope.schema_utils


def _fake_assessment_point_values(
    *,
    assessment_content: dict,
) -> dict:
    point_values = dict()

    if assessment_content["id"] == "gad-7":
        for question in assessment_content.get("questions", []):
            point_values[question["id"]] = random.randint(0, 3)
    elif assessment_content["id"] == "medication":
        for question in assessment_content.get("questions", []):
            point_values[question["id"]] = random.randint(0, 1)
    elif assessment_content["id"] == "mood":
        for question in assessment_content.get("questions", []):
            point_values[question["id"]] = random.randint(1, 10)
    elif assessment_content["id"] == "phq-9":
        for question in assessment_content.get("questions", []):
            point_values[question["id"]] = random.randint(0, 3)
    else:
        raise ValueError("Unknown assessment_content.")

    return point_values


def _fake_assessment_logs(
    *,
    faker_factory: faker.Faker,
    scheduled_assessments: List[dict],
    assessment_contents: List[dict],
) -> List[dict]:
    # A utility dictionary for "id" lookups
    assessment_content_by_id = {
        assessment_content["id"]: assessment_content
        for assessment_content in assessment_contents
    }

    fake_assessment_logs = []
    for scheduled_assessment_current in scheduled_assessments:
        fake_point_values = _fake_assessment_point_values(
            assessment_content=assessment_content_by_id[
                scheduled_assessment_current[
                    scope.database.patient.assessments.SEMANTIC_SET_ID
                ]
            ]
        )

        fake_assessment_log = {
            "_type": scope.database.patient.assessment_logs.DOCUMENT_TYPE,
            scope.database.patient.scheduled_assessments.SEMANTIC_SET_ID: scheduled_assessment_current[
                scope.database.patient.scheduled_assessments.SEMANTIC_SET_ID
            ],
            scope.database.patient.assessments.SEMANTIC_SET_ID: scheduled_assessment_current[
                scope.database.patient.assessments.SEMANTIC_SET_ID
            ],
            "recordedDateTime": scheduled_assessment_current["dueDateTime"],
            "comment": faker_factory.text(),
            "patientSubmitted": random.choice([True, False]),
            # "submittedByProviderId": data_fake_identity_factory(), # TODO: identity information
            "pointValues": fake_point_values,
            "totalScore": random.randint(0, 27),
        }

        fake_assessment_logs.append(fake_assessment_log)

    return fake_assessment_logs


def fake_assessment_logs_factory(
    *,
    faker_factory: faker.Faker,
    scheduled_assessments: List[dict],
    assessment_contents: List[dict],
) -> Callable[[], List[dict]]:
    """
    Obtain a factory that will generate a list of fake assessment log documents.
    """

    if len(scheduled_assessments) < 1:
        raise ValueError("scheduled_assessments must include at least one element.")

    for scheduled_assessment_current in scheduled_assessments:
        if (
            scope.database.patient.scheduled_assessments.SEMANTIC_SET_ID
            not in scheduled_assessment_current
        ):
            raise ValueError(
                'scheduled_assessments must include "{}".'.format(
                    scope.database.patient.scheduled_assessments.SEMANTIC_SET_ID
                )
            )

    def factory() -> List[dict]:
        fake_assessment_logs = _fake_assessment_logs(
            faker_factory=faker_factory,
            scheduled_assessments=scheduled_assessments,
            assessment_contents=assessment_contents,
        )

        sampled_fake_assessment_logs = random.sample(
            fake_assessment_logs, random.randint(1, len(fake_assessment_logs))
        )

        return sampled_fake_assessment_logs

    return factory


@pytest.fixture(name="data_fake_assessment_log_factory")
def fixture_data_fake_assessment_log_factory(
    faker: faker.Faker,
    data_fake_assessment_logs_factory: Callable[[], List[dict]],
) -> Callable[[], dict]:
    """
    Fixture for data_fake_assessment_log_factory.
    """

    def factory() -> dict:
        fake_assessment_log = random.choice(data_fake_assessment_logs_factory())

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.assessment_log_schema,
            data=fake_assessment_log,
        )

        return fake_assessment_log

    return factory


@pytest.fixture(name="data_fake_assessment_logs_factory")
def fixture_data_fake_assessment_logs_factory(
    faker: faker.Faker,
    data_fake_scheduled_assessments_factory: Callable[[], List[dict]],
    data_fake_assessment_contents_factory: Callable[[], List[dict]],
) -> Callable[[], List[dict]]:
    """
    Fixture for data_fake_assessment_logs_factory.
    """

    scheduled_assessments = data_fake_scheduled_assessments_factory()
    assessment_contents = data_fake_assessment_contents_factory()

    # Simulate IDs that can be referenced in fake assessment logs
    for scheduled_assessment_current in scheduled_assessments:
        generated_set_id = collection_utils.generate_set_id()
        scheduled_assessment_current["_set_id"] = generated_set_id
        scheduled_assessment_current[
            scope.database.patient.scheduled_assessments.SEMANTIC_SET_ID
        ] = generated_set_id

    unvalidated_factory = fake_assessment_logs_factory(
        faker_factory=faker,
        scheduled_assessments=scheduled_assessments,
        assessment_contents=assessment_contents,
    )

    def factory() -> List[dict]:
        fake_assessment_logs = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.assessment_logs_schema,
            data=fake_assessment_logs,
        )

        return fake_assessment_logs

    return factory
