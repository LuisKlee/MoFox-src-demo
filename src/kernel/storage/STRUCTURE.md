# Storage Module 文件夹结构

## 目录布局

```
storage/
├── 核心源代码
│   ├── json_store.h          # C++ 头文件 - 类定义
│   ├── json_store.cpp        # C++ 实现 - 完整功能
│   ├── json_store.py         # Python 原始版本
│   ├── old.txt               # Python 版本备份
│   └── __init__.py           # Python 包初始化
│
├── 示例和库文件
│   ├── example.cpp           # C++ 示例程序
│   ├── example.py            # Python 示例程序
│   └── CMakeLists.txt        # CMake 编译配置
│
├── docs/                     # 📚 文档文件夹
│   ├── README.md             # 总体文档
│   └── TEST_GUIDE.md         # 测试运行指南
│
└── tests/                    # 🧪 测试文件夹
    ├── test.cpp              # C++ 单元测试
    ├── test.ps1              # PowerShell 测试脚本（Windows）
    ├── test.sh               # Bash 测试脚本（Linux/Mac）
    ├── demo.ps1              # 演示脚本（彩色输出）
    ├── demo_verify.ps1       # 完整验证脚本
    └── run_demo.ps1          # 运行演示脚本
```

## 文件说明

### 核心源代码
- **json_store.h** - C++ 类声明，包括 JSONStore、DictJSONStore、ListJSONStore、LogStore
- **json_store.cpp** - C++ 完整实现，包括线程安全、压缩、异常处理
- **json_store.py** - Python 原始版本（保持兼容）
- **old.txt** - Python 源代码完整备份

### 构建和编译
- **CMakeLists.txt** - CMake 编译配置
  - 配置选项：`BUILD_EXAMPLES`、`BUILD_TESTS`
  - 编译目标：json_store 库、示例、测试
  - 依赖项：zlib、nlohmann_json

### 示例程序
- **example.cpp** - C++ 示例（6 个使用场景）
- **example.py** - Python 示例

### 📚 文档（docs/）
- **README.md** - 模块总体文档
- **TEST_GUIDE.md** - 详细的测试编译和运行指南

### 🧪 测试（tests/）
- **test.cpp** - C++ 单元测试套件（30+ 个测试用例）
- **test.ps1** - Windows PowerShell 测试运行脚本
- **test.sh** - Linux/macOS Bash 测试运行脚本
- **demo_verify.ps1** - 完整的系统验证脚本（检查依赖、环境等）

## 使用流程

### 编译和测试
```bash
# 进入模块目录
cd src/kernel/storage

# 创建构建目录
mkdir build
cd build

# 配置
cmake .. -DBUILD_EXAMPLES=ON -DBUILD_TESTS=ON

# 编译
cmake --build . --config Release

# 运行测试
./Release/json_store_test.exe
```

### 查看文档
```bash
# 查看总体文档
cat docs/README.md

# 查看测试指南
cat docs/TEST_GUIDE.md
```

### 运行演示（无需编译）
```powershell
# Windows PowerShell
.\tests\demo_verify.ps1
```

## 版本信息

- **Python 版本** - 保留在根目录，提供兼容性
- **C++ 版本** - 完整重写，性能优化，线程安全
- **备份** - old.txt 保存原始 Python 代码

## CMakeLists.txt 更新

CMakeLists.txt 已更新以支持新的文件夹结构：
```cmake
add_executable(json_store_test tests/test.cpp)
```

## 下一步

1. **安装依赖** - 安装 CMake、编译器、zlib、nlohmann_json
2. **编译** - 按照上面的步骤编译项目
3. **运行测试** - 执行测试脚本验证功能
4. **查看文档** - 阅读 docs/ 中的文档了解 API

---
**最后更新**: 2026年1月9日
