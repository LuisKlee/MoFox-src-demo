# MoFox Application Layer Documentation

应用层（App Layer）文档目录

## 📚 目录结构

```
app/
├── README.md                    # 本文件
├── bot/
│   ├── BOT_ARCHITECTURE.md     # Bot 架构设计
│   ├── API_GUIDE.md            # API 使用指南
│   ├── LAUNCHER_GUIDE.md       # 启动器使用指南
│   ├── DEVELOPMENT_GUIDE.md    # 开发指南
│   └── DEPLOYMENT_GUIDE.md     # 部署指南
└── monitors/                    # 监控系统文档（待补充）
```

## 📖 文档索引

### Bot 相关文档

#### 1. [Bot 架构设计](bot/BOT_ARCHITECTURE.md)
- 系统架构概述
- 分层设计说明
- 组件交互关系
- 数据流图

#### 2. [API 使用指南](bot/API_GUIDE.md)
- Core API 详细说明
- Kernel API 详细说明
- API 最佳实践
- 常见使用场景

#### 3. [启动器使用指南](bot/LAUNCHER_GUIDE.md)
- 启动器功能说明
- 命令行参数详解
- 配置文件说明
- 启动流程详解

#### 4. [开发指南](bot/DEVELOPMENT_GUIDE.md)
- 开发环境搭建
- 自定义 Bot 开发
- 扩展功能开发
- 调试技巧

#### 5. [部署指南](bot/DEPLOYMENT_GUIDE.md)
- 生产环境部署
- 容器化部署
- 性能优化
- 监控告警

## 🚀 快速开始

### 最简单的启动方式

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动 Bot
python start.py
```

### 阅读顺序建议

1. **初学者**: 架构设计 → 启动器使用 → API 使用
2. **开发者**: API 使用 → 开发指南 → 架构设计
3. **运维人员**: 启动器使用 → 部署指南

## 📋 版本信息

- 文档版本: v0.1.0
- 更新日期: 2026-01-11
- MoFox 版本: v0.1.0

## 🤝 贡献

欢迎完善文档！请参考项目的 [贡献指南](../../CONTRIBUTING.md)。

