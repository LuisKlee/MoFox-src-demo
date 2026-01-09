#!/bin/bash

# JSON Storage C++ 版本测试脚本
# 支持 Linux 和 macOS

set -e

# ===== 颜色定义 =====
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ===== 辅助函数 =====
print_header() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}📝 $1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# ===== 主程序 =====
echo -e "\n${CYAN}╔════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  JSON Storage C++ 测试脚本 (Linux/macOS)  ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════╝${NC}"

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

print_warning "工作目录: $SCRIPT_DIR"

# 检查源文件
print_header "检查源文件"
FILES_TO_CHECK=("json_store.h" "json_store.cpp" "CMakeLists.txt" "example.cpp" "test.cpp")

for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$SCRIPT_DIR/$file" ]; then
        print_success "找到 $file"
    else
        print_error "缺少 $file"
        exit 1
    fi
done

# 处理命令行参数
CLEAN=false
BUILD_ONLY=false
TEST_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --clean)
            CLEAN=true
            shift
            ;;
        --build-only)
            BUILD_ONLY=true
            shift
            ;;
        --test-only)
            TEST_ONLY=true
            shift
            ;;
        *)
            print_error "未知参数: $1"
            exit 1
            ;;
    esac
done

# 清理之前的构建
if [ "$CLEAN" = true ]; then
    print_header "清理之前的构建"
    if [ -d "$SCRIPT_DIR/build" ]; then
        rm -rf "$SCRIPT_DIR/build"
        print_success "已删除 build 目录"
    fi
fi

# 创建构建目录
BUILD_DIR="$SCRIPT_DIR/build"
if [ ! -d "$BUILD_DIR" ]; then
    mkdir -p "$BUILD_DIR"
    print_success "创建 build 目录"
else
    print_warning "build 目录已存在"
fi

# 编译步骤
if [ "$TEST_ONLY" = false ]; then
    print_header "编译 C++ 代码"
    
    # 检查 CMake
    if ! command -v cmake &> /dev/null; then
        print_error "CMake 未找到，请先安装 CMake"
        exit 1
    fi
    print_success "找到 CMake: $(which cmake)"
    
    # 检查编译器
    if ! command -v g++ &> /dev/null && ! command -v clang++ &> /dev/null; then
        print_error "C++ 编译器未找到"
        exit 1
    fi
    print_success "找到 C++ 编译器"
    
    # 进入构建目录
    cd "$BUILD_DIR"
    
    # 运行 CMake
    print_warning "运行 CMake 配置..."
    cmake .. -DBUILD_EXAMPLES=ON -DBUILD_TESTS=ON
    if [ $? -ne 0 ]; then
        print_error "CMake 配置失败"
        exit 1
    fi
    print_success "CMake 配置完成"
    
    # 构建项目
    print_warning "编译项目..."
    cmake --build . --config Release
    if [ $? -ne 0 ]; then
        print_error "编译失败"
        exit 1
    fi
    print_success "编译完成"
    
    # 返回脚本目录
    cd "$SCRIPT_DIR"
fi

# 运行示例程序
if [ "$TEST_ONLY" = false ] && [ "$BUILD_ONLY" = false ]; then
    print_header "运行示例程序"
    
    # 查找可执行文件
    EXAMPLE_EXE=""
    for path in "$BUILD_DIR/json_store_example" "$BUILD_DIR/Release/json_store_example"; do
        if [ -f "$path" ]; then
            EXAMPLE_EXE="$path"
            break
        fi
    done
    
    if [ -z "$EXAMPLE_EXE" ]; then
        print_warning "未找到示例可执行文件"
    else
        print_warning "运行: $EXAMPLE_EXE\n"
        "$EXAMPLE_EXE"
        if [ $? -eq 0 ]; then
            print_success "示例程序执行成功"
        else
            print_error "示例程序执行失败"
        fi
    fi
fi

# 运行测试
if [ "$BUILD_ONLY" = false ]; then
    print_header "运行单元测试"
    
    # 查找可执行文件
    TEST_EXE=""
    for path in "$BUILD_DIR/json_store_test" "$BUILD_DIR/Release/json_store_test"; do
        if [ -f "$path" ]; then
            TEST_EXE="$path"
            break
        fi
    done
    
    if [ -z "$TEST_EXE" ]; then
        print_warning "未找到测试可执行文件"
    else
        print_warning "运行: $TEST_EXE\n"
        "$TEST_EXE"
        TEST_RESULT=$?
        if [ $TEST_RESULT -eq 0 ]; then
            print_success "所有测试通过"
        else
            print_warning "某些测试失败，返回码: $TEST_RESULT"
        fi
    fi
fi

# 最终总结
print_header "总结"
echo ""
print_success "脚本执行完成"
print_warning "更多信息请查看文档:"
echo -e "${CYAN}  - C++ 实现指南: docs/kernel/storage/CPP_IMPLEMENTATION.md${NC}"
echo -e "${CYAN}  - 快速参考: src/kernel/storage/QUICK_REFERENCE.md${NC}"
echo -e "${CYAN}  - 示例代码: src/kernel/storage/example.cpp${NC}"
echo ""
