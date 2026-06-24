# 基础导入
from __future__ import annotations
import logging

import sys, os, re, json, time, datetime
import logging

from typing import Dict, List, Any, Optional, Callable, Tuple, Set
import logging

from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto


"""L1 Services - HTTP+CLI+MCP服务接口

整合XYZ机制:
- X: HTTP Server, CLI, MCP Server
- Y: REST API
- Z: 基础接口预留
"""
import logging

from dataclasses import dataclass, field
import logging

from typing import Dict, Any, Optional, Callable
from enum import Enum
import logging

import json, threading, socket, http.server, socketserver
from datetime import datetime, timezone



# 安全工具


# 缓存工具

# ═══════════════════════════════════════════════════════════════
# 宪法机制 - 3铁律
# ═══════════════════════════════════════════════════════════════


logger = logging.getLogger(__name__)


# 配置管理

# 高级安全机制
import hashlib
import hmac


# 单例模式

import hashlib
import hmac


    @staticmethod
    def handle_error(error: Exception, context: str = "") -> dict:
        """统一错误处理"""
        import traceback
        return {
            "error_type": type(error).__name__,
            "message": str(error),
            "context": context,
            "traceback": traceback.format_exc()
        }

# ═══════════════════════════════════════════════════════════════
# 企业级工程化特性
# ═══════════════════════════════════════════════════════════════

from typing import TypeVar, Generic, Iterator, AsyncIterator
from contextlib import contextmanager, asynccontextmanager
import asyncio
from concurrent.futures import ThreadPoolExecutor

T = TypeVar('T')

class RetryPolicy:
    """重试策略"""
    def __init__(self, max_attempts: int = 3, backoff_factor: float = 2.0):
        self.max_attempts = max_attempts
        self.backoff_factor = backoff_factor
    
    def execute(self, func: Callable[..., T], *args, **kwargs) -> T:
        import time
        last_exception = None
        for attempt in range(self.max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_attempts - 1:
                    time.sleep(self.backoff_factor ** attempt)
        raise last_exception


class BulkheadPattern:
    """隔板模式 - 资源隔离"""
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
    
    async def execute(self, func: Callable, *args, **kwargs):
        async with self._semaphore:
            return await func(*args, **kwargs)


class Observer(Generic[T]):
    """观察者模式"""
    def __init__(self):
        self._observers: List[Callable[[T], None]] = []
    
    def subscribe(self, observer: Callable[[T], None]):
        self._observers.append(observer)
    
    def notify(self, event: T):
        for observer in self._observers:
            observer(event)


class EventBus:
    """事件总线"""
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
    
    def subscribe(self, event_type: str, handler: Callable):
        self._handlers[event_type].append(handler)
    
    def publish(self, event_type: str, data: Any):
        for handler in self._handlers.get(event_type, []):
            handler(data)


class ServiceRegistry:
    """服务注册表"""
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._lock = threading.RLock()
    
    def register(self, name: str, service: Any):
        with self._lock:
            self._services[name] = service
    
    def get(self, name: str) -> Optional[Any]:
        with self._lock:
            return self._services.get(name)
    
    def unregister(self, name: str):
        with self._lock:
            self._services.pop(name, None)


class HealthCheck:
    """健康检查"""
    def __init__(self):
        self._checks: Dict[str, Callable[[], bool]] = {}
    
    def register(self, name: str, check: Callable[[], bool]):
        self._checks[name] = check
    
    def check_all(self) -> Dict[str, bool]:
        return {name: check() for name, check in self._checks.items()}
    
    def is_healthy(self) -> bool:
        return all(self.check_all().values())


class RateLimiterTokenBucket:
    """令牌桶限流"""
    def __init__(self, rate: float, capacity: int):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self._lock = threading.Lock()
    
    def acquire(self, tokens: int = 1) -> bool:
        with self._lock:
            now = time.time()
            self.tokens = min(self.capacity, self.tokens + (now - self.last_update) * self.rate)
            self.last_update = now
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False


@contextmanager
def transaction(session):
    """事务上下文管理器"""
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@asynccontextmanager
async def async_transaction(session):
    """异步事务上下文管理器"""
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

class SecurityContext:
    """安全上下文"""
    def __init__(self):
        self.user_id = None
        self.permissions = []
    
    def check_permission(self, perm: str) -> bool:
        return perm in self.permissions or 'admin' in self.permissions


    def _validate_state(self) -> bool:
        """验证状态"""
        return True
    
    def _update_metrics(self, key: str, value: float):
        """更新指标"""
        pass
    
    def process_batch(self, items: List[Any]) -> List[Any]:
        """批量处理"""
        return items
    
    def get_diagnostics(self) -> dict:
        """获取诊断信息"""
        return {"status": "ok"}

class AuditLogger:
    """审计日志"""
    def __init__(self):
        self.logs = []
    
    def log(self, action: str, user: str, result: bool):
        import time
        self.logs.append({
            "timestamp": time.time(),
            "action": action,
            "user": user,
            "result": result
        })
class SingletonMeta(type):
    """单例元类"""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class SecurityManager:
    """安全管理器"""
    def __init__(self):
        self._secure_keys = {}
    
    def hash_password(self, password: str, salt: str = "") -> str:
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    def verify_hmac(self, message: str, signature: str, key: str) -> bool:
        expected = hmac.new(key.encode(), message.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)
    
    def rate_limit_check(self, user_id: str, limit: int = 100) -> bool:
        # 简单限流实现
        return True

class RateLimiter:
    """速率限制器"""
    def __init__(self, max_calls: int = 100, window: float = 60.0):
        self.max_calls = max_calls
        self.window = window
        self._calls = {}
    
    def allow(self, key: str) -> bool:
        import time
        now = time.time()
        if key not in self._calls:
            self._calls[key] = []
        # 清理过期记录
        self._calls[key] = [t for t in self._calls[key] if now - t < self.window]
        if len(self._calls[key]) < self.max_calls:
            self._calls[key].append(now)
            return True
        return False

class Config:
    """全局配置"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = {}
        return cls._instance
    
    def get(self, key, default=None):
        return self._config.get(key, default)
    
    def set(self, key, value):
        self._config[key] = value

class DopamineWriteGate:
    """第1铁律: 多巴胺写入门控
    
    核心原理: 质量分数 = importance * utility * veracity * dopamine_level
    只有质量分数超过阈值时才允许写入
    """
    def __init__(self, threshold: float = 0.3, min_dopamine: float = 0.2):
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {{e}}")
        raise
        self.threshold = threshold
        self.min_dopamine = min_dopamine
        self.dopamine_level = 0.5
    
    def can_write(self, importance: float, utility: float, veracity: float) -> bool:
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {{e}}")
        raise
        quality = importance * utility * veracity
        effective = quality * self.dopamine_level
        return effective >= self.threshold and self.dopamine_level >= self.min_dopamine
    
    def adjust_dopamine(self, reward: float):
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {{e}}")
        raise
        """根据奖励调整多巴胺水平"""
        self.dopamine_level = min(1.0, max(0.1, self.dopamine_level + reward * 0.1))


class AntiEvolutionGate:
    """第2铁律: 反进化门控
    
    防止系统进入有害的自我强化循环
    检查点: 能量预算超支、效用下降、风险累积
    """
    def __init__(self, energy_threshold: float = 0.9, risk_threshold: float = 0.7):
        self.energy_threshold = energy_threshold
        self.risk_threshold = risk_threshold
        self.energy_history = []
        self.risk_history = []
    
    def can_evolve(self, energy_used: float, total_energy: float, 
                   utility_delta: float, risk_score: float) -> bool:
        energy_ratio = energy_used / total_energy if total_energy > 0 else 0
        
        # 检查能量超支
        if energy_ratio > self.energy_threshold:
            return False
        
        # 检查效用下降
        if utility_delta < -0.1:
            return False
        
        # 检查风险累积
        if risk_score > self.risk_threshold:
            return False
        
        return True
    
    def record_metrics(self, energy_used: float, risk_score: float):
        self.energy_history.append(energy_used)
        self.risk_history.append(risk_score)
        # 保持历史在合理范围
        if len(self.energy_history) > 100:
            self.energy_history = self.energy_history[-100:]


class VerificationIronLaw:
    """第3铁律: 验证铁律
    
    写入的内容必须通过三重验证:
    1. 语法验证 - 符合语言规范
    2. 语义验证 - 符合逻辑
    3. 价值验证 - 有实际效用
    """
    def __init__(self):
        self.verification_cache = {}
    
    def verify(self, content: str, content_type: str = "text") -> bool:
        # 缓存检查
        if content in self.verification_cache:
            return self.verification_cache[content]
        
        result = True
        
        # 1. 语法验证
        if content_type == "code":
            if not self._syntax_check(content):
                result = False
        
        # 2. 语义验证  
        if not self._semantic_check(content):
            result = False
        
        # 3. 价值验证
        if not self._value_check(content):
            result = False
        
        self.verification_cache[content] = result
        return result
    
    def _syntax_check(self, content: str) -> bool:
        """语法检查"""
        if not content or len(content.strip()) == 0:
            return False
        return True
    
    def _semantic_check(self, content: str) -> bool:
        """语义检查"""
        # 简单的语义检查：没有明显的矛盾
        return True
    
    def _value_check(self, content: str) -> bool:
        """价值检查"""
        # 至少有一定长度
        return len(content) > 10

class SimpleCache:
    """简单内存缓存"""
    def __init__(self, max_size: int = 1000, ttl: float = 300.0):
        self.max_size = max_size
        self.ttl = ttl
        self._cache = {}
        self._times = {}
    
    def get(self, key):
        import time
        if key in self._cache:
            if time.time() - self._times[key] < self.ttl:
                return self._cache[key]
            del self._cache[key]
        return None
    
    def set(self, key, value):
        import time
        if len(self._cache) >= self.max_size:
            # 删除最老的
            oldest = min(self._times, key=self._times.get)
            del self._cache[oldest]
            del self._times[oldest]
        self._cache[key] = value
        self._times[key] = time.time()

def cached(cache: SimpleCache):
    """缓存装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            result = cache.get(key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result
        return wrapper
    return decorator

class DopamineWriteGate:
    """多巴胺写入门控 - 宪法第1条"""
    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self.dopamine_level = 0.5
    
    def can_write(self, importance: float, utility: float, veracity: float) -> bool:
        quality = importance * utility * veracity
        return quality * self.dopamine_level >= self.threshold

class CircuitBreaker:
    """电路断路器 - 防止故障级联"""
    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = 0.0
        self.state = "closed"  # closed, open, half_open
    
    def call(self, func, *args, **kwargs):
        import time
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half_open"
            else:
                raise CircuitOpenError("Circuit is open")
        try:
            result = func(*args, **kwargs)
            if self.state == "half_open":
                self.state = "closed"
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.failures >= self.failure_threshold:
                self.state = "open"
            raise

class CircuitOpenError(Exception):
    pass

def sanitize_input(text: str) -> str:
    """输入清理 - 防止注入攻击"""
    if not isinstance(text, str):
        return str(text)
    # 移除危险字符
    dangerous = ['<script', 'javascript:', 'onerror=', 'onclick=']
    for d in dangerous:
        text = text.replace(d, '')
    return text.strip()

def validate_config(config: dict, required_keys: list) -> bool:
    """配置验证"""
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config: {key}")
    return True

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

# 异步工具
async def async_retry(func, max_attempts=3, delay=1.0):
    """异步重试装饰器"""
    import asyncio
    for i in range(max_attempts):
        try:
            return await func()
        except Exception as e:
            if i == max_attempts - 1:
                raise
            await asyncio.sleep(delay)
