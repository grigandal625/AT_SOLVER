from at_krl.core.knowledge_base import KnowledgeBase
from at_krl.core.kb_rule import KBRule
from at_krl.core.kb_value import KBValue
from at_krl.core.kb_instruction import KBInstruction
from at_krl.core.kb_instruction import AssignInstruction
from at_solver.core.wm import WorkingMemory
from at_solver.core.goals import GoalTreeMap
from at_solver.core.goals import Goal
from at_solver.evaluations.basic import BasicEvaluator
from at_solver.core.trace import Trace
from at_solver.core.trace import ForwardStep
from at_solver.core.trace import SelectGoalStep
from at_solver.core.trace import ReachGoalStep

from typing import List, Union


class SOLVER_MODE:
    forwards = 'forward'
    backwards = 'backward'
    mixed = 'mixed'


class Solver:
    wm: WorkingMemory = None
    kb: KnowledgeBase = None
    trace: Trace = None

    mode: str = None
    goal_tree: GoalTreeMap = None
    goals: List[Goal] = None
    goal_stack: List[Goal] = None
    _watched_goals: List[Goal] = None

    def __init__(self, kb: KnowledgeBase, mode: str, goals: list) -> None:
        self.wm = WorkingMemory(kb)
        self.mode = mode
        self.goal_tree = GoalTreeMap(kb)
        self.goals = [self.goal_tree.get_or_create_goal_by_ref(goal.ref) for goal in goals]
        self.trace = Trace()
        self.goal_stack = []
        self._watched_goals = []

    def reset_wm(self):
        self.wm = WorkingMemory(self.wm.kb)

    @property
    def fired_rules(self) -> List[KBRule]:
        relevant_steps = [step for step in self.trace.steps if hasattr(step, 'fired_rules')]
        if relevant_steps:
            return relevant_steps[-1].fired_rules
        return []

    def match_forward(self) -> List[KBRule]:
        result = []
        evaluator = BasicEvaluator(self)
        for rule in self.wm.env.type_or_class.rules:
            if rule not in self.fired_rules:
                evaluated_condition = evaluator.eval(rule.condition)
                if evaluated_condition is not None and evaluated_condition.content is not None:
                    if evaluated_condition.content and rule.instructions or not evaluated_condition.content and rule.else_instructions:
                        rule.evaluated_condition = evaluated_condition
                        result.append(rule)
        return result # тут нужна сортировка
    
    def make_step_forward(self) -> ForwardStep:
        step = ForwardStep(self.wm)
        step.conflict_rules = self.match_forward()
        if step.conflict_rules:
            step.selected_rule = step.conflict_rules[0]
            step.rule_condition_value = KBValue.from_dict(step.selected_rule.evaluated_condition.__dict__())
            self.fire_rule(step.selected_rule)
            step.fired_rules = self.fired_rules + [step.selected_rule]
            step.final_wm_state = self.wm
        return step
        
    def run_forward(self) -> Trace:
        self.trace.steps = []
        
        while True:
            step = self.make_step_forward()
            if not step.conflict_rules:
                break
            self.trace.steps.append(step)
        return self.trace

    def goal_is_reached(self, goal: Goal):
        v = self.wm.get_value_by_ref(goal.ref)
        return (v is not None) and (v.content is not None)
    
    def get_rules_deducting_goal(self, goal: Goal) -> List[KBRule]:
        evaluator = BasicEvaluator(self)
        rules = []
        for rule in self.wm.env.type_or_class.rules:
            rule_refs = self.goal_tree.get_rule_instructions_references(rule)
            for ref in rule_refs:
                if self.goal_tree.check_references_equal(ref, goal.ref):
                    rule_condition_value = evaluator.eval(rule.condition)
                    if (rule_condition_value is not None) and rule_condition_value.content is not None:
                        rule.evaluated_condition = rule_condition_value
                        rules.append(rule)
                        break
        return rules

    def goal_is_reachable(self, goal: Goal):
        return bool(len(self.get_rules_deducting_goal(goal)))
    
    def goal_in_stack(self, goal: Goal):
        for g in self.goal_stack:
            if self.goal_tree.check_references_equal(goal.ref, g.ref):
                return True
        return False
    
    def goal_is_watched(self, goal: Goal):
        for g in self._watched_goals:
            if self.goal_tree.check_references_equal(goal.ref, g.ref):
                return True
        return False

    def match_backward(self, rules: List[KBRule]) -> List[KBRule]:
        return rules # тут нужна сортировка

    def make_step_backward(self) -> Union[SelectGoalStep, ReachGoalStep]:
        current_goal = self.goal_stack[-1]
        current_goal_rules = self.get_rules_deducting_goal(current_goal)
        step = None
        if self.goal_is_reached(current_goal):
            step = SelectGoalStep(self.wm)
            step.current_goal_stack = [g for g in self.goal_stack]
            if self.goal_stack:
                self.goal_stack.pop()
            if len(self.goal_stack):
                step.final_goal = self.goal_stack[-1]
        if len(current_goal_rules):
            step = ReachGoalStep(self.wm)
            step.current_goal_stack = [g for g in self.goal_stack]
            step.current_goal = current_goal
            step.conflict_rules = self.match_backward(current_goal_rules)
            step.selected_rule = step.conflict_rules[0]
            step.rule_condition_value = KBValue.from_dict(step.selected_rule.evaluated_condition.__dict__())
            self.fire_rule(step.selected_rule)
            step.fired_rules = self.fired_rules + [step.selected_rule]
            step.final_wm_state = self.wm
            if self.goal_stack:
                self.goal_stack.pop()
            if len(self.goal_stack):
                step.final_goal = self.goal_stack[-1]
        else:
            step = SelectGoalStep(self.wm)
            step.current_goal_stack = [g for g in self.goal_stack]
            subgoals = [g for g in current_goal.subgoals if not self.goal_in_stack(g) and not self.goal_is_watched(self)]
            if len(subgoals):
                final_subgoal = max(subgoals, key=lambda g: len(g.subgoals))
                step.final_goal = final_subgoal
                self.goal_stack.append(final_subgoal)
            else:
                self._watched_goals.append(current_goal)
                if self.goal_stack:
                    self.goal_stack.pop()
                if len(self.goal_stack):
                    step.final_goal = self.goal_stack[-1]
        step.final_goal_stack = [g for g in self.goal_stack]
        return step
    
    def run_backward(self) -> Trace:
        self.trace.steps = []
        self.goal_stack = [g for g in self.goals]
        self.goal_stack.sort(key=lambda g: len(g.subgoals))

        while len(self.goal_stack):
            step = self.make_step_backward()
            self.trace.steps.append(step)
        
        return self.trace

    def fire_rule(self, rule: KBRule):
        if rule.evaluated_condition.content:
            for instruction in rule.instructions:
                self.interprite_instruction(instruction)
        else:
            for instruction in rule.else_instructions:
                self.interprite_instruction(instruction)

    def interprite_instruction(self, instruction: KBInstruction):
        if isinstance(instruction, AssignInstruction):
            self.interprite_assign(instruction)

    def interprite_assign(self, instruction: AssignInstruction):
        evaluator = BasicEvaluator(self)
        value = evaluator.eval(instruction.value)
        self.wm.set_value(instruction.ref, value)