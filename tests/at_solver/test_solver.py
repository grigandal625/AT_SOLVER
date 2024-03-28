from at_solver.core.solver import Solver, SOLVER_MODE
from at_krl.core.knowledge_base import KnowledgeBase
from at_solver.core.trace import ForwardStep
from at_krl.core.kb_reference import KBReference
from at_solver.core.goals import Goal
from typing import List

def build_solver(goals: List[Goal] = []):
    kb_dict = {
        "types": [{"id": "numbers", "meta": "number", "desc": "numbers", "from": -10000.0, "to": 10000.0}], 
        "intervals": [], 
        "events": [], 
        "classes": [
            {
                "tag": "class", 
                "id": "КЛАСС_obj1", 
                "desc": "obj1", "group": "ГРУППА1", 
                "properties": [
                    {"id": "attr1", "type": "numbers", "desc": "attr1", "source": "asked", "tag": "property"}, 
                    {"id": "attr2", "type": "numbers", "desc": "attr2", "source": "asked", "tag": "property"}, 
                    {"id": "attr3", "type": "numbers", "desc": "attr3", "source": "asked", "tag": "property"}
                ], 
                "rules": []
            }, 
            {
                "tag": "class", 
                "id": "world", 
                "desc": "Класс верхнего уровня, включающий в себя экземпляры других классов и общие правила", 
                "group": "ГРУППА1", 
                "properties": [
                    {"id": "obj1", "type": "КЛАСС_obj1", "desc": "obj1", "source": "asked", "tag": "property", "value": {"content": 140300712697984, "tag": "value"}}
                ], 
                "rules": [
                    {
                        "condition": {"sign": ">", "left": {"id": "obj1", "ref": {"id": "attr1", "tag": "ref", "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}}, "tag": "ref", "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}}, "right": {"content": 5, "tag": "value"}, "tag": "gt", "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}}, 
                        "instructions": [{"ref": {"id": "obj1", "ref": {"id": "attr2", "tag": "ref", "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}}, "tag": "ref"}, "value": {"sign": "+", "left": {"id": "obj1", "ref": {"id": "attr1", "tag": "ref", "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}}, "tag": "ref", "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}}, "right": {"content": 8, "tag": "value"}, "tag": "add"}, "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}, "tag": "assign"}, {"ref": {"id": "obj1", "ref": {"id": "attr3", "tag": "ref", "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}}, "tag": "ref"}, "value": {"sign": "-", "left": {"id": "obj1", "ref": {"id": "attr1", "tag": "ref", "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}}, "tag": "ref", "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}}, "right": {"content": 9, "tag": "value"}, "tag": "sub"}, "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}, "tag": "assign"}], 
                        "else_instructions": [{"ref": {"id": "obj1", "ref": {"id": "attr1", "tag": "ref", "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}}, "tag": "ref"}, "value": {"sign": "+", "left": {"id": "obj1", "ref": {"id": "attr1", "tag": "ref", "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}}, "tag": "ref", "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}}, "right": {"content": 1, "tag": "value"}, "tag": "add"}, "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}, "tag": "assign"}],
                        "id": "rule1", 
                        "meta": "simple", 
                        "desc": "rule1", 
                        "tag": "rule", 
                    },
                    {
                        "condition": {"sign": ">", "left": {"id": "obj1", "ref": {"id": "attr2", "tag": "ref", "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}}, "tag": "ref", "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}}, "right": {"content": 5, "tag": "value"}, "tag": "gt", "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}}, 
                        "instructions": [{"ref": {"id": "obj1", "ref": {"id": "attr3", "tag": "ref", "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}}, "tag": "ref"}, "value": {"sign": "+", "left": {"id": "obj1", "ref": {"id": "attr2", "tag": "ref", "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}}, "tag": "ref", "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}}, "right": {"content": 15, "tag": "value"}, "tag": "add"}, "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}, "tag": "assign"}], 
                        "else_instructions": [{"ref": {"id": "obj1", "ref": {"id": "attr2", "tag": "ref", "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}}, "tag": "ref"}, "value": {"sign": "+", "left": {"id": "obj1", "ref": {"id": "attr2", "tag": "ref", "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}}, "tag": "ref", "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}}, "right": {"content": 1, "tag": "value"}, "tag": "add"}, "non_factor": {"belief": 50, "probability": 100, "accuracy": 0, "tag": "with"}, "tag": "assign"}],
                        "id": "rule2", 
                        "meta": "simple", 
                        "desc": "rule2", 
                        "tag": "rule", 
                    },
                ]
            }
        ]
    }
    knowledge_base = KnowledgeBase.from_dict(kb_dict)
    solver = Solver(knowledge_base, SOLVER_MODE.forwards, goals=goals)
    return solver

def test_forward():
    solver = build_solver()
    a1 = "obj1.attr1"
    a2 = "obj1.attr2"
    a3 = "obj1.attr3"
    solver.wm.set_value(a1, 20)
    solver.wm.set_value(a2, 0)
    solver.wm.set_value(a3, 0)

    solver.run_forward()
    for i, step in enumerate(solver.trace.steps):
        if isinstance(step, ForwardStep):
            print('\nSTEP', i)
            print(step.selected_rule.id, '\n')
            print('Rule condition value', step.rule_condition_value.__dict__(), '\n')
            print('firing instrictions:')
            if step.rule_condition_value.content:
                for instr in step.selected_rule.instructions:
                    print('\t', instr.krl)
            else:
                for instr in step.selected_rule.else_instructions:
                    print('\t', instr.krl)
            print('Result')
            print(a1, step.final_wm_state.get_value(a1).__dict__())
            print(a2, step.final_wm_state.get_value(a2).__dict__())
            print(a3, step.final_wm_state.get_value(a3).__dict__())

    print('\nFINAL STATE')
    print(a1, solver.wm.get_value(a1).__dict__())
    print(a2, solver.wm.get_value(a2).__dict__())
    print(a3, solver.wm.get_value(a3).__dict__())

def test_backward():
    
    a1 = "obj1.attr1"
    a2 = "obj1.attr2"
    a3 = "obj1.attr3"
    

    r1 = KBReference.parse(a1)
    g = Goal(r1)
    
    solver = build_solver(goals=[g])
    solver.wm.set_value(a1, 20)

    solver.run_backward()
    print(solver.trace.steps)