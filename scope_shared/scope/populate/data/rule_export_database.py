from typing import List, Optional

from scope.populate.types import PopulateAction, PopulateContext, PopulateRule

ACTION_NAME = "export_database"


class ExportDatabase(PopulateRule):
    def match(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> Optional[PopulateAction]:
        for action_current in populate_config["actions"]:
            if action_current.get("action", None) == ACTION_NAME:
                return _ExportDatabaseAction()

        return None


class _ExportDatabaseAction(PopulateAction):
    def prompt(self) -> List[str]:
        return ["Export database"]

    def perform(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> dict:
        # Retrieve and remove our action
        for action_current in populate_config["actions"]:
            if action_current.get("action", None) == ACTION_NAME:
                populate_config["actions"].remove(action_current)
                break

        return populate_config
