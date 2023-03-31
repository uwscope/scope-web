# Allow typing to forward reference
# TODO: Not necessary with Python 3.11
from __future__ import annotations

import copy
from dataclasses import dataclass
import datetime
from pathlib import Path
from typing import Dict, List, Optional

from scope.database import collection_utils, date_utils
from scope.documents.document_set import datetime_from_document, document_key, document_id_from_datetime, DocumentSet
import scope.populate.data.archive
import scope.schema
import scope.schema_utils


def archive_migrate_v0_7_0(
    *,
    archive_path: Path,
    archive: scope.populate.data.archive.Archive,
) -> scope.populate.data.archive.Archive:
    print("Migrating to v0.7.0.")

    #
    # These specific collections in the dev database are leftovers from testing, delete them
    #
    if archive_path.name.startswith("archive_dev_v0.7.0_"):
        delete_collections = [
            'patient_eqy3qm5xvguvk',
            'patient_efbavfkbwjm6w',
            'patient_psfy75n7irege',
        ]

        delete_documents = []
        for delete_collection_current in delete_collections:
            delete_documents.extend(archive.collection_documents(collection=delete_collection_current))

        migrated_entries = {
            key_current: document_current
            for (key_current, document_current) in archive.entries.items()
            if document_current not in delete_documents
        }

        print("Deleted {} collections totaling {} documents.".format(
            len(delete_collections),
            len(archive.entries) - len(migrated_entries),
        ))

        archive = scope.populate.data.archive.Archive(entries=migrated_entries)

    #
    # Go through each patient collection
    #
    patients_documents = archive.patients_documents(
        remove_sentinel=True,
        remove_revisions=True,
    )

    for patients_document_current in patients_documents:
        print("Migrating patient '{}'.".format(patients_document_current["name"]))

        patient_collection = archive.collection_documents(
            collection=patients_document_current["collection"],
        )

        # Cleaning up individual fields
        patient_collection = _migrate_assessment_log_with_embedded_assessment(
            collection=patient_collection,
        )
        patient_collection = _migrate_activity_remove_reminder(
            collection=patient_collection,
        )
        patient_collection = _migrate_scheduled_activity_deletion(
            collection=patient_collection
        )
        patient_collection = _migrate_scheduled_activity_remove_reminder(
            collection=patient_collection,
        )

        # Set aside documents in the old activity format
        patient_collection = _migrate_activity_rename_type_old_format(
            collection=patient_collection,
        )
        # Refactor values and activities out of values inventory
        patient_collection = _migrate_values_inventory_refactor_values_and_activities(
            collection=patient_collection,
        )

        archive.replace_collection_documents(
            collection=patients_document_current["collection"],
            document_set=patient_collection,
        )

    return archive


def _migrate_activity_rename_type_old_format(
@dataclass(frozen=True)
class ValueInterval:
    name: str
    lifeAreaId: str
    datetimeStart: datetime.datetime
    hasEnd: bool
    datetimeEnd: Optional[datetime.datetime]


def _group_matching_value_intervals(
    intervals: List[ValueInterval]
) -> Dict[(str, str), List[ValueInterval]]:
    unsorted_groups: Dict[(str, str), List[ValueInterval]] = {}
    for interval_current in intervals:
        key = (
            interval_current.name,
            interval_current.lifeAreaId,
        )

        if key in unsorted_groups:
            unsorted_groups[key].append(interval_current)
        else:
            unsorted_groups[key] = [interval_current]

    sorted_groups: Dict[(str, str), List[ValueInterval]] = {
        key_current: sorted(
            unsorted_intervals_current,
            key=lambda interval_sort_current: (
                interval_sort_current.datetimeStart
            ),
        )
        for (key_current, unsorted_intervals_current) in unsorted_groups.items()
    }

    return sorted_groups


def _validate_value_intervals(
    intervals: List[ValueInterval]
) -> None:
    # Every interval must have a start before its end.
    for interval_current in intervals:
        if interval_current.hasEnd:
            assert interval_current.datetimeStart < interval_current.datetimeEnd

    # Grouped intervals must be in order and non-overlapping.
    grouped_matching_intervals = _group_matching_value_intervals(intervals=intervals)
    for group_current in grouped_matching_intervals.values():
        interval_previous = None
        for (index_current, interval_current) in enumerate(group_current):
            # If an interval does not end, it must be the final interval.
            # This also implies there can be only one interval that does not end.
            if not interval_current.hasEnd:
                assert index_current == len(group_current) - 1

            if interval_previous:
                # Must be in order.
                assert interval_previous.datetimeStart < interval_current.datetimeStart
                # Implemented as strictly less than because otherwise they should have merged.
                assert interval_previous.hasEnd
                assert interval_previous.datetimeEnd < interval_current.datetimeStart
            interval_previous = interval_current


def _fuse_value_interval(
    *,
    existing_intervals: List[ValueInterval],
    new_interval: ValueInterval,
) -> List[ValueInterval]:
    # Validate the provided intervals
    _validate_value_intervals([new_interval])
    _validate_value_intervals(existing_intervals)

    # Goal is to identify one overlapping segment, resolve that, and recurse for any other overlap.

    # Obtain existing intervals that match, sorted by their datetimeStart
    matching_intervals = _group_matching_value_intervals(
        intervals=existing_intervals,
    ).get(
        (
            new_interval.name,
            new_interval.lifeAreaId,
        ),
        [],
    )

    # Condition: No Existing Interval
    # - There are no matching intervals.
    # - Keep the new interval.
    if len(matching_intervals) == 0:
        result_intervals: List[ValueInterval] = copy.deepcopy(existing_intervals)
        result_intervals.append(new_interval)

        _validate_value_intervals(result_intervals)

        return result_intervals

    # Identify the first matching interval
    # that ends at or after this new interval starts.
    # That is the first interval that could potentially overlap.
    # All previous matching intervals end before our new interval starts.
    search_index: int = 0
    search_found: bool = False
    while not search_found and search_index < len(matching_intervals):
        search_matching_interval = matching_intervals[search_index]

        search_found = (
            not search_matching_interval.hasEnd
            or search_matching_interval.datetimeEnd >= new_interval.datetimeStart
        )

        if not search_found:
            search_index += 1

    if search_index == len(matching_intervals):
        # Search failed,
        # every matching interval ends before this new interval starts.
        assert matching_intervals[len(matching_intervals) - 1].hasEnd
        assert matching_intervals[len(matching_intervals) - 1].datetimeEnd
        assert matching_intervals[len(matching_intervals) - 1].datetimeEnd < new_interval.datetimeStart

        # Condition:
        # - All matching intervals end before the new interval starts.
        # - Keep the new interval.
        result_intervals: List[ValueInterval] = copy.deepcopy(existing_intervals)
        result_intervals.append(new_interval)

        _validate_value_intervals(result_intervals)

        return result_intervals
    else:
        # Search succeeded, index is the first interval that ends after new interval starts.
        matching_interval = matching_intervals[search_index]

        # Order the intervals by their start time
        first_interval: ValueInterval
        second_interval: ValueInterval
        if new_interval.datetimeStart <= matching_interval.datetimeStart:
            first_interval = new_interval
            second_interval = matching_interval
        else:
            first_interval = matching_interval
            second_interval = new_interval

        if first_interval.hasEnd and first_interval.datetimeEnd < second_interval.datetimeStart:
            # Condition:
            # - The two intervals do not actually overlap.
            # - Keep the new interval.

            # print("No Overlap")
            # print("  + {} -> {}".format(first_interval.datetimeStart, first_interval.datetimeEnd))
            # print("  + {} -> {}".format(second_interval.datetimeStart, second_interval.datetimeEnd))

            result_intervals: List[ValueInterval] = copy.deepcopy(existing_intervals)
            result_intervals.append(new_interval)

            _validate_value_intervals(result_intervals)

            return result_intervals

        # Confirmed these intervals overlap
        assert (
            not first_interval.hasEnd
            or second_interval.datetimeStart <= first_interval.datetimeEnd
        )

        # Condition:
        # - The intervals overlap.
        # - Fuse their start and end times.
        # - Then recurse for any additional overlaps.
        fused_start = first_interval.datetimeStart
        fused_has_end = first_interval.hasEnd and second_interval.hasEnd
        fused_end = max(first_interval.datetimeEnd, second_interval.datetimeEnd) if fused_has_end else None

        assert first_interval.name == second_interval.name
        assert first_interval.lifeAreaId == second_interval.lifeAreaId
        fused_interval = ValueInterval(
            name=first_interval.name,
            lifeAreaId=first_interval.lifeAreaId,
            datetimeStart=fused_start,
            hasEnd=fused_has_end,
            datetimeEnd=fused_end,
        )

        # print("Fuse Intervals")
        # print("  - {} -> {}".format(first_interval.datetimeStart, first_interval.datetimeEnd))
        # print("  - {} -> {}".format(second_interval.datetimeStart, second_interval.datetimeEnd))
        # print("  + {} -> {}".format(fused_interval.datetimeStart, fused_interval.datetimeEnd))

        result_intervals: List[ValueInterval] = copy.deepcopy(existing_intervals)
        result_intervals.remove(matching_interval)

        result_intervals = _fuse_value_interval(
            existing_intervals=result_intervals,
            new_interval=fused_interval,
        )
        _validate_value_intervals(result_intervals)

        return result_intervals


@dataclass(frozen=True)
class ActivityInterval:
    name: str
    valueId: str
    enjoyment: Optional[int]
    importance: Optional[int]
    datetimeStart: datetime.datetime
    hasEnd: bool
    datetimeEnd: Optional[datetime.datetime]


def _group_matching_activity_intervals(
    intervals: List[ActivityInterval]
) -> Dict[(str, str), List[ActivityInterval]]:
    unsorted_groups: Dict[(str, str), List[ActivityInterval]] = {}
    for interval_current in intervals:
        key = (
            interval_current.name,
            interval_current.valueId,
        )

        if key in unsorted_groups:
            unsorted_groups[key].append(interval_current)
        else:
            unsorted_groups[key] = [interval_current]

    sorted_groups: Dict[(str, str), List[ActivityInterval]] = {
        key_current: sorted(
            unsorted_intervals_current,
            key=lambda interval_sort_current: (
                interval_sort_current.datetimeStart
            ),
        )
        for (key_current, unsorted_intervals_current) in unsorted_groups.items()
    }

    return sorted_groups


def _validate_activity_intervals(
    intervals: List[ActivityInterval]
) -> None:
    # Every interval must have a start before its end.
    for interval_current in intervals:
        if interval_current.hasEnd:
            assert interval_current.datetimeStart < interval_current.datetimeEnd

    # Grouped intervals must be in order and non-overlapping.
    grouped_matching_intervals = _group_matching_activity_intervals(intervals=intervals)
    for group_current in grouped_matching_intervals.values():
        interval_previous = None
        for (index_current, interval_current) in enumerate(group_current):
            # If an interval does not end, it must be the final interval.
            # This also implies there can be only one interval that does not end.
            if not interval_current.hasEnd:
                assert index_current == len(group_current) - 1

            if interval_previous:
                # Must be in order.
                assert interval_previous.datetimeStart < interval_current.datetimeStart
                # Intervals either have a gap or have different enjoyment/importance, otherwise they should have merged.
                assert interval_previous.hasEnd
                assert (
                    interval_previous.datetimeEnd < interval_current.datetimeStart
                    or interval_previous.enjoyment != interval_current.enjoyment
                    or interval_previous.importance != interval_current.importance
                )
            interval_previous = interval_current


def _fuse_activity_interval(
    *,
    existing_intervals: List[ActivityInterval],
    new_interval: ActivityInterval,
) -> List[ActivityInterval]:
    # Validate the provided intervals
    _validate_activity_intervals([new_interval])
    _validate_activity_intervals(existing_intervals)

    # Goal is to identify one overlapping segment, resolve that, and recurse for any other overlap.

    # Obtain existing intervals that match, sorted by their datetimeStart
    matching_intervals = _group_matching_activity_intervals(
        intervals=existing_intervals,
    ).get(
        (
            new_interval.name,
            new_interval.valueId,
        ),
        [],
    )

    # Condition: No Existing Interval
    # - There are no matching intervals.
    # - Keep the new interval.
    if len(matching_intervals) == 0:
        result_intervals: List[ActivityInterval] = copy.deepcopy(existing_intervals)
        result_intervals.append(new_interval)

        _validate_activity_intervals(result_intervals)

        return result_intervals

    # Identify the first matching interval
    # that ends at or after this new interval starts.
    # That is the first interval that could potentially overlap.
    # All previous matching intervals end before our new interval starts.
    search_index: int = 0
    search_found: bool = False
    while not search_found and search_index < len(matching_intervals):
        search_matching_interval = matching_intervals[search_index]

        search_found = (
            not search_matching_interval.hasEnd
            or search_matching_interval.datetimeEnd >= new_interval.datetimeStart
        )

        if not search_found:
            search_index += 1

    if search_index == len(matching_intervals):
        # Search failed,
        # every matching interval ends before this new interval starts.
        assert matching_intervals[len(matching_intervals) - 1].hasEnd
        assert matching_intervals[len(matching_intervals) - 1].datetimeEnd
        assert matching_intervals[len(matching_intervals) - 1].datetimeEnd < new_interval.datetimeStart

        # Condition:
        # - All matching intervals end before the new interval starts.
        # - Keep the new interval.
        result_intervals: List[ActivityInterval] = copy.deepcopy(existing_intervals)
        result_intervals.append(new_interval)

        _validate_activity_intervals(result_intervals)

        return result_intervals
    else:
        # Search succeeded, index is the first interval that ends after new interval starts.
        matching_interval = matching_intervals[search_index]

        # Order the intervals by their start time
        first_interval: ActivityInterval
        second_interval: ActivityInterval
        if new_interval.datetimeStart <= matching_interval.datetimeStart:
            first_interval = new_interval
            second_interval = matching_interval
        else:
            first_interval = matching_interval
            second_interval = new_interval

        # If a second interval does not have an enjoyment/importance,
        # pre-emptively fuse those from the first interval.
        # This will allow fusing the intervals together,
        # so we can later focus on actual changes to the enjoyment/importance.
        if second_interval.enjoyment is None:
            second_interval = ActivityInterval(
                name=second_interval.name,
                valueId=second_interval.valueId,
                enjoyment=first_interval.enjoyment,
                importance=second_interval.importance,
                datetimeStart=second_interval.datetimeStart,
                hasEnd=second_interval.hasEnd,
                datetimeEnd=second_interval.datetimeEnd,
            )
        if second_interval.importance is None:
            second_interval = ActivityInterval(
                name=second_interval.name,
                valueId=second_interval.valueId,
                enjoyment=second_interval.enjoyment,
                importance=first_interval.importance,
                datetimeStart=second_interval.datetimeStart,
                hasEnd=second_interval.hasEnd,
                datetimeEnd=second_interval.datetimeEnd,
            )

        # If the two intervals start at the same time, one will be erased.
        # That is fine if they have the same enjoyment/importance, but an error if they do not.
        if (
            first_interval.datetimeStart == second_interval.datetimeStart
            and (
                first_interval.enjoyment != second_interval.enjoyment
                or first_interval.importance != second_interval.importance
            )
        ):
            raise ValueError("Conflicting Values of Enjoyment/Importance")

        if first_interval.hasEnd and first_interval.datetimeEnd < second_interval.datetimeStart:
            # Condition:
            # - The two intervals do not actually overlap.
            # - Keep the new interval.

            # print("No Overlap")
            # print("  + {} -> {}".format(first_interval.datetimeStart, first_interval.datetimeEnd))
            # print("  + {} -> {}".format(second_interval.datetimeStart, second_interval.datetimeEnd))

            result_intervals: List[ActivityInterval] = copy.deepcopy(existing_intervals)
            result_intervals.append(new_interval)

            _validate_activity_intervals(result_intervals)

            return result_intervals

        if (
            first_interval.hasEnd
            and first_interval.datetimeEnd == second_interval.datetimeStart
            and (
                first_interval.enjoyment != second_interval.enjoyment
                or first_interval.importance != second_interval.importance
            )
        ):
            # Condition:
            # - The two intervals are directly adjacent.
            # - The intervals have different enjoyment/importance.
            # - Keep the new interval.

            result_intervals: List[ActivityInterval] = copy.deepcopy(existing_intervals)
            result_intervals.append(new_interval)

            _validate_activity_intervals(result_intervals)

            return result_intervals

        # Confirmed these intervals overlap
        assert (
            not first_interval.hasEnd
            or second_interval.datetimeStart <= first_interval.datetimeEnd
        )

        if (
            first_interval.enjoyment == second_interval.enjoyment
            and first_interval.importance == second_interval.importance
        ):
            # Condition:
            # - The intervals overlap.
            # - The intervals have identical enjoyment/importance.
            # - Fuse their start and end times.
            # - Then recurse for any additional overlaps.
            fused_start = first_interval.datetimeStart
            fused_has_end = first_interval.hasEnd and second_interval.hasEnd
            fused_end = max(first_interval.datetimeEnd, second_interval.datetimeEnd) if fused_has_end else None

            assert first_interval.name == second_interval.name
            assert first_interval.valueId == second_interval.valueId
            assert first_interval.enjoyment == second_interval.enjoyment
            assert first_interval.importance == second_interval.importance
            fused_interval = ActivityInterval(
                name=first_interval.name,
                valueId=first_interval.valueId,
                enjoyment=first_interval.enjoyment,
                importance=first_interval.importance,
                datetimeStart=fused_start,
                hasEnd=fused_has_end,
                datetimeEnd=fused_end,
            )

            # print("Fuse Intervals")
            # print("  - {} -> {}".format(first_interval.datetimeStart, first_interval.datetimeEnd))
            # print("  - {} -> {}".format(second_interval.datetimeStart, second_interval.datetimeEnd))
            # print("  + {} -> {}".format(fused_interval.datetimeStart, fused_interval.datetimeEnd))

            result_intervals: List[ActivityInterval] = copy.deepcopy(existing_intervals)
            result_intervals.remove(matching_interval)

            return _fuse_activity_interval(
                existing_intervals=result_intervals,
                new_interval=fused_interval,
            )
        else:
            # Condition:
            # - The intervals overlap.
            # - The intervals have different enjoyment/importance.
            # - The first interval's enjoyment/importance continues until the second.
            # - The second interval's enjoyment/importance is fused, then continues from its start time.
            # - Then recurse for any additional overlaps.

            assert first_interval.name == second_interval.name
            assert first_interval.valueId == second_interval.valueId
            fused_first_interval = ActivityInterval(
                name=first_interval.name,
                valueId=first_interval.valueId,
                enjoyment=first_interval.enjoyment,
                importance=first_interval.importance,
                datetimeStart=first_interval.datetimeStart,
                hasEnd=True,
                datetimeEnd=second_interval.datetimeStart,
            )

            fused_has_end = first_interval.hasEnd and second_interval.hasEnd
            fused_end = max(first_interval.datetimeEnd, second_interval.datetimeEnd) if fused_has_end else None
            fused_second_interval = ActivityInterval(
                name=second_interval.name,
                valueId=second_interval.valueId,
                enjoyment=second_interval.enjoyment,
                importance=second_interval.importance,
                datetimeStart=second_interval.datetimeStart,
                hasEnd=fused_has_end,
                datetimeEnd=fused_end,
            )

            # print("Fuse Enjoyment/Importance")
            # print("  - {} -> {}".format(first_interval.datetimeStart, first_interval.datetimeEnd))
            # print("    E: {} I: {}".format(first_interval.enjoyment, first_interval.importance))
            # print("  - {} -> {}".format(second_interval.datetimeStart, second_interval.datetimeEnd))
            # print("    E: {} I: {}".format(second_interval.enjoyment, second_interval.importance))
            # print("  + {} -> {}".format(fused_first_interval.datetimeStart, fused_first_interval.datetimeEnd))
            # print("    E: {} I: {}".format(fused_first_interval.enjoyment, fused_first_interval.importance))
            # print("  + {} -> {}".format(fused_second_interval.datetimeStart, fused_second_interval.datetimeEnd))
            # print("    E: {} I: {}".format(fused_second_interval.enjoyment, fused_second_interval.importance))

            result_intervals: List[ActivityInterval] = copy.deepcopy(existing_intervals)
            result_intervals.remove(matching_interval)

            result_intervals = _fuse_activity_interval(
                existing_intervals=result_intervals,
                new_interval=fused_first_interval,
            )
            _validate_activity_intervals(result_intervals)

            result_intervals = _fuse_activity_interval(
                existing_intervals=result_intervals,
                new_interval=fused_second_interval,
            )
            _validate_activity_intervals(result_intervals)

            return result_intervals


def _migrate_activity_old_format_refactor_value_helper(
    *,
    documents_values: DocumentSet,
    documents_activities_old_format: DocumentSet,
    verbose: bool,
) -> DocumentSet:
    #
    # Build up a set of fused values
    #
    fused_value_intervals = []

    #
    # First fuse values obtained from the values inventory
    #
    for value_revisions in documents_values.group_revisions().values():
        value_revisions = value_revisions.order_by_revision()

        for (revision_index, value_revision_current) in enumerate(value_revisions):
            # We do not create intervals for deletions.
            # They are represented by the datetimeEnd of the previous interval.
            if "_deleted" in value_revision_current:
                assert revision_index == len(value_revisions) - 1
            else:
                # Create and fuse this interval

                # If there is no revision after this,
                # this value is expected to be valid in our final state
                datetime_end = None
                if revision_index + 1 < len(value_revisions):
                    # Otherwise this value is expected to be valid until the next revision.
                    datetime_end = datetime_from_document(
                        document=value_revisions[revision_index + 1],
                    )

                fused_value_intervals = _fuse_value_interval(
                    existing_intervals=fused_value_intervals,
                    new_interval=ValueInterval(
                        name=value_revision_current["name"],
                        lifeAreaId=value_revision_current["lifeAreaId"],
                        datetimeStart=datetime_from_document(
                            document=value_revision_current,
                        ),
                        hasEnd=datetime_end is not None,
                        datetimeEnd=datetime_end,
                    )
                )

    #
    # Then fuse values obtained from the old activity format
    #
    for old_format_activity_revisions in documents_activities_old_format.group_revisions().values():
        old_format_activity_revisions = old_format_activity_revisions.order_by_revision()

        for (revision_index, old_format_activity_current) in enumerate(old_format_activity_revisions):
            if old_format_activity_current["isDeleted"]:
                assert revision_index == len(old_format_activity_revisions) - 1
            else:
                # Create and fuse this interval

                # If there is no revision after this,
                # this value is expected to be valid in our final state
                datetime_end = None
                if revision_index + 1 < len(old_format_activity_revisions):
                    # Otherwise this value is expected to be valid until the next revision.
                    datetime_end = datetime_from_document(
                        document=old_format_activity_revisions[revision_index + 1],
                    )

                fused_value_intervals = _fuse_value_interval(
                    existing_intervals=fused_value_intervals,
                    new_interval=ValueInterval(
                        name=old_format_activity_current["value"],
                        lifeAreaId=old_format_activity_current["lifeareaId"],
                        datetimeStart=datetime_from_document(
                            document=old_format_activity_current,
                        ),
                        hasEnd=datetime_end is not None,
                        datetimeEnd=datetime_end,
                    )
                )

    #
    # Convert the value intervals into value documents
    #
    documents_values_migrated: List[dict] = []
    for interval_group_current in _group_matching_value_intervals(intervals=fused_value_intervals).values():
        # Variables for tracking within a sequence of documents
        value_id_current: Optional[str] = None
        revision_current: int = 0
        document_migrated_previous: Optional[dict] = None
        for (index_current, interval_current) in enumerate(interval_group_current):
            if not value_id_current:
                value_id_current = collection_utils.generate_set_id()
            revision_current += 1
            document_migrated = {
                "_id": document_id_from_datetime(generation_time=interval_current.datetimeStart),
                "_type": "value",
                "_set_id": value_id_current,
                "_rev": revision_current,
                "valueId": value_id_current,
                "name": interval_current.name,
                "lifeAreaId": interval_current.lifeAreaId,
                "editedDateTime": date_utils.format_datetime(interval_current.datetimeStart),
            }

            if verbose:
                if revision_current == 1:
                    print("  - Create Value {}".format(value_id_current))
                    print("    + Now: {}".format(document_migrated["name"]))
                    print("           {}".format(document_migrated["lifeAreaId"]))
                else:
                    print("  - Update Value {}".format(value_id_current))
                    print("    + Now: {}".format(document_migrated["name"]))
                    print("           {}".format(document_migrated["lifeAreaId"]))
                    print("    + Was: {}".format(document_migrated_previous["name"]))
                    print("           {}".format(document_migrated_previous["lifeAreaId"]))

            scope.schema_utils.assert_schema(
                data=document_migrated,
                schema=scope.schema.value_schema,
            )
            documents_values_migrated.append(document_migrated)
            document_migrated_previous = document_migrated

            # If this interval has an end time,
            # which is not also the start time of the next interval,
            # then it corresponds to a value deletion.
            if (
                interval_current.hasEnd
                and (
                    index_current == len(interval_group_current) - 1
                    or interval_group_current[index_current + 1].datetimeStart > interval_current.datetimeEnd
                )
            ):
                revision_current += 1
                document_migrated = {
                    "_id": document_id_from_datetime(generation_time=interval_current.datetimeEnd),
                    "_type": "value",
                    "_set_id": value_id_current,
                    "_rev": revision_current,
                    "_deleted": True
                }

                scope.schema_utils.assert_schema(
                    data=document_migrated,
                    schema=scope.schema.set_tombstone_schema,
                )
                documents_values_migrated.append(document_migrated)

                if verbose:
                    print("  - Deleted Value {}".format(value_id_current))
                    print("    + Was: {}".format(document_migrated_previous["name"]))
                    print("           {}".format(document_migrated_previous["lifeAreaId"]))

                revision_current = 0
                value_id_current = None
                document_migrated_previous = None

    # Convert migrated values into a document set for ease
    documents_values_migrated: DocumentSet = DocumentSet(documents=documents_values_migrated)

    #
    # Confirm necessary values exist at the times they are supposed to exist
    #
    for original_value_current in documents_values.filter_match(
        match_deleted=False,
    ):
        assert documents_values_migrated.filter_match(
            match_datetime_at=datetime_from_document(document=original_value_current),
            match_values={
                "name": original_value_current["name"],
                "lifeAreaId": original_value_current["lifeAreaId"]
            }
        ).unique()
    for original_activity_old_format_current in documents_activities_old_format:
        if not original_activity_old_format_current["isDeleted"]:
            assert documents_values_migrated.filter_match(
                match_datetime_at=datetime_from_document(document=original_activity_old_format_current),
                match_values={
                    "name": original_activity_old_format_current["value"],
                    "lifeAreaId": original_activity_old_format_current["lifeareaId"]
                }
            ).unique()

    #
    # Confirm that the final set of values are the same in both representations
    #
    original_value_set = set()
    for original_value_current in documents_values.remove_revisions().filter_match(
        match_deleted=False,
    ):
        original_value_set.add((
            original_value_current["name"],
            original_value_current["lifeAreaId"],
        ))

    for original_activity_old_format_current in documents_activities_old_format.remove_revisions():
        if not original_activity_old_format_current["isDeleted"]:
            original_value_set.add((
                original_activity_old_format_current["value"],
                original_activity_old_format_current["lifeareaId"],
            ))

    migrated_value_set = set()
    for migrated_value_current in documents_values_migrated.remove_revisions().filter_match(
        match_deleted=False,
    ):
        migrated_value_set.add((
            migrated_value_current["name"],
            migrated_value_current["lifeAreaId"],
        ))

    assert original_value_set == migrated_value_set

    return documents_values_migrated


def _migrate_activity_old_format_refactor_activity_helper(
    *,
    documents_values: DocumentSet,
    documents_values_migrated: DocumentSet,
    documents_activities: DocumentSet,
    documents_activities_old_format: DocumentSet,
    verbose: bool,
) -> DocumentSet:
    #
    # Build up a set of fused activities
    #
    fused_activity_intervals = []

    #
    # First fuse activities obtained from the values inventory
    #
    for activity_revisions in documents_activities.group_revisions().values():
        activity_revisions = activity_revisions.order_by_revision()

        for (revision_index, activity_revision_current) in enumerate(activity_revisions):
            # We do not create intervals for deletions.
            # They are represented by the datetimeEnd of the previous interval.
            if "_deleted" in activity_revision_current:
                assert revision_index == len(activity_revisions) - 1
            else:
                # Create and fuse this interval

                # The activity created from the values inventory references
                # an id of a value created at the same time, which has since been migrated.
                # Recover an id in the migrated values.
                original_value = documents_values.filter_match(
                    match_deleted=False,
                    match_datetime_at=datetime_from_document(document=activity_revision_current),
                    match_values={
                        "valueId": activity_revision_current["valueId"]
                    }
                ).unique()
                migrated_value_id = documents_values_migrated.filter_match(
                    match_deleted=False,
                    match_datetime_at=datetime_from_document(document=activity_revision_current),
                    match_values={
                        "name": original_value["name"],
                        "lifeAreaId": original_value["lifeAreaId"],
                    }
                ).unique()["valueId"]

                # If there is no revision after this,
                # this activity is expected to be valid in our final state
                datetime_end = None
                if revision_index + 1 < len(activity_revisions):
                    # Otherwise this activity is expected to be valid until the next revision.
                    datetime_end = datetime_from_document(
                        document=activity_revisions[revision_index + 1],
                    )

                fused_activity_intervals = _fuse_activity_interval(
                    existing_intervals=fused_activity_intervals,
                    new_interval=ActivityInterval(
                        name=activity_revision_current["name"],
                        valueId=migrated_value_id,
                        enjoyment=activity_revision_current.get("enjoyment", None),
                        importance=activity_revision_current.get("importance", None),
                        datetimeStart=datetime_from_document(
                            document=activity_revision_current,
                        ),
                        hasEnd=datetime_end is not None,
                        datetimeEnd=datetime_end,
                    )
                )

    #
    # Then fuse activities obtained from the old activity format
    #
    for old_format_activity_revisions in documents_activities_old_format.group_revisions().values():
        old_format_activity_revisions = old_format_activity_revisions.order_by_revision()

        for (revision_index, old_format_activity_current) in enumerate(old_format_activity_revisions):
            if old_format_activity_current["isDeleted"]:
                assert revision_index == len(old_format_activity_revisions) - 1
            else:
                # Create and fuse this interval

                migrated_value_id = documents_values_migrated.filter_match(
                    match_deleted=False,
                    match_datetime_at=datetime_from_document(document=old_format_activity_current),
                    match_values={
                        "name": old_format_activity_current["value"],
                        "lifeAreaId": old_format_activity_current["lifeareaId"],
                    }
                ).unique()["valueId"]

                # If there is no revision after this,
                # this activity is expected to be valid in our final state
                datetime_end = None
                if revision_index + 1 < len(old_format_activity_revisions):
                    # Otherwise this activity is expected to be valid until the next revision.
                    datetime_end = datetime_from_document(
                        document=old_format_activity_revisions[revision_index + 1],
                    )

                fused_activity_intervals = _fuse_activity_interval(
                    existing_intervals=fused_activity_intervals,
                    new_interval=ActivityInterval(
                        name=old_format_activity_current["name"],
                        valueId=migrated_value_id,
                        enjoyment=None,
                        importance=None,
                        datetimeStart=datetime_from_document(
                            document=old_format_activity_current,
                        ),
                        hasEnd=datetime_end is not None,
                        datetimeEnd=datetime_end,
                    )
                )

    #
    # Convert the activity intervals into activity documents
    #
    documents_activities_migrated: List[dict] = []
    for interval_group_current in _group_matching_activity_intervals(intervals=fused_activity_intervals).values():
        # Variables for tracking within a sequence of documents
        activity_id_current: Optional[str] = None
        revision_current: int = 0
        document_migrated_previous: Optional[dict] = None
        for (index_current, interval_current) in enumerate(interval_group_current):
            if not activity_id_current:
                activity_id_current = collection_utils.generate_set_id()
            revision_current += 1
            document_migrated = {
                "_id": document_id_from_datetime(generation_time=interval_current.datetimeStart),
                "_type": "activity",
                "_set_id": activity_id_current,
                "_rev": revision_current,
                "activityId": activity_id_current,
                "name": interval_current.name,
                "valueId": interval_current.valueId,
                "editedDateTime": date_utils.format_datetime(interval_current.datetimeStart),
            }
            if interval_current.enjoyment:
                document_migrated.update({
                    "enjoyment": interval_current.enjoyment
                })
            if interval_current.importance:
                document_migrated.update({
                    "importance": interval_current.importance
                })

            if verbose:
                if revision_current == 1:
                    print("  - Create Activity {}".format(activity_id_current))
                    print("    + Now: {}".format(document_migrated["name"]))
                    print("           {}".format(document_migrated["valueId"]))
                    print("           E: {} I: {}".format(
                        document_migrated.get("enjoyment", None),
                        document_migrated.get("importance", None),
                    ))
                else:
                    print("  - Update Activity {}".format(activity_id_current))
                    print("    + Now: {}".format(document_migrated["name"]))
                    print("           {}".format(document_migrated["valueId"]))
                    print("           E: {} I: {}".format(
                        document_migrated.get("enjoyment", None),
                        document_migrated.get("importance", None),
                    ))
                    print("    + Was: {}".format(document_migrated_previous["name"]))
                    print("           {}".format(document_migrated_previous["valueId"]))
                    print("           E: {} I: {}".format(
                        document_migrated_previous.get("enjoyment", None),
                        document_migrated_previous.get("importance", None),
                    ))

            scope.schema_utils.assert_schema(
                data=document_migrated,
                schema=scope.schema.activity_schema,
            )
            documents_activities_migrated.append(document_migrated)
            document_migrated_previous = document_migrated

            # If this interval has an end time,
            # which is not also the start time of the next interval,
            # then it corresponds to an activity deletion.
            if (
                interval_current.hasEnd
                and (
                    index_current == len(interval_group_current) - 1
                    or interval_group_current[index_current + 1].datetimeStart > interval_current.datetimeEnd
                )
            ):
                revision_current += 1
                document_migrated = {
                    "_id": document_id_from_datetime(generation_time=interval_current.datetimeEnd),
                    "_type": "activity",
                    "_set_id": activity_id_current,
                    "_rev": revision_current,
                    "_deleted": True
                }

                scope.schema_utils.assert_schema(
                    data=document_migrated,
                    schema=scope.schema.set_tombstone_schema,
                )
                documents_activities_migrated.append(document_migrated)

                if verbose:
                    print("  - Deleted Activity {}".format(activity_id_current))
                    print("    + Was: {}".format(document_migrated_previous["name"]))
                    print("           {}".format(document_migrated_previous["valueId"]))
                    print("           E: {} I: {}".format(
                        document_migrated_previous.get("enjoyment", None),
                        document_migrated_previous.get("importance", None),
                    ))

                revision_current = 0
                activity_id_current = None
                document_migrated_previous = None

    # Convert migrated activities into a document set for ease
    documents_activities_migrated: DocumentSet = DocumentSet(documents=documents_activities_migrated)

    #
    # Confirm necessary activities exist at the times they are supposed to exist
    #
    for original_activity_current in documents_activities.filter_match(
        match_deleted=False,
    ):
        # The activity created from the values inventory references
        # an id of a value created at the same time, which has since been migrated.
        # Recover an id in the migrated values.
        original_value = documents_values.filter_match(
            match_deleted=False,
            match_datetime_at=datetime_from_document(document=original_activity_current),
            match_values={
                "valueId": original_activity_current["valueId"]
            }
        ).unique()
        migrated_value_id = documents_values_migrated.filter_match(
            match_deleted=False,
            match_datetime_at=datetime_from_document(document=original_activity_current),
            match_values={
                "name": original_value["name"],
                "lifeAreaId": original_value["lifeAreaId"],
            }
        ).unique()["valueId"]

        assert documents_activities_migrated.filter_match(
            match_datetime_at=datetime_from_document(document=original_activity_current),
            match_values={
                "name": original_activity_current["name"],
                "valueId": migrated_value_id,
            }
        ).unique()
    for original_activity_old_format_current in documents_activities_old_format:
        if not original_activity_old_format_current["isDeleted"]:
            migrated_value_id = documents_values_migrated.filter_match(
                match_deleted=False,
                match_datetime_at=datetime_from_document(document=original_activity_old_format_current),
                match_values={
                    "name": original_activity_old_format_current["value"],
                    "lifeAreaId": original_activity_old_format_current["lifeareaId"],
                }
            ).unique()["valueId"]

            assert documents_activities_migrated.filter_match(
                match_deleted=False,
                match_datetime_at=datetime_from_document(document=original_activity_old_format_current),
                match_values={
                    "name": original_activity_old_format_current["name"],
                    "valueId": migrated_value_id,
                }
            ).unique()

    #
    # Confirm that the final set of activities are the same in both representations
    #
    original_activity_set = set()
    for original_activity_current in documents_activities.remove_revisions().filter_match(
        match_deleted=False,
    ):
        original_value = documents_values.filter_match(
            match_deleted=False,
            match_datetime_at=datetime_from_document(document=original_activity_current),
            match_values={
                "valueId": original_activity_current["valueId"]
            }
        ).unique()

        original_activity_set.add((
            original_activity_current["name"],
            original_value["name"],
            original_value["lifeAreaId"],
        ))

    for original_activity_old_format_current in documents_activities_old_format.remove_revisions():
        if not original_activity_old_format_current["isDeleted"]:
            original_activity_set.add((
                original_activity_old_format_current["name"],
                original_activity_old_format_current["value"],
                original_activity_old_format_current["lifeareaId"],
            ))

    migrated_activity_set = set()
    for migrated_activity_current in documents_activities_migrated.remove_revisions().filter_match(
        match_deleted=False,
    ):
        migrated_value = documents_values_migrated.filter_match(
            match_deleted=False,
            match_datetime_at=datetime_from_document(document=migrated_activity_current),
            match_values={
                "valueId": migrated_activity_current["valueId"]
            }
        ).unique()

        migrated_activity_set.add((
            migrated_activity_current["name"],
            migrated_value["name"],
            migrated_value["lifeAreaId"],
        ))

    assert original_activity_set == migrated_activity_set

    return documents_activities_migrated


    *,
    collection: DocumentSet,
) -> DocumentSet:
    """
    Renames the type of existing activities.

    This gets them out of the way while we create activities from the values inventory.
    """

    print("  migrate_activity_rename_type_old_format")

    # Migrate documents, tracking which are migrated
    documents_original = []
    documents_migrated = []
    for document_current in collection.filter_match(
        match_type="activity",
        match_deleted=False,
    ):
        is_migrated = False
        document_original = document_current
        document_migrated = copy.deepcopy(document_current)

        # Presence of "startDateTime" indicates this activity
        # is in the old format that includes an embedded schedule
        if "startDateTime" in document_migrated:
            is_migrated = True

            document_migrated["_type"] = "activity_OldFormat"

        if is_migrated:
            # scope.schema_utils.assert_schema(
            #     data=document_migrated,
            #     schema=scope.schema.activity_schema,
            # )

            documents_original.append(document_original)
            documents_migrated.append(document_migrated)

    if len(documents_migrated):
        print("  - Updated {} documents.".format(
            len(documents_migrated),
        ))

    return collection.remove_all(
        documents=documents_original,
    ).union(
        documents=documents_migrated
    )


def _migrate_activity_remove_reminder(
    *,
    collection: DocumentSet,
) -> DocumentSet:
    """
    Remove reminder fields from any activity.
    """

    print("  migrate_activity_remove_reminder")

    # Migrate documents, tracking which are migrated
    documents_original = []
    documents_migrated = []
    for document_current in collection.filter_match(
        match_type="activity",
        match_deleted=False,
    ):
        is_migrated = False
        document_original = document_current
        document_migrated = copy.deepcopy(document_current)

        # Ensure "hasReminder" is always False
        if document_migrated["hasReminder"]:
            is_migrated = True

            document_migrated["hasReminder"] = False

        # Remove any "reminderTimeOfDay"
        if "reminderTimeOfDay" in document_migrated:
            is_migrated = True

            del document_migrated["reminderTimeOfDay"]

        if is_migrated:
            # scope.schema_utils.assert_schema(
            #     data=document_migrated,
            #     schema=scope.schema.activity_schema,
            # )

            documents_original.append(document_original)
            documents_migrated.append(document_migrated)

    if len(documents_migrated):
        print("  - Updated {} documents.".format(
            len(documents_migrated),
        ))

    return collection.remove_all(
        documents=documents_original,
    ).union(
        documents=documents_migrated
    )


def _migrate_activity_log_snapshot(
    *,
    collection: DocumentSet,
) -> DocumentSet:
    """
    Create snapshots for any activity log that does not have one.
    """

    print("  migrate_activity_log_snapshot")

    # Migrate documents, tracking which are migrated
    documents_original = []
    documents_migrated = []
    for document_current in collection.filter_match(
        match_type="activityLog",
        match_deleted=False,
    ):
        is_migrated = False
        document_original = document_current
        document_migrated = copy.deepcopy(document_current)

        # Including the snapshot led to removal of several incomplete fields
        if "activityId" in document_migrated:
            is_migrated = True

            del document_migrated["activityId"]

        if "activityName" in document_migrated:
            is_migrated = True

            del document_migrated["activityName"]

        # completed was determined to be redundant with existence of the log
        if "completed" in document_migrated:
            is_migrated = True

            del document_migrated["completed"]

        # Development included experimentation with an embedded activity document
        if "activity" in document_migrated:
            is_migrated = True

            del document_migrated["activity"]

        # Schema was enhanced to enforce that success No disallows alternative
        # Prior to that the client was storing empty strings
        if document_migrated["success"] == "No":
            if "alternative" in document_migrated:
                is_migrated = True

                assert document_migrated["alternative"] == ""
                del document_migrated["alternative"]

        # Development included generation of some snapshots that
        # captured the scheduledActivity before marking it complete
        if "dataSnapshot" in document_migrated:
            if "scheduledActivity" in document_migrated["dataSnapshot"]:
                if not document_migrated["dataSnapshot"]["scheduledActivity"]["completed"]:
                    is_migrated = True

                    # We expect only two instances of this,
                    # pay attention if we unexpectedly see other instances
                    assert document_migrated["_id"] in [
                        "63eea4a7ac019fe9b4bc07cc",
                        "63efc99eac019fe9b4bc08d2",
                    ]
                    del document_migrated["dataSnapshot"]["scheduledActivity"]

        if "dataSnapshot" not in document_migrated:
            is_migrated = True

            document_migrated["dataSnapshot"] = {}

        if "scheduledActivity" not in document_migrated["dataSnapshot"]:
            is_migrated = True

            document_migrated["dataSnapshot"]["scheduledActivity"] = collection.filter_match(
                match_type="scheduledActivity",
                match_deleted=False,
                match_datetime_at=datetime_from_document(document=document_migrated),
                match_values={
                    "scheduledActivityId": document_migrated["scheduledActivityId"]
                }
            ).unique()

        if is_migrated:
            # scope.schema_utils.assert_schema(
            #     data=document_migrated,
            #     schema=scope.schema.activity_log_schema,
            # )

            documents_original.append(document_original)
            documents_migrated.append(document_migrated)

    if len(documents_migrated):
        print("  - Updated {} documents.".format(
            len(documents_migrated),
        ))

    return collection.remove_all(
        documents=documents_original,
    ).union(
        documents=documents_migrated
    )


def _migrate_assessment_log_with_embedded_assessment(
    *,
    collection: DocumentSet,
) -> DocumentSet:
    """
    Some assessmentLog documents have an embedded assessment.
    These resulted from early experimentation in developing snapshots.
    """

    print("  migrate_assessment_log_with_embedded_assessment")

    # Migrate documents, tracking which are migrated
    documents_original = []
    documents_migrated = []
    for document_current in collection.filter_match(
        match_type="assessmentLog",
        match_deleted=False,
    ):
        is_migrated = False
        document_original = document_current
        document_migrated = copy.deepcopy(document_current)

        if "assessment" in document_migrated:
            is_migrated = True

            # We expect only one instance of this,
            # pay attention if we unexpectedly see other instances
            assert document_migrated["_id"] in [
                "63d04ccf30b3259d115d7503",
            ]

            document_migrated["assessmentId"] = document_migrated["assessment"]["assessmentId"]
            del document_migrated["assessment"]

        if is_migrated:
            # scope.schema_utils.assert_schema(
            #     data=document_migrated,
            #     schema=scope.schema.assessment_log_schema,
            # )

            documents_original.append(document_original)
            documents_migrated.append(document_migrated)

    if len(documents_migrated):
        print("  - Updated {} documents.".format(
            len(documents_migrated),
        ))

    return collection.remove_all(
        documents=documents_original,
    ).union(
        documents=documents_migrated
    )


def _migrate_scheduled_activity_deletion(
    *,
    collection: DocumentSet,
) -> DocumentSet:
    """
    Remove extra fields from any scheduled activity that is a deletion.
    These are left over from an earlier ad-hoc implementation of deletion.
    """

    print("  migrate_scheduled_activity_deletion")

    # Migrate documents, tracking which are migrated
    documents_original = []
    documents_migrated = []
    for document_current in collection.filter_match(
        match_type="scheduledActivity",
    ):
        is_migrated = False
        document_original = document_current
        document_migrated = copy.deepcopy(document_current)

        if "_deleted" in document_migrated:
            # Remove any fields that are not needed in a deletion tombstone
            remove_fields = [
                "activityId",
                "activityName",
                "completed",
                "dueDate",
                "dueDateTime",
                "dueTimeOfDay",
                "reminderDate",
                "reminderDateTime",
                "reminderTimeOfDay",
                "scheduledActivityId",
            ]
            for remove_field_current in remove_fields:
                if remove_field_current in document_migrated:
                    is_migrated = True

                    del document_migrated[remove_field_current]

        if is_migrated:
            scope.schema_utils.assert_schema(
                data=document_migrated,
                schema=scope.schema.set_tombstone_schema,
            )

            documents_original.append(document_original)
            documents_migrated.append(document_migrated)

    if len(documents_migrated):
        print("  - Updated {} documents.".format(
            len(documents_migrated),
        ))

    return collection.remove_all(
        documents=documents_original,
    ).union(
        documents=documents_migrated
    )


def _migrate_scheduled_activity_remove_reminder(
    *,
    collection: DocumentSet,
) -> DocumentSet:
    """
    Remove reminder fields from any scheduled activity.
    """

    print("  migrate_scheduled_activity_remove_reminder")

    # Migrate documents, tracking which are migrated
    documents_original = []
    documents_migrated = []
    for document_current in collection.filter_match(
        match_type="scheduledActivity",
        match_deleted=False,
    ):
        is_migrated = False
        document_original = document_current
        document_migrated = copy.deepcopy(document_current)

        # Remove any "reminderDate"
        if "reminderDate" in document_migrated:
            is_migrated = True

            del document_migrated["reminderDate"]

        # Remove any "reminderDateTime"
        if "reminderDateTime" in document_migrated:
            is_migrated = True

            del document_migrated["reminderDateTime"]

        # Remove any "reminderTimeOfDay"
        if "reminderTimeOfDay" in document_migrated:
            is_migrated = True

            del document_migrated["reminderTimeOfDay"]

        if is_migrated:
            # scope.schema_utils.assert_schema(
            #     data=document_migrated,
            #     schema=scope.schema.scheduled_activity_schema,
            # )

            documents_original.append(document_original)
            documents_migrated.append(document_migrated)

    if len(documents_migrated):
        print("  - Updated {} documents.".format(
            len(documents_migrated),
        ))

    return collection.remove_all(
        documents=documents_original,
    ).union(
        documents=documents_migrated
    )


def _migrate_scheduled_activity_snapshot(
    *,
    collection: DocumentSet,
) -> DocumentSet:
    """
    Create snapshots for any scheduled activity that does not have one.
    """

    print("  migrate_scheduled_activity_snapshot")

    # Migrate documents, tracking which are migrated
    documents_original = []
    documents_migrated = []
    for document_current in collection.filter_match(
        match_type="scheduledActivity",
        match_deleted=False,
    ):
        is_migrated = False
        document_original = document_current
        document_migrated = copy.deepcopy(document_current)

        if "dataSnapshot" not in document_migrated:
            is_migrated = True

            document_migrated["dataSnapshot"] = {}

        if "activitySchedule" not in document_migrated["dataSnapshot"]:
            is_migrated = True

            document_migrated["dataSnapshot"]["activitySchedule"] = collection.filter_match(
                match_type="activitySchedule",
                match_deleted=False,
                match_datetime_at=datetime_from_document(document=document_migrated),
                match_values={
                    "activityScheduleId": document_migrated["activityScheduleId"]
                }
            ).unique()

        if "activity" not in document_migrated["dataSnapshot"]:
            is_migrated = True

            document_migrated["dataSnapshot"]["activity"] = collection.filter_match(
                match_type="activity",
                match_deleted=False,
                match_datetime_at=datetime_from_document(document=document_migrated),
                match_values={
                    "activityId": document_migrated["dataSnapshot"]["activitySchedule"]["activityId"]
                }
            ).unique()

        if "valueId" in document_migrated["dataSnapshot"]["activity"]:
            if "value" not in document_migrated["dataSnapshot"]:
                is_migrated = True

                document_migrated["dataSnapshot"]["value"] = collection.filter_match(
                    match_type="value",
                    match_deleted=False,
                    match_datetime_at=datetime_from_document(document=document_migrated),
                    match_values={
                        "valueId": document_migrated["dataSnapshot"]["activity"]["valueId"]
                    }
                ).unique()

        if is_migrated:
            # scope.schema_utils.assert_schema(
            #     data=document_migrated,
            #     schema=scope.schema.scheduled_activity_schema,
            # )

            documents_original.append(document_original)
            documents_migrated.append(document_migrated)

    if len(documents_migrated):
        print("  - Updated {} documents.".format(
            len(documents_migrated),
        ))

    return collection.remove_all(
        documents=documents_original,
    ).union(
        documents=documents_migrated
    )


def _migrate_values_inventory_refactor_values_and_activities(
    *,
    collection: DocumentSet,
) -> DocumentSet:
    """
    Remove values and activities from values inventory and refactor them into documents.

    This steps through the ordered sequence of values inventory documents.
    At each document, values and activities created for previous documents therefore exist.
    """

    print("  migrate_values_inventory_refactor_values_and_activities")

    # Performance optimization
    documents_filtered_relevant = collection.filter_match(
        match_type="valuesInventory",
    ).union(
        documents=collection.filter_match(
            match_type="value",
        ),
    ).union(
        documents=collection.filter_match(
            match_type="activity",
        ),
    )

    # For each value and activity, createdDateTime functions as a de facto unique id.
    # We need to be able to look these up in both directions.
    value_id_by_created_datetime = {}
    created_datetime_by_value_id = {}
    activity_id_by_created_datetime = {}
    created_datetime_by_activity_id = {}

    # Migrate documents, tracking which are migrated
    documents_original = []
    documents_migrated = []
    documents_created = []
    for document_current in documents_filtered_relevant.filter_match(
        match_type="valuesInventory",
        match_deleted=False,
    ).order_by_revision():
        is_migrated = False
        document_original = document_current
        document_migrated = copy.deepcopy(document_current)

        # Presence of "values" indicates the old format
        if "values" in document_migrated:
            is_migrated = True

            # The createdDateTime of all currently existing values
            document_migrated_values_created_datetimes = [
                value_entry_current["createdDateTime"]
                for value_entry_current in document_migrated["values"]
            ]
            # createdDateTime will always be unique within a set of values
            assert len(document_migrated_values_created_datetimes) == len(set(document_migrated_values_created_datetimes))

            # The createdDateTime of all currently existing activities
            document_migrated_activities_created_datetimes = []
            for value_entry_current in document_migrated["values"]:
                for activity_entry_current in value_entry_current["activities"]:
                    document_migrated_activities_created_datetimes.append(activity_entry_current["createdDateTime"])
            # createdDateTime will always be unique within a set of activities
            assert len(document_migrated_activities_created_datetimes) == len(set(document_migrated_activities_created_datetimes))

            #
            # Values existing at the beginning of this migration step
            #
            values_existing = documents_filtered_relevant.remove_all(
                documents=documents_original,
            ).union(
                documents=documents_migrated,
            ).union(
                documents=documents_created,
            ).filter_match(
                match_type="value",
                match_deleted=False,
                match_datetime_at=datetime_from_document(document=document_migrated)
            )

            #
            # Delete any values that no longer exist
            #
            for value_document_current in values_existing:
                created_datetime = created_datetime_by_value_id[value_document_current["valueId"]]
                if created_datetime not in document_migrated_values_created_datetimes:
                    print("  - Delete Value:")
                    print("    + Was: {}".format(value_document_current["name"]))

                    document_value_deleted = {
                        "_id": document_id_from_datetime(
                            generation_time=datetime_from_document(
                                document=document_migrated,
                            )
                        ),
                        "_type": "value",
                        "_set_id": value_document_current["_set_id"],
                        "_rev": value_document_current["_rev"] + 1,
                        "_deleted": True,
                    }

                    scope.schema_utils.assert_schema(
                        data=document_value_deleted,
                        schema=scope.schema.set_tombstone_schema,
                    )

                    documents_created.append(document_value_deleted)

            #
            # Create/Maintain any values in this values inventory document
            #
            for value_entry_current in document_migrated["values"]:
                if value_entry_current["createdDateTime"] not in value_id_by_created_datetime:
                    # Creating a new value
                    print("  - Create Value:")
                    print("    + Now: {}".format(value_entry_current["name"]))

                    # Generate a new value id
                    value_id = collection_utils.generate_set_id()

                    # Maintain our maps in both directions
                    value_id_by_created_datetime[value_entry_current["createdDateTime"]] = value_id
                    created_datetime_by_value_id[value_id] = value_entry_current["createdDateTime"]

                    value_document_created = {
                        "_id": document_id_from_datetime(
                            generation_time=datetime_from_document(
                                document=document_migrated,
                            )
                        ),
                        "_type": "value",
                        "_set_id": value_id,
                        "_rev": 1,
                        "valueId": value_id,
                        "name": value_entry_current["name"],
                        "lifeAreaId": value_entry_current["lifeareaId"],
                        "editedDateTime": value_entry_current["editedDateTime"],
                    }

                    scope.schema_utils.assert_schema(
                        data=value_document_created,
                        schema=scope.schema.value_schema,
                    )

                    documents_created.append(value_document_created)
                else:
                    # Maintaining an existing value
                    value_id = value_id_by_created_datetime[value_entry_current["createdDateTime"]]

                    value_document_current = values_existing.filter_match(
                        match_values={
                            "valueId": value_id,
                        }
                    ).unique()

                    value_document_changed = (
                        value_document_current["name"] != value_entry_current["name"]
                        or value_document_current["lifeAreaId"] != value_entry_current["lifeareaId"]
                    )

                    if value_document_changed:
                        print("  - Update Value:")
                        print("    + Now: {}".format(value_entry_current["name"]))
                        print("    + Was: {}".format(value_document_current["name"]))

                        value_document_created = {
                            "_id": document_id_from_datetime(
                                generation_time=datetime_from_document(
                                    document=document_migrated,
                                )
                            ),
                            "_type": "value",
                            "_set_id": value_document_current["_set_id"],
                            "_rev": value_document_current["_rev"] + 1,
                            "valueId": value_document_current["valueId"],
                            "name": value_entry_current["name"],
                            "lifeAreaId": value_entry_current["lifeareaId"],
                            "editedDateTime": value_entry_current["editedDateTime"],
                        }

                        scope.schema_utils.assert_schema(
                            data=value_document_created,
                            schema=scope.schema.value_schema,
                        )

                        documents_created.append(value_document_created)

            #
            # The two representations of values should now be the same
            #
            values_existing = documents_filtered_relevant.remove_all(
                documents=documents_original,
            ).union(
                documents=documents_migrated,
            ).union(
                documents=documents_created,
            ).filter_match(
                match_type="value",
                match_deleted=False,
                match_datetime_at=datetime_from_document(document=document_migrated)
            )
            original_values_tuples = [
                (value_entry_current["lifeareaId"], value_entry_current["name"])
                for value_entry_current in document_migrated["values"]
            ]
            migrated_values_tuples = [
                (value_document_current["lifeAreaId"], value_document_current["name"])
                for value_document_current in values_existing
            ]

            assert len(original_values_tuples) == len(migrated_values_tuples)
            assert set(original_values_tuples) == set(migrated_values_tuples)

            #
            # Activities existing at the beginning of this migration step
            #
            activities_existing = documents_filtered_relevant.remove_all(
                documents=documents_original,
            ).union(
                documents=documents_migrated,
            ).union(
                documents=documents_created,
            ).filter_match(
                match_type="activity",
                match_deleted=False,
                match_datetime_at=datetime_from_document(document=document_migrated)
            )

            #
            # Delete any activities that no longer exist
            #
            for activity_document_current in activities_existing:
                created_datetime = created_datetime_by_activity_id[activity_document_current["activityId"]]
                if created_datetime not in document_migrated_activities_created_datetimes:
                    print("  - Delete Activity:")
                    print("    + Was: {}".format(activity_document_current["name"]))

                    document_activity_deleted = {
                        "_id": document_id_from_datetime(
                            generation_time=datetime_from_document(
                                document=document_migrated,
                            )
                        ),
                        "_type": "activity",
                        "_set_id": activity_document_current["_set_id"],
                        "_rev": activity_document_current["_rev"] + 1,
                        "_deleted": True,
                    }

                    scope.schema_utils.assert_schema(
                        data=document_activity_deleted,
                        schema=scope.schema.set_tombstone_schema,
                    )

                    documents_created.append(document_activity_deleted)

            #
            # Create/Maintain any values in this values inventory document
            #
            for value_entry_current in document_migrated["values"]:
                value_document_current = values_existing.filter_match(
                    match_values={
                        "valueId": value_id_by_created_datetime[value_entry_current["createdDateTime"]],
                    }
                ).unique()

                for activity_entry_current in value_entry_current["activities"]:
                    if activity_entry_current["createdDateTime"] not in activity_id_by_created_datetime:
                        # Creating a new activity
                        print("  - Create Activity:")
                        print("    + Now: {}".format(activity_entry_current["name"]))
                        print("           E: {} / I: {}".format(
                            activity_entry_current["enjoyment"],
                            activity_entry_current["importance"],
                        ))

                        # Generate a new activity id
                        activity_id = collection_utils.generate_set_id()

                        # Maintain our maps in both directions
                        activity_id_by_created_datetime[activity_entry_current["createdDateTime"]] = activity_id
                        created_datetime_by_activity_id[activity_id] = activity_entry_current["createdDateTime"]

                        activity_document_created = {
                            "_id": document_id_from_datetime(
                                generation_time=datetime_from_document(
                                    document=document_migrated,
                                )
                            ),
                            "_type": "activity",
                            "_set_id": activity_id,
                            "_rev": 1,
                            "activityId": activity_id,
                            "name": activity_entry_current["name"],
                            "enjoyment": activity_entry_current["enjoyment"],
                            "importance": activity_entry_current["importance"],
                            "valueId": value_document_current["valueId"],
                            "editedDateTime": activity_entry_current["editedDateTime"],
                        }

                        scope.schema_utils.assert_schema(
                            data=activity_document_created,
                            schema=scope.schema.activity_schema,
                        )

                        documents_created.append(activity_document_created)
                    else:
                        # Maintaining an existing activity
                        activity_document_current = activities_existing.filter_match(
                            match_values={
                                "activityId": activity_id_by_created_datetime[activity_entry_current["createdDateTime"]]
                            }
                        ).unique()

                        activity_document_changed = (
                            activity_document_current["name"] != activity_entry_current["name"]
                            or activity_document_current["enjoyment"] != activity_entry_current["enjoyment"]
                            or activity_document_current["importance"] != activity_entry_current["importance"]
                        )

                        if activity_document_changed:
                            print("  - Update Activity:")
                            print("    + Now: {}".format(activity_entry_current["name"]))
                            print("           E: {} / I: {}".format(
                                activity_entry_current["enjoyment"],
                                activity_entry_current["importance"],
                            ))
                            print("    + Was: {}".format(activity_document_current["name"]))
                            print("           E: {} / I: {}".format(
                                activity_document_current["enjoyment"],
                                activity_document_current["importance"],
                            ))

                            activity_document_created = {
                                "_id": document_id_from_datetime(
                                    generation_time=datetime_from_document(
                                        document=document_migrated,
                                    )
                                ),
                                "_type": "activity",
                                "_set_id": activity_document_current["_set_id"],
                                "_rev": activity_document_current["_rev"] + 1,
                                "activityId": activity_document_current["activityId"],
                                "name": activity_entry_current["name"],
                                "enjoyment": activity_entry_current["enjoyment"],
                                "importance": activity_entry_current["importance"],
                                "valueId": value_document_current["valueId"],
                                "editedDateTime": activity_entry_current["editedDateTime"],
                            }

                            scope.schema_utils.assert_schema(
                                data=activity_document_created,
                                schema=scope.schema.activity_schema,
                            )

                            documents_created.append(activity_document_created)

            #
            # The two representations of activities should now be the same
            #
            activities_existing = documents_filtered_relevant.remove_all(
                documents=documents_original,
            ).union(
                documents=documents_migrated,
            ).union(
                documents=documents_created,
            ).filter_match(
                match_type="activity",
                match_deleted=False,
                match_datetime_at=datetime_from_document(document=document_migrated)
            )
            original_activities_tuples = []
            for value_entry_current in document_migrated["values"]:
                for activity_entry_current in value_entry_current["activities"]:
                    original_activities_tuples.append((
                        activity_entry_current["name"],
                        activity_entry_current["enjoyment"],
                        activity_entry_current["importance"],
                        value_entry_current["name"],
                        value_entry_current["lifeareaId"],
                    ))

            migrated_activities_tuples = []
            for activity_document_current in activities_existing:
                value_document_current = values_existing.filter_match(
                    match_values={
                        "valueId": activity_document_current["valueId"],
                    },
                ).unique()

                migrated_activities_tuples.append((
                    activity_document_current["name"],
                    activity_document_current["enjoyment"],
                    activity_document_current["importance"],
                    value_document_current["name"],
                    value_document_current["lifeAreaId"],
                ))

            assert len(original_activities_tuples) == len(migrated_activities_tuples)
            assert set(original_activities_tuples) == set(migrated_activities_tuples)

            #
            # Migrated fields can now be removed from the values inventory
            #
            del document_migrated["values"]
            del document_migrated["lastUpdatedDateTime"]

        if is_migrated:
            scope.schema_utils.assert_schema(
                data=document_migrated,
                schema=scope.schema.values_inventory_schema,
            )

            documents_original.append(document_original)
            documents_migrated.append(document_migrated)

    if len(documents_migrated):
        print("  - Updated {} documents.".format(
            len(documents_migrated),
        ))
    if len(documents_created):
        print("  - Created {} documents.".format(
            len(documents_created),
        ))

    return collection.remove_all(
        documents=documents_original,
    ).union(
        documents=documents_migrated
    ).union(
        documents=documents_created,
    )
