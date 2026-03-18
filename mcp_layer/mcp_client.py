from mcp_layer.mcp_server import MCPServer


class MCPClient:
    def __init__(self, server: MCPServer):
        self.server = server

    def get_resource(self, request_id: str, name: str, params: dict | None = None) -> dict:
        return self.server.handle_request({
            "request_id": request_id,
            "kind": "resource",
            "name": name,
            "params": params or {},
        })

    def call_tool(self, request_id: str, name: str, params: dict | None = None) -> dict:
        return self.server.handle_request({
            "request_id": request_id,
            "kind": "tool",
            "name": name,
            "params": params or {},
        })