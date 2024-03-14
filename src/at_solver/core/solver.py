from at_krl.core.knowledge_base import KnowledgeBase
from at_solver.core.wm import WorkingMemory
from at_solver.core.goals import GoalTreeMap
from at_solver.core.goals import Goal

from typing import List

class SOLVER_MODE:
    forwards = 'forward'
    backwards = 'backward'
    mixed = 'mixed'

class Solver:
    wm: WorkingMemory = None
    kb: KnowledgeBase = None

    mode: str = None
    goal_tree: GoalTreeMap = None
    goals: List[Goal] = None

    def __init__(self, kb: KnowledgeBase, mode: str, goals: list) -> None:
        self.wm = WorkingMemory(kb)
        self.mode = mode
        self.goals = goals
        self.goal_tree = GoalTreeMap(kb)
