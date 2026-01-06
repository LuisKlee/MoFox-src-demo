# 数据库模块文档索引（Database Module Documentation Index）

欢迎使用 MoFox 数据库内核模块！本页面为您快速定位所需的文档。

## 🗺️ 文档导航地图

```
docs/kernel/db/
├── INDEX.md .......................... 📍 你在这里
├── README.md ......................... 📌 开始这里（全面概览 + 快速开始）
├── QUICK_REFERENCE.md ............... ⚡ 速查表（常用代码片段）
├── DATABASE_GUIDE.md ................ 🎯 数据库选择与配置指南
├── CACHE_GUIDE.md ................... 💾 缓存系统完整指南
└── OPTIMIZATION_GUIDE.md ............ 🚀 性能优化与架构设计
```

---

## 📚 文档概览

### 1️⃣ [README.md](README.md) - 数据库模块总览

**适合场景：** 第一次使用 | 想了解全貌 | 需要快速开始

**包含内容：**
- ✅ 核心特性介绍
- ✅ 5 个数据库快速开始示例（SQLite、MySQL、PostgreSQL、Redis、MongoDB）
- ✅ 核心组件说明（EngineManager、SessionManager、Repository、QuerySpec）
- ✅ 缓存系统介绍
- ✅ API 参考（所有 Repository 的方法）
- ✅ 生产环境配置示例
- ✅ 最佳实践
- ✅ 常见问题 FAQ

**快速链接：**
- [快速开始](#快速开始) - 5 种数据库使用示例
- [核心组件](#核心组件) - 系统架构
- [最佳实践](#最佳实践) - 推荐做法

---

### 2️⃣ [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 快速参考卡

**适合场景：** 需要复制代码 | 想不起命令 | 快速查询

**包含内容：**
- ✅ 数据库选择速查表
- ✅ 常见代码模式（CRUD、批量、分页、缓存）
- ✅ 配置参数表
- ✅ 性能参考数据
- ✅ 常见错误与修复
- ✅ 学习路径（初级→中级→高级）
- ✅ 实战代码示例
- ✅ 常见问题速答

**快速链接：**
- [核心概念速查表](#🎯-核心概念速查表) - 数据库对比
- [常见模式](#🚀-常见模式) - 代码片段
- [配置参数](#🔧-配置参数) - 参数说明

**💡 提示：** 遇到问题时先查这个文件！

---

### 3️⃣ [DATABASE_GUIDE.md](DATABASE_GUIDE.md) - 数据库选择与配置

**适合场景：** 选择数据库 | 部署到生产 | 性能调优 | 故障排除

**包含内容：**
- ✅ 5 个数据库的详细对比分析
  - SQLite - 本地开发
  - MySQL - 成熟生产
  - PostgreSQL - 高性能方案
  - Redis - 缓存数据库
  - MongoDB - 文档数据库
- ✅ 每个数据库的优劣分析
- ✅ 适用场景说明
- ✅ 完整配置示例（含高可用）
- ✅ Docker Compose 一键启动
- ✅ 环境变量配置方案
- ✅ 性能基准测试数据
- ✅ 常见问题与故障排除
- ✅ 迁移指南（SQLite→MySQL→PostgreSQL）

**快速链接：**
- [数据库对比](#概览表) - 一目了然的对比表
- [快速启动](#docker-compose-快速启动) - Docker 配置
- [故障排除](#故障排除) - 问题解决

**使用场景举例：**
```
Q: MySQL 连接被拒绝怎么办？
A: 见 [MySQL 常见问题](#mysql-常见问题)

Q: 想把 SQLite 升级到 MySQL？
A: 见 [迁移指南](#迁移指南)
```

---

### 4️⃣ [CACHE_GUIDE.md](CACHE_GUIDE.md) - 缓存系统完整指南

**适合场景：** 使用缓存 | 提升性能 | 理解缓存机制

**包含内容：**
- ✅ 缓存系统概述
- ✅ LocalCache 本地缓存
  - 内存存储 + LRU 自动清理
  - TTL 支持 + 线程安全
- ✅ RedisCache 分布式缓存
  - 多进程共享 + 自动序列化
  - Pipeline 优化 + 过期管理
- ✅ CacheManager 统一管理
  - @cached 装饰器用法
  - 自定义 key_builder
  - 函数结果自动缓存
- ✅ 实战应用场景
  - LLM 响应缓存
  - 数据库查询缓存
  - 配置缓存
  - 用户信息缓存
- ✅ 多级缓存架构
- ✅ 缓存穿透/击穿/雪崩解决方案
- ✅ 缓存预热策略

**快速链接：**
- [LocalCache 使用](#localcache-本地缓存) - 本地方案
- [RedisCache 使用](#rediscache-分布式缓存) - 分布式方案
- [@cached 装饰器](#cached-装饰器) - 最简单的用法
- [实战应用](#实战应用场景) - 真实例子

**最常用的代码：**
```python
# 最简单的缓存方式
@cache_mgr.cached()
def get_user(user_id):
    return db.get(user_id)
```

---

### 5️⃣ [OPTIMIZATION_GUIDE.md](OPTIMIZATION_GUIDE.md) - 优化与架构

**适合场景：** 性能优化 | 高可用设计 | 生产部署 | 架构设计

**包含内容：**
- ✅ 系统架构详解
  - 分层架构图
  - 多数据库选择矩阵
- ✅ 连接池优化
  - 参数计算公式
  - 连接池监控
  - 自动诊断
- ✅ 查询优化
  - QuerySpec 分页
  - 索引优化
  - MongoDB 聚合优化
  - Redis 批量操作
- ✅ 缓存策略
  - 多级缓存实现
  - 缓存穿透保护
  - 缓存击穿保护
  - 缓存雪崩保护
  - 缓存预热
- ✅ 事务管理
  - 基础事务
  - 嵌套事务与保存点
  - 分布式事务
- ✅ 监控与诊断
  - 查询性能监控
  - 连接池健康检查
  - Redis 性能监控
- ✅ 高可用设计
  - MySQL/PostgreSQL 主从复制
  - MongoDB 副本集
  - Redis Sentinel
  - 自动故障转移

**快速链接：**
- [连接池优化](#连接池优化) - 性能关键
- [查询优化](#查询优化) - 常用技巧
- [缓存策略](#缓存策略) - 完整方案
- [高可用设计](#高可用设计) - 生产必读

**生产部署必读章节：**
- [连接池优化](#连接池参数调优)
- [监控与诊断](#监控与诊断)
- [高可用设计](#高可用设计)

---

## 🎯 快速查找

### 我想...

#### 快速开始使用
1. 先读 [README.md - 快速开始](#快速开始) - 5 分钟
2. 再看 [QUICK_REFERENCE.md - 常见模式](#🚀-常见模式) - 参考代码

#### 选择合适的数据库
1. 查看 [QUICK_REFERENCE.md - 数据库选择速查](#数据库选择速查) - 1 分钟
2. 详细了解 [DATABASE_GUIDE.md](#数据库对比) - 10 分钟
3. 对比特定数据库 [DATABASE_GUIDE.md](#详细对比) - 5 分钟

#### 添加缓存层
1. 看 [QUICK_REFERENCE.md - 缓存操作](#6-缓存操作) - 2 分钟
2. 学习 [CACHE_GUIDE.md](#缓存系统概述) - 15 分钟
3. 查看实战例子 [CACHE_GUIDE.md - 实战应用](#实战应用场景) - 10 分钟

#### 优化性能
1. 看 [QUICK_REFERENCE.md - 性能参考](#📊-性能参考) - 1 分钟
2. 学习 [OPTIMIZATION_GUIDE.md - 查询优化](#查询优化) - 20 分钟
3. 实施 [OPTIMIZATION_GUIDE.md - 缓存策略](#缓存策略) - 30 分钟

#### 部署到生产
1. 阅读 [DATABASE_GUIDE.md - 环境配置](#环境配置) - 15 分钟
2. 学习 [OPTIMIZATION_GUIDE.md - 高可用设计](#高可用设计) - 30 分钟
3. 设置 [OPTIMIZATION_GUIDE.md - 监控与诊断](#监控与诊断) - 20 分钟

#### 解决问题
1. 查 [QUICK_REFERENCE.md - 常见错误](#⚠️-常见错误) - 3 分钟
2. 见 [DATABASE_GUIDE.md - 故障排除](#故障排除) - 5-10 分钟
3. 查看对应数据库的常见问题

---

## 📊 学习路径建议

### 🌱 初级（1-2天）

```
Day 1:
├─ 10分钟 : 阅读 README.md 概览
├─ 20分钟 : SQLite 快速开始（README.md）
├─ 15分钟 : 基础 CRUD（QUICK_REFERENCE.md）
└─ 15分钟 : 简单缓存使用（CACHE_GUIDE.md）

Day 2:
├─ 20分钟 : 学习 QuerySpec 和分页
├─ 20分钟 : MySQL 基础配置
└─ 20分钟 : LocalCache 使用
```

**成果：** 能开发简单应用，数据持久化，基础缓存

---

### 🎯 中级（3-7天）

```
Day 3:
├─ 30分钟 : DATABASE_GUIDE.md 全读
├─ 30分钟 : PostgreSQL vs MySQL 对比
└─ 30分钟 : Docker 环境搭建

Day 4:
├─ 30分钟 : 完整的 CACHE_GUIDE.md
├─ 30分钟 : RedisCache 分布式缓存
└─ 30分钟 : @cached 装饰器实战

Day 5:
├─ 30分钟 : OPTIMIZATION_GUIDE.md 前半部分
├─ 30分钟 : 连接池优化
└─ 30分钟 : 查询优化技巧

Day 6-7:
├─ 40分钟 : 多级缓存架构
├─ 40分钟 : 缓存穿透/击穿/雪崩
└─ 40分钟 : 事务管理
```

**成果：** 能设计中等规模应用，多数据库协作，多级缓存

---

### 🚀 高级（1-2周）

```
Week 2:
├─ OPTIMIZATION_GUIDE.md 全部
├─ 高可用设计（主从、副本集、Sentinel）
├─ 监控与诊断系统
├─ 性能测试与基准
└─ 生产部署最佳实践
```

**成果：** 能设计高并发应用，完整的监控，高可用架构

---

## 🔍 如何有效使用这些文档

### 最佳实践 ✨

1. **第一次使用：** 按顺序读 README → QUICK_REFERENCE
2. **需要代码：** 直接跳到 QUICK_REFERENCE 复制粘贴
3. **深入学习：** 根据主题选择对应文档
4. **遇到问题：** 先看 QUICK_REFERENCE 的常见错误
5. **生产部署：** 必读 OPTIMIZATION_GUIDE 的高可用设计和监控部分

### 阅读建议 📖

- **碎片化阅读：** 用 QUICK_REFERENCE 的速查表
- **系统学习：** 按主题阅读完整指南
- **参考查询：** 用目录快速定位

### 文档快捷键 ⌨️

在各文档中使用 Ctrl+F（或 Cmd+F）快速搜索：

```
搜索                    找到位置
─────────────────────────────────────
"池大小应该多大"      QUICK_REFERENCE 的 FAQ
"我想加快查询"        OPTIMIZATION_GUIDE 的查询优化
"MySQL 连接失败"      DATABASE_GUIDE 的故障排除
"如何缓存 LLM"        CACHE_GUIDE 的实战应用
"主从复制"            OPTIMIZATION_GUIDE 的高可用
```

---

## 📋 文档检查清单

### 新手入门清单 ✅

- [ ] 阅读 README.md（10 分钟）
- [ ] 选择数据库并做快速开始（20 分钟）
- [ ] 学习 CRUD 基础操作（15 分钟）
- [ ] 尝试第一个缓存（15 分钟）

### 生产部署清单 ✅

- [ ] 选择合适的数据库组合
- [ ] 阅读 OPTIMIZATION_GUIDE.md 的高可用设计
- [ ] 设置 OPTIMIZATION_GUIDE.md 的监控与诊断
- [ ] 配置 DATABASE_GUIDE.md 的环境变量
- [ ] 进行性能基准测试
- [ ] 制定缓存策略

---

## 🤝 获取帮助

### 文档查不到的问题？

1. **搜索关键词** - 在各文档中 Ctrl+F 搜索
2. **看常见问题** - QUICK_REFERENCE.md FAQ 部分
3. **查故障排除** - DATABASE_GUIDE.md 故障排除部分
4. **查源代码** - src/kernel/db/ 中的代码注释（中英文）

### 反馈与改进

如果发现文档错误或不清楚的地方，欢迎提交 Issue 或 PR！

---

## 📈 文档版本

| 版本 | 日期 | 主要更新 |
|------|------|---------|
| 1.0 | 2026年 | 初始发布，包含 5 个完整指南 |

---

## 🎓 相关资源

### 官方文档
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [PyMongo](https://pymongo.readthedocs.io/)
- [redis-py](https://redis-py.readthedocs.io/)
- [psycopg2](https://www.psycopg.org/psycopg2/)

### 数据库官方
- [MySQL](https://dev.mysql.com/)
- [PostgreSQL](https://www.postgresql.org/docs/)
- [MongoDB](https://docs.mongodb.com/)
- [Redis](https://redis.io/documentation/)

---

## 🚀 开始使用

**现在就开始！选择一个链接：**

👉 [📌 READ ME FIRST - 全面概览与快速开始](README.md)

👉 [⚡ 或直接看速查表 - 常用代码片段](QUICK_REFERENCE.md)

---

**Happy Coding! 🎉**

