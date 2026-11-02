from typing import Protocol


class MetaGateway(Protocol):
    """Puerto futuro; ningún adaptador de red se distribuye en el demo."""

    def list_campaigns(self, tenant_id: str) -> list[dict]: ...
    def publish(self, tenant_id: str, plan: dict) -> dict: ...


class DisabledMetaGateway:
    def list_campaigns(self, tenant_id: str):
        raise NotImplementedError("Meta desconectado: integrar OAuth y lectura autorizada")

    def publish(self, tenant_id: str, plan: dict):
        raise PermissionError("Publicación real deshabilitada en este MVP")
