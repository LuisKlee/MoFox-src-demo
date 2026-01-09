"""
视频关键帧提取演示

展示如何使用 inkfox 进行视频关键帧提取
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kernel.llm import (
    VideoKeyframeExtractor,
    extract_keyframes_from_video,
    get_system_info,
    check_inkfox_available,
    INKFOX_AVAILABLE
)
from kernel.logger import get_logger

logger = get_logger(__name__)


def demo_check_availability():
    """演示：检查 inkfox 可用性"""
    print("=" * 60)
    print("检查 inkfox 可用性")
    print("=" * 60)
    
    available = check_inkfox_available()
    print(f"inkfox 可用: {available}")
    print(f"INKFOX_AVAILABLE 常量: {INKFOX_AVAILABLE}")
    
    if available:
        system_info = get_system_info()
        print("\n系统信息:")
        for key, value in system_info.items():
            print(f"  {key}: {value}")
    
    print()


def demo_quick_extract():
    """演示：快速提取关键帧"""
    print("=" * 60)
    print("快速提取关键帧（使用便捷函数）")
    print("=" * 60)
    
    if not INKFOX_AVAILABLE:
        print("❌ inkfox 不可用，跳过演示")
        return
    
    # 示例视频路径（请替换为实际视频）
    video_path = "sample_video.mp4"
    output_dir = "./output/keyframes_quick"
    
    # 检查视频文件是否存在
    if not os.path.exists(video_path):
        print(f"⚠️  示例视频不存在: {video_path}")
        print("请提供实际的视频文件路径")
        return
    
    try:
        # 使用便捷函数提取关键帧
        result = extract_keyframes_from_video(
            video_path=video_path,
            output_dir=output_dir,
            max_keyframes=10,
            max_save=10,
            verbose=True
        )
        
        print("\n提取结果:")
        print(f"  视频文件: {result['video_file']}")
        print(f"  总帧数: {result['total_frames']}")
        print(f"  关键帧数: {result['keyframes_extracted']}")
        print(f"  关键帧比例: {result['keyframe_ratio']:.2%}")
        print(f"  总耗时: {result['total_time_ms']:.2f} ms")
        print(f"  处理速度: {result['processing_fps']:.2f} FPS")
        print(f"  SIMD 加速: {result['simd_enabled']}")
        print(f"  线程数: {result['threads_used']}")
        print(f"  优化类型: {result['optimization_type']}")
        
        print(f"\n✅ 关键帧已保存到: {output_dir}")
        
    except Exception as e:
        print(f"❌ 提取失败: {e}")
        logger.exception("关键帧提取失败")
    
    print()


def demo_extractor_class():
    """演示：使用 VideoKeyframeExtractor 类"""
    print("=" * 60)
    print("使用 VideoKeyframeExtractor 类")
    print("=" * 60)
    
    if not INKFOX_AVAILABLE:
        print("❌ inkfox 不可用，跳过演示")
        return
    
    video_path = "sample_video.mp4"
    output_dir = "./output/keyframes_class"
    
    if not os.path.exists(video_path):
        print(f"⚠️  示例视频不存在: {video_path}")
        print("请提供实际的视频文件路径")
        return
    
    try:
        # 创建提取器实例
        extractor = VideoKeyframeExtractor(
            threads=4,  # 使用 4 个线程
            verbose=True
        )
        
        # 获取 CPU 特性
        cpu_features = extractor.get_cpu_features()
        print("\nCPU 特性:")
        for feature, supported in cpu_features.items():
            status = "✓" if supported else "✗"
            print(f"  {status} {feature}")
        
        print(f"\n配置的线程数: {extractor.get_thread_count()}")
        
        # 提取关键帧
        print("\n开始提取关键帧...")
        result = extractor.extract_keyframes(
            video_path=video_path,
            output_dir=output_dir,
            max_keyframes=15,
            max_save=10,
            use_simd=True  # 强制使用 SIMD
        )
        
        print("\n提取结果:")
        print(f"  关键帧数: {result['keyframes_extracted']}")
        print(f"  总耗时: {result['total_time_ms']:.2f} ms")
        print(f"  帧提取: {result['frame_extraction_time_ms']:.2f} ms")
        print(f"  关键帧分析: {result['keyframe_analysis_time_ms']:.2f} ms")
        
        print(f"\n✅ 关键帧已保存到: {output_dir}")
        
    except Exception as e:
        print(f"❌ 提取失败: {e}")
        logger.exception("关键帧提取失败")
    
    print()


def demo_benchmark():
    """演示：性能基准测试"""
    print("=" * 60)
    print("性能基准测试")
    print("=" * 60)
    
    if not INKFOX_AVAILABLE:
        print("❌ inkfox 不可用，跳过演示")
        return
    
    video_path = "sample_video.mp4"
    
    if not os.path.exists(video_path):
        print(f"⚠️  示例视频不存在: {video_path}")
        print("请提供实际的视频文件路径")
        return
    
    try:
        extractor = VideoKeyframeExtractor(verbose=False)
        
        # 测试不同配置
        configs = [
            ("无 SIMD", {"use_simd": False}),
            ("启用 SIMD", {"use_simd": True}),
            ("SIMD + 大块", {"use_simd": True, "block_size": 16}),
        ]
        
        results = []
        
        for test_name, config in configs:
            print(f"\n运行测试: {test_name}")
            result = extractor.benchmark(
                video_path=video_path,
                max_keyframes=10,
                test_name=test_name,
                **config
            )
            results.append((test_name, result))
            print(f"  耗时: {result['total_time_ms']:.2f} ms")
            print(f"  FPS: {result['processing_fps']:.2f}")
        
        # 对比结果
        print("\n" + "=" * 60)
        print("性能对比")
        print("=" * 60)
        print(f"{'测试名称':<15} {'耗时(ms)':<12} {'FPS':<10} {'加速比'}")
        print("-" * 60)
        
        baseline_time = results[0][1]['total_time_ms']
        for test_name, result in results:
            time_ms = result['total_time_ms']
            fps = result['processing_fps']
            speedup = baseline_time / time_ms
            print(f"{test_name:<15} {time_ms:<12.2f} {fps:<10.2f} {speedup:.2f}x")
        
    except Exception as e:
        print(f"❌ 基准测试失败: {e}")
        logger.exception("基准测试失败")
    
    print()


def demo_with_llm():
    """演示：结合 LLM 分析关键帧"""
    print("=" * 60)
    print("结合 LLM 分析关键帧（示例流程）")
    print("=" * 60)
    
    if not INKFOX_AVAILABLE:
        print("❌ inkfox 不可用，跳过演示")
        return
    
    video_path = "sample_video.mp4"
    output_dir = "./output/keyframes_llm"
    
    if not os.path.exists(video_path):
        print(f"⚠️  示例视频不存在: {video_path}")
        print("请提供实际的视频文件路径")
        return
    
    try:
        from kernel.llm import compress_image, image_to_base64
        
        # 1. 提取关键帧
        print("\n步骤 1: 提取视频关键帧")
        result = extract_keyframes_from_video(
            video_path=video_path,
            output_dir=output_dir,
            max_keyframes=5,
            max_save=5
        )
        print(f"  提取了 {result['keyframes_extracted']} 个关键帧")
        
        # 2. 处理关键帧图片
        print("\n步骤 2: 处理关键帧图片（压缩、编码）")
        keyframe_files = sorted(Path(output_dir).glob("keyframe_*.jpg"))
        
        processed_frames = []
        for i, frame_path in enumerate(keyframe_files[:3]):  # 只处理前3个
            print(f"  处理 {frame_path.name}")
            
            # 压缩图片
            compressed = compress_image(
                str(frame_path),
                max_size=(512, 512),
                quality=85
            )
            
            # 转换为 Base64
            base64_str = image_to_base64(
                str(frame_path),
                compress=True,
                max_size=(512, 512)
            )
            
            processed_frames.append({
                'index': i,
                'path': str(frame_path),
                'size': len(compressed),
                'base64_length': len(base64_str)
            })
        
        # 3. 准备发送给 LLM（伪代码）
        print("\n步骤 3: 准备 LLM 分析（示例）")
        print("  可以将处理后的关键帧发送给视觉 LLM 进行分析")
        print("  例如: 场景识别、物体检测、动作分析等")
        
        for frame in processed_frames:
            print(f"  - 帧 {frame['index']}: {frame['size']} bytes")
        
        print("\n💡 示例 LLM 提示词:")
        print("  '请分析这些视频关键帧，描述主要场景和动作'")
        
        print(f"\n✅ 处理完成，关键帧位于: {output_dir}")
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        logger.exception("LLM 集成示例失败")
    
    print()


def main():
    """主函数"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "inkfox 视频关键帧提取演示" + " " * 16 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    # 运行所有演示
    demos = [
        ("检查可用性", demo_check_availability),
        ("快速提取", demo_quick_extract),
        ("类接口", demo_extractor_class),
        ("性能测试", demo_benchmark),
        ("LLM 集成", demo_with_llm),
    ]
    
    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"❌ 演示 '{name}' 失败: {e}")
            logger.exception(f"演示失败: {name}")
    
    print("\n" + "=" * 60)
    print("演示完成")
    print("=" * 60)
    print("\n使用说明:")
    print("1. 确保已安装 inkfox: pip install inkfox")
    print("2. 准备一个测试视频文件（例如 sample_video.mp4）")
    print("3. 根据需要调整参数（关键帧数量、输出目录等）")
    print("4. inkfox 会自动使用 FFmpeg 提取帧并分析关键帧")
    print("5. 提取的关键帧可以用于 LLM 视觉分析")
    print()


if __name__ == "__main__":
    main()
