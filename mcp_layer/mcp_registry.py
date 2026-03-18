from typing import Callable, Dict


class MCPRegistry:
    def __init__(self):
        self.resources: Dict[str, Callable] = {}
        self.tools: Dict[str, Callable] = {}

    def register_resource(self, name: str, handler: Callable) -> None:
        self.resources[name] = handler

    def register_tool(self, name: str, handler: Callable) -> None:
        self.tools[name] = handler

    def get_resource(self, name: str):
        return self.resources.get(name)

    def get_tool(self, name: str):
        return self.tools.get(name)

    def list_resources(self):
        return list(self.resources.keys())

    def list_tools(self):
        return list(self.tools.keys())