from at_krl.core.kb_class import KBInstance, KBClass, KBProperty, TypeOrClassReference
from at_krl.core.kb_value import KBValue
from at_krl.core.kb_type import KBType
from at_krl.core.kb_entity import KBEntity
from at_krl.core.kb_reference import KBReference
from at_krl.core.knowledge_base import KnowledgeBase
from typing import Dict, Any, Union, TypedDict
from at_solver.evaluations.basic import BasicEvaluator
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class NonFactorDict(TypedDict):
    belief: Union[int, float]
    probability: Union[int, float]
    accuracy: Union[int, float]


class KBValueDict(TypedDict):
    content: Union[str, int, float, bool, None]
    non_factor: Union[NonFactorDict, None]


@dataclass(kw_only=True)
class WorkingMemory:
    env: KBInstance = field(init=False)
    locals: Dict[str, KBValue] = field(init=False, default_factory=dict)
    kb: KnowledgeBase

    def create_instance(self, id: str, kb_class: KBClass, desc: str = None, evaluator: BasicEvaluator | None = None, as_property: bool = False) -> KBInstance:
        evaluator = evaluator or BasicEvaluator(self)
        type = TypeOrClassReference(id=kb_class.id)
        type.target = kb_class
        if as_property:
            instance = KBProperty(id=id, type=type, desc=desc)
        else:
            instance = KBInstance(id=id, type=type, desc=desc)
        if kb_class.properties:
            for prop_def in kb_class.properties:
                if not prop_def.type.fullfiled:
                    raise ValueError(f"Property {prop.id} of instance {id}: {kb_class.id} has not fullfiled type reference {prop_def.type.id}")
                if isinstance(prop_def.type.target, KBClass):
                    prop = self.create_instance(id=prop_def.id, kb_class=prop_def.type.target, evaluator=evaluator, as_property=True)
                else:
                    prop = KBProperty(id=prop_def.id, type=prop_def.type)
                    if prop_def.value:
                        prop.value = evaluator.eval(prop_def.value)
                prop.definition = prop_def
                prop.owner = instance
                instance.properties.append(prop)
        return instance


    def __post_init__(self):
        self.env = self.create_instance('env', self.kb.world)

    def set_value(self, path: str | KBReference, value: KBValue | Any):
        v = value
        if not isinstance(v, KBValue):
            v = KBValue(content=v)
        if isinstance(path, KBReference):
            ref = path
        else:
            ref = KBReference.from_simple(KBReference.parse(path))
        if self.ref_is_accessible(ref):
            self.set_value_by_ref(ref, v)
        else:
            key = path
            if isinstance(path, KBReference):
                key = path.to_simple().krl
            self.locals[key] = v

    def ref_is_accessible(self, ref: KBReference):
        return self.get_instance_by_ref(ref) is not None

    def set_value_by_ref(self, ref: KBReference, value: KBValue):
        inst = self.get_instance_by_ref(ref)
        return self.assign_value(inst, value)

    def assign_value(self, inst: KBInstance, value: KBValue) -> KBInstance:
        inst.value = value
        return inst

    def get_instance_by_ref(self, ref: KBReference, env: KBInstance = None) -> KBInstance:
        env = env or self.env
        if ref.fullfiled:
            if ref.ref is None:
                return ref.target
            return self.get_instance_by_ref(ref.ref, ref.target)
        for prop in env.properties:
            if prop.id == ref.id:
                ref.target = prop
                if ref.ref is not None:
                    return self.get_instance_by_ref(ref.ref, prop)
                return prop
            
    def get_value_by_ref(self, ref: KBReference, env: KBInstance = None) -> KBValue:
        env = env or self.env
        instance = self.get_instance_by_ref(ref, env)
        if instance is not None:
            return instance.value
        return self.locals.get(ref.to_simple().krl)
    
    def get_value(self, path: KBReference | str, env: KBInstance = None) -> KBValue:
        env = env or self.env
        
        ref = path
        if not isinstance(path, KBReference):
            ref = KBReference.parse(path)
        return self.get_value_by_ref(ref, env)
    
    @property
    def all_values_dict(self) -> Dict[str, KBValueDict]:
        res = {}
        if self.env.properties:
            for inst in self.env.properties:
                res.update(self._get_instance_values_dict(inst))
        return res
    
    def _get_instance_values_dict(self, instance: KBInstance, owner_id: str = None) -> Dict[str, KBValueDict]:
        if isinstance(instance.type.target, KBType):
            key = instance.id
            if owner_id is not None:
                key = owner_id + '.' + key
            if isinstance(instance.value, KBValue):
                return {key: instance.value.to_representation()}
            else:
                return {}
        else:
            res = {}
            if instance.properties:
                for prop in instance.properties:
                    prop_res = self._get_instance_values_dict(prop, owner_id=instance.id)
                    res.update(prop_res)
            return res