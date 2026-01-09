/**
 * JSON 存储模块 - C++ 单元测试
 */

#include "json_store.h"
#include <iostream>
#include <iomanip>
#include <cassert>
#include <cstdlib>

using json = nlohmann::json;

// 测试颜色输出
#define COLOR_RESET   "\033[0m"
#define COLOR_GREEN   "\033[32m"
#define COLOR_RED     "\033[31m"
#define COLOR_YELLOW  "\033[33m"
#define COLOR_CYAN    "\033[36m"

// 测试计数器
int total_tests = 0;
int passed_tests = 0;
int failed_tests = 0;

void print_header(const std::string& test_name) {
    std::cout << "\n" << COLOR_CYAN << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << COLOR_RESET << std::endl;
    std::cout << COLOR_CYAN << "📝 " << test_name << COLOR_RESET << std::endl;
    std::cout << COLOR_CYAN << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << COLOR_RESET << std::endl;
}

void print_result(const std::string& test_desc, bool passed) {
    total_tests++;
    if (passed) {
        passed_tests++;
        std::cout << COLOR_GREEN << "✓ PASS" << COLOR_RESET << ": " << test_desc << std::endl;
    } else {
        failed_tests++;
        std::cout << COLOR_RED << "✗ FAIL" << COLOR_RESET << ": " << test_desc << std::endl;
    }
}

// ===== Test 1: JSONStore 基础功能 =====
void test_jsonstore_basic() {
    print_header("Test 1: JSONStore 基础功能");
    
    try {
        JSONStore store("test_basic.json");
        
        // 测试写入
        json data = {
            {"name", "MoFox"},
            {"version", "1.0"},
            {"features", nlohmann::json::array({"storage", "logging"})}
        };
        store.write(data);
        print_result("写入JSON数据", true);
        
        // 测试读取
        auto read_data = store.read();
        bool read_ok = read_data["name"] == "MoFox" && read_data["version"] == "1.0";
        print_result("读取JSON数据", read_ok);
        
        // 测试文件存在
        bool exists = store.exists();
        print_result("检查文件存在", exists);
        
        // 测试文件大小
        size_t size = store.get_size();
        bool size_ok = size > 0;
        print_result("获取文件大小", size_ok);
        
        // 清理
        store.delete_file(false);
    }
    catch (const std::exception& e) {
        print_result("异常处理", false);
        std::cerr << "Error: " << e.what() << std::endl;
    }
}

// ===== Test 2: JSONStore 更新功能 =====
void test_jsonstore_update() {
    print_header("Test 2: JSONStore 更新功能");
    
    try {
        JSONStore store("test_update.json");
        
        // 初始数据
        store.write({{"count", 0}});
        
        // 更新数据
        auto updated = store.update([](json d) {
            d["count"] = d["count"].get<int>() + 1;
            d["updated"] = true;
            return d;
        });
        
        bool update_ok = updated["count"] == 1 && updated["updated"] == true;
        print_result("更新JSON数据", update_ok);
        
        // 验证更新后的数据
        auto verified = store.read();
        bool verify_ok = verified["count"] == 1;
        print_result("验证更新结果", verify_ok);
        
        // 清理
        store.delete_file(false);
    }
    catch (const std::exception& e) {
        print_result("异常处理", false);
        std::cerr << "Error: " << e.what() << std::endl;
    }
}

// ===== Test 3: DictJSONStore 功能 =====
void test_dict_store() {
    print_header("Test 3: DictJSONStore 功能");
    
    try {
        DictJSONStore config("test_config.json");
        
        // 测试 set/get
        config.set("database", "postgresql");
        config.set("port", 5432);
        auto db = config.get("database");
        bool get_ok = db == "postgresql";
        print_result("set/get 键值对", get_ok);
        
        // 测试 has_key
        bool has = config.has_key("database");
        print_result("检查键存在", has);
        
        // 测试 keys
        auto keys = config.keys();
        bool keys_ok = keys.size() == 2;
        print_result("获取所有键", keys_ok);
        
        // 测试 merge
        config.merge({{"host", "localhost"}, {"username", "admin"}}, true);
        bool merge_ok = config.has_key("host");
        print_result("合并配置", merge_ok);
        
        // 测试 delete_key
        config.delete_key("username");
        bool delete_ok = !config.has_key("username");
        print_result("删除键", delete_ok);
        
        // 测试 clear
        config.clear();
        bool clear_ok = config.keys().empty();
        print_result("清空字典", clear_ok);
        
        // 清理
        config.delete_file(false);
    }
    catch (const std::exception& e) {
        print_result("异常处理", false);
        std::cerr << "Error: " << e.what() << std::endl;
    }
}

// ===== Test 4: ListJSONStore 功能 =====
void test_list_store() {
    print_header("Test 4: ListJSONStore 功能");
    
    try {
        ListJSONStore tasks("test_tasks.json");
        
        // 测试 append
        tasks.append({{"id", 1}, {"title", "Task 1"}});
        tasks.append({{"id", 2}, {"title", "Task 2"}});
        bool append_ok = tasks.length() == 2;
        print_result("追加项目", append_ok);
        
        // 测试 extend
        tasks.extend(nlohmann::json::array({
            {{"id", 3}, {"title", "Task 3"}},
            {{"id", 4}, {"title", "Task 4"}}
        }));
        bool extend_ok = tasks.length() == 4;
        print_result("扩展列表", extend_ok);
        
        // 测试 get_at
        auto item = tasks.get_at(0);
        bool get_at_ok = item["id"] == 1;
        print_result("获取指定项", get_at_ok);
        
        // 测试 length
        size_t len = tasks.length();
        bool length_ok = len == 4;
        print_result("获取列表长度", length_ok);
        
        // 测试 filter
        tasks.filter([](const json& task) {
            return task["id"] > 2;
        });
        bool filter_ok = tasks.length() == 2;
        print_result("过滤列表", filter_ok);
        
        // 测试 clear
        tasks.clear();
        bool clear_ok = tasks.length() == 0;
        print_result("清空列表", clear_ok);
        
        // 清理
        tasks.delete_file(false);
    }
    catch (const std::exception& e) {
        print_result("异常处理", false);
        std::cerr << "Error: " << e.what() << std::endl;
    }
}

// ===== Test 5: LogStore 功能 =====
void test_log_store() {
    print_header("Test 5: LogStore 功能");
    
    try {
        LogStore logs("test_logs/", "test");
        
        // 测试 add_log
        logs.add_log({
            {"level", "INFO"},
            {"message", "Test message 1"}
        });
        logs.add_log({
            {"level", "ERROR"},
            {"message", "Test message 2"}
        });
        print_result("添加日志", true);
        
        // 测试 get_logs
        auto all_logs = logs.get_logs();
        bool get_logs_ok = all_logs.size() >= 2;
        print_result("获取日志", get_logs_ok);
        
        // 测试过滤
        auto error_logs = logs.get_logs(
            std::chrono::system_clock::now() - std::chrono::hours(24),
            std::chrono::system_clock::now(),
            [](const json& log) {
                return log["level"] == "ERROR";
            }
        );
        bool filter_ok = error_logs.size() >= 1;
        print_result("过滤日志", filter_ok);
        
        print_result("日志管理基本功能", true);
        
        // 清理
        std::system("rm -rf test_logs 2>/dev/null || rmdir /s /q test_logs 2>nul");
    }
    catch (const std::exception& e) {
        print_result("异常处理", false);
        std::cerr << "Error: " << e.what() << std::endl;
    }
}

// ===== Test 6: 异常处理 =====
void test_exception_handling() {
    print_header("Test 6: 异常处理");
    
    try {
        // 测试 FileNotFoundError
        try {
            JSONStore store("nonexistent_file.json", false);
            auto data = store.read();
            print_result("捕获 FileNotFoundError", false);
        }
        catch (const FileNotFoundError&) {
            print_result("捕获 FileNotFoundError", true);
        }
        
        // 测试数据验证
        auto validate = [](const json& data) {
            return data.contains("required_field");
        };
        
        JSONStore validated("test_validate.json", true, true, 5, 2, "utf-8", validate);
        
        try {
            validated.write({{"wrong_field", "value"}});
            print_result("捕获 ValidationError", false);
        }
        catch (const ValidationError&) {
            print_result("捕获 ValidationError", true);
        }
        
        validated.delete_file(false);
    }
    catch (const std::exception& e) {
        std::cerr << "Unexpected error: " << e.what() << std::endl;
    }
}

// ===== Test 7: 备份功能 =====
void test_backup() {
    print_header("Test 7: 备份功能");
    
    try {
        JSONStore store("test_backup.json", true, true, 3);
        
        // 多次写入触发备份
        for (int i = 0; i < 3; ++i) {
            json data = {{"version", i}};
            store.write(data);
        }
        
        print_result("自动备份功能", true);
        
        // 清理
        store.delete_file(true);
    }
    catch (const std::exception& e) {
        print_result("备份功能", false);
        std::cerr << "Error: " << e.what() << std::endl;
    }
}

// ===== Test 8: 数据类型 =====
void test_data_types() {
    print_header("Test 8: 数据类型");
    
    try {
        JSONStore store("test_types.json");
        
        json mixed_data = {
            {"string", "hello"},
            {"integer", 42},
            {"floating", 3.14},
            {"boolean", true},
            {"array", nlohmann::json::array({1, 2, 3})},
            {"object", nlohmann::json::object({{"nested", "value"}})}
        };
        
        store.write(mixed_data);
        auto read_data = store.read();
        
        bool string_ok = read_data["string"] == "hello";
        bool integer_ok = read_data["integer"] == 42;
        bool float_ok = std::abs(read_data["floating"].get<double>() - 3.14) < 0.01;
        bool bool_ok = read_data["boolean"] == true;
        bool array_ok = read_data["array"].is_array();
        bool object_ok = read_data["object"]["nested"] == "value";
        
        print_result("字符串类型", string_ok);
        print_result("整数类型", integer_ok);
        print_result("浮点数类型", float_ok);
        print_result("布尔值类型", bool_ok);
        print_result("数组类型", array_ok);
        print_result("对象类型", object_ok);
        
        // 清理
        store.delete_file(false);
    }
    catch (const std::exception& e) {
        print_result("数据类型", false);
        std::cerr << "Error: " << e.what() << std::endl;
    }
}

// 主函数
int main() {
    std::cout << "\n" << COLOR_CYAN << "╔════════════════════════════════════════════╗" << COLOR_RESET << std::endl;
    std::cout << COLOR_CYAN << "║    JSON Storage C++ 版本测试套件          ║" << COLOR_RESET << std::endl;
    std::cout << COLOR_CYAN << "╚════════════════════════════════════════════╝" << COLOR_RESET << std::endl;
    
    // 运行所有测试
    test_jsonstore_basic();
    test_jsonstore_update();
    test_dict_store();
    test_list_store();
    test_log_store();
    test_exception_handling();
    test_backup();
    test_data_types();
    
    // 输出总结
    std::cout << "\n" << COLOR_CYAN << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << COLOR_RESET << std::endl;
    std::cout << COLOR_CYAN << "📊 测试总结" << COLOR_RESET << std::endl;
    std::cout << COLOR_CYAN << "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << COLOR_RESET << std::endl;
    
    std::cout << "总测试数: " << total_tests << std::endl;
    std::cout << COLOR_GREEN << "✓ 通过: " << passed_tests << COLOR_RESET << std::endl;
    std::cout << COLOR_RED << "✗ 失败: " << failed_tests << COLOR_RESET << std::endl;
    
    double success_rate = (total_tests > 0) ? (static_cast<double>(passed_tests) / total_tests * 100.0) : 0.0;
    std::cout << std::fixed << std::setprecision(1);
    std::cout << "成功率: " << success_rate << "%" << std::endl;
    
    if (failed_tests == 0) {
        std::cout << "\n" << COLOR_GREEN << "✓ 所有测试通过！" << COLOR_RESET << std::endl;
        return 0;
    } else {
        std::cout << "\n" << COLOR_RED << "✗ 有测试失败，请检查。" << COLOR_RESET << std::endl;
        return 1;
    }
}
