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
            if isinstance(res, KBValue):
                return res
            return KBValue(content=res)
            
        elif isinstance(v, KBOperation):
            if v.is_binary:
                return EVALUATORS[v.tag](
                    self.eval(v.left), 
                    self.eval(v.right)
                )
            return EVALUATORS[v.tag](self.eval(v.left))


def unify_number(n):
    f = float(n)
    i = int(f)
    return i if i == f else f


def eval_eq(left: KBValue, right: KBValue) -> KBValue:
    content = left.content == right.content
    non_factor = None #TODO: calculate non_factor
    return KBValue(content, non_factor=non_factor)


def eval_gt(left: KBValue, right: KBValue) -> KBValue:
    content = left.content > right.content
    non_factor = None #TODO: calculate non_factor
    return KBValue(content, non_factor=non_factor)


def eval_ge(left: KBValue, right: KBValue) -> KBValue:
    content = left.content >= right.content
    non_factor = None #TODO: calculate non_factor
    return KBValue(content, non_factor=non_factor)


def eval_lt(left: KBValue, right: KBValue) -> KBValue:
    content = left.content < right.content
    non_factor = None #TODO: calculate non_factor
    return KBValue(content, non_factor=non_factor)


def eval_le(left: KBValue, right: KBValue) -> KBValue:
    content = left.content <= right.content
    non_factor = None #TODO: calculate non_factor
    return KBValue(content, non_factor=non_factor)


def eval_ne(left: KBValue, right: KBValue) -> KBValue:
    content = left.content != right.content
    non_factor = None #TODO: calculate non_factor
    return KBValue(content, non_factor=non_factor)


def eval_and(left: KBValue, right: KBValue) -> KBValue:
    content = left.content and right.content
    non_factor = None #TODO: calculate non_factor
    return KBValue(content, non_factor=non_factor)


def eval_or(left: KBValue, right: KBValue) -> KBValue:
    content = left.content or right.content
    non_factor = None #TODO: calculate non_factor
    return KBValue(content, non_factor=non_factor)


def eval_not(v: KBValue, *args, **kwargs) -> KBValue:
    content = not v.content
    non_factor = None #TODO: calculate non_factor
    return KBValue(content, non_factor=non_factor)


def eval_xor(left: KBValue, right: KBValue) -> KBValue:
    content = (left.content and not right.content) or (right and not left.content)
    non_factor = None # TODO: calculate non_factor
    return KBValue(content, non_factor=non_factor)


def eval_neg(v: KBValue, *args, **kwargs) -> KBValue:
    content = -1 * unify_number(v.content)
    non_factor = None # TODO: calculate non_factor
    return KBValue(content, non_factor=non_factor)


def eval_add(left: KBValue, right: KBValue) -> KBValue:
    content = left.content + right.content
    non_factor = None # TODO: calculate non_factor
    return KBValue(content, non_factor=non_factor)


def eval_sub(left: KBValue, right: KBValue) -> KBValue:
    content = left.content - right.content
    non_factor = None # TODO: calculate non_factor
    return KBValue(content, non_factor=non_factor)


def eval_mul(left: KBValue, right: KBValue) -> KBValue:
    content = unify_number(left.content) * unify_number(right.content)
    non_factor = None # TODO: calculate non_factor
    return KBValue(content, non_factor=non_factor)


def eval_div(left: KBValue, right: KBValue) -> KBValue:
    content = unify_number(left.content) / unify_number(right.content)
    non_factor = None # TODO: calculate non_factor
    return KBValue(content, non_factor=non_factor)


def eval_mod(left: KBValue, right: KBValue) -> KBValue:
    content = unify_number(left.content) % unify_number(right.content)
    non_factor = None # TODO: calculate non_factor
    return KBValue(content, non_factor=non_factor)


def eval_pow(left: KBValue, right: KBValue) -> KBValue:
    content = unify_number(left.content) ** unify_number(right.content)
    non_factor = None # TODO: calculate non_factor
    return KBValue(content, non_factor=non_factor)


EVALUATORS = {
    "eq": eval_eq,
    "gt": eval_gt,
    "ge": eval_ge,
    "lt": eval_lt,
    "le": eval_le,
    "ne": eval_ne,
    "and": eval_and,
    "or": eval_or,
    "not": eval_not,
    "xor": eval_xor,
    "neg": eval_neg,
    "add": eval_add,
    "sub": eval_sub,
    "mul": eval_mul,
    "div": eval_div,
    "mod": eval_mod,
    "pow": eval_pow,
}