"""
向量数据库日志集成测试
"""
import pytest
import asyncio
from kernel.vector_db import create_vector_db_async, VectorDocument
from kernel.logger import setup_logger, get_logger


@pytest.fixture
def setup_test_logger():
    """设置测试日志"""
    setup_logger()
    yield
    

@pytest.mark.asyncio
async def test_vector_db_with_logging(setup_test_logger, tmp_path):
    """测试向量数据库的日志记录"""
    
    # 创建数据库实例（会记录初始化日志）
    db = await create_vector_db_async(
        db_type='chromadb',
        config={
            'client_type': 'ephemeral'  # 使用内存模式进行测试
        }
    )
    
    try:
        # 创建集合（会记录日志）
        await db.create_collection('test_collection')
        
        # 添加文档（会记录日志）
        documents = [
            VectorDocument(
                id='doc1',
                content='测试文档1',
                vector=[0.1, 0.2, 0.3],
                metadata={'category': 'test'}
            ),
            VectorDocument(
                id='doc2',
                content='测试文档2',
                vector=[0.2, 0.3, 0.4],
                metadata={'category': 'test'}
            )
        ]
        await db.add_documents('test_collection', documents)
        
        # 查询（会记录日志）
        results = await db.query_similar(
            collection_name='test_collection',
            query_vector=[0.15, 0.25, 0.35],
            top_k=2
        )
        
        assert len(results) > 0
        
        # 健康检查（会记录日志）
        is_healthy = await db.health_check()
        assert is_healthy
        
        # 删除文档（会记录日志）
        await db.delete_documents('test_collection', ['doc1'])
        
        # 删除集合（会记录日志）
        await db.delete_collection('test_collection')
        
    finally:
        # 关闭数据库（会记录日志）
        await db.close()


@pytest.mark.asyncio
async def test_vector_db_error_logging(setup_test_logger):
    """测试向量数据库的错误日志记录"""
    
    db = await create_vector_db_async(
        db_type='chromadb',
        config={'client_type': 'ephemeral'}
    )
    
    try:
        # 尝试查询不存在的集合（会记录错误日志）
        with pytest.raises(Exception):
            await db.query_similar(
                collection_name='non_existent_collection',
                query_vector=[0.1, 0.2, 0.3],
                top_k=5
            )
    finally:
        await db.close()


if __name__ == '__main__':
    # 运行测试
    pytest.main([__file__, '-v', '-s'])
