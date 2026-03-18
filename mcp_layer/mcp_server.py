from mcp_layer.mcp_models import MCPRequest, MCPResponse
from mcp_layer.mcp_registry import MCPRegistry


class MCPServer:
    def __init__(self):
        self.registry = MCPRegistry()

    def handle_request(self, request_data: dict) -> dict:
        try:
            request = MCPRequest(**request_data)
        except Exception as e:
            return MCPResponse(
                request_id=request_data.get("request_id", "unknown"),
                status="error",
                error=f"Invalid MCP request: {str(e)}",
            ).model_dump()

        if request.kind == "resource":
            handler = self.registry.get_resource(request.name)
        elif request.kind == "tool":
            handler = self.registry.get_tool(request.name)
        else:
            return MCPResponse(
                request_id=request.request_id,
                status="error",
                error=f"Unknown MCP kind: {request.kind}",
            ).model_dump()

        if not handler:
            return MCPResponse(
                request_id=request.request_id,
                status="error",
                error=f"MCP target not found: {request.name}",
            ).model_dump()

        try:
            data = handler(request.params)
            return MCPResponse(
                request_id=request.request_id,
                status="success",
                data=data or {},
            ).model_dump()
        except Exception as e:
            return MCPResponse(
                request_id=request.request_id,
                status="error",
                error=str(e),
            ).model_dump()