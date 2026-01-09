"""
inkfox 视频处理模块测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from kernel.llm import (
    VideoKeyframeExtractor,
    extract_keyframes_from_video,
    get_system_info,
    check_inkfox_available,
    INKFOX_AVAILABLE
)


class TestInkfoxAvailability:
    """测试 inkfox 可用性检查"""
    
    def test_check_inkfox_available(self):
        """测试检查 inkfox 可用性"""
        result = check_inkfox_available()
        assert isinstance(result, bool)
        assert result == INKFOX_AVAILABLE
    
    def test_inkfox_available_constant(self):
        """测试 INKFOX_AVAILABLE 常量"""
        assert isinstance(INKFOX_AVAILABLE, bool)


@pytest.mark.skipif(not INKFOX_AVAILABLE, reason="inkfox not available")
class TestVideoKeyframeExtractor:
    """测试 VideoKeyframeExtractor 类"""
    
    def test_init(self):
        """测试初始化"""
        extractor = VideoKeyframeExtractor()
        assert extractor is not None
    
    def test_init_with_params(self):
        """测试带参数初始化"""
        extractor = VideoKeyframeExtractor(
            threads=4,
            verbose=True
        )
        assert extractor is not None
        assert extractor.get_thread_count() > 0
    
    def test_get_cpu_features(self):
        """测试获取 CPU 特性"""
        extractor = VideoKeyframeExtractor()
        features = extractor.get_cpu_features()
        
        assert isinstance(features, dict)
        assert len(features) > 0
        
        # 检查常见的 CPU 特性
        for key, value in features.items():
            assert isinstance(key, str)
            assert isinstance(value, bool)
    
    def test_get_thread_count(self):
        """测试获取线程数"""
        extractor = VideoKeyframeExtractor()
        count = extractor.get_thread_count()
        
        assert isinstance(count, int)
        assert count > 0
    
    @pytest.mark.parametrize("threads", [0, 2, 4, 8])
    def test_different_thread_counts(self, threads):
        """测试不同的线程数配置"""
        extractor = VideoKeyframeExtractor(threads=threads)
        actual_threads = extractor.get_thread_count()
        assert actual_threads > 0
    
    def test_extract_keyframes_missing_file(self):
        """测试提取不存在的视频文件"""
        extractor = VideoKeyframeExtractor()
        
        with pytest.raises(FileNotFoundError):
            extractor.extract_keyframes(
                video_path="nonexistent_video.mp4",
                output_dir="./output",
                max_keyframes=10
            )


@pytest.mark.skipif(not INKFOX_AVAILABLE, reason="inkfox not available")
class TestExtractKeyframesFunction:
    """测试 extract_keyframes_from_video 函数"""
    
    def test_function_missing_file(self):
        """测试提取不存在的视频文件"""
        with pytest.raises((FileNotFoundError, RuntimeError)):
            extract_keyframes_from_video(
                video_path="nonexistent_video.mp4",
                output_dir="./output",
                max_keyframes=10
            )


@pytest.mark.skipif(not INKFOX_AVAILABLE, reason="inkfox not available")
class TestSystemInfo:
    """测试系统信息获取"""
    
    def test_get_system_info(self):
        """测试获取系统信息"""
        info = get_system_info()
        
        assert isinstance(info, dict)
        assert len(info) > 0


class TestInkfoxNotAvailable:
    """测试 inkfox 不可用时的行为"""
    
    @pytest.mark.skipif(INKFOX_AVAILABLE, reason="inkfox is available")
    def test_extractor_raises_error_when_not_available(self):
        """测试 inkfox 不可用时抛出错误"""
        with pytest.raises(RuntimeError, match="inkfox 视频处理模块不可用"):
            VideoKeyframeExtractor()
    
    @pytest.mark.skipif(INKFOX_AVAILABLE, reason="inkfox is available")
    def test_extract_function_raises_error_when_not_available(self):
        """测试 inkfox 不可用时函数抛出错误"""
        with pytest.raises(RuntimeError, match="inkfox 视频处理模块不可用"):
            extract_keyframes_from_video(
                video_path="video.mp4",
                output_dir="./output"
            )
    
    @pytest.mark.skipif(INKFOX_AVAILABLE, reason="inkfox is available")
    def test_get_system_info_raises_error_when_not_available(self):
        """测试 inkfox 不可用时获取系统信息抛出错误"""
        with pytest.raises(RuntimeError, match="inkfox 视频处理模块不可用"):
            get_system_info()


@pytest.mark.integration
@pytest.mark.skipif(not INKFOX_AVAILABLE, reason="inkfox not available")
class TestInkfoxIntegration:
    """inkfox 集成测试（需要实际视频文件）"""
    
    @pytest.fixture
    def sample_video(self, tmp_path):
        """创建示例视频文件（模拟）"""
        # 注意：这只是一个占位符
        # 实际测试需要真实的视频文件
        video_path = tmp_path / "sample.mp4"
        video_path.touch()
        return str(video_path)
    
    @pytest.fixture
    def output_dir(self, tmp_path):
        """创建输出目录"""
        output = tmp_path / "output"
        output.mkdir()
        return str(output)
    
    @pytest.mark.skip(reason="需要真实的视频文件")
    def test_full_extraction_workflow(self, sample_video, output_dir):
        """测试完整的提取流程"""
        # 这个测试需要真实的视频文件才能运行
        result = extract_keyframes_from_video(
            video_path=sample_video,
            output_dir=output_dir,
            max_keyframes=5,
            max_save=5
        )
        
        assert 'total_frames' in result
        assert 'keyframes_extracted' in result
        assert result['keyframes_extracted'] > 0


@pytest.mark.skipif(not INKFOX_AVAILABLE, reason="inkfox not available")
class TestInkfoxImport:
    """测试 inkfox 模块导入"""
    
    def test_import_from_kernel_llm(self):
        """测试从 kernel.llm 导入"""
        from kernel.llm import (
            VideoKeyframeExtractor,
            extract_keyframes_from_video,
            get_system_info,
            check_inkfox_available,
            INKFOX_AVAILABLE
        )
        
        assert VideoKeyframeExtractor is not None
        assert extract_keyframes_from_video is not None
        assert get_system_info is not None
        assert check_inkfox_available is not None
        assert isinstance(INKFOX_AVAILABLE, bool)
    
    def test_import_from_video_utils(self):
        """测试从 video_utils 导入"""
        from kernel.llm.video_utils import (
            VideoKeyframeExtractor,
            extract_keyframes_from_video
        )
        
        assert VideoKeyframeExtractor is not None
        assert extract_keyframes_from_video is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
