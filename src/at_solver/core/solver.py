from at_krl.core.knowledge_base import KnowledgeBase
from at_solver.core.wm import WorkingMemory

class Solver:
    wm: WorkingMemory = None
    kb: KnowledgeBase = None

    mode: str = None
    goals: list = None