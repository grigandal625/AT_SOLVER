from typing import List
from at_krl.core.kb_reference import KBReference
from at_krl.core.knowledge_base import KnowledgeBase

class Goal:
    _subgoals: List['Goal']
    ref: KBReference = None

    def __init__(self, ref: KBReference):
        self.ref = ref
        self._subgoals = []

    @property
    def subgoals(self) -> List['Goal']:
        return self._subgoals


class GoalTreeMap:
    root_goals: List[Goal]
    _kb: KnowledgeBase

    def __init__(self, kb) -> None:
        self._kb = kb

    @property
    def kb(self) -> KnowledgeBase:
        return self._kb