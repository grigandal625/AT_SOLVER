from dataclasses import dataclass
from typing import List
from typing import TYPE_CHECKING

from at_krl.core.kb_operation import KBOperation
from at_krl.core.kb_reference import KBReference
from at_krl.core.kb_value import Evaluatable
from at_krl.core.kb_value import KBValue
from at_krl.core.non_factor import NonFactor
from at_krl.core.temporal.allen_evaluatable import AllenEvaluatable

if TYPE_CHECKING:
    from at_solver.core.wm import WorkingMemory


@dataclass
class BasicEvaluator:
    wm: "WorkingMemory"

    def eval(self, v: Evaluatable, ref_stack: List[KBReference] = None) -> KBValue:
        ref_stack = ref_stack or []
        if v is None:
            return KBValue(content=None)
        elif isinstance(v, KBValue):
            return v
        elif isinstance(v, KBReference):
            if self.wm.ref_is_accessible(v):
                instance = self.wm.get_instance_by_ref(v)
                if [r.to_simple().krl for r in ref_stack].count(v.to_simple().krl) > 1:
                    raise ValueError(
                        f"""Reference {v.to_simple().krl} has recursive link in wm to evaluate.

                        Reference value is getting form:
                        {instance.krl}
                        """
                    )
                ref_stack.append(v)
                return self.eval(instance.value, ref_stack=ref_stack)
            else:
                local = self.wm.locals.get(v.to_simple().krl)
                return self.eval(local)
        elif isinstance(v, AllenEvaluatable):  # Пытаемся достать то, что посчитал темпоральный решатель
            res = self.wm.locals.get(f"signifier.{v.xml_owner_path}")
            if isinstance(res, KBValue):
                return res
            return KBValue(content=res)

        elif isinstance(v, KBOperation):
            left_v = self.eval(v.left)
            if left_v.content is None:
                return KBValue(content=None)
            if v.is_binary:
                right_v = self.eval(v.right)
                if right_v.content is None:
                    return KBValue(content=None)
                return EVALUATORS[v.operation_name](left_v, right_v)
            return EVALUATORS[v.operation_name](left_v)


def unify_number(n):
    f = float(n)
    i = int(f)
    return i if i == f else f


def eval_eq(left: KBValue, right: KBValue) -> KBValue:
    content = left.content == right.content
    non_factor = NonFactor()  # TODO: calculate non_factor
    return KBValue(content=content, non_factor=non_factor)


def eval_gt(left: KBValue, right: KBValue) -> KBValue:
    content = left.content > right.content
    non_factor = NonFactor()  # TODO: calculate non_factor
    return KBValue(content=content, non_factor=non_factor)


def eval_ge(left: KBValue, right: KBValue) -> KBValue:
    content = left.content >= right.content
    non_factor = NonFactor()  # TODO: calculate non_factor
    return KBValue(content=content, non_factor=non_factor)


def eval_lt(left: KBValue, right: KBValue) -> KBValue:
    content = left.content < right.content
    non_factor = NonFactor()  # TODO: calculate non_factor
    return KBValue(content=content, non_factor=non_factor)


def eval_le(left: KBValue, right: KBValue) -> KBValue:
    content = left.content <= right.content
    non_factor = NonFactor()  # TODO: calculate non_factor
    return KBValue(content=content, non_factor=non_factor)


def eval_ne(left: KBValue, right: KBValue) -> KBValue:
    content = left.content != right.content
    non_factor = NonFactor()  # TODO: calculate non_factor
    return KBValue(content=content, non_factor=non_factor)


def eval_and(left: KBValue, right: KBValue) -> KBValue:
    content = left.content and right.content
    non_factor = NonFactor()  # TODO: calculate non_factor
    return KBValue(content=content, non_factor=non_factor)


def eval_or(left: KBValue, right: KBValue) -> KBValue:
    content = left.content or right.content
    non_factor = NonFactor()  # TODO: calculate non_factor
    return KBValue(content=content, non_factor=non_factor)


def eval_not(v: KBValue, *args, **kwargs) -> KBValue:
    content = not v.content
    non_factor = NonFactor()  # TODO: calculate non_factor
    return KBValue(content=content, non_factor=non_factor)


def eval_xor(left: KBValue, right: KBValue) -> KBValue:
    content = (left.content and not right.content) or (right and not left.content)
    non_factor = NonFactor()  # TODO: calculate non_factor
    return KBValue(content=content, non_factor=non_factor)


def eval_neg(v: KBValue, *args, **kwargs) -> KBValue:
    content = -1 * unify_number(v.content)
    non_factor = NonFactor()  # TODO: calculate non_factor
    return KBValue(content=content, non_factor=non_factor)


def eval_add(left: KBValue, right: KBValue) -> KBValue:
    content = left.content + right.content
    non_factor = NonFactor()  # TODO: calculate non_factor
    return KBValue(content=content, non_factor=non_factor)


def eval_sub(left: KBValue, right: KBValue) -> KBValue:
    content = left.content - right.content
    non_factor = NonFactor()  # TODO: calculate non_factor
    return KBValue(content=content, non_factor=non_factor)


def eval_mul(left: KBValue, right: KBValue) -> KBValue:
    content = unify_number(left.content) * unify_number(right.content)
    non_factor = NonFactor()  # TODO: calculate non_factor
    return KBValue(content=content, non_factor=non_factor)


def eval_div(left: KBValue, right: KBValue) -> KBValue:
    content = unify_number(left.content) / unify_number(right.content)
    non_factor = NonFactor()  # TODO: calculate non_factor
    return KBValue(content=content, non_factor=non_factor)


def eval_mod(left: KBValue, right: KBValue) -> KBValue:
    content = unify_number(left.content) % unify_number(right.content)
    non_factor = NonFactor()  # TODO: calculate non_factor
    return KBValue(content=content, non_factor=non_factor)


def eval_pow(left: KBValue, right: KBValue) -> KBValue:
    content = unify_number(left.content) ** unify_number(right.content)
    non_factor = NonFactor()  # TODO: calculate non_factor
    return KBValue(content=content, non_factor=non_factor)


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
