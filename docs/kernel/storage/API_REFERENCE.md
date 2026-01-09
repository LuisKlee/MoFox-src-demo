# Storage API 参考文档

本文档提供 Storage 模块的完整 API 参考，包括所有类、方法、参数和返回值的详细说明。

**注意**: 本文档主要介绍 Python 版本。C++ 版本的 API 文档请参考 [C++ 实现指南](./CPP_IMPLEMENTATION.md)。

---

## 目录

- [版本选择](#版本选择)
- [JSONStore](#jsonstore)
- [DictJSONStore](#dictjsonstore)
- [ListJSONStore](#listjsonstore)
- [LogStore](#logstore)
- [异常类](#异常类)

---

## 版本选择

### Python vs C++

| 方面 | Python | C++ |
|------|--------|-----|
| **适用场景** | 快速开发、原型设计 | 性能关键、生产环境 |
| **性能** | 基准 | ⚡ 5-10倍更快 |
| **易用性** | 🟢 极简 | 🟡 需要编译 |
| **类型安全** | 弱类型 | 强类型 |
| **学习成本** | 低 | 中等 |

选择 Python 版本继续使用本文档。选择 C++ 版本请参考 [C++ 实现指南](./CPP_IMPLEMENTATION.md) 和 [快速参考](../../src/kernel/storage/QUICK_REFERENCE.md)。

---

## JSONStore

基础JSON存储器，提供通用的JSON文件读写、备份、压缩等功能。

### 构造函数

```python
JSONStore(
    file_path: Union[str, Path],
    auto_create: bool = True,
    auto_backup: bool = True,
    max_backups: int = 5,
    indent: Optional[int] = 2,
    encoding: str = 'utf-8',
    validate_func: Optional[Callable[[Any], bool]] = None
)
```

**参数**:

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| file_path | `str \| Path` | 必需 | JSON文件路径 |
| auto_create | `bool` | `True` | 文件不存在时是否自动创建 |
| auto_backup | `bool` | `True` | 写入前是否自动备份 |
| max_backups | `int` | `5` | 最大备份文件数量 |
| indent | `int \| None` | `2` | JSON缩进空格数，`None`为紧凑格式 |
| encoding | `str` | `'utf-8'` | 文件编码 |
| validate_func | `Callable \| None` | `None` | 数据验证函数 |

**示例**:
```python
from kernel.storage import JSONStore

store = JSONStore('data.json')
store = JSONStore('config.json', auto_backup=True, max_backups=10)
```

---

### read()

读取JSON数据。

```python
def read(default: Any = None) -> Any
```

**参数**:

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| default | `Any` | `None` | 文件不存在时返回的默认值 |

**返回值**: `Any` - 解析后的JSON数据

**异常**:
- `FileNotFoundError` - 文件不存在且未提供默认值
- `JSONStoreError` - 读取或解析失败

**示例**:
```python
# 基本读取
data = store.read()

# 使用默认值
data = store.read(default={})
data = store.read(default=[])

# 异常处理
try:
    data = store.read()
except FileNotFoundError:
    print("文件不存在")
except JSONStoreError as e:
    print(f"读取失败: {e}")
```

---

### write()

写入JSON数据（原子操作）。

```python
def write(data: Any, validate: bool = True) -> None
```

**参数**:

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| data | `Any` | 必需 | 要写入的数据 |
| validate | `bool` | `True` | 是否执行数据验证 |

**返回值**: `None`

**异常**:
- `ValidationError` - 数据验证失败
- `JSONStoreError` - 写入失败

**说明**:
- 使用临时文件+原子重命名机制
- 如果启用了 `auto_backup`，会在写入前自动创建备份
- 写入过程线程安全

**示例**:
```python
# 基本写入
store.write({'name': 'MoFox', 'version': '1.0'})

# 跳过验证
store.write(data, validate=False)

# 异常处理
try:
    store.write(data)
except ValidationError:
    print("数据验证失败")
except JSONStoreError as e:
    print(f"写入失败: {e}")
```

---

### update()

原子更新数据（读取-修改-写入）。

```python
def update(update_func: Callable[[Any], Any]) -> Any
```

**参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| update_func | `Callable[[Any], Any]` | 更新函数，接收当前数据，返回新数据 |

**返回值**: `Any` - 更新后的数据

**异常**:
- `ValidationError` - 数据验证失败
- `JSONStoreError` - 读取或写入失败

**说明**:
- 整个过程是原子的，线程安全
- 适合需要基于当前值进行更新的场景

**示例**:
```python
# 更新字典
store.update(lambda data: {**data, 'updated': True})

# 计数器递增
store.update(lambda data: {'count': data.get('count', 0) + 1})

# 列表添加项
store.update(lambda data: data + [new_item] if isinstance(data, list) else [new_item])

# 复杂更新
def complex_update(data):
    if not isinstance(data, dict):
        data = {}
    data['timestamp'] = datetime.now().isoformat()
    data['counter'] = data.get('counter', 0) + 1
    return data

result = store.update(complex_update)
```

---

### delete()

删除JSON文件。

```python
def delete(create_backup: bool = True) -> bool
```

**参数**:

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| create_backup | `bool` | `True` | 删除前是否创建备份 |

**返回值**: `bool` - 是否成功删除（文件不存在返回`False`）

**异常**:
- `JSONStoreError` - 删除失败

**示例**:
```python
# 删除并备份
success = store.delete()

# 删除但不备份
success = store.delete(create_backup=False)

if success:
    print("文件已删除")
else:
    print("文件不存在")
```

---

### exists()

检查文件是否存在。

```python
def exists() -> bool
```

**返回值**: `bool` - 文件是否存在

**示例**:
```python
if store.exists():
    data = store.read()
else:
    store.write({})
```

---

### get_size()

获取文件大小。

```python
def get_size() -> int
```

**返回值**: `int` - 文件大小（字节），文件不存在返回`0`

**示例**:
```python
size = store.get_size()
print(f"文件大小: {size} bytes")
print(f"文件大小: {size / 1024:.2f} KB")
```

---

### compress()

压缩JSON文件为gzip格式。

```python
def compress(output_path: Optional[Union[str, Path]] = None) -> Path
```

**参数**:

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| output_path | `str \| Path \| None` | `None` | 输出路径，默认为原文件名+`.gz` |

**返回值**: `Path` - 压缩文件的路径

**异常**:
- `FileNotFoundError` - 源文件不存在
- `JSONStoreError` - 压缩失败

**示例**:
```python
# 压缩到默认位置
gz_path = store.compress()
# data.json -> data.json.gz

# 压缩到指定位置
gz_path = store.compress('backup/data_20260106.gz')

print(f"压缩文件: {gz_path}")
```

---

### decompress()

从gzip文件解压到当前文件。

```python
def decompress(compressed_path: Union[str, Path]) -> None
```

**参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| compressed_path | `str \| Path` | 压缩文件路径 |

**返回值**: `None`

**异常**:
- `FileNotFoundError` - 压缩文件不存在
- `JSONStoreError` - 解压失败

**示例**:
```python
# 从压缩文件恢复
store.decompress('backup/data.json.gz')

# 验证数据
data = store.read()
print(f"恢复数据: {data}")
```

---

## DictJSONStore

字典型JSON存储器，专门处理字典数据。继承所有 `JSONStore` 的方法。

### 构造函数

```python
DictJSONStore(
    file_path: Union[str, Path],
    **kwargs  # 与 JSONStore 相同的参数
)
```

**示例**:
```python
from kernel.storage import DictJSONStore

config = DictJSONStore('config.json')
config = DictJSONStore('config.json', auto_backup=True, max_backups=10)
```

---

### get()

获取指定键的值。

```python
def get(key: str, default: Any = None) -> Any
```

**参数**:

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| key | `str` | 必需 | 键名 |
| default | `Any` | `None` | 键不存在时的默认值 |

**返回值**: `Any` - 键对应的值，或默认值

**示例**:
```python
# 获取值
name = config.get('name')

# 使用默认值
port = config.get('port', 8000)
debug = config.get('debug', False)

# 嵌套访问需要自己处理
db_config = config.get('database', {})
host = db_config.get('host', 'localhost')
```

---

### set()

设置键值对。

```python
def set(key: str, value: Any) -> None
```

**参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| key | `str` | 键名 |
| value | `Any` | 值（可JSON序列化） |

**返回值**: `None`

**说明**:
- 如果键已存在，会覆盖原值
- 如果文件中的数据不是字典，会被替换为字典

**示例**:
```python
# 设置值
config.set('name', 'MoFox')
config.set('port', 8000)
config.set('debug', True)

# 设置复杂值
config.set('database', {
    'host': 'localhost',
    'port': 5432,
    'name': 'mydb'
})

config.set('servers', ['server1', 'server2'])
```

---

### delete_key()

删除指定的键。

```python
def delete_key(key: str) -> bool
```

**参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| key | `str` | 要删除的键名 |

**返回值**: `bool` - 始终返回 `True`

**示例**:
```python
# 删除键
config.delete_key('debug')
config.delete_key('temporary_setting')

# 键不存在也不会报错
config.delete_key('non_existent_key')  # 安全操作
```

---

### has_key()

检查键是否存在。

```python
def has_key(key: str) -> bool
```

**参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| key | `str` | 键名 |

**返回值**: `bool` - 键是否存在

**示例**:
```python
if config.has_key('debug'):
    debug = config.get('debug')
    print(f"Debug mode: {debug}")

# 避免KeyError
if not config.has_key('api_key'):
    config.set('api_key', generate_api_key())
```

---

### keys()

获取所有键。

```python
def keys() -> List[str]
```

**返回值**: `List[str]` - 所有键的列表

**示例**:
```python
# 获取所有键
all_keys = config.keys()
print(f"配置项: {', '.join(all_keys)}")

# 遍历所有配置
for key in config.keys():
    value = config.get(key)
    print(f"{key}: {value}")
```

---

### values()

获取所有值。

```python
def values() -> List[Any]
```

**返回值**: `List[Any]` - 所有值的列表

**示例**:
```python
# 获取所有值
all_values = config.values()

# 检查某个值是否存在
if 'localhost' in config.values():
    print("使用本地主机")
```

---

### items()

获取所有键值对。

```python
def items() -> List[tuple]
```

**返回值**: `List[tuple]` - 键值对列表，每个元素是 `(key, value)` 元组

**示例**:
```python
# 遍历所有配置
for key, value in config.items():
    print(f"{key}: {value}")

# 转换为字典
config_dict = dict(config.items())

# 过滤配置
db_items = [(k, v) for k, v in config.items() if k.startswith('db_')]
```

---

### clear()

清空所有数据。

```python
def clear() -> None
```

**返回值**: `None`

**说明**:
- 将数据重置为空字典 `{}`
- 会创建备份（如果启用了 `auto_backup`）

**示例**:
```python
# 清空所有配置
config.clear()

# 验证
assert config.keys() == []
assert config.read() == {}
```

---

### merge()

合并字典数据。

```python
def merge(other: Dict[str, Any], overwrite: bool = True) -> None
```

**参数**:

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| other | `Dict[str, Any]` | 必需 | 要合并的字典 |
| overwrite | `bool` | `True` | 是否覆盖已存在的键 |

**返回值**: `None`

**说明**:
- `overwrite=True`: 新值覆盖旧值
- `overwrite=False`: 只添加不存在的键

**示例**:
```python
# 覆盖模式（默认）
config.merge({
    'host': 'new-host',  # 覆盖
    'port': 3306,        # 覆盖
    'timeout': 30        # 新增
}, overwrite=True)

# 保留模式
config.merge({
    'host': 'fallback-host',  # 不覆盖
    'timeout': 60             # 只在不存在时添加
}, overwrite=False)

# 合并默认配置
defaults = {
    'host': 'localhost',
    'port': 8000,
    'debug': False,
    'timeout': 30
}
config.merge(defaults, overwrite=False)
```

---

## ListJSONStore

列表型JSON存储器，专门处理列表数据。继承所有 `JSONStore` 的方法。

### 构造函数

```python
ListJSONStore(
    file_path: Union[str, Path],
    **kwargs  # 与 JSONStore 相同的参数
)
```

**示例**:
```python
from kernel.storage import ListJSONStore

tasks = ListJSONStore('tasks.json')
tasks = ListJSONStore('tasks.json', auto_backup=True)
```

---

### append()

在列表末尾追加项目。

```python
def append(item: Any) -> None
```

**参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| item | `Any` | 要追加的项目（可JSON序列化） |

**返回值**: `None`

**说明**:
- 如果文件中的数据不是列表，会被替换为列表

**示例**:
```python
# 追加简单值
tasks.append('学习Python')
tasks.append('写代码')

# 追加字典
tasks.append({
    'id': 1,
    'title': '完成项目',
    'done': False
})

# 追加列表
tasks.append(['步骤1', '步骤2', '步骤3'])
```

---

### extend()

扩展列表（批量添加）。

```python
def extend(items: List[Any]) -> None
```

**参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| items | `List[Any]` | 要添加的项目列表 |

**返回值**: `None`

**示例**:
```python
# 批量添加
new_tasks = [
    {'id': 1, 'title': '任务1'},
    {'id': 2, 'title': '任务2'},
    {'id': 3, 'title': '任务3'}
]
tasks.extend(new_tasks)

# 比多次append高效
# ❌ 不推荐
for task in new_tasks:
    tasks.append(task)  # 多次写入

# ✅ 推荐
tasks.extend(new_tasks)  # 一次写入
```

---

### remove()

移除列表中的项目（按值）。

```python
def remove(item: Any) -> bool
```

**参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| item | `Any` | 要移除的项目 |

**返回值**: `bool` - 始终返回 `True`

**说明**:
- 只移除第一个匹配的项目
- 如果项目不存在，不会报错

**示例**:
```python
# 移除简单值
tasks.remove('学习Python')

# 移除字典（需要完全匹配）
tasks.remove({'id': 1, 'title': '任务1'})

# 项目不存在也安全
tasks.remove('不存在的任务')  # 不会报错
```

---

### remove_at()

移除指定索引的项目。

```python
def remove_at(index: int) -> Any
```

**参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| index | `int` | 索引位置（0开始） |

**返回值**: `Any` - 被移除的项目，索引无效返回 `None`

**示例**:
```python
# 移除第一个项目
first = tasks.remove_at(0)

# 移除最后一个项目
last = tasks.remove_at(tasks.length() - 1)

# 使用负数索引需要自己处理
# tasks.remove_at(-1)  # 不支持负数索引

# 安全移除
if tasks.length() > 0:
    tasks.remove_at(0)
```

---

### get_at()

获取指定索引的项目。

```python
def get_at(index: int, default: Any = None) -> Any
```

**参数**:

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| index | `int` | 必需 | 索引位置（0开始） |
| default | `Any` | `None` | 索引无效时的默认值 |

**返回值**: `Any` - 项目，或默认值

**示例**:
```python
# 获取项目
first = tasks.get_at(0)
second = tasks.get_at(1)

# 使用默认值
item = tasks.get_at(999, default={'title': '默认任务'})

# 安全访问
if tasks.length() > 0:
    first = tasks.get_at(0)
```

---

### length()

获取列表长度。

```python
def length() -> int
```

**返回值**: `int` - 列表长度，数据不是列表返回 `0`

**示例**:
```python
# 获取长度
count = tasks.length()
print(f"共有 {count} 个任务")

# 检查是否为空
if tasks.length() == 0:
    print("列表为空")

# 遍历
for i in range(tasks.length()):
    task = tasks.get_at(i)
    print(f"{i+1}. {task}")
```

---

### clear()

清空列表。

```python
def clear() -> None
```

**返回值**: `None`

**说明**:
- 将数据重置为空列表 `[]`
- 会创建备份（如果启用了 `auto_backup`）

**示例**:
```python
# 清空列表
tasks.clear()

# 验证
assert tasks.length() == 0
assert tasks.read() == []
```

---

### filter()

过滤列表项目。

```python
def filter(filter_func: Callable[[Any], bool]) -> None
```

**参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| filter_func | `Callable[[Any], bool]` | 过滤函数，返回 `True` 保留项目 |

**返回值**: `None`

**说明**:
- 原地修改列表
- 只保留使过滤函数返回 `True` 的项目

**示例**:
```python
# 过滤未完成的任务
tasks.filter(lambda task: not task.get('done', False))

# 过滤特定类型
tasks.filter(lambda task: task.get('type') == 'urgent')

# 过滤数值范围
numbers = ListJSONStore('numbers.json')
numbers.filter(lambda n: 0 <= n <= 100)

# 复杂过滤
def is_valid_task(task):
    return (
        isinstance(task, dict) and
        'id' in task and
        'title' in task and
        len(task['title']) > 0
    )

tasks.filter(is_valid_task)
```

---

## LogStore

日志存储器，专门用于存储日志记录，支持自动轮转和时间范围查询。

### 构造函数

```python
LogStore(
    directory: Union[str, Path],
    prefix: str = "log",
    max_entries_per_file: int = 1000,
    auto_rotate: bool = True
)
```

**参数**:

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| directory | `str \| Path` | 必需 | 日志文件存储目录 |
| prefix | `str` | `"log"` | 日志文件名前缀 |
| max_entries_per_file | `int` | `1000` | 每个文件最大日志条目数 |
| auto_rotate | `bool` | `True` | 是否自动轮转 |

**说明**:
- 日志文件格式: `{prefix}_{YYYYMMDD}.json`
- 达到最大条目数时自动轮转: `{prefix}_{YYYYMMDD_HHMMSS}.json`

**示例**:
```python
from kernel.storage import LogStore

# 基本使用
logger = LogStore(directory='logs')

# 完整配置
app_logger = LogStore(
    directory='logs/app',
    prefix='app',
    max_entries_per_file=5000,
    auto_rotate=True
)

# 不同类型的日志
access_logger = LogStore(directory='logs', prefix='access')
error_logger = LogStore(directory='logs', prefix='error')
```

---

### add_log()

添加日志条目。

```python
def add_log(log_entry: Dict[str, Any]) -> None
```

**参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| log_entry | `Dict[str, Any]` | 日志条目（字典格式） |

**返回值**: `None`

**说明**:
- 如果日志中没有 `timestamp` 字段，会自动添加当前时间
- 自动处理文件轮转

**示例**:
```python
# 基本日志
logger.add_log({
    'level': 'INFO',
    'message': '应用启动'
})

# 完整日志
logger.add_log({
    'level': 'ERROR',
    'message': '数据库连接失败',
    'error': 'Connection timeout',
    'retry_count': 3,
    'user': 'admin'
})

# 自定义时间戳
from datetime import datetime
logger.add_log({
    'timestamp': datetime.now().isoformat(),
    'level': 'DEBUG',
    'message': '调试信息'
})

# 结构化日志
logger.add_log({
    'level': 'INFO',
    'event': 'user_login',
    'user_id': '12345',
    'ip': '192.168.1.1',
    'user_agent': 'Mozilla/5.0'
})
```

---

### get_logs()

查询日志记录。

```python
def get_logs(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    filter_func: Optional[Callable[[Dict], bool]] = None
) -> List[Dict[str, Any]]
```

**参数**:

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| start_date | `datetime \| None` | `None` | 开始时间（包含） |
| end_date | `datetime \| None` | `None` | 结束时间（包含） |
| filter_func | `Callable \| None` | `None` | 自定义过滤函数 |

**返回值**: `List[Dict[str, Any]]` - 日志记录列表

**说明**:
- 所有参数都是可选的
- 时间过滤基于日志中的 `timestamp` 字段
- 会读取所有匹配的日志文件

**示例**:
```python
from datetime import datetime, timedelta

# 获取所有日志
all_logs = logger.get_logs()

# 按时间范围
today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
today_logs = logger.get_logs(start_date=today)

# 最近7天
week_ago = datetime.now() - timedelta(days=7)
recent_logs = logger.get_logs(start_date=week_ago)

# 特定时间段
start = datetime(2026, 1, 1)
end = datetime(2026, 1, 31)
jan_logs = logger.get_logs(start_date=start, end_date=end)

# 使用过滤函数
error_logs = logger.get_logs(
    filter_func=lambda log: log.get('level') == 'ERROR'
)

# 组合条件
critical_recent = logger.get_logs(
    start_date=week_ago,
    filter_func=lambda log: log.get('level') in ['ERROR', 'CRITICAL']
)

# 复杂查询
def is_user_action(log):
    return (
        log.get('user_id') == '12345' and
        log.get('event') in ['login', 'logout', 'update']
    )

user_logs = logger.get_logs(
    start_date=today,
    filter_func=is_user_action
)
```

---

### clear_old_logs()

清理旧日志文件。

```python
def clear_old_logs(days: int = 30) -> int
```

**参数**:

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| days | `int` | `30` | 保留最近N天的日志 |

**返回值**: `int` - 删除的文件数量

**说明**:
- 基于文件的修改时间判断
- 只删除匹配当前prefix的文件

**示例**:
```python
# 清理30天前的日志（默认）
deleted = logger.clear_old_logs()
print(f"删除了 {deleted} 个旧日志文件")

# 只保留最近7天
deleted = logger.clear_old_logs(days=7)

# 清理所有日志（保留当天）
deleted = logger.clear_old_logs(days=0)

# 定期清理（建议在定时任务中执行）
import schedule

def cleanup_logs():
    deleted = logger.clear_old_logs(days=30)
    if deleted > 0:
        print(f"清理了 {deleted} 个旧日志文件")

# 每天凌晨3点清理
schedule.every().day.at("03:00").do(cleanup_logs)
```

---

## 异常类

### JSONStoreError

基础异常类，所有 Storage 异常的父类。

```python
class JSONStoreError(Exception):
    """JSON存储异常基类"""
    pass
```

**用途**: 捕获所有 Storage 相关异常

**示例**:
```python
from kernel.storage import JSONStore, JSONStoreError

store = JSONStore('data.json')

try:
    store.write(data)
except JSONStoreError as e:
    print(f"存储操作失败: {e}")
```

---

### FileNotFoundError

文件不存在异常。

```python
class FileNotFoundError(JSONStoreError):
    """文件不存在异常"""
    pass
```

**触发条件**:
- 读取文件时文件不存在且未提供默认值
- 压缩时源文件不存在
- 解压时压缩文件不存在

**示例**:
```python
from kernel.storage import JSONStore, FileNotFoundError

store = JSONStore('data.json', auto_create=False)

try:
    data = store.read()
except FileNotFoundError:
    print("文件不存在，创建默认数据")
    store.write({'initialized': True})
```

---

### ValidationError

数据验证异常。

```python
class ValidationError(JSONStoreError):
    """数据验证异常"""
    pass
```

**触发条件**:
- 写入数据时验证函数返回 `False`
- 数据不符合预期格式

**示例**:
```python
from kernel.storage import DictJSONStore, ValidationError

def validate(data):
    return isinstance(data, dict) and 'required_field' in data

store = DictJSONStore('config.json', validate_func=validate)

try:
    store.write({'invalid': 'data'})
except ValidationError:
    print("数据验证失败")
    store.write({'required_field': 'value'})
```

---

## 完整示例

### 配置管理系统

```python
from kernel.storage import DictJSONStore, ValidationError

class ConfigManager:
    def __init__(self, config_file='config.json'):
        def validate(data):
            required = ['app_name', 'version']
            return isinstance(data, dict) and all(k in data for k in required)
        
        self.store = DictJSONStore(
            config_file,
            auto_backup=True,
            max_backups=10,
            validate_func=validate
        )
        self._ensure_defaults()
    
    def _ensure_defaults(self):
        if not self.store.exists():
            self.store.write({
                'app_name': 'MoFox',
                'version': '1.0.0',
                'debug': False,
                'port': 8000
            })
    
    def get(self, key, default=None):
        return self.store.get(key, default)
    
    def set(self, key, value):
        self.store.set(key, value)
    
    def update_multiple(self, updates):
        self.store.merge(updates, overwrite=True)
    
    def reset(self):
        self._ensure_defaults()

# 使用
config = ConfigManager()
print(f"App: {config.get('app_name')}")
config.set('debug', True)
config.update_multiple({'port': 3000, 'host': 'localhost'})
```

### 任务队列系统

```python
from kernel.storage import ListJSONStore
from datetime import datetime
import uuid

class TaskQueue:
    def __init__(self, queue_file='tasks.json'):
        self.store = ListJSONStore(queue_file, auto_backup=True)
    
    def add(self, task_type, data):
        task = {
            'id': str(uuid.uuid4()),
            'type': task_type,
            'data': data,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        self.store.append(task)
        return task['id']
    
    def get_pending(self):
        tasks = self.store.read(default=[])
        return [t for t in tasks if t.get('status') == 'pending']
    
    def mark_done(self, task_id):
        def update(tasks):
            for task in tasks:
                if task.get('id') == task_id:
                    task['status'] = 'completed'
                    task['completed_at'] = datetime.now().isoformat()
            return tasks
        self.store.update(update)
    
    def clear_completed(self):
        self.store.filter(lambda t: t.get('status') != 'completed')

# 使用
queue = TaskQueue()
task_id = queue.add('email', {'to': 'user@example.com', 'subject': 'Hello'})
pending = queue.get_pending()
queue.mark_done(task_id)
queue.clear_completed()
```

### 日志审计系统

```python
from kernel.storage import LogStore
from datetime import datetime, timedelta

class AuditLogger:
    def __init__(self, log_dir='audit_logs'):
        self.store = LogStore(
            directory=log_dir,
            prefix='audit',
            max_entries_per_file=5000,
            auto_rotate=True
        )
    
    def log(self, action, resource, user_id, details=None):
        self.store.add_log({
            'action': action,
            'resource': resource,
            'user_id': user_id,
            'details': details
        })
    
    def get_user_activity(self, user_id, days=7):
        start = datetime.now() - timedelta(days=days)
        return self.store.get_logs(
            start_date=start,
            filter_func=lambda log: log.get('user_id') == user_id
        )
    
    def get_security_events(self):
        critical = ['login_failed', 'permission_denied', 'data_deleted']
        return self.store.get_logs(
            filter_func=lambda log: log.get('action') in critical
        )
    
    def cleanup(self, days=90):
        return self.store.clear_old_logs(days)

# 使用
audit = AuditLogger()
audit.log('login', '/api/auth', 'user_001')
audit.log('update', '/api/users/profile', 'user_001', {'field': 'email'})
activity = audit.get_user_activity('user_001')
security_events = audit.get_security_events()
audit.cleanup(days=90)
```

---

## 类型注解参考

```python
from typing import Any, Callable, Dict, List, Optional, Union
from pathlib import Path
from datetime import datetime

# 构造函数类型
FilePath = Union[str, Path]
ValidateFunc = Optional[Callable[[Any], bool]]
UpdateFunc = Callable[[Any], Any]
FilterFunc = Callable[[Any], bool]
LogFilterFunc = Callable[[Dict[str, Any]], bool]

# 返回类型
JsonData = Any  # 任何可JSON序列化的数据
DictData = Dict[str, Any]
ListData = List[Any]
LogEntry = Dict[str, Any]
```

---

## 下一步

- 查看 [配置指南](./CONFIGURATION_GUIDE.md) 了解详细配置
- 查看 [最佳实践](./BEST_PRACTICES.md) 学习使用模式
- 查看 [故障排查](./TROUBLESHOOTING.md) 解决常见问题
