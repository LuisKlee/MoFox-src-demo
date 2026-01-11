#!/usr/bin/env python3
"""
快速启动脚本

快速启动 MoFox Bot 的便捷脚本
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# 导入并运行 main
from app.bot.main import main
import asyncio

if __name__ == "__main__":
    print("=" * 60)
    print("  MoFox Bot - Quick Start")
    print("=" * 60)
    asyncio.run(main())
