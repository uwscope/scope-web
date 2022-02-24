import datetime
import faker
import pytest
import random
from typing import Callable, List

import scope.database.document_utils as document_utils
import scope.database.format_utils as format_utils
import scope.database.patient.assessment_logs
import scope.database.patient.scheduled_assessments
import scope.schema
import scope.testing.fake_data.enums
import scope.testing.fake_data.fake_utils as fake_utils


def _fake_assessment_point_values(
    *,
    fake_assessment_contents: List[dict],
    assessment_id: str,
) -> dict:
    point_values = dict()
    for fake_assessment_content in fake_assessment_contents:
        if fake_assessment_content["id"] == assessment_id:
            if fake_assessment_content["id"] == "gad-7":
                for question in fake_assessment_content.get("questions", []):
                    point_values[question["id"]] = random.randint(0, 3)
            elif fake_assessment_content["id"] == "medication":
                for question in fake_assessment_content.get("questions", []):
                    point_values[question["id"]] = random.randint(0, 1)
            elif fake_assessment_content["id"] == "mood":
                for question in fake_assessment_content.get("questions", []):
                    point_values[question["id"]] = random.randint(1, 10)
            elif fake_assessment_content["id"] == "phq-9":
                for question in fake_assessment_content.get("questions", []):
                    point_values[question["id"]] = random.randint(0, 3)
            break
    return point_values


def _fake_assessment_logs(
    *,
    faker_factory: faker.Faker,
    fake_scheduled_assessments: List[dict],
    fake_assessment_contents: List[dict],
) -> List[dict]:

    n = random.randint(1, len(fake_scheduled_assessments))

    fake_assessment_logs = [
        {
            "_type": scope.database.patient.assessment_logs.DOCUMENT_TYPE,
            "recordedDate": fake_scheduled_assessment["dueDate"],
            "comment": faker_factory.text(),
            "scheduleId": fake_scheduled_assessment[
                scope.database.patient.scheduled_assessments.SEMANTIC_SET_ID
            ],
            "assessmentId": fake_scheduled_assessment["assessmentId"],
            "completed": random.choice([True, False]),
            "patientSubmitted": random.choice([True, False]),
            # "submittedBy": data_fake_identity_factory(), # TODO: identity information
            "pointValues": _fake_assessment_point_values(
                fake_assessment_contents=fake_assessment_contents,
                assessment_id=fake_scheduled_assessment["assessmentId"],
            ),
            "totalScore": random.randint(0, 27),
        }
        for fake_scheduled_assessment in random.sample(fake_scheduled_assessments, n)
    ]

    return fake_assessment_logs


def fake_assessment_log_factory(
    *,
    faker_factory: faker.Faker,
    fake_scheduled_assessments: List[dict],
    fake_assessment_contents: List[dict],
) -> Callable[[], dict]:
    """
    Obtain a factory that will generate fake assessment log document.
    """

    def factory() -> dict:

        fake_assessment_log = random.choice(
            _fake_assessment_logs(
                faker_factory=faker_factory,
                fake_scheduled_assessments=fake_scheduled_assessments,
                fake_assessment_contents=fake_assessment_contents,
            )
        )

        return document_utils.normalize_document(document=fake_assessment_log)

    return factory


def fake_assessment_logs_factory(
    *,
    faker_factory: faker.Faker,
    fake_scheduled_assessments: List[dict],
    fake_assessment_contents: List[dict],
) -> Callable[[], List[dict]]:
    """
    Obtain a factory that will generate a list of fake assessment log documents.
    """

    def factory() -> dict:

        fake_assessment_logs = _fake_assessment_logs(
            faker_factory=faker_factory,
            fake_scheduled_assessments=fake_scheduled_assessments,
            fake_assessment_contents=fake_assessment_contents,
        )

        return document_utils.normalize_documents(documents=fake_assessment_logs)

    return factory


@pytest.fixture(name="data_fake_assessment_log_factory")
def fixture_data_fake_assessment_log_factory(
    faker: faker.Faker,
    data_fake_scheduled_assessments: List[dict],
    data_fake_assessment_contents: List[dict],
) -> Callable[[], dict]:
    """
    Fixture for data_fake_assessment_log_factory.
    """

    unvalidated_factory = fake_assessment_log_factory(
        faker_factory=faker,
        fake_scheduled_assessments=data_fake_scheduled_assessments,
        fake_assessment_contents=data_fake_assessment_contents,
    )

    def factory() -> dict:
        fake_assessment_log = unvalidated_factory()

        fake_utils.xfail_for_invalid(
            schema=scope.schema.assessment_log_schema,
            document=fake_assessment_log,
        )

        return fake_assessment_log

    return factory


@pytest.fixture(name="data_fake_assessment_logs_factory")
def fixture_data_fake_assessment_logs_factory(
    faker: faker.Faker,
    data_fake_scheduled_assessments: List[dict],
    data_fake_assessment_contents: List[dict],
) -> Callable[[], List[dict]]:
    """
    Fixture for data_fake_assessment_logs_factory.
    """

    unvalidated_factory = fake_assessment_logs_factory(
        faker_factory=faker,
        fake_scheduled_assessments=data_fake_scheduled_assessments,
        fake_assessment_contents=data_fake_assessment_contents,
    )

    def factory() -> dict:
        fake_assessment_logs = unvalidated_factory()

        fake_utils.xfail_for_invalid(
            schema=scope.schema.assessment_logs_schema,
            document=fake_assessment_logs,
        )

        return fake_assessment_logs

    return factory
