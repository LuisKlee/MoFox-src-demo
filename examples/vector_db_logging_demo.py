"""
向量数据库日志使用示例

演示如何在使用向量数据库时查看和利用日志信息
"""
import asyncio
from kernel.vector_db import create_vector_db_async, VectorDocument
from kernel.logger import setup_logger, LoggerConfig


async def main():
    # 1. 配置日志系统
    config = LoggerConfig(
        name="vector_db_example",
        level="DEBUG",  # 设置为 DEBUG 级别以查看详细日志
        console_enabled=True,
        console_colors=True,
        file_enabled=True,
        file_path="logs/vector_db.log",
        file_format="json"  # 使用 JSON 格式便于分析
    )
    setup_logger(config)
    
    print("=" * 60)
    print("向量数据库日志集成示例")
    print("=" * 60)
    print()
    
    # 2. 创建向量数据库实例（会记录初始化日志）
    print("📦 创建向量数据库实例...")
    db = await create_vector_db_async(
        db_type='chromadb',
        config={
            'client_type': 'persistent',
            'persist_directory': './data/chroma_logs_demo'
        }
    )
    print("✓ 数据库实例创建成功\n")
    
    try:
        # 3. 创建集合（会记录日志）
        print("📁 创建集合...")
        collection_name = 'demo_articles'
        if not await db.collection_exists(collection_name):
            await db.create_collection(collection_name)
            print(f"✓ 集合 '{collection_name}' 创建成功\n")
        else:
            print(f"ℹ 集合 '{collection_name}' 已存在\n")
        
        # 4. 添加文档（会记录日志）
        print("📝 添加文档...")
        documents = [
            VectorDocument(
                id='article_1',
                content='人工智能是计算机科学的一个分支',
                vector=[0.1, 0.2, 0.3, 0.4, 0.5],
                metadata={
                    'category': 'AI',
                    'author': 'Zhang San',
                    'date': '2026-01-06'
                }
            ),
            VectorDocument(
                id='article_2',
                content='机器学习是人工智能的核心技术',
                vector=[0.15, 0.25, 0.35, 0.45, 0.55],
                metadata={
                    'category': 'ML',
                    'author': 'Li Si',
                    'date': '2026-01-05'
                }
            ),
            VectorDocument(
                id='article_3',
                content='深度学习在图像识别中应用广泛',
                vector=[0.2, 0.3, 0.4, 0.5, 0.6],
                metadata={
                    'category': 'DL',
                    'author': 'Wang Wu',
                    'date': '2026-01-04'
                }
            )
        ]
        
        await db.add_documents(collection_name, documents)
        print(f"✓ 成功添加 {len(documents)} 个文档\n")
        
        # 5. 查询文档（会记录日志）
        print("🔍 查询相似文档...")
        query_vector = [0.18, 0.28, 0.38, 0.48, 0.58]
        results = await db.query_similar(
            collection_name=collection_name,
            query_vector=query_vector,
            top_k=3
        )
        
        print(f"✓ 查询返回 {len(results)} 个结果:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. ID: {result.id}")
            print(f"     相似度: {result.score:.4f}")
            print(f"     内容: {result.content}")
            print(f"     作者: {result.metadata.get('author')}")
            print()
        
        # 6. 批量查询（会记录日志）
        print("🔍 批量查询...")
        query_vectors = [
            [0.12, 0.22, 0.32, 0.42, 0.52],
            [0.18, 0.28, 0.38, 0.48, 0.58]
        ]
        batch_results = await db.batch_query_similar(
            collection_name=collection_name,
            query_vectors=query_vectors,
            top_k=2
        )
        print(f"✓ 批量查询完成，{len(batch_results)} 个查询")
        for i, results in enumerate(batch_results, 1):
            print(f"  查询 {i}: {len(results)} 个结果")
        print()
        
        # 7. 统计文档（会记录日志）
        print("📊 统计文档数量...")
        count = await db.count_documents(collection_name)
        print(f"✓ 集合 '{collection_name}' 共有 {count} 个文档\n")
        
        # 8. 更新文档（会记录日志）
        print("✏️ 更新文档...")
        updated_doc = VectorDocument(
            id='article_1',
            content='人工智能是计算机科学的重要分支',
            vector=[0.11, 0.21, 0.31, 0.41, 0.51],
            metadata={
                'category': 'AI',
                'author': 'Zhang San',
                'date': '2026-01-06',
                'updated': True
            }
        )
        await db.update_documents(collection_name, [updated_doc])
        print("✓ 文档更新成功\n")
        
        # 9. 健康检查（会记录日志）
        print("🏥 执行健康检查...")
        is_healthy = await db.health_check()
        print(f"✓ 数据库健康状态: {'正常' if is_healthy else '异常'}\n")
        
        # 10. 获取集合信息
        print("📋 获取集合信息...")
        info = await db.get_collection_info(collection_name)
        if info:
            print(f"  集合名称: {info.name}")
            print(f"  文档数量: {info.count}")
            print(f"  向量维度: {info.dimension}")
        print()
        
        # 11. 删除文档（会记录日志）
        print("🗑️ 删除文档...")
        await db.delete_documents(collection_name, ['article_3'])
        print("✓ 文档删除成功\n")
        
        # 验证删除
        remaining_count = await db.count_documents(collection_name)
        print(f"ℹ 删除后剩余文档数: {remaining_count}\n")
        
        print("=" * 60)
        print("✓ 示例执行完成")
        print("=" * 60)
        print()
        print("📄 查看日志文件以获取详细信息:")
        print("   - 控制台：彩色日志输出")
        print("   - 文件：logs/vector_db.log (JSON格式)")
        print()
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 12. 关闭数据库（会记录日志）
        print("\n🔒 关闭数据库连接...")
        await db.close()
        print("✓ 数据库已关闭")


if __name__ == '__main__':
    asyncio.run(main())
