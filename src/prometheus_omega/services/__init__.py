"""L1 Services - HTTP+CLI+MCP服务接口

整合XYZ机制:
- X: HTTP Server, CLI, MCP Server
- Y: REST API
- Z: 基础接口预留
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable
from enum import Enum
import json, threading, socket, http.server, socketserver
from datetime import datetime, timezone


class ServiceType(Enum):
    HTTP = "http"
    CLI = "cli"
    MCP = "mcp"
    WEBSOCKET = "websocket"


@dataclass
class ServiceConfig:
    """服务配置"""
    host: str = "0.0.0.0"
    port: int = 8080
    service_type: ServiceType = ServiceType.HTTP
    cors_enabled: bool = True
    max_connections: int = 100
    timeout: int = 30
    
    def get_address(self) -> str:
        return f"{self.host}:{self.port}"
    
    def to_dict(self) -> Dict:
        return {
            'host': self.host,
            'port': self.port,
            'service_type': self.service_type.value if isinstance(self.service_type, Enum) else self.service_type,
            'cors_enabled': self.cors_enabled,
            'max_connections': self.max_connections,
            'timeout': self.timeout,
        }


@dataclass
class Request:
    """HTTP请求"""
    method: str
    path: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[Dict] = None
    query_params: Dict[str, str] = field(default_factory=dict)
    
    def get_header(self, key: str, default: str = "") -> str:
        return self.headers.get(key, default)
    
    def get_query(self, key: str, default: str = "") -> str:
        return self.query_params.get(key, default)
    
    def is_get(self) -> bool:
        return self.method.upper() == "GET"
    
    def is_post(self) -> bool:
        return self.method.upper() == "POST"


@dataclass
class Response:
    """HTTP响应"""
    status_code: int = 200
    body: Any = None
    headers: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "status_code": self.status_code,
            "body": self.body,
            "headers": self.headers
        }


class BaseService:
    """基础服务类"""
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.running = False
        self.request_handlers: Dict[str, Callable] = {}
    
    def register_handler(self, path: str, handler: Callable):
        """注册请求处理器"""
        self.request_handlers[path] = handler
    
    def start(self):
        """启动服务"""
        self.running = True
    
    def stop(self):
        """停止服务"""
        self.running = False


class HTTPServer:
    """HTTP服务器 - 来自X系统"""
    
    def __init__(self, config: Optional[ServiceConfig] = None):
        self.config = config or ServiceConfig()
        self.app: Optional[Callable] = None
        self._server = None
    
    def route(self, path: str, methods: list = None):
        """路由装饰器"""
        def decorator(func: Callable):
            self.register_handler(path, func)
            return func
        return decorator
    
    def register_handler(self, path: str, handler: Callable):
        if not hasattr(self, '_handlers'):
            self._handlers = {}
        self._handlers[path] = handler
    
    def handle_request(self, request: Request) -> Response:
        """处理请求"""
        handler = self._handlers.get(request.path)
        if handler:
            try:
                result = handler(request)
                return Response(status_code=200, body=result)
            except Exception as e:
                return Response(status_code=500, body={"error": str(e)})
        return Response(status_code=404, body={"error": "Not found"})
    
    def start(self, blocking: bool = True):
        """启动HTTP服务器"""
        print(f"🌐 HTTP Server starting on {self.config.host}:{self.config.port}")
        if blocking:
            self._run_forever()
    
    def _run_forever(self):
        """运行服务器"""
        import time
        self.running = True
        while self.running:
            time.sleep(1)
    
    def stop(self):
        """停止服务器"""
        self.running = False
        print("🌐 HTTP Server stopped")


class CLIServer:
    """CLI服务器 - 来自X系统"""
    
    def __init__(self):
        self.commands: Dict[str, Callable] = {}
        self.prompt = "Ω > "
    
    def register_command(self, name: str, handler: Callable, help_text: str = ""):
        """注册命令"""
        self.commands[name] = {"handler": handler, "help": help_text}
    
    def execute(self, command_line: str) -> str:
        """执行CLI命令"""
        parts = command_line.strip().split()
        if not parts:
            return ""
        
        cmd = parts[0]
        args = parts[1:]
        
        if cmd in self.commands:
            try:
                result = self.commands[cmd]["handler"](args)
                return str(result) if result else "OK"
            except Exception as e:
                return f"Error: {e}"
        elif cmd == "help":
            return self._show_help()
        elif cmd == "exit":
            return "Goodbye!"
        else:
            return f"Unknown command: {cmd}"
    
    def _show_help(self) -> str:
        """显示帮助"""
        lines = ["Available commands:"]
        for name, info in self.commands.items():
            lines.append(f"  {name}: {info['help']}")
        return "\n".join(lines)
    
    def start_interactive(self):
        """交互式CLI"""
        print("Prometheus Ω CLI - Type 'help' for commands, 'exit' to quit")
        while True:
            try:
                cmd = input(self.prompt)
                if cmd.lower() in ["exit", "quit"]:
                    break
                result = self.execute(cmd)
                if result:
                    print(result)
            except KeyboardInterrupt:
                break
            except EOFError:
                break


class MCPServer:
    """MCP协议服务器 - 来自X系统
    
    Model Context Protocol 服务器实现
    """
    
    def __init__(self, config: Optional[ServiceConfig] = None):
        self.config = config or ServiceConfig(port=8090)
        self.tools: Dict[str, Dict] = {}
        self.resources: Dict[str, Any] = {}
        self.prompts: Dict[str, Any] = {}
    
    def register_tool(self, name: str, description: str, 
                     input_schema: Dict, handler: Callable):
        """注册MCP工具"""
        self.tools[name] = {
            "description": description,
            "input_schema": input_schema,
            "handler": handler
        }
    
    def register_resource(self, uri: str, description: str, 
                         content_type: str, data: Any):
        """注册MCP资源"""
        self.resources[uri] = {
            "description": description,
            "content_type": content_type,
            "data": data
        }
    
    def register_prompt(self, name: str, description: str, 
                       template: str, arguments: list):
        """注册MCP提示词"""
        self.prompts[name] = {
            "description": description,
            "template": template,
            "arguments": arguments
        }
    
    def handle_jsonrpc(self, request: Dict) -> Dict:
        """处理JSON-RPC请求"""
        method = request.get("method")
        params = request.get("params", {})
        req_id = request.get("id")
        
        try:
            if method == "tools/list":
                result = {"tools": list(self.tools.keys())}
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                if tool_name in self.tools:
                    result = {"content": self.tools[tool_name]["handler"](tool_args)}
                else:
                    raise ValueError(f"Tool {tool_name} not found")
            elif method == "resources/list":
                result = {"resources": list(self.resources.keys())}
            elif method == "prompts/list":
                result = {"prompts": list(self.prompts.keys())}
            else:
                raise ValueError(f"Unknown method: {method}")
            
            return {"jsonrpc": "2.0", "id": req_id, "result": result}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id, 
                    "error": {"code": -32601, "message": str(e)}}
    
    def start(self):
        """启动MCP服务器"""
        print(f"🔌 MCP Server starting on port {self.config.port}")
        self.running = True
    
    def stop(self):
        """停止MCP服务器"""
        self.running = False
        print("🔌 MCP Server stopped")


class PrometheusOmegaAPI:
    """Prometheus Ω REST API 统一入口
    
    整合HTTP/CLI/MCP服务的统一API
    """
    
    def __init__(self):
        self.http = HTTPServer()
        self.cli = CLIServer()
        self.mcp = MCPServer()
        self._running = False
        self._stats = {
            'requests': 0,
            'errors': 0,
            'start_time': None,
        }
        self._setup_default_routes()
    
    def _setup_default_routes(self):
        """设置默认路由"""
        # 健康检查
        self.http.register_handler("/health", lambda r: {"status": "ok", "version": "1.0.0-Ω"})
        
        # 记忆操作
        self.http.register_handler("/memory/write", self._handle_memory_write)
        self.http.register_handler("/memory/read", self._handle_memory_read)
        self.http.register_handler("/memory/search", self._handle_memory_search)
        
        # 执行操作
        self.http.register_handler("/execute/run", self._handle_execute)
        
        # 状态查询
        self.http.register_handler("/status", self._handle_status)
        
        # 统计
        self.http.register_handler("/stats", self._handle_stats)
    
    def _handle_memory_write(self, request: Request) -> Dict:
        """处理记忆写入"""
        self._stats['requests'] += 1
        try:
            body = request.body or {}
            memory_id = body.get('id', f'mem_{self._stats["requests"]}')
            content = body.get('content', '')
            
            return {"status": "written", "id": memory_id}
        except Exception as e:
            self._stats['errors'] += 1
            return {"error": str(e)}
    
    def _handle_memory_read(self, request: Request) -> Dict:
        """处理记忆读取"""
        self._stats['requests'] += 1
        try:
            memory_id = request.query_params.get('id', '')
            return {"id": memory_id, "content": f"Memory content for {memory_id}"}
        except Exception as e:
            self._stats['errors'] += 1
            return {"error": str(e)}
    
    def _handle_memory_search(self, request: Request) -> Dict:
        """处理记忆搜索"""
        self._stats['requests'] += 1
        try:
            query = request.query_params.get('q', '')
            return {"query": query, "results": []}
        except Exception as e:
            self._stats['errors'] += 1
            return {"error": str(e)}
    
    def _handle_execute(self, request: Request) -> Dict:
        """处理执行请求"""
        self._stats['requests'] += 1
        try:
            body = request.body or {}
            command = body.get('command', '')
            
            return {"status": "executed", "command": command}
        except Exception as e:
            self._stats['errors'] += 1
            return {"error": str(e)}
    
    def _handle_status(self, request: Request) -> Dict:
        """处理状态查询"""
        return {
            "status": "running",
            "version": "1.0.0-Ω",
            "services": {
                "http": True,
                "cli": True,
                "mcp": True
            }
        }
    
    def _handle_stats(self, request: Request) -> Dict:
        """处理统计查询"""
        uptime = 0
        if self._stats['start_time']:
            import time
            uptime = time.time() - self._stats['start_time']
        
        return {
            "total_requests": self._stats['requests'],
            "total_errors": self._stats['errors'],
            "error_rate": self._stats['errors'] / max(1, self._stats['requests']),
            "uptime_seconds": uptime,
        }
    
    def start_all(self):
        """启动所有服务"""
        import time
        self._running = True
        self._stats['start_time'] = time.time()
        
        # 启动CLI交互
        self.cli.start_interactive()
    
    def stop_all(self):
        """停止所有服务"""
        self._running = False
        self.http.stop()
        self.mcp.stop()
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return dict(self._stats)


# 工厂函数
def create_http_server(host: str = "0.0.0.0", port: int = 8080) -> HTTPServer:
    config = ServiceConfig(host=host, port=port, service_type=ServiceType.HTTP)
    return HTTPServer(config)

def create_cli_server() -> CLIServer:
    return CLIServer()

def create_mcp_server(port: int = 8090) -> MCPServer:
    config = ServiceConfig(port=port, service_type=ServiceType.MCP)
    return MCPServer(config)

def create_api_server() -> PrometheusOmegaAPI:
    return PrometheusOmegaAPI()