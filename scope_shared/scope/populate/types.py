import abc
from typing import List, Optional


class PopulateAction(abc.ABC):
    @abc.abstractmethod
    def prompt(self) -> List[str]:
        """
        Provide a short string describing the action to be performed.
        This will be displayed as the confirmation prompt.
        """
        pass

    @abc.abstractmethod
    def perform(self, *, populate_config: dict) -> dict:
        """
        Perform the action.
        Return a new state of the populate config.
        """
        pass


class PopulateRule(abc.ABC):
    """
    A rule that can be matched against a current populate config.

    If the rule matches, it will provide a PopulateAction that can be performed.
    """

    @abc.abstractmethod
    def match(self, *, populate_config: dict) -> Optional[PopulateAction]:
        pass
