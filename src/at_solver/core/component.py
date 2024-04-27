from at_queue.core.session import ConnectionParameters
from at_solver.core.solver import Solver, SOLVER_MODE
from at_queue.core.at_component import ATComponent
from at_queue.utils.decorators import authorized_method
from at_krl.core.knowledge_base import KnowledgeBase
from at_krl.core.kb_value import KBValue
from at_krl.core.kb_reference import KBReference
from at_krl.core.non_factor import NonFactor
from typing import Dict, TypedDict, Union, Optional, List
from at_solver.core.wm import WorkingMemory
from at_solver.core.wm import KBValueDict
from at_solver.core.goals import Goal
import logging

logger = logging.getLogger(__name__)


class WMItemDict(TypedDict):
    ref: str
    value: Optional[Union[str, int, float, bool]]
    belief: Optional[Union[int, float]]
    probability: Optional[Union[int, float]]
    accuracy: Optional[Union[int, float]]


class ForwardStepDict(TypedDict):
    initial_wm_state: Dict[str, KBValueDict]
    final_wm_state: Dict[str, KBValueDict]
    conflict_rules: List[str]
    selected_rule: str
    fired_rules: List[str]
    rule_condition_value: Union[int, float, str, bool, None]


class SelectGoalStepDict(TypedDict):
    initial_wm_state: Dict[str, KBValueDict]
    final_goal: str
    final_goal_stack: List[str]
    current_goal: str
    current_goal_stack: List[str]


class ReachGoalStepDict:
    initial_wm_state: Dict[str, KBValueDict]
    final_wm_state: Dict[str, KBValueDict]
    conflict_rules: List[str]
    selected_rule: str
    fired_rules: List[str]
    rule_condition_value: Union[int, float, str, bool, None]

    final_goal: str
    final_goal_stack: List[str]
    current_goal: str
    current_goal_stack: List[str]


class TraceDict(TypedDict):
    steps: List[Union[ForwardStepDict, SelectGoalStepDict, ReachGoalStepDict]]


class RunResultDict(TypedDict):
    wm: Dict[str, KBValueDict]
    trace: TraceDict


class ATSolver(ATComponent):
    solvers: Dict[str, Solver]

    def __init__(self, connection_parameters: ConnectionParameters, *args, **kwargs):
        super().__init__(connection_parameters, *args, **kwargs)
        self.solvers = {}

    @authorized_method
    def create_solver(self, kb: dict, mode:str=None, goals: List[str] = None, auth_token: str = None) -> bool:
        mode = mode or SOLVER_MODE.forwards

        if mode not in [SOLVER_MODE.forwards, SOLVER_MODE.backwards, SOLVER_MODE.mixed]:
            raise ValueError(f'Invalid solver mode "{mode}"')
        
        auth_token = auth_token or 'default'
        
        knowledge_base = KnowledgeBase.from_dict(kb)
        knowledge_base.validate()

        parsed_goals = []

        if (mode == SOLVER_MODE.backwards) or (mode == SOLVER_MODE.mixed):
            if goals is None or not len(goals):
                raise ValueError(f"Expected goals to config solver with mode {mode}")
        for goal_ref in goals:
            parsed_goals.append(Goal(KBReference.parse(goal_ref)))
        solver = Solver(knowledge_base, mode=mode, goals=parsed_goals)
        self.solvers[auth_token] = solver
        return True
    
    @authorized_method
    def has_solver(self, auth_token: str = None) -> bool:
        try:
            self.get_solver(auth_token)
            return True
        except ValueError:
            return False
    
    def get_solver(self, auth_token: str = None) -> Solver:
        auth_token = auth_token or 'default'
        solver = self.solvers.get(auth_token)
        if solver is None:
            raise ValueError("Solver for token '%s' is not created" % auth_token)
        return solver

    @authorized_method
    def update_wm(self, items: List[WMItemDict], clear_befor: bool = True, auth_token: str = None) -> bool:
        
        solver = self.get_solver(auth_token=auth_token)
        if clear_befor:
            solver.wm = WorkingMemory(solver.kb)
        for item in items:
            nf = NonFactor(
                belief=item.get('belief'), 
                probability=item.get('probability'), 
                accuracy=item.get('accuracy')
            )
            v = KBValue(content=item['value'], non_factor=nf)
            solver.wm.set_value(item['ref'], v)
        
        return True
    
    @authorized_method
    def set_mode(self, mode: str, goals: List[str] = None, auth_token: str = None) -> bool:
        
        if mode not in [SOLVER_MODE.forwards, SOLVER_MODE.backwards, SOLVER_MODE.mixed]:
            raise ValueError(f'Invalid solver mode "{mode}"')

        solver = self.get_solver(auth_token=auth_token)
        parsed_goals = []

        if mode == SOLVER_MODE.forwards and ((goals is not None and len(goals))):
            logger.warning(f'Goals will not be applied to solver for mode "{mode}"')

        if (mode == SOLVER_MODE.backwards) or (mode == SOLVER_MODE.mixed):
            if not len(solver.goals) and (goals is None or not len(goals)):
                raise ValueError(f"Expected goals to config solver with mode \"{mode}\"")
            for goal_ref in goals:
                parsed_goals.append(Goal(KBReference.parse(goal_ref)))

            if parsed_goals:
                solver.set_goals(parsed_goals)
        solver.mode = mode
    
    @authorized_method
    def run(self, auth_token: str) -> RunResultDict:
        
        solver = self.get_solver(auth_token)
        trace = solver.run()
        return {
            'trace': trace.__dict__,
            'wm': solver.wm.all_values_dict
        }
    
    @authorized_method
    async def arun(self, auth_token: str) -> RunResultDict:
        
        solver = self.get_solver(auth_token)
        trace = await solver.arun()
        return {
            'trace': trace.__dict__,
            'wm': solver.wm.all_values_dict
        }
    
    