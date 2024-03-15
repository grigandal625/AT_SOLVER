from at_krl.core.knowledge_base import KnowledgeBase
from at_krl.core.kb_rule import KBRule
from at_krl.core.kb_instruction import KBInstruction
from at_krl.core.kb_instruction import AssignInstruction
from at_solver.core.wm import WorkingMemory
from at_solver.core.goals import GoalTreeMap
from at_solver.core.goals import Goal
from at_solver.evaluations.basic import BasicEvaluator
from at_solver.core.trace import Trace
from at_solver.core.trace import ForwardStep

from typing import List


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

    def __init__(self, kb: KnowledgeBase, mode: str, goals: list) -> None:
        self.wm = WorkingMemory(kb)
        self.mode = mode
        self.goals = goals
        self.goal_tree = GoalTreeMap(kb)
        self.trace = Trace()

    @property
    def fired_rules(self) -> List[KBRule]:
        relevant_steps = [step for step in self.trace.steps if hasattr(step, 'fire_rules')]
        if relevant_steps:
            relevant_steps[-1].fired_rules
        return []

    def match_forward(self) -> List[KBRule]:
        result = []
        evaluator = BasicEvaluator(self)
        for rule in self.wm.env._type_or_class.rules:
            if rule not in self.fired_rules:
                evaluated_condition = evaluator.eval(rule.condition)
                if evaluated_condition is not None and evaluated_condition.content is not None:
                    if evaluated_condition.content and rule.instructions or not evaluated_condition.content and rule.else_instructions:
                        rule.evaluated_condition = evaluated_condition
                        result.append(rule)

        return result
    
    def make_step_forward(self) -> ForwardStep:
        step = ForwardStep(self.wm)
        step.conflict_rules = self.match_forward()
        if step.conflict_rules:
            step.selected_rule = step.conflict_rules[0]
            self.fire_rule(step.selected_rule)
            step.fired_rules = self.fired_rules + [step.selected_rule]
            step.final_wm_state = self.wm
        return step
        
    def run_forward(self):
        self.trace.steps = []
        
        while True:
            step = self.make_step_forward()
            if not step.conflict_rules:
                break
            self.trace.steps.append(step)

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