from typing import Callable, Dict


class AgentMethodRegistry:
    def __init__(self):
        self._methods: Dict[str, Callable] = {}

    def register(self, method_name: str, handler: Callable) -> None:
        self._methods[method_name] = handler

    def get(self, method_name: str):
        return self._methods.get(method_name)

    def list_methods(self):
        return list(self._methods.keys())