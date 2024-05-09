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
        self.initial_wm_state.env.validate(self.initial_wm_state.kb)

    @property
    def __dict__(self):
        return {
            'initial_wm_state': self.initial_wm_state.all_values_dict
        }
        

class ForwardStep(TraceStep):
    _final_wm_state: WorkingMemory
    conflict_rules: List[KBRule]
    selected_rule: KBRule
    fired_rules: List[KBRule]
    rule_condition_value: KBValue = None

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

    @property
    def __dict__(self):
        return {
            'final_wm_state': self.final_wm_state.all_values_dict,
            'conflict_rules': [rule.id for rule in self.conflict_rules],
            'selected_rule': self.selected_rule.id,
            'fired_rules': [rule.id for rule in self.fired_rules],
            'rule_condition_value': self.rule_condition_value.content,
            **super().__dict__
        }


class BackwardStep(TraceStep):
    final_goal: Goal
    final_goal_stack: List[Goal]

    @property
    def __dict__(self):
        return {
            'final_goal': self.final_goal.ref.id,
            'final_goal_stack': [g.ref.id for g in self.final_goal_stack],
            **super().__dict__
        }


class SelectGoalStep(BackwardStep):
    current_goal: Goal
    current_goal_stack: List[Goal]

    @property
    def __dict__(self):
        return {
            'current_goal': self.current_goal.ref.id,
            'current_goal_stack': [g.ref.id for g in self.current_goal_stack],
            **super().__dict__
        }


class ReachGoalStep(SelectGoalStep, ForwardStep):
    
    @property
    def __dict__(self):
        return {
            'initial_wm_state': self.initial_wm_state.all_values_dict,
            'final_wm_state': self.final_wm_state.all_values_dict,
            'conflict_rules': [rule.id for rule in self.conflict_rules],
            'selected_rule': self.selected_rule.id,
            'fired_rules': [rule.id for rule in self.fired_rules],
            'rule_condition_value': self.rule_condition_value.content,
            'current_goal': self.current_goal.ref.id,
            'current_goal_stack': [g.ref.id for g in self.current_goal_stack],
            'final_goal': self.final_goal.ref.id,
            'final_goal_stack': [g.ref.id for g in self.final_goal_stack],
        }


class Trace:
    steps: List[TraceStep]

    def __init__(self) -> None:
        self.steps = []

    @property
    def __dict__(self):
        return {
            'steps': [step.__dict__ for step in self.steps]
        }
