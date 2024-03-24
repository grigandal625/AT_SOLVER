from typing import List, Union
from at_krl.core.kb_reference import KBReference
from at_krl.core.temporal.kb_allen_operation import KBAllenOperation
from at_krl.core.knowledge_base import KnowledgeBase
from at_krl.core.kb_rule import KBRule
from at_krl.core.kb_value import Evaluatable
from at_krl.core.kb_operation import KBOperation
from at_krl.core.kb_instruction import AssignInstruction


class Goal:
    _subgoals: List['Goal']
    _pregoals: List['Goal']
    ref: KBReference = None
    _goal_tree_map: 'GoalTreeMap'

    def __init__(self, ref: KBReference, goal_tree_map: 'GoalTreeMap'):
        self.ref = ref
        self._goal_tree_map = goal_tree_map
        self.goal_tree_map.all_goals.append(self)

    @property
    def goal_tree_map(self):
        return self._goal_tree_map

    @property
    def subgoals(self) -> List['Goal']:
        if self._subgoals is None:
            self._subgoals = []
            for rule in self.goal_tree_map.kb.world.rules:
                if self.goal_tree_map.rule_has_ref_in_instructions(self.ref):
                    self._subgoals += [
                        self.goal_tree_map.get_or_create_goal_by_ref(ref)
                        for ref in self.goal_tree_map.get_rule_condition_references(rule)
                    ]
        return self._subgoals

    @property
    def pregoals(self) -> List['Goal']:
        if self._pregoals is None:
            self._pregoals = []
            for rule in self.goal_tree_map.kb.world.rules:
                if self.goal_tree_map.rule_has_ref_in_condition(self.ref):
                    self._pregoals += [
                        self.goal_tree_map.get_or_create_goal_by_ref(ref)
                        for ref in self.goal_tree_map.get_rule_instructions_references(rule)
                    ]
        return self._pregoals
    

class GoalTreeMap:
    _root_goals: List[Goal] = None
    _final_goals: List[Goal] = None
    _kb: KnowledgeBase
    all_goals: List[Goal] = None

    def __init__(self, kb) -> None:
        self._kb = kb
        self.all_goals = []
        self.build()

    def get_goal_by_ref(self, ref: KBReference) -> Union[Goal, None]:
        for g in self.all_goals:
            if self.check_references_equal(g.ref, ref):
                return g
            
    def get_or_create_goal_by_ref(self, ref: KBReference) -> Goal:
        goal = self.get_goal_by_ref(ref)
        if goal is None:
            goal = Goal(ref, self)
        return goal

    @property
    def kb(self) -> KnowledgeBase:
        return self._kb
    
    def build(self) -> None:
        self.root_goals
        self.final_goals
        for rule in self.kb.world.rules:
            for ref in self.get_rule_condition_references(rule):
                self.get_or_create_goal_by_ref(ref)
            for ref in self.get_rule_instructions_references(rule):
                self.get_or_create_goal_by_ref(ref)
        for goal in self.all_goals:
            goal.subgoals
            goal.pregoals

    @property
    def final_goals(self) -> List[Goal]:
        if self._final_goals is None:
            self._final_goals = []
            for rule in self.kb.world.rules:
                instr_references = self.get_rule_instructions_references(rule)
                for ref in instr_references:
                    if not len([r for r in self.kb.world.rules if not self.rule_has_ref_in_condition(r, ref)]):
                        self._final_goals.append(self.get_or_create_goal_by_ref(ref))
        return self._final_goals

    @property
    def root_goals(self) -> List[Goal]:
        if self._root_goals is None:
            self._root_goals = []
            for rule in self.kb.world.rules:
                condition_references = self.get_rule_condition_references(rule)
                for ref in condition_references:
                    if not len([r for r in self.kb.world.rules if not self.rule_has_ref_in_instructions(r, ref)]):
                        self._root_goals.append(self.get_or_create_goal_by_ref(ref))
        return self._root_goals

    @staticmethod
    def get_rule_condition_references(rule: KBRule) -> List[KBReference]:
        return GoalTreeMap.get_evaluatable_references(rule.condition)
    
    @staticmethod
    def get_rule_instructions_references(rule: KBRule) -> List[KBReference]:
        return [
            instr.ref
            for instr in rule.instructions if isinstance(instr, AssignInstruction)
        ] + [
            instr.ref
            for instr in rule.else_instructions if isinstance(instr, AssignInstruction)
        ]

    @staticmethod
    def get_evaluatable_references(e: Evaluatable) -> List[KBReference]:
        if e is None:
            return []
        if isinstance(e, KBReference):
            return [e]
        if isinstance(e, KBAllenOperation):
            return []
        if isinstance(e, KBOperation):
            return GoalTreeMap.get_evaluatable_references(e.left) + GoalTreeMap.get_evaluatable_references(e.right)
        return []
    
    @staticmethod
    def rule_has_ref_in_condition(rule: KBRule, ref: KBReference) -> bool:
        return GoalTreeMap.evaluatable_contains_ref(rule.condition, ref)

    @staticmethod
    def rule_has_ref_in_instructions(rule: KBRule, ref: KBReference) -> bool:
        for instr in rule.instructions:
            if isinstance(instr, AssignInstruction):
                if GoalTreeMap.check_references_equal(instr.ref, ref):
                    return True
        for instr in rule.else_instructions:
            if isinstance(instr, AssignInstruction):
                if GoalTreeMap.check_references_equal(instr.ref, ref):
                    return True
        return False
        
    @staticmethod
    def evaluatable_contains_ref(e: Evaluatable, ref: KBReference) -> bool:
        if e is None:
            return False
        if isinstance(e, KBReference):
            return GoalTreeMap.check_references_equal(e, ref)
        if isinstance(e, KBAllenOperation):
            return False
        if isinstance(e, KBOperation):
            return GoalTreeMap.evaluatable_contains_ref(e.left, ref) or GoalTreeMap.evaluatable_contains_ref(e.right, ref)
        return False
        
    @staticmethod
    def check_references_equal(r1: KBReference, r2: KBReference) -> bool:
        if r1 is None and r2 is not None or r1 is not None and r2 is None:
            return False
        if r1.id != r2.id:
            return False
        if r1.ref is None and r2.ref is None:
            return True
        return GoalTreeMap.check_references_equal(r1.ref, r2.ref)
        