from __future__ import annotations

import copy
import json
import pprint

import aws_infrastructure.tasks.ssh
import boto3
import contextlib
from dataclasses import asdict, dataclass
import datetime
from enum import Enum
from invoke import task
import operator
from pathlib import Path
import pytz
import re
import ruamel.yaml
from typing import Dict, List, Optional, Union


import scope.config
import scope.database.date_utils
import scope.database.document_utils
import scope.database.initialize
import scope.database.patient
import scope.database.patient.activities
import scope.database.patient.assessments
import scope.database.patient.safety_plan
import scope.database.patient.scheduled_activities
import scope.database.patient.scheduled_assessments
import scope.database.patient.values_inventory
import scope.database.patients
import scope.documentdb.client
import scope.documents.document_set
import scope.enums
import scope.populate
import scope.schema
import scope.schema_utils
import scope.utils.compute_patient_summary


class ScopeInstanceId(Enum):
    """
    Based on the string we expect in the database configuration.
    """

    DEV = "dev"
    DEMO = "demo"
    FREDHUTCH = "scca"
    MULTICARE = "multicare"


class ScriptAssessmentId(Enum):
    """
    Which assessments should the script examine.
    """

    PHQ9 = "phq-9"
    GAD7 = "gad-7"


@dataclass(frozen=True)
class ScriptAssessmentData:
    # Id of this assessment.
    assessment_id: str

    # Whether the assignment is currently assigned.
    assigned: bool
    # Full document of the assessment.
    assessment_document: dict

    # Assessment document to create.
    assessment_document_to_create: dict

    # Existing scheduled assessments.
    scheduled_assessment_documents: List[dict]

    # Scheduled assessment documents to be deleted or created.
    scheduled_assessment_documents_to_delete: List[dict]
    scheduled_assessment_documents_to_create: List[dict]


@dataclass(frozen=True)
class ScriptActivityScheduleData:
    # Id of this activity schedule.
    activity_schedule_id: str

    # Full document of this activity schedule.
    activity_schedule_document: dict

    # Full document of the corresponding activity.
    activity_document: dict

    # A determination of whether to extend it.
    extend_activity_schedule: bool

    # Existing scheduled activities.
    scheduled_activity_documents: List[dict]

    # Scheduled activity documents to be deleted or created.
    scheduled_activity_documents_to_delete: List[dict]
    scheduled_activity_documents_to_create: List[dict]


@dataclass(frozen=True)
class ScriptExecutionData:
    assessment_data: Dict[str, ScriptAssessmentData]
    activity_schedule_data: Dict[str, ScriptActivityScheduleData]


#     patient_email: str
#     testing_destination_email: str
#
#     date_today_formatted_subject: str
#     date_today_formatted_body: str
#
#     link_app: str
#
#     assigned_safety_plan: bool
#     assigned_values_inventory: bool
#     due_check_in_anxiety: bool
#     due_check_in_depression: bool
#
#     scheduled_activities_due_today: List[_ContentScheduledActivity]
#     scheduled_activities_overdue: List[_ContentScheduledActivity]


class ScriptProcessStatus(Enum):
    IN_PROGRESS = 0

    STOPPED_FAILED_ALLOW_LIST = 1
    STOPPED_MATCHED_DENY_LIST = 2
    STOPPED_COGNITO_ACCOUNT_NOT_ACTIVE = 3
    STOPPED_TREATMENT_STATUS = 4


#     STOPPED_CONTENT_NOTHING_DUE = 4
#
#     EMAIL_SUCCESS = 10


@dataclass(frozen=True)
class ScriptProcessData:
    patient_id: str
    patient_name: str

    pool_id: str
    cognito_id: str

    execution_data: Optional[ScriptExecutionData]

    status: ScriptProcessStatus

    @property
    def patient_summary(self) -> List[str]:
        summary = []

        # Patient identifier.
        summary.append(
            "{} : {}".format(
                self.patient_id,
                self.patient_name,
            )
        )

        # If execution data has been prepared.
        if self.execution_data:
            # Go through each assessment.
            for assessment_current in self.execution_data.assessment_data.values():
                # Whether the assessment is currently assigned.
                if assessment_current.assigned:
                    summary.extend(
                        [
                            "          {} : Assigned Since {}".format(
                                assessment_current.assessment_id.value,
                                scope.database.date_utils.parse_datetime(
                                    assessment_current.assessment_document[
                                        "assignedDateTime"
                                    ]
                                ).strftime("%Y-%m-%d"),
                            ),
                            "                  {} {}".format(
                                assessment_current.assessment_document["dayOfWeek"],
                                assessment_current.assessment_document["frequency"],
                            ),
                        ]
                    )
                else:
                    summary.append(
                        "          {} : Not Currently Assigned".format(
                            assessment_current.assessment_id.value,
                        )
                    )

                # Whether the assessment is being re-created to the previous date.
                if assessment_current.assessment_document_to_create:
                    summary.extend(
                        [
                            "            add : Re-Create Prior Assignment Since {}".format(
                                scope.database.date_utils.parse_datetime(
                                    assessment_current.assessment_document_to_create[
                                        "assignedDateTime"
                                    ]
                                ).strftime("%Y-%m-%d"),
                            ),
                            "                  {} {}".format(
                                assessment_current.assessment_document_to_create[
                                    "dayOfWeek"
                                ],
                                assessment_current.assessment_document_to_create[
                                    "frequency"
                                ],
                            ),
                        ]
                    )

                # Summary of scheduled assessments to be deleted.
                if assessment_current.scheduled_assessment_documents_to_delete:
                    summary.append(
                        "            "
                        + "del : {} ScheduledAssessment from {} to {}".format(
                            len(
                                assessment_current.scheduled_assessment_documents_to_delete
                            ),
                            scope.database.date_utils.parse_date(
                                assessment_current.scheduled_assessment_documents_to_delete[
                                    0
                                ][
                                    "dueDate"
                                ]
                            ).strftime("%Y-%m-%d"),
                            scope.database.date_utils.parse_date(
                                assessment_current.scheduled_assessment_documents_to_delete[
                                    -1
                                ][
                                    "dueDate"
                                ]
                            ).strftime("%Y-%m-%d"),
                        )
                    )

                # Summary of scheduled assessments to be created.
                if assessment_current.scheduled_assessment_documents_to_create:
                    summary.append(
                        "            "
                        + "add : {} ScheduledAssessment from {} to {}".format(
                            len(
                                assessment_current.scheduled_assessment_documents_to_create
                            ),
                            scope.database.date_utils.parse_date(
                                assessment_current.scheduled_assessment_documents_to_create[
                                    0
                                ][
                                    "dueDate"
                                ]
                            ).strftime("%Y-%m-%d"),
                            scope.database.date_utils.parse_date(
                                assessment_current.scheduled_assessment_documents_to_create[
                                    -1
                                ][
                                    "dueDate"
                                ]
                            ).strftime("%Y-%m-%d"),
                        )
                    )

                # # Scheduled assessments that exist, will be deleted, or will be created.
                # for scheduled_assessment_current in (
                #     assessment_current.scheduled_assessment_documents
                #     + assessment_current.scheduled_assessment_documents_to_create
                # ):
                #     _formattedAction = "   "
                #     if (
                #         scheduled_assessment_current
                #         in assessment_current.scheduled_assessment_documents_to_delete
                #     ):
                #         _formattedAction = "del"
                #     elif (
                #         scheduled_assessment_current
                #         in assessment_current.scheduled_assessment_documents_to_create
                #     ):
                #         _formattedAction = "add"
                #
                #     _formattedDate = scope.database.date_utils.parse_date(
                #         scheduled_assessment_current["dueDate"]
                #     ).strftime("%Y-%m-%d")
                #
                #     _formattedIdAndRev = None
                #     if "_set_id" in scheduled_assessment_current:
                #         _formattedIdAndRev = "{} r{}".format(
                #             scheduled_assessment_current["_set_id"],
                #             scheduled_assessment_current["_rev"],
                #         )
                #
                #     _formattedCompleted = None
                #     if scheduled_assessment_current["completed"]:
                #         _formattedCompleted = "Completed"
                #
                #     summary.append(
                #         "            "
                #         + " : ".join(
                #             filter(
                #                 None,
                #                 [
                #                     _formattedAction,
                #                     _formattedDate,
                #                     _formattedIdAndRev,
                #                     _formattedCompleted,
                #                 ],
                #             )
                #         )
                #     )

            def _format_repeat_day_flags(repeat_day_flags: dict) -> str:
                result = ""
                for day_of_week_current in scope.enums.DayOfWeek:
                    if repeat_day_flags[day_of_week_current.value]:
                        result += day_of_week_current.value[0:2]

                return result

            for (
                activity_schedule_current
            ) in self.execution_data.activity_schedule_data.values():
                # Summary of the activity schedule.
                summary.extend(
                    filter(
                        None,
                        [
                            "  {} : {}".format(
                                activity_schedule_current.activity_schedule_id,
                                activity_schedule_current.activity_document["name"],
                            ),
                            "                  Scheduled {} {}h{}".format(
                                scope.database.date_utils.parse_date(
                                    activity_schedule_current.activity_schedule_document[
                                        "date"
                                    ]
                                ).strftime("%Y-%m-%d"),
                                activity_schedule_current.activity_schedule_document[
                                    "timeOfDay"
                                ],
                                " Repeating {} Until {}".format(
                                    _format_repeat_day_flags(
                                        activity_schedule_current.activity_schedule_document[
                                            "repeatDayFlags"
                                        ]
                                    ),
                                    scope.database.date_utils.parse_date(
                                        activity_schedule_current.scheduled_activity_documents[
                                            -1
                                        ][
                                            "dueDate"
                                        ]
                                    ).strftime("%Y-%m-%d"),
                                )
                                if activity_schedule_current.activity_schedule_document[
                                    "hasRepetition"
                                ]
                                else " Non-Repeating",
                            ),
                            "                  Extend Activity Schedule"
                            if activity_schedule_current.extend_activity_schedule
                            else None,
                            "                  Do Not Extend Activity Schedule"
                            if not activity_schedule_current.extend_activity_schedule
                            else None,
                        ],
                    )
                )

                # Summary of scheduled activities to be deleted.
                if activity_schedule_current.scheduled_activity_documents_to_delete:
                    summary.append(
                        "            "
                        + "del : {} ScheduledActivity from {} to {}".format(
                            len(
                                activity_schedule_current.scheduled_activity_documents_to_delete
                            ),
                            scope.database.date_utils.parse_date(
                                activity_schedule_current.scheduled_activity_documents_to_delete[
                                    0
                                ][
                                    "dueDate"
                                ]
                            ).strftime("%Y-%m-%d"),
                            scope.database.date_utils.parse_date(
                                activity_schedule_current.scheduled_activity_documents_to_delete[
                                    -1
                                ][
                                    "dueDate"
                                ]
                            ).strftime("%Y-%m-%d"),
                        )
                    )

                # Summary of scheduled activities to be created.
                if activity_schedule_current.scheduled_activity_documents_to_create:
                    summary.append(
                        "            "
                        + "add : {} ScheduledActivity from {} to {}".format(
                            len(
                                activity_schedule_current.scheduled_activity_documents_to_create
                            ),
                            scope.database.date_utils.parse_date(
                                activity_schedule_current.scheduled_activity_documents_to_create[
                                    0
                                ][
                                    "dueDate"
                                ]
                            ).strftime("%Y-%m-%d"),
                            scope.database.date_utils.parse_date(
                                activity_schedule_current.scheduled_activity_documents_to_create[
                                    -1
                                ][
                                    "dueDate"
                                ]
                            ).strftime("%Y-%m-%d"),
                        )
                    )

                # Scheduled activities that will be deleted or created.
                # for scheduled_activity_current in (
                #     activity_schedule_current.scheduled_activity_documents
                #     + activity_schedule_current.scheduled_activity_documents_to_create
                # ):
                #     _formattedAction = "   "
                #     if (
                #         scheduled_activity_current
                #         in activity_schedule_current.scheduled_activity_documents_to_delete
                #     ):
                #         _formattedAction = "del"
                #     elif (
                #         scheduled_activity_current
                #         in activity_schedule_current.scheduled_activity_documents_to_create
                #     ):
                #         _formattedAction = "add"
                #
                #     _formattedDate = scope.database.date_utils.parse_date(
                #         scheduled_activity_current["dueDate"]
                #     ).strftime("%Y-%m-%d")
                #
                #     if _formattedAction.strip():
                #         summary.append(
                #             "    "
                #             + " : ".join(
                #                 filter(
                #                     None,
                #                     [
                #                         _formattedAction,
                #                         _formattedDate,
                #                     ],
                #                 )
                #             )
                #         )

        return summary

    @classmethod
    def from_execution_data(
        cls,
        *,
        current: ScriptProcessData,
        execution_data: ScriptExecutionData,
    ):
        return ScriptProcessData(
            patient_id=current.patient_id,
            patient_name=current.patient_name,
            pool_id=current.pool_id,
            cognito_id=current.cognito_id,
            execution_data=execution_data,
            status=current.status,
        )

    @classmethod
    def from_patient_data(
        cls,
        *,
        patient_id: str,
        patient_name: str,
        pool_id: str,
        cognito_id: str,
    ):
        return ScriptProcessData(
            patient_id=patient_id,
            patient_name=patient_name,
            pool_id=pool_id,
            cognito_id=cognito_id,
            execution_data=None,
            status=ScriptProcessStatus.IN_PROGRESS,
        )

    @classmethod
    def from_status(
        cls,
        *,
        current: ScriptProcessData,
        status: ScriptProcessStatus,
    ):
        return ScriptProcessData(
            patient_id=current.patient_id,
            patient_name=current.patient_name,
            pool_id=current.pool_id,
            cognito_id=current.cognito_id,
            execution_data=current.execution_data,
            status=status,
        )


# @dataclass(frozen=True)
# class TemplatesEmailReminder:
#     template_email_reminder_body: str
#     template_email_reminder_subject: str
#     template_email_reminder_testing_body_header: str
#     template_email_reminder_testing_subject_prefix: str
#
#     @classmethod
#     def from_paths(
#         cls,
#         *,
#         template_email_reminder_body_path: Union[Path, str],
#         template_email_reminder_subject_path: Union[Path, str],
#         template_email_reminder_testing_body_header_path: Union[Path, str],
#         template_email_reminder_testing_subject_prefix_path: Union[Path, str],
#     ):
#         template_email_reminder_body = None
#         with open(template_email_reminder_body_path, "r") as file_template:
#             template_email_reminder_body = file_template.read().strip()
#
#         template_email_reminder_subject = None
#         with open(template_email_reminder_subject_path, "r") as file_template:
#             template_email_reminder_subject = file_template.read().strip()
#
#         template_email_reminder_testing_body_header = None
#         with open(
#             template_email_reminder_testing_body_header_path, "r"
#         ) as file_template:
#             template_email_reminder_testing_body_header = file_template.read().strip()
#
#         template_email_reminder_testing_subject_prefix = None
#         with open(
#             template_email_reminder_testing_subject_prefix_path, "r"
#         ) as file_template:
#             template_email_reminder_testing_subject_prefix = (
#                 file_template.read().strip()
#             )
#
#         return TemplatesEmailReminder(
#             template_email_reminder_body=template_email_reminder_body,
#             template_email_reminder_subject=template_email_reminder_subject,
#             template_email_reminder_testing_body_header=template_email_reminder_testing_body_header,
#             template_email_reminder_testing_subject_prefix=template_email_reminder_testing_subject_prefix,
#         )
#
#
# def _content_link_app(
#     *,
#     scope_instance_id: ScopeInstanceId,
# ) -> str:
#     if scope_instance_id == ScopeInstanceId.DEV:
#         return "https://app.dev.uwscope.org/"
#     elif scope_instance_id == ScopeInstanceId.DEMO:
#         return "https://app.demo.uwscope.org/"
#     elif scope_instance_id == ScopeInstanceId.FREDHUTCH:
#         return "https://app.fredhutch.uwscope.org/"
#     elif scope_instance_id == ScopeInstanceId.MULTICARE:
#         return "https://app.multicare.uwscope.org/"
#     else:
#         raise ValueError("Unknown SCOPE Instance: {}".format(scope_instance_id))
#
#
# @dataclass(frozen=True)
# class _ContentPatientSummaryResult:
#     assigned_values_inventory: bool
#     assigned_safety_plan: bool
#     due_check_in_anxiety: bool
#     due_check_in_depression: bool
#
#
# def _content_patient_summary(
#     *,
#     patient_document_set: scope.documents.document_set.DocumentSet,
#     date_due: datetime.date,
# ) -> _ContentPatientSummaryResult:
#     # Work with only the current documents
#     current_document_set = patient_document_set.remove_revisions()
#
#     activity_documents = current_document_set.filter_match(
#         match_type=scope.database.patient.activities.DOCUMENT_TYPE,
#         match_deleted=False,
#     ).documents
#
#     safety_plan_document = current_document_set.filter_match(
#         match_type=scope.database.patient.safety_plan.DOCUMENT_TYPE,
#         match_deleted=False,
#     ).unique()
#
#     scheduled_assessment_documents = current_document_set.filter_match(
#         match_type=scope.database.patient.scheduled_assessments.DOCUMENT_TYPE,
#         match_deleted=False,
#     ).documents
#
#     values_inventory_document = current_document_set.filter_match(
#         match_type=scope.database.patient.values_inventory.DOCUMENT_TYPE,
#         match_deleted=False,
#     ).unique()
#
#     patient_summary = scope.utils.compute_patient_summary.compute_patient_summary(
#         activity_documents=activity_documents,
#         safety_plan_document=safety_plan_document,
#         scheduled_assessment_documents=scheduled_assessment_documents,
#         values_inventory_document=values_inventory_document,
#         date_due=date_due,
#     )
#
#     dueScheduledAssessmentsGad7 = [
#         scheduled_assessment_current
#         for scheduled_assessment_current in patient_summary[
#             "assignedScheduledAssessments"
#         ]
#         if scheduled_assessment_current["assessmentId"] == "gad-7"
#     ]
#     dueScheduledAssessmentsGad7 = scope.database.document_utils.normalize_documents(
#         documents=dueScheduledAssessmentsGad7
#     )
#
#     dueScheduledAssessmentsPhq9 = [
#         scheduled_assessment_current
#         for scheduled_assessment_current in patient_summary[
#             "assignedScheduledAssessments"
#         ]
#         if scheduled_assessment_current["assessmentId"] == "phq-9"
#     ]
#     dueScheduledAssessmentsPhq9 = scope.database.document_utils.normalize_documents(
#         documents=dueScheduledAssessmentsPhq9
#     )
#
#     return _ContentPatientSummaryResult(
#         assigned_safety_plan=patient_summary["assignedSafetyPlan"],
#         assigned_values_inventory=patient_summary["assignedValuesInventory"],
#         due_check_in_anxiety=len(dueScheduledAssessmentsGad7) > 0,
#         due_check_in_depression=len(dueScheduledAssessmentsPhq9) > 0,
#     )
#
#
# @dataclass(frozen=True)
# class _ContentScheduledActivity:
#     activity_name: str
#     due_date: datetime.date
#     due_time_of_day: int
#
#
# @dataclass(frozen=True)
# class _ContentScheduledActivitiesResult:
#     due_today: List[_ContentScheduledActivity]
#     overdue: List[_ContentScheduledActivity]
#
#
# def _content_scheduled_activities(
#     *,
#     patient_document_set: scope.documents.document_set.DocumentSet,
#     date_due: datetime.date,
# ) -> _ContentScheduledActivitiesResult:
#     # Work with only the current documents.
#     current_document_set = patient_document_set.remove_revisions()
#
#     # Obtain scheduled activities which we have not yet completed.
#     scheduled_activities = current_document_set.filter_match(
#         match_type=scope.database.patient.scheduled_activities.DOCUMENT_TYPE,
#         match_values={"completed": False},
#         match_deleted=False,
#     ).documents
#
#     def _map_content_scheduled_activity(
#         scheduled_activity_document: dict,
#     ) -> _ContentScheduledActivity:
#         return _ContentScheduledActivity(
#             activity_name=scheduled_activity_document["dataSnapshot"]["activity"][
#                 "name"
#             ],
#             due_date=scope.database.date_utils.parse_date(
#                 scheduled_activity_document["dueDate"]
#             ),
#             due_time_of_day=scheduled_activity_document["dueTimeOfDay"],
#         )
#
#     def _content_scheduled_activity_key(
#         content_scheduled_activity: _ContentScheduledActivity,
#     ):
#         return (
#             content_scheduled_activity.due_date,
#             content_scheduled_activity.due_time_of_day,
#             content_scheduled_activity.activity_name,
#         )
#
#     # Filter and map scheduled activities that are due today.
#     scheduled_activities_due_today = []
#     for scheduled_activity_current in scheduled_activities:
#         scheduled_activity_current_date_due = scope.database.date_utils.parse_date(
#             scheduled_activity_current["dueDate"]
#         )
#
#         if scheduled_activity_current_date_due == date_due:
#             scheduled_activities_due_today.append(
#                 _map_content_scheduled_activity(scheduled_activity_current)
#             )
#
#     # Sort the activities that are due today.
#     scheduled_activities_due_today = sorted(
#         scheduled_activities_due_today,
#         key=operator.attrgetter("due_time_of_day", "activity_name"),
#     )
#
#     # Filter and map scheduled activities that are overdue.
#     scheduled_activities_overdue = []
#     for scheduled_activity_current in scheduled_activities:
#         scheduled_activity_current_date_due = scope.database.date_utils.parse_date(
#             scheduled_activity_current["dueDate"]
#         )
#
#         if scheduled_activity_current_date_due < date_due:
#             if scheduled_activity_current_date_due >= date_due - datetime.timedelta(
#                 days=7
#             ):
#                 scheduled_activities_overdue.append(
#                     _map_content_scheduled_activity(scheduled_activity_current)
#                 )
#
#     # Sort the activities that are overdue.
#     scheduled_activities_overdue = sorted(
#         scheduled_activities_overdue,
#         key=operator.attrgetter("due_time_of_day", "activity_name"),
#     )
#     scheduled_activities_overdue = sorted(
#         scheduled_activities_overdue, key=operator.attrgetter("due_date"), reverse=True
#     )
#
#     return _ContentScheduledActivitiesResult(
#         due_today=scheduled_activities_due_today,
#         overdue=scheduled_activities_overdue,
#     )


def _filter_allowlist(
    *,
    allowlist_patient_id_extend_schedules: List[str],
    patient_id: str,
) -> bool:
    # A patient_id must match an element of this list to be allowed.
    for allow_current in allowlist_patient_id_extend_schedules:
        if re.fullmatch(allow_current, patient_id):
            return True

    return False


def _filter_denylist(
    *,
    denylist_patient_id_extend_schedules: List[str],
    patient_id: str,
) -> bool:
    # A patient_id that matches an element of this list will be denied.
    for deny_current in denylist_patient_id_extend_schedules:
        if re.fullmatch(deny_current, patient_id):
            return False

    return True


def _get_cognito_user_using_cognito_id(
    *,
    boto_userpool,
    pool_id: str,
    cognito_id: str,
) -> Optional[dict]:
    """
    Filter the list of existing Cognito users with cognito_id.
    """
    response = boto_userpool.list_users(
        UserPoolId=pool_id,
        Filter=f'sub = "{cognito_id}"',
    )

    if response["Users"]:
        return response["Users"][0]

    return None


def _filter_cognito_account_not_active(
    *,
    pool_id: str,
    cognito_id: str,
) -> bool:
    """
    Filter based on whether a Cognito account is not active.
    :param pool_id: Cognito UserPoolId that is a unique identifier for a user pool.
    :param cognito_id: Unique identifier assigned to each user within a user pool.
    :return: true if enabled, false if disabled.
    """

    # A cognito_id of "DISABLED" has been introduced to
    # prevent logging in to a specific instance.
    if cognito_id == "DISABLED":
        return False

    # boto will obtain AWS context from environment variables, but will have obtained those at an unknown time.
    # Creating a boto session ensures it uses the current value of AWS configuration environment variables.
    boto_session = boto3.Session()
    boto_userpool = boto_session.client("cognito-idp")

    cognito_user = _get_cognito_user_using_cognito_id(
        boto_userpool=boto_userpool,
        pool_id=pool_id,
        cognito_id=cognito_id,
    )

    # Patient must exist, would be an error if it did not.
    if not cognito_user:
        raise ValueError(
            f"User with cognito_id {cognito_id} not found in pool {pool_id}"
        )

    # Cognito must have "UserStatus" of "CONFIRMED".
    # Otherwise it is probably "FORCE_CHANGE_PASSWORD", meaning they have not yet logged in.
    if cognito_user["UserStatus"] != "CONFIRMED":
        return False

    # Cognito must be enabled.
    # Otherwise it has been explicitly disabled.
    if not cognito_user["Enabled"]:
        return False

    return True


# def _filter_content_nothing_due(
#     *,
#     content_data: EmailContentData,
# ) -> bool:
#     """
#     Filter if this reminder would not include anything that is due.
#     """
#
#     return any(
#         [
#             content_data.assigned_safety_plan,
#             content_data.assigned_values_inventory,
#             content_data.due_check_in_anxiety,
#             content_data.due_check_in_depression,
#             len(content_data.scheduled_activities_due_today) > 0,
#         ]
#     )


def _filter_treatment_status(
    *,
    patient_document_set: scope.documents.document_set.DocumentSet,
) -> bool:
    """
    Filter if treatment status is Discharged or End.
    """

    # Work with only the current documents
    current_document_set = patient_document_set.remove_revisions()

    patient_profile_document = current_document_set.filter_match(
        match_type=scope.database.patient.patient_profile.DOCUMENT_TYPE,
        match_deleted=False,
    ).unique()

    # If no status is yet assigned, allow to proceed.
    if not "depressionTreatmentStatus" in patient_profile_document:
        return True

    # Allow to proceed if status is not Discharged or End.
    return patient_profile_document["depressionTreatmentStatus"] not in [
        scope.enums.DepressionTreatmentStatus.Discharged.value,
        scope.enums.DepressionTreatmentStatus.End.value,
    ]


# @dataclass(frozen=True)
# class _FormatEmailResult:
#     body: str
#     subject: str
#
#
# def _format_email(
#     *,
#     email_content_data: EmailContentData,
#     templates_email_reminder: TemplatesEmailReminder,
#     testing_destination_email: str,
# ) -> _FormatEmailResult:
#     # Start from the production templates.
#     template_body = templates_email_reminder.template_email_reminder_body
#     template_subject = templates_email_reminder.template_email_reminder_subject
#
#     # Apply transformations for testing.
#     if testing_destination_email:
#         # Because we are testing, apply the testing body header.
#         template_body = template_body.replace(
#             "{template_email_reminder_testing_body_header}",
#             templates_email_reminder.template_email_reminder_testing_body_header,
#         )
#         # Because we are testing, apply the subject prefix.
#         # Force a space after the template, because all the templates are being stripped.
#         template_subject = template_subject.replace(
#             "{template_email_reminder_testing_subject_prefix}",
#             templates_email_reminder.template_email_reminder_testing_subject_prefix
#             + " ",
#         )
#     else:
#         # Because we are not testing, delete the placeholder for the testing body header.
#         template_body = template_body.replace(
#             "{template_email_reminder_testing_body_header}",
#             "",
#         )
#         # Because we are not testing, delete the placeholder for the testing subject prefix.
#         template_subject = template_subject.replace(
#             "{template_email_reminder_testing_subject_prefix}",
#             "",
#         )
#
#     # Calculate what to display for "Requested by Provider".
#     requested_by_provider_count = len(
#         [
#             request_current
#             for request_current in [
#                 email_content_data.assigned_values_inventory,
#                 email_content_data.assigned_safety_plan,
#                 email_content_data.due_check_in_depression,
#                 email_content_data.due_check_in_anxiety,
#             ]
#             if request_current
#         ]
#     )
#     requested_by_provider_formatted = ""
#     if requested_by_provider_count > 0:
#         requested_by_provider_formatted += "<h3>Requested by Provider</h3>"
#         requested_by_provider_formatted += (
#             "<p>Your social worker has {} requests:</p>".format(
#                 requested_by_provider_count
#             )
#         )
#         if email_content_data.assigned_values_inventory:
#             requested_by_provider_formatted += (
#                 "<p>- Complete Values & Activities Inventory</p>"
#             )
#         if email_content_data.assigned_safety_plan:
#             requested_by_provider_formatted += "<p>- Complete Safety Plan</p>"
#         if email_content_data.due_check_in_depression:
#             requested_by_provider_formatted += "<p>- Complete Depression Check-In</p>"
#         if email_content_data.due_check_in_anxiety:
#             requested_by_provider_formatted += "<p>- Complete Anxiety Check-In</p>"
#
#     def _format_due_time_of_day(due_time_of_day: int) -> str:
#         due_time_of_day_12_hour = due_time_of_day % 12
#         if due_time_of_day_12_hour == 0:
#             due_time_of_day_12_hour = 12
#
#         due_time_of_day_am_pm = "am"
#         if due_time_of_day >= 12:
#             due_time_of_day_am_pm = "pm"
#
#         return "{}:00 {}".format(due_time_of_day_12_hour, due_time_of_day_am_pm)
#
#     # Calculate what to display for "My Plan for Today".
#     my_plan_for_today_formatted = ""
#     my_plan_for_today_formatted += "<h3>My Plan for Today</h3>"
#     if len(email_content_data.scheduled_activities_due_today) > 0:
#         my_plan_for_today_formatted += "<p>You scheduled the following activities:</p>"
#         for (
#             scheduled_activity_current
#         ) in email_content_data.scheduled_activities_due_today:
#             my_plan_for_today_formatted += "<p>- {}: {}</p>".format(
#                 _format_due_time_of_day(scheduled_activity_current.due_time_of_day),
#                 scheduled_activity_current.activity_name,
#             )
#     else:
#         my_plan_for_today_formatted += (
#             "<p>"
#             + "You have no activities scheduled. "
#             + "You can use the Values & Activities Inventory in the Tools tab to help brainstorm and schedule pleasant activities. "
#             + "You can also use the Activities tab to add and schedule activities.</p>"
#         )
#
#     # Calculate what to display for "My Past Week".
#     my_past_week_formatted = ""
#     if len(email_content_data.scheduled_activities_overdue) > 0:
#         my_past_week_formatted += "<h3>My Past Week</h3>"
#         my_past_week_formatted += (
#             "<p>"
#             + "To help identify activities most helpful to you, "
#             + "remember to log whether you completed an activity and how it made you feel."
#             + "</p>"
#         )
#
#     # Provide our email content data and our formatted content.
#     format_params = dict(vars(email_content_data))
#     format_params["requested_by_provider_formatted"] = requested_by_provider_formatted
#     format_params["my_plan_for_today_formatted"] = my_plan_for_today_formatted
#     format_params["my_past_week_formatted"] = my_past_week_formatted
#
#     formatted_body = template_body.format_map(format_params)
#     formatted_subject = template_subject.format_map(format_params)
#
#     return _FormatEmailResult(
#         body=formatted_body,
#         subject=formatted_subject,
#     )
#
#


def _patient_calculate_script_execution_assessment_data(
    *,
    patient_document_set: scope.documents.document_set.DocumentSet,
    maintenance_datetime: datetime.datetime,
) -> Dict[str, ScriptAssessmentData]:
    # Iterate over the relevant assessments.
    assessment_data = {}
    for assessment_id_current in ScriptAssessmentId:
        # Obtain assignments of the assessment.
        assessment_documents = patient_document_set.filter_match(
            match_type=scope.database.patient.assessments.DOCUMENT_TYPE,
            match_values={"assessmentId": assessment_id_current.value},
        )

        # Obtain the most recent version of the assignment.
        assessment_current = assessment_documents.remove_revisions().unique()

        # July 15 maintenance was done in a rush, see if this is a record to update based on that.
        assessment_current_needs_update = True
        assessment_previous = None
        if assessment_current_needs_update:
            # Require the assessment is currently assigned.
            assessment_current_needs_update = assessment_current["assigned"]
        if assessment_current_needs_update:
            # Require that assignment happened on July 15 2025.
            assessment_current_needs_update = (
                scope.database.date_utils.parse_datetime(
                    assessment_current["assignedDateTime"]
                ).strftime("%Y-%m-%d")
                == "2025-07-15"
            )
        if assessment_current_needs_update:
            # Obtain the most recent assignment prior to July 15 2025.
            assessment_previous = list(
                filter(
                    lambda doc: scope.database.date_utils.parse_datetime(
                        doc["assignedDateTime"]
                    ).strftime("%Y-%m-%d")
                    != "2025-07-15",
                    sorted(
                        assessment_documents.documents,
                        key=operator.itemgetter("_rev"),
                    ),
                )
            )[-1]

            # Require the previous assignment:
            # - was an assignment
            # - was otherwise the same as what did happen on July 15 2025
            compare_keys = ["dayOfWeek", "frequency"]

            assessment_current_needs_update = assessment_previous[
                "assigned"
            ] and operator.itemgetter(*compare_keys)(
                assessment_current
            ) == operator.itemgetter(
                *compare_keys
            )(
                assessment_previous
            )

        # Based on the above filter, determine if we are creating an assessment document.
        assessment_document_to_create = None
        if assessment_current_needs_update:
            assessment_document_to_create = copy.deepcopy(assessment_current)
            assessment_document_to_create["assignedDateTime"] = assessment_previous[
                "assignedDateTime"
            ]
            del assessment_document_to_create["_id"]

        # Obtain the current version of each existing scheduled assessment.
        # This will include many in the past, including that have and have not been completed.
        # It may include in the future.
        scheduled_assessment_documents = sorted(
            patient_document_set.remove_revisions()
            .filter_match(
                match_type=scope.database.patient.scheduled_assessments.DOCUMENT_TYPE,
                match_values={"assessmentId": assessment_id_current.value},
                match_deleted=False,
            )
            .documents,
            key=lambda doc: (
                scope.database.date_utils.parse_date(doc["dueDate"]).strftime(
                    "%Y-%m-%d"
                )
            ),
        )

        # Determine existing scheduled assessments to delete.
        scheduled_assessment_documents_to_delete = scope.database.patient.assessments._calculate_scheduled_assessments_to_delete(
            scheduled_assessments=scheduled_assessment_documents,
            assessment_id=assessment_id_current.value,
            maintenance_datetime=maintenance_datetime,
        )

        # New scheduled assessments to create.
        scheduled_assessment_documents_to_create = scope.database.patient.assessments._calculate_scheduled_assessments_to_create(
            assessment_id=assessment_id_current.value,
            assessment=assessment_current,
            maintenance_datetime=maintenance_datetime,
        )

        # If we would delete and then re-create a scheduled assessment, skip both.
        duplicates = [
            [to_delete, to_create]
            for to_delete in scheduled_assessment_documents_to_delete
            for to_create in scheduled_assessment_documents_to_create
            if to_delete["dueDate"] == to_create["dueDate"]
        ]
        for duplicate_current in duplicates:
            ignore_keys = ["_id", "_rev", "_set_id", "scheduledAssessmentId"]
            assert {
                key_current: value_current
                for key_current, value_current in duplicate_current[0].items()
                if key_current not in ignore_keys
            } == {
                key_current: value_current
                for key_current, value_current in duplicate_current[1].items()
                if key_current not in ignore_keys
            }

            scheduled_assessment_documents_to_delete.remove(duplicate_current[0])
            scheduled_assessment_documents_to_create.remove(duplicate_current[1])

        # Store all the resulting documents.
        assessment_data[assessment_id_current] = ScriptAssessmentData(
            assessment_id=assessment_id_current,
            assigned=assessment_current["assigned"],
            assessment_document=assessment_current,
            assessment_document_to_create=assessment_document_to_create,
            scheduled_assessment_documents=scheduled_assessment_documents,
            scheduled_assessment_documents_to_delete=scheduled_assessment_documents_to_delete,
            scheduled_assessment_documents_to_create=scheduled_assessment_documents_to_create,
        )

    return assessment_data


def _patient_calculate_script_execution_activity_schedule_data(
    *,
    patient_document_set: scope.documents.document_set.DocumentSet,
    maintenance_datetime: datetime.datetime,
) -> Dict[str, ScriptAssessmentData]:
    activity_schedule_documents = sorted(
        patient_document_set.remove_revisions()
        .filter_match(
            match_type=scope.database.patient.activity_schedules.DOCUMENT_TYPE,
            match_deleted=False,
        )
        .documents,
        key=lambda doc: (
            doc["activityId"],
            scope.database.date_utils.parse_date(doc["date"]).strftime("%Y-%m-%d"),
        ),
    )

    # Iterate over all activity schedules.
    activity_schedule_data = {}
    for activity_schedule_current in activity_schedule_documents:
        # Extract the id.
        activity_schedule_id_current = activity_schedule_current["activityScheduleId"]

        # Look up the corresponding activity.
        activity_current = (
            patient_document_set.remove_revisions()
            .filter_match(
                match_type=scope.database.patient.activities.DOCUMENT_TYPE,
                match_values={"activityId": activity_schedule_current["activityId"]},
                match_deleted=False,
            )
            .unique()
        )

        # And the instances of the scheduled activity.
        scheduled_activity_documents = sorted(
            patient_document_set.remove_revisions()
            .filter_match(
                match_type=scope.database.patient.scheduled_activities.DOCUMENT_TYPE,
                match_values={"activityScheduleId": activity_schedule_id_current},
                match_deleted=False,
            )
            .documents,
            key=lambda doc: (
                scope.database.date_utils.parse_date(doc["dueDate"]).strftime(
                    "%Y-%m-%d"
                )
            ),
        )

        # By default, we will extend repeating activity schedules.
        # We will not extend if it seems a patient observed the end of a schedule, then re-scheduled on their own.
        # Such examples will be manually identified and gathered here.
        extend_activity_schedule = activity_schedule_current[
            "hasRepetition"
        ] and activity_schedule_id_current not in [
            #
            # Demo Patients
            #
            # Patient ul2bsiq2hgcw6
            "unbg2rpvbakgk",  # Expired and replaced with ckh4hb5kgeigk
            # Patient hzsrpij2dziki
            "ryp2h6w7md4es",  # Expired, multiple other activities since scheduled
            "2twjmfzuuktv6",  # Expired, multiple other activities since scheduled
            "dz5lrre7sii6k",  # Expired, multiple other activities since scheduled
            "nral7gigzueba",  # Expired, multiple other activities since scheduled
            "36ozkfbjqb262",  # Expired, multiple other activities since scheduled
            "4meuloula2gis",  # Expired, multiple other activities since scheduled
            "iu44cb5xdr4e6",  # Expired, multiple other activities since scheduled
            "pmgzcpl7fpnac",  # Expired, multiple other activities since scheduled
            "2jtirussluw7i",  # Expired, multiple other activities since scheduled
            "2obf3oiat3xsu",  # Expired, multiple other activities since scheduled
            "f2izxtmqqvfjs",  # Expired, multiple other activities since scheduled
            "h55rivlmyc5f4",  # Expired, multiple other activities since scheduled
            "pxzn2xrhkcynq",  # Expired, multiple other activities since scheduled
            "75a3gutdu3tso",  # Expired, multiple other activities since scheduled
            "f7kqqs6jjfx6w",  # Expired, multiple other activities since scheduled
            "qy5c42pd4tp62",  # Expired and replaced with 34pb3gczmom3e
            # Patient efvduspqydjdi
            "jqae7pswphhq2",  # Expired, multiple other activities since scheduled
            "xxy6tq2xuy7ti",  # Expired, multiple other activities since scheduled
            "t76yar7zx5ec4",  # Expired, multiple other activities since scheduled
            # Patient igkafyyklb52o
            "e6m6kkf6hfvok",  # Expired, multiple other activities since scheduled
            "oqbd64tqoyc2e",  # Expired, multiple other activities since scheduled
            "5yrovhhpzzdtk",  # Expired, multiple other activities since scheduled
            "bossthi266rbe",  # Expired and replaced with 26eszmijiywim
            "26eszmijiywim",  # Expired, multiple other activities since scheduled
            "fsi3epurct4cm",  # Expired, multiple other activities since scheduled
            "tppzcs6mqvqg2",  # Expired, multiple other activities since scheduled
            "huy2dpemtimpc",  # Expired, multiple other activities since scheduled
            # Patient k3mxdqrzdpkn4
            "3wzeu77olvk5q",  # Expired, multiple other activities since scheduled
            # Patient ieqklfi3tgjfc
            "w7papkcyh6cbo",  # Expired, multiple other activities since scheduled
            "kzrrlc7tw7gc6",  # Expired, multiple other activities since scheduled
            "ax2jo6wau2w7c",  # Expired, multiple other activities since scheduled
            "uroetxfz42bty",  # Expired, multiple other activities since scheduled
            "u5uau5pwulzly",  # Expired, multiple other activities since scheduled
            "3k2767hhtsn5g",  # Expired, multiple other activities since scheduled
            "64bkgu6rb4fec",  # Expired, multiple other activities since scheduled
            "st6bi4f3ouhdo",  # Expired, multiple other activities since scheduled
            "wsksbvmyscz7q",  # Expired, multiple other activities since scheduled
            "xalzmpcudfama",  # Expired, multiple other activities since scheduled
            "bsiuxtj2kk2di",  # Expired, multiple other activities since scheduled
            "znkzi2lroigko",  # Expired and replaced with 465qsm2pgfdmc
            "uyraybnrxahdw",  # Expired and replaced with 465qsm2pgfdmc
            "qbts3rfckhnnw",  # Expired, multiple other activities since scheduled
            "ljowxot2jrutm",  # Expired, multiple other activities since scheduled
            "ntcaacnis5y4o",  # Expired, multiple other activities since scheduled
            "hfb7a57jmajpi",  # Expired and replaced with mp2u5dxa2akzy
            "r24ls6vhvo5za",  # Expired, multiple other activities since scheduled
            "mgjmmaklodm2i",  # Expired, multiple other activities since scheduled
            "2xegaodxx3xty",  # Expired, multiple other activities since scheduled
            "2mfakq4ogtv3a",  # Expired, multiple other activities since scheduled
            "4ddcq34ha55rq",  # Expired, multiple other activities since scheduled
            "3yu5jkn443d6y",  # Expired, multiple other activities since scheduled
            "ffrm6avqqtcfk",  # Expired, multiple other activities since scheduled
            "m2zjtpgxjbe2y",  # Expired, multiple other activities since scheduled
            "wtbrb4fjr4luw",  # Expired, multiple other activities since scheduled
            "rccdwzzni73ae",  # Expired and replaced by 7wrjc6pt2cwsk
            "57rcuscjvyemo",  # Expired, multiple other activities since scheduled
            #
            # MultiCare Patients
            #
            # Patient oi7ticuq7prgg
            "emqwalwmpknde",  # Expired and replaced with kmc7677pf4rrw
            "ctxlc3drstue2",  # Expired and replaced with konhauc3zobx4
            "a2b5xfxsedupw",  # Expired, multiple other activities since scheduled
            "piq5tuolloztw",  # Expired and replaced with pz3jlbjog6x5q
            "ibaavtht77gfm",  # Expired and replaced with 3nujaak4mi4ay
            "w3yu3zxawkn3e",  # Expired and replaced with j4wh2cyrehwtw
            "pdetx7mk733na",  # Expired, multiple other activities since scheduled
            #
            # SCCA/FHCC Patients
            #
            # Patient hhbqy5ucx3fck
            "2xtyqb6x7eutm",  # Expired and replaced with 55ey7abapfvwm
            "fuej56qlfc5zm",  # Expired and replaced with ylejsxzkvsu4y
            "qoqcgmq6ty2fu",  # Expired and replaced with ylejsxzkvsu4y
            "apeproshzhkua",  # Expired and replaced with gmcnq5ibqlr6c
            # Patient gmrd4pi5cxlhk
            # Has notable duplicate activity schedules.
            # Perhaps wanted indication to do activity multiple times per day.
            # Or perhaps just confused.
            # They have not expired, so duplicates were all extended for consistency.
            "434tliezpbs4q",  # Expired and replaced with qb2lrr4xixoek
            "a6ubz556bs75q",  # Expired and replaced with zswr7lk672uj2
            "jsajz4uksj6kq",  # Expired, multiple other activities since scheduled
            "wsjn7vnmlsg7m",  # Expired and replaced with hfwdai4j7bqes and 5saf5xkhv5vgk
            "e7kbg3whjjriq",  # Expired and replaced with 47wr5oduade52 and chy7jhcxvylry
            "qymp6gsmyukwk",  # Expired and replaced with kh6arrmr7hbba
            "as53c3ps6fsmy",  # Expired and replaced with hfdd27podeawm and 4iu4iuhfbn23w
            # Patient 5a433bxvx4ato
            # Has notable duplicate activity schedules.
            # But they had expired, so only extending one of each.
            "ascszo4p2mmvs",  # Expired and duplicated by iye5t477oao7g
            "s62q5neu2j37y",  # Expired and duplicated by jlw5vrdqdain2
            "pd5ulylzcm4gy",  # Expired and duplicated by 225aspetnbvqa
            "tsk73xpmz6imy",  # Expired and duplicated by fodmekfegra6c
        ]

        # Determine existing scheduled activities to delete.
        scheduled_activity_documents_to_delete = []
        if extend_activity_schedule:
            scheduled_activity_documents_to_delete = scope.database.patient.activity_schedules._calculate_scheduled_activities_to_delete(
                scheduled_activities=scheduled_activity_documents,
                activity_schedule_id=activity_schedule_id_current,
                maintenance_datetime=maintenance_datetime,
            )

        # New scheduled activities to create.
        scheduled_activity_documents_to_create = []
        if extend_activity_schedule:
            scheduled_activity_documents_to_create = scope.database.patient.activity_schedules._calculate_scheduled_activities_to_create(
                activity_schedule_id=activity_schedule_id_current,
                activity_schedule=activity_schedule_current,
                maintenance_datetime=maintenance_datetime,
            )

            data_snapshot = (
                scope.database.patient.scheduled_activities.build_data_snapshot(
                    activity_schedule_id=activity_schedule_id_current,
                    activity_schedules=[activity_schedule_current],
                    activities=[activity_current],
                    values=patient_document_set.remove_revisions()
                    .filter_match(
                        match_type=scope.database.patient.values.DOCUMENT_TYPE,
                        match_deleted=False,
                    )
                    .documents,
                )
            )

            for scheduled_activity_current in scheduled_activity_documents_to_create:
                scheduled_activity_current["dataSnapshot"] = data_snapshot

        # If we would delete and then re-create a scheduled activity, skip both.
        duplicates = [
            [to_delete, to_create]
            for to_delete in scheduled_activity_documents_to_delete
            for to_create in scheduled_activity_documents_to_create
            if to_delete["dueDate"] == to_create["dueDate"]
        ]
        for duplicate_current in duplicates:
            ignore_keys = ["_id", "_rev", "_set_id", "scheduledActivityId"]
            assert {
                key_current: value_current
                for key_current, value_current in duplicate_current[0].items()
                if key_current not in ignore_keys
            } == {
                key_current: value_current
                for key_current, value_current in duplicate_current[1].items()
                if key_current not in ignore_keys
            }

            scheduled_activity_documents_to_delete.remove(duplicate_current[0])
            scheduled_activity_documents_to_create.remove(duplicate_current[1])

        activity_schedule_data[
            activity_schedule_id_current
        ] = ScriptActivityScheduleData(
            activity_schedule_id=activity_schedule_id_current,
            activity_schedule_document=activity_schedule_current,
            activity_document=activity_current,
            extend_activity_schedule=extend_activity_schedule,
            scheduled_activity_documents=scheduled_activity_documents,
            scheduled_activity_documents_to_delete=scheduled_activity_documents_to_delete,
            scheduled_activity_documents_to_create=scheduled_activity_documents_to_create,
        )

    return activity_schedule_data


def _patient_calculate_script_execution_data(
    *,
    script_process_data: ScriptProcessData,
    patient_document_set: scope.documents.document_set.DocumentSet,
    scope_instance_id: ScopeInstanceId,
) -> ScriptProcessData:
    # Time to use in schedule maintenance.
    maintenance_datetime: datetime.datetime = pytz.utc.localize(
        datetime.datetime.utcnow()
    )

    assessment_data = _patient_calculate_script_execution_assessment_data(
        patient_document_set=patient_document_set,
        maintenance_datetime=maintenance_datetime,
    )

    activity_schedule_data = _patient_calculate_script_execution_activity_schedule_data(
        patient_document_set=patient_document_set,
        maintenance_datetime=maintenance_datetime,
    )

    return ScriptProcessData.from_execution_data(
        current=script_process_data,
        execution_data=ScriptExecutionData(
            assessment_data=assessment_data,
            activity_schedule_data=activity_schedule_data,
        ),
    )


# def _patient_calculate_email_content_data(
#     *,
#     email_process_data: EmailProcessData,
#     patient_document_set: scope.documents.document_set.DocumentSet,
#     scope_instance_id: ScopeInstanceId,
#     testing_destination_email: str,
# ) -> EmailProcessData:
#     date_today = datetime.date.today()
#
#     content_patient_summary = _content_patient_summary(
#         patient_document_set=patient_document_set,
#         date_due=date_today,
#     )
#     content_scheduled_activities = _content_scheduled_activities(
#         patient_document_set=patient_document_set,
#         date_due=date_today,
#     )
#
#     return EmailProcessData.from_content_data(
#         current=email_process_data,
#         content_data=EmailContentData(
#             # Email addresses.
#             patient_email=email_process_data.patient_email,
#             testing_destination_email=testing_destination_email,
#             # Date of today formatted for rendering.
#             date_today_formatted_subject="{} {} {}".format(
#                 date_today.strftime(format="%a"),
#                 date_today.strftime(format="%b"),
#                 date_today.day,
#             ),
#             date_today_formatted_body="{}, {} {}".format(
#                 date_today.strftime(format="%A"),
#                 date_today.strftime(format="%B"),
#                 date_today.day,
#             ),
#             # Link to scope app.
#             link_app=_content_link_app(
#                 scope_instance_id=scope_instance_id,
#             ),
#             # Content requested by provider.
#             assigned_safety_plan=content_patient_summary.assigned_safety_plan,
#             assigned_values_inventory=content_patient_summary.assigned_values_inventory,
#             due_check_in_anxiety=content_patient_summary.due_check_in_anxiety,
#             due_check_in_depression=content_patient_summary.due_check_in_depression,
#             scheduled_activities_due_today=content_scheduled_activities.due_today,
#             scheduled_activities_overdue=content_scheduled_activities.overdue,
#         ),
#     )


def _patient_filter_script_process_data(
    *,
    script_process_data: ScriptProcessData,
    patient_document_set: scope.documents.document_set.DocumentSet,
    allowlist_patient_id_extend_schedules: List[str],
    denylist_patient_id_extend_schedules: List[str],
) -> ScriptProcessData:
    """
    Apply all filtering criteria.
    """

    # Filter if the patient does not appear in an allow list.
    if not _filter_allowlist(
        allowlist_patient_id_extend_schedules=allowlist_patient_id_extend_schedules,
        patient_id=script_process_data.patient_id,
    ):
        return ScriptProcessData.from_status(
            current=script_process_data,
            status=ScriptProcessStatus.STOPPED_FAILED_ALLOW_LIST,
        )

    # Filter if the patient appears in a deny list.
    if not _filter_denylist(
        denylist_patient_id_extend_schedules=denylist_patient_id_extend_schedules,
        patient_id=script_process_data.patient_id,
    ):
        return ScriptProcessData.from_status(
            current=script_process_data,
            status=ScriptProcessStatus.STOPPED_MATCHED_DENY_LIST,
        )

    # Filter if the patient Cognito account has been disabled.
    if not _filter_cognito_account_not_active(
        pool_id=script_process_data.pool_id,
        cognito_id=script_process_data.cognito_id,
    ):
        return ScriptProcessData.from_status(
            current=script_process_data,
            status=ScriptProcessStatus.STOPPED_COGNITO_ACCOUNT_NOT_ACTIVE,
        )

    # Filter according to treatment status indicating whether they are active.
    if not _filter_treatment_status(
        patient_document_set=patient_document_set,
    ):
        return ScriptProcessData.from_status(
            current=script_process_data,
            status=ScriptProcessStatus.STOPPED_TREATMENT_STATUS,
        )

    #     # Filter if content indicates nothing is currently due for a reminder.
    #     if not _filter_content_nothing_due(
    #         content_data=email_process_data.content_data,
    #     ):
    #         return EmailProcessData.from_status(
    #             current=email_process_data,
    #             status=EmailProcessStatus.STOPPED_CONTENT_NOTHING_DUE,
    #         )

    return script_process_data


def _patient_script_extend_schedules(
    *,
    script_process_data: ScriptProcessData,
    patient_document_set: scope.documents.document_set.DocumentSet,
    scope_instance_id: ScopeInstanceId,
    allowlist_patient_id_extend_schedules: List[str],
    denylist_patient_id_extend_schedules: List[str],
    # templates_email_reminder: TemplatesEmailReminder,
    # testing_destination_email: Optional[str],
) -> ScriptProcessData:
    #     # Calculate values needed for an email.
    #     email_process_data = _patient_calculate_email_content_data(
    #         email_process_data=email_process_data,
    #         patient_document_set=patient_document_set,
    #         scope_instance_id=scope_instance_id,
    #         testing_destination_email=testing_destination_email,
    #     )
    #     if email_process_data.status != EmailProcessStatus.IN_PROGRESS:
    #         return email_process_data

    # Filter whether this patient will be processed.
    script_process_data = _patient_filter_script_process_data(
        script_process_data=script_process_data,
        patient_document_set=patient_document_set,
        allowlist_patient_id_extend_schedules=allowlist_patient_id_extend_schedules,
        denylist_patient_id_extend_schedules=denylist_patient_id_extend_schedules,
    )
    if script_process_data.status != ScriptProcessStatus.IN_PROGRESS:
        return script_process_data

    # Calculate documents to be modified.
    script_process_data = _patient_calculate_script_execution_data(
        script_process_data=script_process_data,
        patient_document_set=patient_document_set,
        scope_instance_id=scope_instance_id,
    )
    if script_process_data.status != ScriptProcessStatus.IN_PROGRESS:
        return script_process_data

    # Validate that all documents to be created match their corresponding schema.
    for (
        assessment_data_current
    ) in script_process_data.execution_data.assessment_data.values():
        if assessment_data_current.assessment_document_to_create:
            scope.schema_utils.assert_schema(
                data=assessment_data_current.assessment_document_to_create,
                schema=scope.schema.assessment_schema,
            )

        scope.schema_utils.assert_schema(
            data=assessment_data_current.scheduled_assessment_documents_to_create,
            schema=scope.schema.scheduled_assessments_schema,
        )

    for (
        activity_schedule_data_current
    ) in script_process_data.execution_data.activity_schedule_data.values():
        scope.schema_utils.assert_schema(
            data=activity_schedule_data_current.scheduled_activity_documents_to_create,
            schema=scope.schema.scheduled_activities_schema,
        )

    #     # Format the actual email.
    #     format_email_result = _format_email(
    #         email_content_data=email_process_data.content_data,
    #         templates_email_reminder=templates_email_reminder,
    #         testing_destination_email=testing_destination_email,
    #     )
    #
    #     # boto will obtain AWS context from environment variables, but will have obtained those at an unknown time.
    #     # Creating a boto session ensures it uses the current value of AWS configuration environment variables.
    #     boto_session = boto3.Session()
    #     boto_ses = boto_session.client("ses")
    #
    #     # Send the formatted email.
    #     response = boto_ses.send_email(
    #         Source="SCOPE Reminders <do-not-reply@uwscope.org>",
    #         Destination={
    #             "ToAddresses": [destination_email],
    #             # "CcAddresses": ["<email@email.org>"],
    #         },
    #         ReplyToAddresses=["do-not-reply@uwscope.org"],
    #         Message={
    #             "Subject": {
    #                 "Data": format_email_result.subject,
    #                 "Charset": "UTF-8",
    #             },
    #             "Body": {
    #                 "Html": {
    #                     "Data": format_email_result.body,
    #                     "Charset": "UTF-8",
    #                 }
    #             },
    #         },
    #     )
    #
    #     return EmailProcessData.from_status(
    #         current=email_process_data,
    #         status=EmailProcessStatus.EMAIL_SUCCESS,
    #     )

    return script_process_data


def task_extend_schedules(
    *,
    instance_ssh_config_path: Union[Path, str],
    cognito_config_path: Union[Path, str],
    documentdb_config_path: Union[Path, str],
    database_config_path: Union[Path, str],
    allowlist_patient_id_extend_schedules_path: Union[Path, str],
    denylist_patient_id_extend_schedules_path: Union[Path, str],
    #     templates_email_reminder: TemplatesEmailReminder,
):

    instance_ssh_config = aws_infrastructure.tasks.ssh.SSHConfig.load(
        instance_ssh_config_path
    )
    cognito_config = scope.config.CognitoClientConfig.load(cognito_config_path)
    documentdb_config = scope.config.DocumentDBClientConfig.load(documentdb_config_path)
    database_config = scope.config.DatabaseClientConfig.load(database_config_path)
    allowlist_patient_id_extend_schedules = None
    with open(
        allowlist_patient_id_extend_schedules_path, encoding="UTF-8"
    ) as config_file:
        yaml = ruamel.yaml.YAML(typ="safe", pure=True)
        allowlist_patient_id_extend_schedules = yaml.load(config_file)
        if allowlist_patient_id_extend_schedules == None:
            allowlist_patient_id_extend_schedules = []
    denylist_patient_id_extend_schedules = None
    with open(
        denylist_patient_id_extend_schedules_path, encoding="UTF-8"
    ) as config_file:
        yaml = ruamel.yaml.YAML(typ="safe", pure=True)
        denylist_patient_id_extend_schedules = yaml.load(config_file)
        if denylist_patient_id_extend_schedules == None:
            denylist_patient_id_extend_schedules = []

    @task(optional=["production", "testing"])
    def extend_schedules(context, production=False, testing=False):
        """
        Extend schedules in {} database.
        """

        # Parameters must either:
        # - Explicitly indicate this is a production execution.
        # - Explicitly indicate this is a testing execution.
        if production:
            if testing:
                raise ValueError("-production does not allow -testing")
        else:
            if not testing:
                raise ValueError("Provide either -production or -testing")

        # Used for determining anything needed according to the specific instance.
        scope_instance_id = ScopeInstanceId(database_config.name)

        # Store state about results.
        script_process_data_results: List[ScriptProcessData] = []

        # Obtain a database client.
        with contextlib.ExitStack() as context_manager:
            database = scope.documentdb.client.documentdb_client_database(
                context_manager=context_manager,
                instance_ssh_config=instance_ssh_config,
                host=documentdb_config.endpoint,
                port=documentdb_config.port,
                direct_connection=True,
                tls_insecure=True,
                database_name=database_config.name,
                user=database_config.user,
                password=database_config.password,
            )

            # Iterate over every patient.
            patients = scope.database.patients.get_patient_identities(database=database)
            for patient_identity_current in patients:

                # Obtain needed documents for this patient.
                patient_collection = database.get_collection(
                    patient_identity_current["collection"]
                )
                patient_profile = scope.database.patient.get_patient_profile(
                    collection=patient_collection
                )

                result_current = _patient_script_extend_schedules(
                    script_process_data=ScriptProcessData.from_patient_data(
                        patient_id=patient_identity_current["patientId"],
                        patient_name=patient_profile["name"],
                        pool_id=cognito_config.poolid,
                        cognito_id=patient_identity_current["cognitoAccount"][
                            "cognitoId"
                        ],
                    ),
                    patient_document_set=scope.documents.document_set.DocumentSet(
                        documents=scope.database.document_utils.normalize_documents(
                            documents=patient_collection.find()
                        )
                    ),
                    scope_instance_id=scope_instance_id,
                    allowlist_patient_id_extend_schedules=allowlist_patient_id_extend_schedules,
                    denylist_patient_id_extend_schedules=denylist_patient_id_extend_schedules,
                    #                     templates_email_reminder=templates_email_reminder,
                )

                # Store the result
                script_process_data_results.append(result_current)

        for status_current in ScriptProcessStatus:
            matching_results = [
                script_process_data_current
                for script_process_data_current in script_process_data_results
                if script_process_data_current.status == status_current
            ]

            if len(matching_results) > 0:
                print(status_current.name)
                for script_process_data_current in matching_results:
                    for line_current in script_process_data_current.patient_summary:
                        print("  {}".format(line_current))
                print()

    extend_schedules.__doc__ = extend_schedules.__doc__.format(database_config.name)

    return extend_schedules
