from at_krl.core.kb_class import KBInstance
from at_krl.core.kb_value import KBValue
from at_krl.core.kb_reference import KBReference
from at_krl.core.knowledge_base import KnowledgeBase
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class WorkingMemory:
    env: KBInstance = None
    locals: Dict[str, KBValue] = None
    _kb: KnowledgeBase = None

    def __init__(self, kb: KnowledgeBase):
        self._kb = kb
        self.env = self.kb.world.create_instance(
            self.kb, 'env', 'Хранилище экземпляров классов')
        self.locals = {}

    @property
    def kb(self):
        return self._kb

    def set_value(self, path: str | KBReference, value: KBValue | Any):
        v = value
        if not isinstance(v, KBValue):
            v = KBValue(v)
        if isinstance(path, KBReference):
            ref = path
        else:
            ref = KBReference.parse(path)
        if self.ref_is_accessible(ref):
            self.set_value_by_ref(ref, v)
        else:
            key = path
            if isinstance(path, KBReference):
                key = path.inner_krl
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
        for prop in env.properties_instances:
            if prop.id == ref.id:
                if ref.ref is not None:
                    return self.get_instance_by_ref(ref.ref, prop)
                return prop
            
    def get_value_by_ref(self, ref: KBReference, env: KBInstance = None) -> KBValue:
        env = env or self.env
        instance = self.get_instance_by_ref(ref, env)
        if instance is not None:
            return instance.value
        return self.locals.get(ref.inner_krl)
    
    def get_value(self, path: KBReference | str, env: KBInstance = None) -> KBValue:
        env = env or self.env
        
        ref = path
        if not isinstance(path, KBReference):
            ref = KBReference.parse(path)
        return self.get_value_by_ref(ref, env)