#!/usr/bin/env pwsh
<#
.SYNOPSIS
    编译和运行 JSON Storage C++ 版本的测试脚本

.DESCRIPTION
    该脚本执行以下步骤：
    1. 检查编译器和依赖库
    2. 创建构建目录
    3. 编译源代码（示例和测试）
    4. 运行示例程序
    5. 运行单元测试
    6. 显示测试结果

.PARAMETER Clean
    清理之前的构建结果

.PARAMETER BuildOnly
    仅编译，不运行测试

.PARAMETER TestOnly
    仅运行测试，不编译

#>

param(
    [switch]$Clean,
    [switch]$BuildOnly,
    [switch]$TestOnly
)

# ===== 颜色定义 =====
$colors = @{
    'Green'  = "`e[32m"
    'Red'    = "`e[31m"
    'Yellow' = "`e[33m"
    'Cyan'   = "`e[36m"
    'Reset'  = "`e[0m"
}

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = 'Reset'
    )
    Write-Host "$($colors[$Color])$Message$($colors['Reset'])"
}

function Write-Header {
    param([string]$Title)
    Write-ColorOutput "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" 'Cyan'
    Write-ColorOutput "📝 $Title" 'Cyan'
    Write-ColorOutput "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" 'Cyan'
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✓ $Message" 'Green'
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "✗ $Message" 'Red'
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠ $Message" 'Yellow'
}

# ===== 主程序 =====
Write-ColorOutput "`n╔════════════════════════════════════════════╗" 'Cyan'
Write-ColorOutput "║  JSON Storage C++ 测试脚本                ║" 'Cyan'
Write-ColorOutput "╚════════════════════════════════════════════╝" 'Cyan'

# 检查目录
$StoragePath = Join-Path $PSScriptRoot ""
if (!(Test-Path $StoragePath)) {
    Write-Error "Storage 模块目录不存在: $StoragePath"
    exit 1
}

Write-ColorOutput "`n📁 工作目录: $StoragePath" 'Yellow'

# 检查源文件
$files_to_check = @(
    "json_store.h"
    "json_store.cpp"
    "CMakeLists.txt"
    "example.cpp"
    "test.cpp"
)

Write-Header "检查源文件"
foreach ($file in $files_to_check) {
    $filepath = Join-Path $StoragePath $file
    if (Test-Path $filepath) {
        Write-Success "找到 $file"
    } else {
        Write-Error "缺少 $file"
        exit 1
    }
}

# 清理构建（如果指定）
if ($Clean) {
    Write-Header "清理之前的构建"
    $builddir = Join-Path $StoragePath "build"
    if (Test-Path $builddir) {
        Remove-Item -Recurse -Force $builddir
        Write-Success "已删除 build 目录"
    }
}

# 创建构建目录
$builddir = Join-Path $StoragePath "build"
if (!(Test-Path $builddir)) {
    New-Item -ItemType Directory -Path $builddir | Out-Null
    Write-Success "创建 build 目录"
} else {
    Write-ColorOutput "build 目录已存在" 'Yellow'
}

# 编译步骤
if (!$TestOnly) {
    Write-Header "编译 C++ 代码"
    
    # 检查 CMake
    Write-Warning "尝试检查 CMake..."
    $cmake = Get-Command cmake -ErrorAction SilentlyContinue
    if (!$cmake) {
        Write-Error "CMake 未找到，请先安装 CMake"
        exit 1
    }
    Write-Success "找到 CMake: $($cmake.Source)"
    
    # 进入构建目录
    Push-Location $builddir
    
    try {
        # 运行 CMake
        Write-ColorOutput "`n运行 CMake 配置..." 'Yellow'
        cmake .. -DBUILD_EXAMPLES=ON
        if ($LASTEXITCODE -ne 0) {
            Write-Error "CMake 配置失败"
            exit 1
        }
        Write-Success "CMake 配置完成"
        
        # 构建项目
        Write-ColorOutput "`n编译项目..." 'Yellow'
        cmake --build . --config Release
        if ($LASTEXITCODE -ne 0) {
            Write-Error "编译失败"
            exit 1
        }
        Write-Success "编译完成"
        
    } finally {
        Pop-Location
    }
}

# 运行示例程序
if (!$TestOnly -and !$BuildOnly) {
    Write-Header "运行示例程序"
    
    # 查找示例可执行文件
    $example_exe = @(
        (Join-Path $builddir "Release" "json_store_example.exe"),
        (Join-Path $builddir "json_store_example.exe"),
        (Join-Path $builddir "json_store_example")
    ) | Where-Object { Test-Path $_ } | Select-Object -First 1
    
    if ($example_exe) {
        Write-ColorOutput "`n运行: $example_exe`n" 'Yellow'
        & $example_exe
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "示例程序执行成功"
        } else {
            Write-Error "示例程序执行失败，返回码: $LASTEXITCODE"
        }
    } else {
        Write-Warning "未找到示例可执行文件"
    }
}

# 运行测试
if (!$BuildOnly) {
    Write-Header "运行单元测试"
    
    # 查找测试可执行文件
    $test_exe = @(
        (Join-Path $builddir "Release" "json_store_test.exe"),
        (Join-Path $builddir "json_store_test.exe"),
        (Join-Path $builddir "json_store_test")
    ) | Where-Object { Test-Path $_ } | Select-Object -First 1
    
    if ($test_exe) {
        Write-ColorOutput "`n运行: $test_exe`n" 'Yellow'
        & $test_exe
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "所有测试通过"
        } else {
            Write-Warning "某些测试失败，返回码: $LASTEXITCODE"
        }
    } else {
        Write-Warning "未找到测试可执行文件"
        Write-ColorOutput "`n说明: 需要在 CMakeLists.txt 中启用 BUILD_EXAMPLES 选项" 'Yellow'
    }
}

# 最终总结
Write-Header "总结"
Write-ColorOutput "`n✓ 脚本执行完成" 'Green'
Write-ColorOutput "📚 更多信息请查看文档:" 'Yellow'
Write-ColorOutput "  - C++ 实现指南: docs/kernel/storage/CPP_IMPLEMENTATION.md" 'Cyan'
Write-ColorOutput "  - 快速参考: src/kernel/storage/QUICK_REFERENCE.md" 'Cyan'
Write-ColorOutput "  - 示例代码: src/kernel/storage/example.cpp" 'Cyan'
