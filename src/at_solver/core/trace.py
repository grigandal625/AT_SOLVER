from at_solver.core.wm import WorkingMemory
from at_krl.core.kb_value import KBValue
from at_krl.core.kb_class import KBInstance
from at_krl.core.kb_rule import KBRule
from at_solver.core.goals import Goal

from typing import List


class TraceStep:
    initial_wm_state: WorkingMemory
    
    def __init__(self, wm: WorkingMemory) -> None:
        self.initial_wm_state = WorkingMemory(wm.kb)

        self.initial_wm_state.locals = {
            key: KBValue(v.content, non_factor=v.non_factor)
            if v is not None
            else KBValue(None)

            for key, v in wm.locals.items()
        }

        self.initial_wm_state.env = KBInstance.from_dict(wm.env.__dict__())
        self.initial_wm_state.env.validate(self.wm_state.kb)
        

class ForwardStep(TraceStep):
    _final_wm_state: WorkingMemory
    conflict_rules: List[KBRule]
    selected_rule: KBRule
    fired_rules: List[KBRule]

    @property
    def final_wm_state(self):
        return self._final_wm_state
    
    @final_wm_state.setter
    def final_wm_state(self, wm: WorkingMemory) -> None:
        self._final_wm_state = WorkingMemory(wm.kb)

        self._final_wm_state.locals = {
            key: KBValue(v.content, non_factor=v.non_factor)
            if v is not None
            else KBValue(None)

            for key, v in wm.locals.items()
        }

        self._final_wm_state.env = KBInstance.from_dict(wm.env.__dict__())
        self._final_wm_state.env.validate(self._final_wm_state.kb)


class BackwardStep(TraceStep):
    final_goal: Goal
    final_goal_stack: List[Goal]


class SelectGoalStep(BackwardStep):
    current_goal: Goal
    current_goal_stack: List[Goal]


class ReachGoalStep(SelectGoalStep, ForwardStep):
    pass


class Trace:
    steps: List[TraceStep]

    def __init__(self) -> None:
        self.steps = []
