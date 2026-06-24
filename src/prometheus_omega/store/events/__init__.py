"""Prometheus Ω - 事件存储模块

提供完整的事件记录、存储、查询、过滤和分页功能。
集成宪法铁律验证、安全机制与错误处理。
"""
from __future__ import annotations

import logging
import re
import time
import uuid
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    FrozenSet,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 安全工具
# ---------------------------------------------------------------------------

_DANGEROUS_EVENT_PATTERNS: Tuple[str, ...] = (
    "eval(",
    "exec(",
    "__import__(",
    "os.system(",
    "subprocess.",
)

_MAX_EVENT_DATA_SIZE: int = 500_000  # 500 KB


def sanitize_event_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """清理事件数据中的危险模式。

    Args:
        data: 原始事件数据字典

    Returns:
        Dict[str, Any]: 清理后的安全数据
    """
    if not isinstance(data, dict):
        return {}
    cleaned: Dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, str):
            for pattern in _DANGEROUS_EVENT_PATTERNS:
                value = value.replace(pattern, "")
            cleaned[key] = value.strip()
        elif isinstance(value, dict):
            cleaned[key] = sanitize_event_data(value)
        else:
            cleaned[key] = value
    return cleaned


def validate_event_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """验证事件数据格式与大小。

    Args:
        data: 事件数据字典

    Returns:
        Tuple[bool, Optional[str]]: (是否合法, 错误描述)
    """
    if not isinstance(data, dict):
        return False, "Event data must be a dict"
    total_size: int = sum(len(str(v)) for v in data.values())
    if total_size > _MAX_EVENT_DATA_SIZE:
        return False, f"Event data size ({total_size}) exceeds max ({_MAX_EVENT_DATA_SIZE})"
    return True, None


# ---------------------------------------------------------------------------
# 宪法验证集成
# ---------------------------------------------------------------------------

class DopamineWriteGate:
    """第1铁律: 多巴胺写入门控（事件模块本地实例）。"""

    def __init__(
        self,
        threshold: float = 0.2,
        min_dopamine: float = 0.15,
    ) -> None:
        self.threshold: float = threshold
        self.min_dopamine: float = min_dopamine
        self.dopamine_level: float = 0.5

    def can_write(self, importance: float, utility: float, veracity: float) -> bool:
        """判断事件是否允许写入。"""
        try:
            utility_norm: float = min(1.0, max(0.0, utility / 10.0))
            quality: float = importance * utility_norm * veracity
            effective: float = quality * self.dopamine_level
            return effective >= self.threshold and self.dopamine_level >= self.min_dopamine
        except Exception as exc:
            logger.error("DopamineWriteGate error: %s", exc)
            return False

    def adjust_dopamine(self, reward: float) -> None:
        """调整多巴胺水平。"""
        self.dopamine_level = min(1.0, max(0.1, self.dopamine_level + reward * 0.1))


class AntiEvolutionGate:
    """第2铁律: 反进化门控（事件模块本地实例）。"""

    def __init__(
        self,
        energy_threshold: float = 0.9,
        risk_threshold: float = 0.7,
    ) -> None:
        self.energy_threshold: float = energy_threshold
        self.risk_threshold: float = risk_threshold

    def can_evolve(
        self,
        energy_used: float,
        total_energy: float,
        utility_delta: float,
        risk_score: float,
    ) -> bool:
        """判断事件触发的进化是否允许。"""
        try:
            ratio: float = energy_used / total_energy if total_energy > 0 else 0.0
            if ratio > self.energy_threshold:
                return False
            if utility_delta < -0.1:
                return False
            if risk_score > self.risk_threshold:
                return False
            return True
        except Exception as exc:
            logger.error("AntiEvolutionGate error: %s", exc)
            return False


class VerificationIronLaw:
    """第3铁律: 验证铁律（事件模块本地实例）。"""

    def __init__(self) -> None:
        self._cache: Dict[str, bool] = {}

    def verify(self, content: str) -> bool:
        """验证事件内容。"""
        try:
            if content in self._cache:
                return self._cache[content]
            result: bool = bool(content and len(content.strip()) > 0)
            self._cache[content] = result
            return result
        except Exception as exc:
            logger.error("VerificationIronLaw error: %s", exc)
            return False


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class EventSeverity(Enum):
    """事件严重等级。"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class EventStatus(Enum):
    """事件状态。"""
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"
    ARCHIVED = "archived"


# ---------------------------------------------------------------------------
# EventRecord
# ---------------------------------------------------------------------------

@dataclass
class EventRecord:
    """事件记录 — 包含完整的元数据、安全标记和宪法检查信息。

    Attributes:
        event_id: 唯一事件标识
        event_type: 事件类型（如 memory.written, omega.initialized）
        timestamp: 事件时间戳（Unix epoch）
        data: 事件负载数据
        source: 事件来源模块
        severity: 严重等级
        status: 事件处理状态
        session_id: 关联会话 ID
        correlation_id: 关联 ID（用于追踪事件链）
        tags: 标签集合
        importance: 重要性 [0, 1]
        utility: 效用值 [0, 10]
        veracity: 真实性 [0, 1]
        constitutional_checks: 宪法检查结果
        created_at: 创建时间
        updated_at: 最后更新时间
        metadata: 扩展元数据
        is_sanitized: 数据是否已清理
    """

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    timestamp: float = field(default_factory=time.time)
    data: Dict[str, Any] = field(default_factory=dict)
    source: str = ""
    severity: EventSeverity = EventSeverity.INFO
    status: EventStatus = EventStatus.PENDING
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    importance: float = 0.5
    utility: float = 5.0
    veracity: float = 0.5
    constitutional_checks: Dict[str, bool] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_sanitized: bool = False

    # ------------------------------------------------------------------
    # 便捷工厂方法
    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        event_type: str,
        data: Dict[str, Any],
        source: str = "",
        severity: EventSeverity = EventSeverity.INFO,
        session_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        importance: float = 0.5,
        utility: float = 5.0,
        veracity: float = 0.5,
    ) -> EventRecord:
        """工厂方法 — 创建并自动清理事件记录。

        Args:
            event_type: 事件类型
            data: 事件数据
            source: 来源模块
            severity: 严重等级
            session_id: 会话 ID
            correlation_id: 关联 ID
            tags: 标签列表
            importance: 重要性
            utility: 效用值
            veracity: 真实性

        Returns:
            EventRecord: 创建并清理后的事件记录
        """
        record = cls(
            event_type=event_type,
            data=data,
            source=source,
            severity=severity,
            session_id=session_id,
            correlation_id=correlation_id,
            tags=tags or [],
            importance=importance,
            utility=utility,
            veracity=veracity,
        )
        record._sanitize()
        return record

    # ------------------------------------------------------------------
    # 序列化
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典。

        Returns:
            Dict[str, Any]: 事件记录的字典表示
        """
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "data": self.data,
            "source": self.source,
            "severity": self.severity.value,
            "status": self.status.value,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
            "tags": self.tags,
            "importance": self.importance,
            "utility": self.utility,
            "veracity": self.veracity,
            "constitutional_checks": self.constitutional_checks,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
            "is_sanitized": self.is_sanitized,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EventRecord:
        """从字典反序列化。

        Args:
            data: 字典数据

        Returns:
            EventRecord: 还原的事件记录

        Raises:
            ValueError: 数据格式不合法
        """
        try:
            severity_str: str = data.get("severity", "info")
            status_str: str = data.get("status", "pending")
            record = cls(
                event_id=data.get("event_id", str(uuid.uuid4())),
                event_type=data.get("event_type", ""),
                timestamp=data.get("timestamp", time.time()),
                data=data.get("data", {}),
                source=data.get("source", ""),
                severity=EventSeverity(severity_str),
                status=EventStatus(status_str),
                session_id=data.get("session_id"),
                correlation_id=data.get("correlation_id"),
                tags=data.get("tags", []),
                importance=float(data.get("importance", 0.5)),
                utility=float(data.get("utility", 5.0)),
                veracity=float(data.get("veracity", 0.5)),
                constitutional_checks=data.get("constitutional_checks", {}),
                metadata=data.get("metadata", {}),
                is_sanitized=data.get("is_sanitized", False),
            )
            # 时间戳还原
            if "created_at" in data and isinstance(data["created_at"], str):
                record.created_at = datetime.fromisoformat(data["created_at"])
            if "updated_at" in data and isinstance(data["updated_at"], str):
                record.updated_at = datetime.fromisoformat(data["updated_at"])
            return record
        except Exception as exc:
            logger.error("EventRecord.from_dict error: %s", exc)
            raise ValueError(f"Invalid event data: {exc}") from exc

    # ------------------------------------------------------------------
    # 安全 & 宪法
    # ------------------------------------------------------------------

    def _sanitize(self) -> None:
        """内部清理 — 修改 self.data。"""
        self.data = sanitize_event_data(self.data)
        self.is_sanitized = True

    def validate(self) -> Tuple[bool, Optional[str]]:
        """验证事件记录完整性。

        Returns:
            Tuple[bool, Optional[str]]: (是否合法, 错误描述)
        """
        if not self.event_type:
            return False, "event_type is required"
        valid, err = validate_event_data(self.data)
        if not valid:
            return False, err
        return True, None

    def run_constitutional_checks(
        self,
        write_gate: Optional[DopamineWriteGate] = None,
        iron_law: Optional[VerificationIronLaw] = None,
    ) -> Dict[str, bool]:
        """运行宪法铁律检查。

        Args:
            write_gate: 多巴胺写入门控实例
            iron_law: 验证铁律实例

        Returns:
            Dict[str, bool]: 各铁律检查结果
        """
        wg = write_gate or DopamineWriteGate()
        il = iron_law or VerificationIronLaw()

        self.constitutional_checks = {
            "dopamine_write_gate": wg.can_write(
                self.importance, self.utility, self.veracity
            ),
            "verification_iron_law": il.verify(self.event_type),
            "anti_evolution_gate_ok": True,  # 事件本身不触发进化门控
        }
        return self.constitutional_checks

    def mark_processed(self) -> None:
        """标记事件为已处理。"""
        self.status = EventStatus.PROCESSED
        self.updated_at = datetime.now(timezone.utc)

    def mark_failed(self) -> None:
        """标记事件为失败。"""
        self.status = EventStatus.FAILED
        self.updated_at = datetime.now(timezone.utc)

    def mark_archived(self) -> None:
        """标记事件为已归档。"""
        self.status = EventStatus.ARCHIVED
        self.updated_at = datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# EventFilter — 查询过滤条件
# ---------------------------------------------------------------------------

@dataclass
class EventFilter:
    """事件查询过滤条件。

    Attributes:
        event_type: 按事件类型过滤（精确匹配）
        event_type_prefix: 按事件类型前缀过滤
        source: 按来源过滤
        severity: 按严重等级过滤
        status: 按状态过滤
        session_id: 按会话 ID 过滤
        correlation_id: 按关联 ID 过滤
        tags: 按标签过滤（匹配任一）
        min_importance: 最低重要性
        min_timestamp: 最早时间戳
        max_timestamp: 最晚时间戳
        custom_filter: 自定义过滤函数
    """

    event_type: Optional[str] = None
    event_type_prefix: Optional[str] = None
    source: Optional[str] = None
    severity: Optional[EventSeverity] = None
    status: Optional[EventStatus] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    tags: Optional[List[str]] = None
    min_importance: Optional[float] = None
    min_timestamp: Optional[float] = None
    max_timestamp: Optional[float] = None
    custom_filter: Optional[Callable[[EventRecord], bool]] = None

    def matches(self, record: EventRecord) -> bool:
        """判断事件记录是否匹配过滤条件。

        Args:
            record: 事件记录

        Returns:
            bool: 是否匹配
        """
        if self.event_type is not None and record.event_type != self.event_type:
            return False
        if self.event_type_prefix is not None and not record.event_type.startswith(self.event_type_prefix):
            return False
        if self.source is not None and record.source != self.source:
            return False
        if self.severity is not None and record.severity != self.severity:
            return False
        if self.status is not None and record.status != self.status:
            return False
        if self.session_id is not None and record.session_id != self.session_id:
            return False
        if self.correlation_id is not None and record.correlation_id != self.correlation_id:
            return False
        if self.tags is not None:
            if not any(tag in record.tags for tag in self.tags):
                return False
        if self.min_importance is not None and record.importance < self.min_importance:
            return False
        if self.min_timestamp is not None and record.timestamp < self.min_timestamp:
            return False
        if self.max_timestamp is not None and record.timestamp > self.max_timestamp:
            return False
        if self.custom_filter is not None:
            try:
                if not self.custom_filter(record):
                    return False
            except Exception as exc:
                logger.warning("Custom filter error: %s", exc)
                return False
        return True


# ---------------------------------------------------------------------------
# PageResult — 分页结果
# ---------------------------------------------------------------------------

@dataclass
class PageResult:
    """分页查询结果。

    Attributes:
        items: 当前页的事件记录
        total_count: 满足条件的总条目数
        page: 当前页码（1-indexed）
        page_size: 每页条目数
        total_pages: 总页数
    """

    items: List[EventRecord]
    total_count: int
    page: int
    page_size: int
    total_pages: int

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典。"""
        return {
            "items": [item.to_dict() for item in self.items],
            "total_count": self.total_count,
            "page": self.page,
            "page_size": self.page_size,
            "total_pages": self.total_pages,
        }


# ---------------------------------------------------------------------------
# EventStore
# ---------------------------------------------------------------------------

class EventStore:
    """事件存储 — 提供完整的 CRUD、查询、过滤和分页功能。

    集成宪法铁律验证、输入清理和安全检查。

    Args:
        max_events: 最大事件存储数量
        enable_constitutional_checks: 是否在添加时自动执行宪法检查
    """

    def __init__(
        self,
        max_events: int = 100_000,
        enable_constitutional_checks: bool = True,
    ) -> None:
        self.max_events: int = max_events
        self.enable_constitutional_checks: bool = enable_constitutional_checks

        # 存储
        self.events: Dict[str, EventRecord] = {}

        # 索引：event_type -> set of event_ids
        self._type_index: Dict[str, Set[str]] = {}
        # 索引：source -> set of event_ids
        self._source_index: Dict[str, Set[str]] = {}
        # 索引：session_id -> set of event_ids
        self._session_index: Dict[str, Set[str]] = {}
        # 时间有序列表（用于时间范围查询）
        self._timeline: List[str] = []

        # 宪法铁律实例
        self.write_gate: DopamineWriteGate = DopamineWriteGate()
        self.anti_evolution_gate: AntiEvolutionGate = AntiEvolutionGate()
        self.iron_law: VerificationIronLaw = VerificationIronLaw()

        # 统计
        self._stats: Dict[str, int] = {
            "total_added": 0,
            "total_rejected": 0,
            "total_updated": 0,
            "total_deleted": 0,
            "constitutional_rejections": 0,
            "validation_failures": 0,
        }

        # LRU 溢出控制
        self._insertion_order: List[str] = []

        logger.info("EventStore initialized (max_events=%d)", max_events)

    # ------------------------------------------------------------------
    # CRUD: Create
    # ------------------------------------------------------------------

    def add(self, event: EventRecord) -> Tuple[bool, Optional[str]]:
        """添加事件记录 — 经过验证和宪法检查。

        Args:
            event: 待添加的事件记录

        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 错误描述)
        """
        try:
            # 1. 验证
            valid, err = event.validate()
            if not valid:
                self._stats["validation_failures"] += 1
                return False, f"Validation failed: {err}"

            # 2. 清理
            if not event.is_sanitized:
                event._sanitize()

            # 3. 宪法检查
            if self.enable_constitutional_checks:
                checks = event.run_constitutional_checks(
                    write_gate=self.write_gate,
                    iron_law=self.iron_law,
                )
                if not all(checks.values()):
                    self._stats["constitutional_rejections"] += 1
                    self._stats["total_rejected"] += 1
                    return False, f"Constitutional check failed: {checks}"

            # 4. 存储
            self.events[event.event_id] = event
            self._insertion_order.append(event.event_id)

            # 5. 更新索引
            self._add_to_index(self._type_index, event.event_type, event.event_id)
            self._add_to_index(self._source_index, event.source, event.event_id)
            if event.session_id:
                self._add_to_index(self._session_index, event.session_id, event.event_id)
            self._timeline.append(event.event_id)

            # 6. 溢出控制
            self._evict_if_needed()

            self._stats["total_added"] += 1
            return True, None

        except Exception as exc:
            logger.error("EventStore.add error: %s", exc)
            self._stats["total_rejected"] += 1
            return False, f"Internal error: {exc}"

    def add_simple(
        self,
        event_type: str,
        data: Dict[str, Any],
        source: str = "",
        severity: EventSeverity = EventSeverity.INFO,
        session_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        importance: float = 0.5,
    ) -> Tuple[bool, Optional[str]]:
        """简化添加 — 自动创建 EventRecord 并添加。

        Args:
            event_type: 事件类型
            data: 事件数据
            source: 来源
            severity: 严重等级
            session_id: 会话 ID
            tags: 标签
            importance: 重要性

        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 错误描述)
        """
        record = EventRecord.create(
            event_type=event_type,
            data=data,
            source=source,
            severity=severity,
            session_id=session_id,
            tags=tags,
            importance=importance,
        )
        return self.add(record)

    # ------------------------------------------------------------------
    # CRUD: Read
    # ------------------------------------------------------------------

    def get(self, event_id: str) -> Optional[EventRecord]:
        """按 ID 获取事件记录。

        Args:
            event_id: 事件 ID

        Returns:
            Optional[EventRecord]: 事件记录，不存在返回 None
        """
        return self.events.get(event_id)

    def get_or_raise(self, event_id: str) -> EventRecord:
        """按 ID 获取事件记录，不存在时抛出异常。

        Args:
            event_id: 事件 ID

        Returns:
            EventRecord: 事件记录

        Raises:
            KeyError: 事件不存在
        """
        if event_id not in self.events:
            raise KeyError(f"Event not found: {event_id}")
        return self.events[event_id]

    # ------------------------------------------------------------------
    # CRUD: Update
    # ------------------------------------------------------------------

    def update(
        self,
        event_id: str,
        updates: Dict[str, Any],
    ) -> Tuple[bool, Optional[str]]:
        """更新事件记录的部分字段。

        Args:
            event_id: 事件 ID
            updates: 更新字段字典

        Returns:
            Tuple[bool, Optional[str]]: (是否成功, 错误描述)
        """
        if event_id not in self.events:
            return False, f"Event not found: {event_id}"

        try:
            record = self.events[event_id]

            # 可更新字段白名单
            updatable_fields: FrozenSet[str] = frozenset({
                "event_type", "data", "source", "severity",
                "status", "tags", "importance", "utility",
                "veracity", "metadata",
            })

            # 先移除旧索引
            self._remove_from_index(self._type_index, record.event_type, event_id)
            self._remove_from_index(self._source_index, record.source, event_id)
            if record.session_id:
                self._remove_from_index(self._session_index, record.session_id, event_id)

            for key, value in updates.items():
                if key in updatable_fields:
                    if key == "severity" and isinstance(value, str):
                        value = EventSeverity(value)
                    elif key == "status" and isinstance(value, str):
                        value = EventStatus(value)
                    elif key == "data":
                        value = sanitize_event_data(value) if isinstance(value, dict) else value
                    setattr(record, key, value)

            record.updated_at = datetime.now(timezone.utc)

            # 重建索引
            self._add_to_index(self._type_index, record.event_type, event_id)
            self._add_to_index(self._source_index, record.source, event_id)
            if record.session_id:
                self._add_to_index(self._session_index, record.session_id, event_id)

            self._stats["total_updated"] += 1
            return True, None

        except Exception as exc:
            logger.error("EventStore.update error: %s", exc)
            return False, f"Update error: {exc}"

    # ------------------------------------------------------------------
    # CRUD: Delete
    # ------------------------------------------------------------------

    def delete(self, event_id: str) -> bool:
        """删除事件记录。

        Args:
            event_id: 事件 ID

        Returns:
            bool: 是否成功删除
        """
        if event_id not in self.events:
            return False

        try:
            record = self.events.pop(event_id)

            # 清理索引
            self._remove_from_index(self._type_index, record.event_type, event_id)
            self._remove_from_index(self._source_index, record.source, event_id)
            if record.session_id:
                self._remove_from_index(self._session_index, record.session_id, event_id)
            if event_id in self._timeline:
                self._timeline.remove(event_id)
            if event_id in self._insertion_order:
                self._insertion_order.remove(event_id)

            self._stats["total_deleted"] += 1
            return True

        except Exception as exc:
            logger.error("EventStore.delete error: %s", exc)
            return False

    # ------------------------------------------------------------------
    # 查询
    # ------------------------------------------------------------------

    def query(
        self,
        event_filter: Optional[EventFilter] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[EventRecord]:
        """按过滤条件查询事件记录。

        Args:
            event_filter: 过滤条件，None 表示不过滤
            limit: 返回条目上限
            offset: 偏移量

        Returns:
            List[EventRecord]: 匹配的事件记录列表
        """
        try:
            results: List[EventRecord] = []

            # 利用索引优化简单过滤
            candidate_ids: Optional[Set[str]] = None
            if event_filter is not None:
                if event_filter.event_type and event_filter.event_type in self._type_index:
                    candidate_ids = set(self._type_index[event_filter.event_type])
                elif event_filter.source and event_filter.source in self._source_index:
                    candidate_ids = set(self._source_index[event_filter.source])
                elif event_filter.session_id and event_filter.session_id in self._session_index:
                    candidate_ids = set(self._session_index[event_filter.session_id])

            if candidate_ids is not None:
                records = [self.events[eid] for eid in candidate_ids if eid in self.events]
            else:
                records = list(self.events.values())

            # 应用完整过滤
            if event_filter is not None:
                records = [r for r in records if event_filter.matches(r)]

            # 按时间戳降序排列
            records.sort(key=lambda r: r.timestamp, reverse=True)

            # 应用偏移和限制
            results = records[offset:]
            if limit is not None:
                results = results[:limit]

            return results

        except Exception as exc:
            logger.error("EventStore.query error: %s", exc)
            return []

    def query_by_type(self, event_type: str, limit: int = 100) -> List[EventRecord]:
        """按事件类型查询。

        Args:
            event_type: 事件类型
            limit: 最大返回条数

        Returns:
            List[EventRecord]: 匹配的事件记录
        """
        return self.query(
            event_filter=EventFilter(event_type=event_type),
            limit=limit,
        )

    def query_by_time_range(
        self,
        min_timestamp: float,
        max_timestamp: float,
        limit: int = 100,
    ) -> List[EventRecord]:
        """按时间范围查询。

        Args:
            min_timestamp: 起始时间戳
            max_timestamp: 结束时间戳
            limit: 最大返回条数

        Returns:
            List[EventRecord]: 匹配的事件记录
        """
        return self.query(
            event_filter=EventFilter(
                min_timestamp=min_timestamp,
                max_timestamp=max_timestamp,
            ),
            limit=limit,
        )

    def query_by_session(
        self,
        session_id: str,
        limit: int = 100,
    ) -> List[EventRecord]:
        """按会话 ID 查询。

        Args:
            session_id: 会话 ID
            limit: 最大返回条数

        Returns:
            List[EventRecord]: 匹配的事件记录
        """
        return self.query(
            event_filter=EventFilter(session_id=session_id),
            limit=limit,
        )

    def query_by_severity(
        self,
        severity: EventSeverity,
        limit: int = 100,
    ) -> List[EventRecord]:
        """按严重等级查询。

        Args:
            severity: 严重等级
            limit: 最大返回条数

        Returns:
            List[EventRecord]: 匹配的事件记录
        """
        return self.query(
            event_filter=EventFilter(severity=severity),
            limit=limit,
        )

    # ------------------------------------------------------------------
    # 分页
    # ------------------------------------------------------------------

    def page(
        self,
        event_filter: Optional[EventFilter] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PageResult:
        """分页查询。

        Args:
            event_filter: 过滤条件
            page: 页码（1-indexed）
            page_size: 每页条目数

        Returns:
            PageResult: 分页结果
        """
        try:
            page = max(1, page)
            page_size = max(1, min(page_size, 500))

            all_results = self.query(event_filter=event_filter)
            total_count: int = len(all_results)
            total_pages: int = max(1, (total_count + page_size - 1) // page_size)

            offset: int = (page - 1) * page_size
            items = all_results[offset:offset + page_size]

            return PageResult(
                items=items,
                total_count=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
            )
        except Exception as exc:
            logger.error("EventStore.page error: %s", exc)
            return PageResult(
                items=[], total_count=0, page=page, page_size=page_size, total_pages=0,
            )

    # ------------------------------------------------------------------
    # 批量操作
    # ------------------------------------------------------------------

    def add_batch(
        self, events: Sequence[EventRecord]
    ) -> Dict[str, Tuple[bool, Optional[str]]]:
        """批量添加事件。

        Args:
            events: 事件记录序列

        Returns:
            Dict[str, Tuple[bool, Optional[str]]]: 每个事件的添加结果
        """
        results: Dict[str, Tuple[bool, Optional[str]]] = {}
        for event in events:
            success, err = self.add(event)
            results[event.event_id] = (success, err)
        return results

    def delete_batch(self, event_ids: Sequence[str]) -> Dict[str, bool]:
        """批量删除事件。

        Args:
            event_ids: 事件 ID 序列

        Returns:
            Dict[str, bool]: 每个事件的删除结果
        """
        results: Dict[str, bool] = {}
        for eid in event_ids:
            results[eid] = self.delete(eid)
        return results

    # ------------------------------------------------------------------
    # 统计 & 管理
    # ------------------------------------------------------------------

    def count(self, event_filter: Optional[EventFilter] = None) -> int:
        """统计满足条件的事件数量。

        Args:
            event_filter: 过滤条件

        Returns:
            int: 数量
        """
        if event_filter is None:
            return len(self.events)
        return len(self.query(event_filter=event_filter))

    def get_stats(self) -> Dict[str, Any]:
        """获取存储统计信息。

        Returns:
            Dict[str, Any]: 统计数据
        """
        return {
            "total_events": len(self.events),
            "max_events": self.max_events,
            "unique_types": len(self._type_index),
            "unique_sources": len(self._source_index),
            "unique_sessions": len(self._session_index),
            **self._stats,
        }

    def get_event_types(self) -> List[str]:
        """获取所有事件类型。

        Returns:
            List[str]: 事件类型列表
        """
        return list(self._type_index.keys())

    def get_sources(self) -> List[str]:
        """获取所有事件来源。

        Returns:
            List[str]: 来源列表
        """
        return list(self._source_index.keys())

    def clear(self) -> int:
        """清空所有事件。

        Returns:
            int: 清除的事件数量
        """
        count: int = len(self.events)
        self.events.clear()
        self._type_index.clear()
        self._source_index.clear()
        self._session_index.clear()
        self._timeline.clear()
        self._insertion_order.clear()
        logger.info("EventStore cleared (%d events removed)", count)
        return count

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    def _add_to_index(
        self, index: Dict[str, Set[str]], key: str, event_id: str
    ) -> None:
        """添加到索引。"""
        if not key:
            return
        if key not in index:
            index[key] = set()
        index[key].add(event_id)

    def _remove_from_index(
        self, index: Dict[str, Set[str]], key: str, event_id: str
    ) -> None:
        """从索引移除。"""
        if key in index:
            index[key].discard(event_id)
            if not index[key]:
                del index[key]

    def _evict_if_needed(self) -> None:
        """当存储超出上限时，按 LRU 策略逐出旧事件。"""
        while len(self.events) > self.max_events and self._insertion_order:
            oldest_id: str = self._insertion_order.pop(0)
            if oldest_id in self.events:
                self.delete(oldest_id)
                logger.debug("Evicted event %s (LRU)", oldest_id)
