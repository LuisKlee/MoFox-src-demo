cmake_minimum_required(VERSION 3.10)
project(json_store)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 选项
option(BUILD_EXAMPLES "构建示例程序" ON)
option(BUILD_TESTS "构建测试程序" ON)

# 查找依赖库
find_package(ZLIB REQUIRED)
find_package(nlohmann_json REQUIRED)

# ===== 创建 json_store 库 =====
add_library(json_store STATIC
    json_store.cpp
)

# 链接依赖
target_link_libraries(json_store
    PRIVATE
        ZLIB::ZLIB
        nlohmann_json::nlohmann_json
)

# 包含目录
target_include_directories(json_store
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}
)

# ===== 示例程序 =====
if(BUILD_EXAMPLES)
    add_executable(json_store_example example.cpp)
    target_link_libraries(json_store_example 
        PRIVATE 
            json_store
    )
    
    # 安装选项
    # install(TARGETS json_store_example DESTINATION bin)
endif()

# ===== 测试程序 =====
if(BUILD_TESTS)
    add_executable(json_store_test tests/test.cpp)
    target_link_libraries(json_store_test 
        PRIVATE 
            json_store
    )
    
    # 启用测试
    enable_testing()
    add_test(
        NAME json_store_tests
        COMMAND json_store_test
    )
endif()

# ===== 打印配置信息 =====
message(STATUS "═══════════════════════════════════════")
message(STATUS "JSON Storage C++ 配置")
message(STATUS "═══════════════════════════════════════")
message(STATUS "C++ 标准: ${CMAKE_CXX_STANDARD}")
message(STATUS "构建示例程序: ${BUILD_EXAMPLES}")
message(STATUS "构建测试程序: ${BUILD_TESTS}")
message(STATUS "═══════════════════════════════════════")
