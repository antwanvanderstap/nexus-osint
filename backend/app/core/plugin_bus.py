from app.modules import ALL_MODULES
from app.modules.base import BaseModule, EntityType, UseCase


class PluginBus:
    def __init__(self) -> None:
        self._modules: dict[str, BaseModule] = {m.metadata.name: m for m in ALL_MODULES}

    def all(self) -> list[BaseModule]:
        return list(self._modules.values())

    def get(self, name: str) -> BaseModule | None:
        return self._modules.get(name)

    def for_entity_type(self, entity_type: EntityType) -> list[BaseModule]:
        return [m for m in self._modules.values() if m.accepts(entity_type)]

    def permitted_for_purpose(self, purpose: UseCase) -> list[BaseModule]:
        return [m for m in self._modules.values() if m.is_permitted_for(purpose)]

    def available(self, entity_type: EntityType, purpose: UseCase) -> list[BaseModule]:
        return [
            m for m in self._modules.values()
            if m.accepts(entity_type) and m.is_permitted_for(purpose)
        ]


plugin_bus = PluginBus()
