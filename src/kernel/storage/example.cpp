/**
 * JSON 存储模块 - C++ 使用示例
 */

#include "json_store.h"
#include <iostream>
#include <iomanip>

using json = nlohmann::json;

int main() {
    try {
        std::cout << "=== JSON 存储模块 C++ 示例 ===" << std::endl << std::endl;

        // ===== 示例 1: JSONStore 基础使用 =====
        std::cout << "1. JSONStore 基础使用" << std::endl;
        std::cout << "------------------------" << std::endl;
        
        JSONStore store("example_data.json");
        
        // 写入数据
        json data = {
            {"name", "Alice"},
            {"age", 30},
            {"email", "alice@example.com"}
        };
        store.write(data);
        std::cout << "写入数据: " << data.dump(2) << std::endl;
        
        // 读取数据
        auto read_data = store.read();
        std::cout << "读取数据: " << read_data.dump(2) << std::endl;
        
        // 更新数据
        auto updated = store.update([](json d) {
            d["status"] = "active";
            return d;
        });
        std::cout << "更新后: " << updated.dump(2) << std::endl << std::endl;

        // ===== 示例 2: DictJSONStore 字典操作 =====
        std::cout << "2. DictJSONStore 字典操作" << std::endl;
        std::cout << "------------------------" << std::endl;
        
        DictJSONStore config("config.json");
        
        // 设置键值对
        config.set("db_host", "localhost");
        config.set("db_port", 5432);
        config.set("db_name", "myapp");
        std::cout << "设置配置项..." << std::endl;
        
        // 获取值
        auto host = config.get("db_host", "default");
        auto port = config.get("db_port", 3306);
        std::cout << "数据库: " << host << ":" << port << std::endl;
        
        // 获取所有键
        auto keys = config.keys();
        std::cout << "所有配置键: ";
        for (const auto& key : keys) {
            std::cout << key << ", ";
        }
        std::cout << std::endl << std::endl;

        // ===== 示例 3: ListJSONStore 列表操作 =====
        std::cout << "3. ListJSONStore 列表操作" << std::endl;
        std::cout << "------------------------" << std::endl;
        
        ListJSONStore tasks("tasks.json");
        
        // 添加任务
        tasks.append({
            {"id", 1},
            {"title", "学习 C++"},
            {"status", "in_progress"}
        });
        tasks.append({
            {"id", 2},
            {"title", "重构存储模块"},
            {"status", "completed"}
        });
        tasks.append({
            {"id", 3},
            {"title", "编写测试"},
            {"status", "pending"}
        });
        std::cout << "添加了 3 个任务" << std::endl;
        
        // 过滤任务
        std::cout << "进行中的任务: ";
        tasks.filter([](const json& task) {
            return task["status"] == "in_progress";
        });
        
        // 获取任务数量
        std::cout << "当前任务数: " << tasks.length() << std::endl << std::endl;

        // ===== 示例 4: LogStore 日志管理 =====
        std::cout << "4. LogStore 日志管理" << std::endl;
        std::cout << "------------------------" << std::endl;
        
        LogStore logs("logs/", "app", 100, true);
        
        // 添加日志
        logs.add_log({
            {"level", "INFO"},
            {"module", "main"},
            {"message", "应用启动"}
        });
        
        logs.add_log({
            {"level", "INFO"},
            {"module", "database"},
            {"message", "数据库连接成功"}
        });
        
        logs.add_log({
            {"level", "ERROR"},
            {"module", "api"},
            {"message", "API 请求超时"}
        });
        
        std::cout << "已添加 3 条日志" << std::endl;
        
        // 获取所有日志
        auto all_logs = logs.get_logs();
        std::cout << "日志总数: " << all_logs.size() << std::endl;
        
        // 获取错误日志
        auto error_logs = logs.get_logs(
            std::chrono::system_clock::now() - std::chrono::hours(24),
            std::chrono::system_clock::now(),
            [](const json& log) {
                return log["level"] == "ERROR";
            }
        );
        std::cout << "错误日志数: " << error_logs.size() << std::endl << std::endl;

        // ===== 示例 5: 异常处理 =====
        std::cout << "5. 异常处理演示" << std::endl;
        std::cout << "------------------------" << std::endl;
        
        try {
            JSONStore nonexistent("nonexistent.json", false);  // 不自动创建
            auto data = nonexistent.read();  // 会抛出异常
        }
        catch (const FileNotFoundError& e) {
            std::cout << "捕获异常: " << e.what() << std::endl;
        }
        
        // 数据验证
        JSONStore validated("validated.json", true, true, 5, 2, "utf-8",
            [](const json& data) {
                return data.contains("name") && data.contains("age");
            }
        );
        
        try {
            validated.write({{"incomplete", "data"}});  // 验证失败
        }
        catch (const ValidationError& e) {
            std::cout << "验证失败: " << e.what() << std::endl;
        }
        
        std::cout << std::endl;

        // ===== 示例 6: 文件操作 =====
        std::cout << "6. 文件操作" << std::endl;
        std::cout << "------------------------" << std::endl;
        
        JSONStore file_ops("file_ops.json");
        file_ops.write({{"data", "important"}});
        
        std::cout << "文件存在: " << (file_ops.exists() ? "是" : "否") << std::endl;
        std::cout << "文件大小: " << file_ops.get_size() << " 字节" << std::endl;
        
        // 压缩文件
        auto compressed = file_ops.compress("file_ops.json.gz");
        std::cout << "压缩文件: " << compressed << std::endl;
        
        // 解压缩
        JSONStore decompressed("decompressed.json");
        decompressed.decompress("file_ops.json.gz");
        std::cout << "已解压缩" << std::endl << std::endl;

        std::cout << "=== 所有示例执行完成 ===" << std::endl;
        
        return 0;
    }
    catch (const std::exception& e) {
        std::cerr << "错误: " << e.what() << std::endl;
        return 1;
    }
}
