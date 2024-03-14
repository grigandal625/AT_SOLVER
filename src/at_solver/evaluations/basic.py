from at_krl.core.kb_value import Evaluatable
from at_krl.core.kb_value import KBValue
from at_krl.core.kb_reference import KBReference
from at_krl.core.kb_operation import KBOperation
from at_krl.core.temporal.kb_allen_operation import KBAllenOperation
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from at_solver.core.solver import Solver

class BasicEvaluator:
    solver: 'Solver' = None

    def __init__(self, solver: 'Solver'):
        self.solver = solver

    def eval(self, v: Evaluatable, ref_stack: List[KBReference]=None) -> KBValue:
        ref_stack = ref_stack or []
        if v is None:
            return KBValue(None)
        elif isinstance(v, KBValue):
            return v
        elif isinstance(v, KBReference):
            if self.solver.wm.ref_is_accessible(v):
                instance = self.solver.wm.get_instance_by_ref(v)
                if [r.inner_krl for r in ref_stack].count(v.inner_krl) > 1:
                    raise ValueError(
                        f'''Reference {v.inner_krl} has recursive link in wm to evaluate.
                        
                        Reference value is getting form:
                        {instance.krl}
                        '''
                    ) 
                ref_stack.append(v)
                return self.eval(instance.value, ref_stack=ref_stack)
            else:
                local = self.solver.wm.locals.get(v.inner_krl)
                return self.eval(local)
        elif isinstance(v, KBAllenOperation): # Пытаемся достать то, что посчитал темпоральный решатель
            res = self.solver.wm.locals.get(f'signifier.{v.xml_owner_path}')
        elif isinstance(v, KBOperation):
            if v.is_binary:
                return EVALUATORS[v.tag](
                    self.eval(v.left), 
                    self.eval(v.right)
                )
            return EVALUATORS[v.tag](self.eval(v.left))

def eval_eq(left: KBValue, right: KBValue):
    content = left.content == right.content
    non_factor = None #TODO: calculate non_factor
    return KBValue(content, non_factor=non_factor)

EVALUATORS = {
    "eq": eval_eq,
    "gt": {
        "values": [">", "gt"],
        "is_binary": True,
        "convert_non_factor": True,
        "meta": "eq",
    },
    "ge": {
        "values": [">=", "ge"],
        "is_binary": True,
        "convert_non_factor": True,
        "meta": "eq",
    },
    "lt": {
        "values": ["<", "lt"],
        "is_binary": True,
        "convert_non_factor": True,
        "meta": "eq",
    },
    "le": {
        "values": ["<=", "le"],
        "is_binary": True,
        "convert_non_factor": True,
        "meta": "eq",
    },
    "ne": {
        "values": ["<>", "!=", "ne"],
        "is_binary": True,
        "convert_non_factor": True,
        "meta": "eq",
    },
    "and": {
        "values": ["&", "&&", "and"],
        "is_binary": True,
        "meta": "log",
    },
    "or": {
        "values": ["|", "||", "or"],
        "is_binary": True,
        "meta": "log",
    },
    "not": {
        "values": ["~", "!", "not"],
        "is_binary": False,
        "meta": "log",
    },
    "xor": {
        "values": ["xor"],
        "is_binary": True,
        "meta": "log",
    },
    "neg": {
        "values": ["-", "neg"],
        "is_binary": False,
        "meta": "super_math",
    },
    "add": {
        "values": ["+", "add"],
        "is_binary": True,
        "meta": "math",
    },
    "sub": {
        "values": ["-", "sub"],
        "is_binary": True,
        "meta": "math",
    },
    "mul": {
        "values": ["*", "mul"],
        "is_binary": True,
        "meta": "math",
    },
    "div": {
        "values": ["/", "div"],
        "is_binary": True,
        "meta": "math",
    },
    "mod": {
        "values": ["%", "mod"],
        "is_binary": True,
        "meta": "super_math",
    },
    "pow": {
        "values": ["^", "**", "pow"],
        "is_binary": True,
        "meta": "super_math",
    },
}