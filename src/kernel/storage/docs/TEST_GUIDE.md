# C++ 版本测试指南

本文档说明如何编译和运行 Storage 模块的 C++ 版本测试。

---

## 快速开始

### Windows (PowerShell)

```powershell
# 进入存储模块目录
cd src\kernel\storage

# 运行测试脚本
.\test.ps1
```

### Linux / macOS (Bash)

```bash
# 进入存储模块目录
cd src/kernel/storage

# 运行测试脚本
chmod +x test.sh
./test.sh
```

---

## 前置条件

### Windows

1. **CMake** (3.10+)
   ```powershell
   # 使用 Chocolatey 安装
   choco install cmake
   
   # 或从官网下载：https://cmake.org/download/
   ```

2. **C++ 编译器** (Visual Studio 或 MinGW)
   ```powershell
   # 使用 Visual Studio 的 MSVC
   # 或使用 MinGW（通过 Chocolatey）
   choco install mingw
   ```

3. **依赖库**
   ```powershell
   # 使用 vcpkg 安装
   vcpkg install zlib:x64-windows nlohmann-json:x64-windows
   ```

### Linux

```bash
# Ubuntu / Debian
sudo apt-get install cmake g++ libz-dev nlohmann-json3-dev

# Fedora
sudo dnf install cmake gcc-c++ zlib-devel nlohmann-json-devel

# Arch
sudo pacman -S cmake gcc zlib nlohmann-json
```

### macOS

```bash
# 使用 Homebrew
brew install cmake zlib nlohmann-json
```

---

## 脚本使用

### PowerShell 脚本选项

```powershell
# 基础运行（编译 + 运行示例 + 运行测试）
.\test.ps1

# 仅编译
.\test.ps1 -BuildOnly

# 仅运行测试（跳过编译）
.\test.ps1 -TestOnly

# 清理后重新编译
.\test.ps1 -Clean
```

### Bash 脚本选项

```bash
# 基础运行（编译 + 运行示例 + 运行测试）
./test.sh

# 仅编译
./test.sh --build-only

# 仅运行测试（跳过编译）
./test.sh --test-only

# 清理后重新编译
./test.sh --clean
```

---

## 手动编译（不使用脚本）

如果脚本不工作，可以手动执行以下步骤：

### 1. 创建构建目录

```bash
# Windows (PowerShell)
mkdir build
cd build

# Linux / macOS (Bash)
mkdir -p build
cd build
```

### 2. 运行 CMake

```bash
# Windows (PowerShell)
cmake .. -G "Visual Studio 16 2019"

# Linux / macOS
cmake ..
```

### 3. 构建项目

```bash
# Windows (PowerShell)
cmake --build . --config Release

# Linux / macOS
make
# 或
cmake --build . --config Release
```

### 4. 运行示例程序

```bash
# Windows
.\Release\json_store_example.exe

# Linux / macOS
./json_store_example
```

### 5. 运行测试

```bash
# Windows
.\Release\json_store_test.exe

# Linux / macOS
./json_store_test
```

---

## 测试程序说明

### 测试覆盖范围

测试程序 (`test.cpp`) 包含 8 个测试套件：

1. **JSONStore 基础功能**
   - 写入/读取 JSON 数据
   - 文件存在性检查
   - 文件大小获取

2. **JSONStore 更新功能**
   - 原子更新操作
   - 更新结果验证

3. **DictJSONStore 功能**
   - set/get 键值对
   - has_key 检查
   - keys/values/items 遍历
   - merge 合并
   - delete_key 删除
   - clear 清空

4. **ListJSONStore 功能**
   - append 追加
   - extend 扩展
   - get_at 获取
   - length 长度
   - filter 过滤
   - clear 清空

5. **LogStore 功能**
   - add_log 添加日志
   - get_logs 查询日志
   - 日志过滤

6. **异常处理**
   - FileNotFoundError 捕获
   - ValidationError 捕获

7. **备份功能**
   - 自动备份验证

8. **数据类型**
   - 字符串、整数、浮点数
   - 布尔值、数组、对象

### 预期输出

成功的测试应输出：

```
╔════════════════════════════════════════════╗
║    JSON Storage C++ 版本测试套件          ║
╚════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 Test 1: JSONStore 基础功能
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ PASS: 写入JSON数据
✓ PASS: 读取JSON数据
✓ PASS: 检查文件存在
✓ PASS: 获取文件大小
...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 测试总结
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
总测试数: 50+
✓ 通过: 50+
✗ 失败: 0
成功率: 100.0%

✓ 所有测试通过！
```

---

## 故障排查

### 问题 1: CMake 未找到

**症状**: `cmake: command not found`

**解决方案**:
- Windows: 安装 CMake 并将其添加到 PATH
- Linux: `sudo apt-get install cmake`
- macOS: `brew install cmake`

### 问题 2: 编译器未找到

**症状**: `error: 'g++': No such file or directory`

**解决方案**:
- Windows: 安装 Visual Studio 或 MinGW
- Linux: `sudo apt-get install build-essential`
- macOS: `xcode-select --install`

### 问题 3: 缺少依赖库

**症状**: `fatal error: nlohmann/json.hpp: No such file`

**解决方案**:
- Windows: 使用 vcpkg 安装依赖
- Linux: `sudo apt-get install nlohmann-json3-dev libz-dev`
- macOS: `brew install nlohmann-json zlib`

### 问题 4: 权限错误 (Linux/macOS)

**症状**: `permission denied: ./test.sh`

**解决方案**:
```bash
chmod +x test.sh
./test.sh
```

### 问题 5: 构建失败

**症状**: 编译过程中出现错误

**解决方案**:
```bash
# 清理并重新编译
rm -rf build
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

---

## 性能测试（可选）

如果想进行性能基准测试，可以修改 `example.cpp` 添加计时代码：

```cpp
#include <chrono>

auto start = std::chrono::high_resolution_clock::now();

// 执行操作
store.write(large_json);

auto end = std::chrono::high_resolution_clock::now();
auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

std::cout << "耗时: " << duration.count() << " ms" << std::endl;
```

---

## 完整的测试工作流

### 场景 1: 首次测试

```bash
# 1. 检查依赖库是否已安装
cmake --version
g++ --version

# 2. 运行完整的测试流程
./test.sh

# 3. 查看测试结果
# 成功: 返回码为 0
# 失败: 返回码为 1
echo $?
```

### 场景 2: 修改代码后重新测试

```bash
# 编辑源代码...

# 重新编译和测试
./test.sh --clean

# 或只重新编译
./test.sh --build-only
```

### 场景 3: 只想运行测试

```bash
# 假设已经编译过了
./test.sh --test-only
```

---

## 与 Python 版本对比

使用类似的脚本测试 Python 版本：

```bash
# Python 版本测试
cd src/kernel/storage
python example.py
python -m pytest  # 如果有 pytest 配置
```

---

## 相关文档

- [C++ 实现指南](../../docs/kernel/storage/CPP_IMPLEMENTATION.md)
- [快速参考](./QUICK_REFERENCE.md)
- [CMakeLists.txt](./CMakeLists.txt)
- [示例代码](./example.cpp)
- [测试代码](./test.cpp)

---

## 常见问题

### Q: 编译需要多长时间？
**A**: 通常 1-2 分钟，首次编译可能更长。

### Q: 测试需要多长时间？
**A**: 通常少于 1 秒。

### Q: 是否支持增量编译？
**A**: 是的，CMake 支持增量编译，只会重新编译变化的部分。

### Q: 如何在 IDE 中使用？
**A**: 大多数 IDE (Visual Studio Code, CLion, Qt Creator) 都原生支持 CMake 项目。

### Q: 为什么有两个脚本（PowerShell 和 Bash）？
**A**: 为了支持不同的操作系统，PowerShell 用于 Windows，Bash 用于 Linux/macOS。

---

**最后更新**: 2026-01-09 | **版本**: 1.0
