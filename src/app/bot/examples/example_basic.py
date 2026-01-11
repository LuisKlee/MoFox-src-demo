"""
基本使用示例

演示 MoFox Bot 的基本使用方法
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from app.bot.main import MoFoxBot


async def example_basic():
    """基本使用示例"""
    print("=" * 60)
    print("  示例 1: 基本使用")
    print("=" * 60)
    
    # 使用上下文管理器
    async with MoFoxBot(app_name="basic_bot") as bot:
        # 处理几条消息
        messages = [
            "你好",
            "今天天气怎么样？",
            "谢谢"
        ]
        
        for msg in messages:
            print(f"\nUser: {msg}")
            response = await bot._process_input(msg)
            print(f"Bot: {response}")


async def example_manual():
    """手动初始化和关闭示例"""
    print("\n" + "=" * 60)
    print("  示例 2: 手动管理生命周期")
    print("=" * 60)
    
    bot = MoFoxBot(app_name="manual_bot")
    
    try:
        # 手动初始化
        await bot.initialize()
        
        # 使用 Bot
        response = await bot._process_input("Hello")
        print(f"\nBot: {response}")
        
    finally:
        # 确保关闭
        await bot.shutdown()


async def example_config():
    """使用配置示例"""
    print("\n" + "=" * 60)
    print("  示例 3: 带配置启动")
    print("=" * 60)
    
    # 可以传入配置文件路径
    async with MoFoxBot(
        app_name="config_bot",
        config_path="config.yaml",  # 如果文件存在的话
        use_core=True,
        use_kernel=True
    ) as bot:
        print("\nBot 已启动并配置完成")
        print(f"Core 层状态: {'✅ 已启用' if bot.core else '❌ 未启用'}")
        print(f"Kernel 层状态: {'✅ 已启用' if bot.kernel else '❌ 未启用'}")


async def main():
    """运行所有示例"""
    try:
        # 示例 1: 基本使用
        await example_basic()
        
        # 示例 2: 手动管理
        await example_manual()
        
        # 示例 3: 配置
        await example_config()
        
        print("\n" + "=" * 60)
        print("  所有示例运行完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 示例运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
