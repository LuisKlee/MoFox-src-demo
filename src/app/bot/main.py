"""
MoFox Bot 启动器

这是 MoFox Bot 的主入口文件，负责初始化和启动应用。

作者: MoFox Team
日期: 2026-01-11
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional
import argparse

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.bot.core_api.core_api import MoFoxCore, get_core
from app.bot.kernel_api_legacy.kernel_api import MoFoxKernel


class MoFoxBot:
    """
    MoFox Bot 主应用类
    
    整合 Core 层和 Kernel 层功能，提供完整的 Bot 应用。
    """
    
    def __init__(
        self,
        app_name: str = "mofox_bot",
        config_path: Optional[str] = None,
        use_core: bool = True,
        use_kernel: bool = True,
    ):
        """
        初始化 MoFox Bot
        
        Args:
            app_name: 应用名称
            config_path: 配置文件路径
            use_core: 是否使用 Core 层
            use_kernel: 是否使用 Kernel 层
        """
        self.app_name = app_name
        self.config_path = config_path
        self.use_core = use_core
        self.use_kernel = use_kernel
        
        self.core: Optional[MoFoxCore] = None
        self.kernel: Optional[MoFoxKernel] = None
        
        self._running = False
    
    async def initialize(self):
        """初始化 Bot"""
        print(f"🚀 正在初始化 {self.app_name}...")
        
        try:
            # 初始化 Core 层
            if self.use_core:
                print("📦 初始化 Core 层...")
                self.core = MoFoxCore(app_name=self.app_name)
                await self.core.initialize()
                print("✅ Core 层初始化完成")
            
            # 初始化 Kernel 层
            if self.use_kernel:
                print("📦 初始化 Kernel 层...")
                self.kernel = MoFoxKernel(
                    app_name=self.app_name,
                    config_path=self.config_path,
                )
                await self.kernel.initialize()
                print("✅ Kernel 层初始化完成")
            
            print(f"✨ {self.app_name} 初始化成功！\n")
            
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            raise
    
    async def run(self):
        """运行 Bot 主循环"""
        self._running = True
        print("🤖 Bot 正在运行...")
        print("💡 提示：按 Ctrl+C 退出\n")
        
        try:
            # 这里是主要的业务逻辑
            await self._main_loop()
            
        except KeyboardInterrupt:
            print("\n\n⏸️  收到中断信号，正在停止...")
        except Exception as e:
            print(f"\n❌ 运行时错误: {e}")
            raise
        finally:
            self._running = False
    
    async def _main_loop(self):
        """主业务循环"""
        # 示例：简单的交互循环
        print("欢迎使用 MoFox Bot！")
        print("输入 'quit' 或 'exit' 退出\n")
        
        while self._running:
            try:
                # 在终端获取用户输入（简化版）
                user_input = await asyncio.to_thread(
                    input,
                    "You: "
                )
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not user_input.strip():
                    continue
                
                # 处理用户输入
                response = await self._process_input(user_input)
                print(f"Bot: {response}\n")
                
            except EOFError:
                break
            except Exception as e:
                print(f"❌ 处理错误: {e}\n")
    
    async def _process_input(self, user_input: str) -> str:
        """
        处理用户输入
        
        Args:
            user_input: 用户输入的文本
            
        Returns:
            Bot 的响应
        """
        # 示例处理逻辑
        # 在实际应用中，这里会调用 LLM、数据库等
        
        if self.kernel and hasattr(self.kernel, 'llm'):
            try:
                # 使用 Kernel 层的 LLM 生成响应
                # response = await self.kernel.llm.chat(user_input)
                # return response
                pass
            except Exception as e:
                print(f"⚠️  LLM 调用失败: {e}")
        
        # 默认响应
        return f"收到消息：{user_input}"
    
    async def shutdown(self):
        """关闭 Bot"""
        print("\n🛑 正在关闭 Bot...")
        
        # 关闭 Core 层
        if self.core:
            try:
                await self.core.shutdown()
                print("✅ Core 层已关闭")
            except Exception as e:
                print(f"⚠️  关闭 Core 层时出错: {e}")
        
        # 关闭 Kernel 层
        if self.kernel:
            try:
                await self.kernel.shutdown()
                print("✅ Kernel 层已关闭")
            except Exception as e:
                print(f"⚠️  关闭 Kernel 层时出错: {e}")
        
        print("👋 再见！\n")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.shutdown()


async def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="MoFox Bot 启动器")
    parser.add_argument(
        "--name",
        type=str,
        default="mofox_bot",
        help="应用名称"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="配置文件路径"
    )
    parser.add_argument(
        "--no-core",
        action="store_true",
        help="禁用 Core 层"
    )
    parser.add_argument(
        "--no-kernel",
        action="store_true",
        help="禁用 Kernel 层"
    )
    
    args = parser.parse_args()
    
    # 创建并运行 Bot
    async with MoFoxBot(
        app_name=args.name,
        config_path=args.config,
        use_core=not args.no_core,
        use_kernel=not args.no_kernel,
    ) as bot:
        await bot.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print(f"\n❌ 程序异常退出: {e}")
        sys.exit(1)
