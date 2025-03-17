from typing import List

import pytest
from at_krl.core.kb_reference import KBReference
from at_krl.core.knowledge_base import KnowledgeBase

from at_solver.core.goals import Goal
from at_solver.core.solver import Solver
from at_solver.core.solver import SOLVER_MODE
from at_solver.core.trace import ForwardStep


@pytest.fixture
def big_kb():
    return KnowledgeBase.from_krl(open("./tests/fixtures/TrafficAccidentsKB.kbs").read())


def build_solver(goals: List[Goal] = []):
    kb_dict = {
        "tag": "knowledge-base",
        "problem_info": None,
        "types": [{"tag": "type", "id": "TEST", "desc": None, "meta": "number", "from": 0, "to": 1000}],
        "classes": [
            {
                "tag": "class",
                "id": "КЛАСС_object1",
                "group": "ГРУППА1",
                "desc": "object1",
                "properties": [
                    {
                        "tag": "property",
                        "id": "attr1",
                        "type": {"tag": "ref", "id": "TEST", "ref": None, "meta": "type_or_class"},
                        "desc": None,
                        "value": None,
                        "source": "asked",
                        "question": None,
                        "query": None,
                    },
                    {
                        "tag": "property",
                        "id": "attr2",
                        "type": {"tag": "ref", "id": "TEST", "ref": None, "meta": "type_or_class"},
                        "desc": None,
                        "value": None,
                        "source": "asked",
                        "question": None,
                        "query": None,
                    },
                    {
                        "tag": "property",
                        "id": "attr3",
                        "type": {"tag": "ref", "id": "TEST", "ref": None, "meta": "type_or_class"},
                        "desc": None,
                        "value": None,
                        "source": "asked",
                        "question": None,
                        "query": None,
                    },
                ],
                "rules": [],
            },
            {
                "tag": "class",
                "id": "world",
                "group": None,
                "desc": "Класс верхнего уровня, включающий в себя экземпляры других классов и общие правила",
                "properties": [
                    {
                        "tag": "property",
                        "id": "object1",
                        "type": {"tag": "ref", "id": "КЛАСС_object1", "ref": None, "meta": "type_or_class"},
                        "desc": "object1",
                        "value": None,
                        "source": "asked",
                        "question": None,
                        "query": None,
                    }
                ],
                "rules": [
                    {
                        "tag": "rule",
                        "id": "TEST_RULE1",
                        "condition": {
                            "tag": "and",
                            "left": {
                                "tag": "ge",
                                "left": {
                                    "tag": "ref",
                                    "id": "object1",
                                    "ref": {"tag": "ref", "id": "attr1", "ref": None},
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                                "right": {
                                    "tag": "value",
                                    "content": 0,
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                                "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                            },
                            "right": {
                                "tag": "lt",
                                "left": {
                                    "tag": "ref",
                                    "id": "object1",
                                    "ref": {"tag": "ref", "id": "attr2", "ref": None},
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                                "right": {
                                    "tag": "ref",
                                    "id": "object1",
                                    "ref": {"tag": "ref", "id": "attr1", "ref": None},
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                                "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                            },
                            "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                        },
                        "instructions": [
                            {
                                "tag": "assign",
                                "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                "ref": {
                                    "tag": "ref",
                                    "id": "object1",
                                    "ref": {
                                        "tag": "ref",
                                        "id": "attr3",
                                        "ref": None,
                                        "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                    },
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                                "value": {
                                    "tag": "add",
                                    "left": {
                                        "tag": "ref",
                                        "id": "object1",
                                        "ref": {"tag": "ref", "id": "attr2", "ref": None},
                                        "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                    },
                                    "right": {
                                        "tag": "ref",
                                        "id": "object1",
                                        "ref": {"tag": "ref", "id": "attr1", "ref": None},
                                        "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                    },
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                            }
                        ],
                        "else_instructions": [],
                        "meta": "simple",
                        "period": None,
                        "desc": None,
                    },
                    {
                        "tag": "rule",
                        "id": "TEST_RULE2",
                        "condition": {
                            "tag": "ge",
                            "left": {
                                "tag": "ref",
                                "id": "object1",
                                "ref": {"tag": "ref", "id": "attr3", "ref": None},
                                "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                            },
                            "right": {
                                "tag": "value",
                                "content": 5,
                                "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                            },
                            "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                        },
                        "instructions": [
                            {
                                "tag": "assign",
                                "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                "ref": {
                                    "tag": "ref",
                                    "id": "object1",
                                    "ref": {
                                        "tag": "ref",
                                        "id": "attr1",
                                        "ref": None,
                                        "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                    },
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                                "value": {
                                    "tag": "value",
                                    "content": 0,
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                            },
                            {
                                "tag": "assign",
                                "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                "ref": {
                                    "tag": "ref",
                                    "id": "object1",
                                    "ref": {
                                        "tag": "ref",
                                        "id": "attr2",
                                        "ref": None,
                                        "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                    },
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                                "value": {
                                    "tag": "value",
                                    "content": 0,
                                    "non_factor": {"tag": "with", "belief": 50, "probability": 100, "accuracy": 0},
                                },
                            },
                        ],
                        "else_instructions": [],
                        "meta": "simple",
                        "period": None,
                        "desc": None,
                    },
                ],
            },
        ],
    }
    knowledge_base = KnowledgeBase.from_json(kb_dict)
    solver = Solver(knowledge_base, SOLVER_MODE.forwards, goals=goals)
    return solver


def test_forward():
    solver = build_solver()
    a1 = "object1.attr1"
    a2 = "object1.attr2"
    a3 = "object1.attr3"
    solver.wm.set_value(a1, 4)
    solver.wm.set_value(a2, 2)
    # solver.wm.set_value(a3, 0)

    solver.run_forward()
    for i, step in enumerate(solver.trace.steps):
        if isinstance(step, ForwardStep):
            print("\nSTEP", i)
            print(step.selected_rule.id, "\n")
            print("Rule condition value", step.rule_condition_value.to_representation(), "\n")
            print("firing instrictions:")
            if step.rule_condition_value.content:
                for instr in step.selected_rule.instructions:
                    print("\t", instr.krl)
            else:
                for instr in step.selected_rule.else_instructions:
                    print("\t", instr.krl)
            print("Result")
            print(a1, step.final_wm_state.get_value(a1).to_representation())
            print(a2, step.final_wm_state.get_value(a2).to_representation())
            print(a3, step.final_wm_state.get_value(a3).to_representation())

    print("\nFINAL STATE")
    print(a1, solver.wm.get_value(a1).to_representation())
    print(a2, solver.wm.get_value(a2).to_representation())
    print(a3, solver.wm.get_value(a3).to_representation())


def test_backward():
    a1 = "object1.attr1"
    # a2 = "object1.attr2"
    # a3 = "object1.attr3"

    r1 = KBReference.parse(a1)
    g = Goal(r1)

    solver = build_solver(goals=[g])
    solver.wm.set_value(a1, 20)

    solver.run_backward()
    print(solver.trace.steps)


def test_big_kb_solver(big_kb):
    solver = Solver(big_kb, mode=SOLVER_MODE.forwards, goals=[])
    assert len(solver.kb.rules) == 60
    solver.run_forward()
