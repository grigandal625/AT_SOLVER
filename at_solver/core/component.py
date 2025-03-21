import logging
from typing import Awaitable
from typing import Dict
from typing import List
from typing import Optional
from typing import TypedDict
from typing import Union
from uuid import UUID
from xml.etree.ElementTree import Element

from aio_pika import IncomingMessage
from at_config.core.at_config_handler import ATComponentConfig
from at_krl.core.kb_reference import KBReference
from at_krl.core.kb_value import KBValue
from at_krl.core.knowledge_base import KnowledgeBase
from at_krl.core.non_factor import NonFactor
from at_queue.core.at_component import ATComponent
from at_queue.core.session import ConnectionParameters
from at_queue.utils.decorators import authorized_method

from at_solver.core.goals import Goal
from at_solver.core.solver import Solver
from at_solver.core.solver import SOLVER_MODE
from at_solver.core.trace import Trace
from at_solver.core.wm import KBValueDict
from at_solver.core.wm import WorkingMemory


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
    solvers: Dict[str | int, Solver]

    def __init__(self, connection_parameters: ConnectionParameters, *args, **kwargs):
        super().__init__(connection_parameters, *args, **kwargs)
        self.solvers = {}

    def get_kb_from_config(self, config: ATComponentConfig) -> KnowledgeBase:
        kb_item = config.items.get("kb")
        if kb_item is None:
            kb_item = config.items.get("knowledge_base")
        if kb_item is None:
            kb_item = config.items.get("knowledge-base")
        if kb_item is None:
            raise ValueError("Knowledge base is required")
        kb_data = kb_item.data
        if isinstance(kb_data, Element):
            return KnowledgeBase.from_xml(kb_data)
        elif isinstance(kb_data, dict):
            return KnowledgeBase.from_json(kb_data)
        elif isinstance(kb_data, str):
            return KnowledgeBase.from_krl(kb_data)
        else:
            raise TypeError("Not valid type of knowledge base configuration")

    async def perform_configurate(self, config: ATComponentConfig, auth_token: str = None, *args, **kwargs) -> bool:
        kb = self.get_kb_from_config(config)
        mode_item = config.items.get("mode")
        mode = SOLVER_MODE.forwards
        if mode_item is not None:
            mode = mode_item.data
        goals_item = config.items.get("goals")
        goals = []
        if goals_item is not None:
            goals = goals_item.data
        return await self.create_solver(kb, mode, goals, auth_token)

    async def create_solver(
        self, kb: KnowledgeBase, mode: str = None, goals: List[str] = None, auth_token: str = None
    ) -> bool:
        mode = mode or SOLVER_MODE.forwards

        if mode not in [SOLVER_MODE.forwards, SOLVER_MODE.backwards, SOLVER_MODE.mixed]:
            raise ValueError(f'Invalid solver mode "{mode}"')

        auth_token = auth_token or "default"

        knowledge_base = kb
        # knowledge_base.validate()

        parsed_goals = []

        if (mode == SOLVER_MODE.backwards) or (mode == SOLVER_MODE.mixed):
            if goals is None or not len(goals):
                logger.warning(f"Expected goals to config solver with mode {mode}")

        for goal_ref in goals:
            parsed_goals.append(Goal(KBReference.parse(goal_ref)))
        solver = Solver(knowledge_base, mode=mode, goals=parsed_goals)

        solver.on_request_value = self.on_request_value(auth_token)

        auth_token_or_user_id = await self.get_user_id_or_token(auth_token, raize_on_failed=False)
        self.solvers[auth_token_or_user_id] = solver
        return True

    def on_request_value(self, auth_token: str) -> Awaitable:
        async def request_value(ref: str):
            if await self.check_external_registered("ATDialoger") and await self.check_external_registered(
                "ATBlackBoard"
            ):
                if await self.check_external_configured("ATDialoger", auth_token=auth_token):
                    await self.exec_external_method("ATDialoger", "request_value", {"ref": ref}, auth_token=auth_token)
                    v = await self.exec_external_method("ATBlackBoard", "get_item", {"ref": ref}, auth_token=auth_token)
                    value = KBValue(
                        content=v.get("value"),
                        non_factor=NonFactor(
                            belief=v.get("belief"),
                            probability=v.get("probability"),
                            accuracy=v.get("accuracy"),
                        ),
                    )
                    solver = self.get_solver(auth_token)
                    solver.wm.set_value(ref, value)

        return request_value

    async def check_configured(
        self,
        *args,
        message: Dict,
        sender: str,
        message_id: str | UUID,
        reciever: str,
        msg: IncomingMessage,
        auth_token: str = None,
        **kwargs,
    ) -> bool:
        auth_token_or_user_id = await self.get_user_id_or_token(auth_token, raize_on_failed=False)
        return self.has_solver(auth_token_or_user_id=auth_token_or_user_id)

    def has_solver(self, auth_token_or_user_id: str | int) -> bool:
        try:
            self.get_solver(auth_token_or_user_id)
            return True
        except ValueError:
            return False

    def get_solver(self, auth_token_or_user_id: str = None) -> Solver:
        auth_token_or_user_id = auth_token_or_user_id or "default"
        solver = self.solvers.get(auth_token_or_user_id)
        if solver is None:
            raise ValueError("Solver for provided token or user id is not created")
        return solver

    @authorized_method
    async def set_goals(self, goals: List[str], auth_token: str = None) -> bool:
        auth_token_or_user_id = await self.get_user_id_or_token(auth_token, raize_on_failed=False)
        solver = self.get_solver(auth_token_or_user_id)
        parsed_goals = []
        for goal_ref in goals:
            parsed_goals.append(Goal(KBReference.parse(goal_ref)))
        solver.set_goals(parsed_goals)
        return True

    @authorized_method
    async def update_wm(self, items: List[WMItemDict], clear_before: bool = True, auth_token: str = None) -> bool:
        auth_token_or_user_id = await self.get_user_id_or_token(auth_token, raize_on_failed=False)
        solver = self.get_solver(auth_token_or_user_id=auth_token_or_user_id)
        if clear_before:
            solver.wm = WorkingMemory(kb=solver.kb)
        for item in items:
            nf = NonFactor(
                belief=item.get("belief", 50) or 50,
                probability=item.get("probability", 100) or 100,
                accuracy=item.get("accuracy", 0) or 0,
            )
            v = KBValue(content=item["value"], non_factor=nf)
            solver.wm.set_value(item["ref"], v)

        return True

    @authorized_method
    async def update_wm_from_bb(self, clear_before: bool = True, auth_token: str = None) -> bool:
        items = await self.exec_external_method("ATBlackBoard", "get_all_items", {}, auth_token=auth_token)
        return await self.update_wm(items=items, clear_before=clear_before, auth_token=auth_token)

    @authorized_method
    async def set_mode(self, mode: str, goals: List[str] = None, auth_token: str = None) -> bool:
        if mode not in [SOLVER_MODE.forwards, SOLVER_MODE.backwards, SOLVER_MODE.mixed]:
            raise ValueError(f'Invalid solver mode "{mode}"')

        auth_token_or_user_id = await self.get_user_id_or_token(auth_token, raize_on_failed=False)
        solver = self.get_solver(auth_token_or_user_id=auth_token_or_user_id)
        parsed_goals = []

        if mode == SOLVER_MODE.forwards and ((goals is not None and len(goals))):
            logger.warning(f'Goals will not be applied to solver for mode "{mode}"')

        if (mode == SOLVER_MODE.backwards) or (mode == SOLVER_MODE.mixed):
            if not len(solver.goals) and (goals is None or not len(goals)):
                logger.warning(f'Expected goals to config solver with mode "{mode}"')
            for goal_ref in goals:
                parsed_goals.append(Goal(KBReference.parse(goal_ref)))

            if parsed_goals:
                solver.set_goals(parsed_goals)
        solver.mode = mode
        return True

    @authorized_method
    async def get_trace_and_wm(self, auth_token: str) -> RunResultDict:
        auth_token_or_user_id = await self.get_user_id_or_token(auth_token, raize_on_failed=False)
        solver = self.get_solver(auth_token_or_user_id=auth_token_or_user_id)
        return {"trace": solver.trace.__dict__, "wm": solver.wm.all_values_dict}

    @authorized_method
    async def reset(self, auth_token: str) -> bool:
        auth_token_or_user_id = await self.get_user_id_or_token(auth_token, raize_on_failed=False)
        solver = self.get_solver(auth_token_or_user_id=auth_token_or_user_id)
        solver.wm = WorkingMemory(kb=solver.kb)
        solver.trace = Trace()
        return True

    @authorized_method
    async def run(self, auth_token: str) -> RunResultDict:
        auth_token_or_user_id = await self.get_user_id_or_token(auth_token, raize_on_failed=False)
        solver = self.get_solver(auth_token_or_user_id=auth_token_or_user_id)
        trace = await solver.run()
        return {"trace": trace.__dict__, "wm": solver.wm.all_values_dict}
