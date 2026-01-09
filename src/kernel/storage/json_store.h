/**
 * JSON 存储模块 (C++ 实现)
 * 
 * 提供统一的JSON本地持久化操作，支持CRUD、原子写入、备份、压缩等功能
 */

#ifndef JSON_STORE_H
#define JSON_STORE_H

#include <string>
#include <vector>
#include <map>
#include <functional>
#include <mutex>
#include <memory>
#include <nlohmann/json.hpp>

// ============= 异常类定义 =============

/**
 * JSON存储异常基类
 */
class JSONStoreError : public std::runtime_error {
public:
    explicit JSONStoreError(const std::string& message);
};

/**
 * 文件不存在异常
 */
class FileNotFoundError : public JSONStoreError {
public:
    explicit FileNotFoundError(const std::string& message);
};

/**
 * 数据验证异常
 */
class ValidationError : public JSONStoreError {
public:
    explicit ValidationError(const std::string& message);
};

// ============= JSONStore 类 =============

/**
 * JSON存储器 - 提供安全的JSON文件读写操作
 */
class JSONStore {
public:
    using ValidateFunc = std::function<bool(const nlohmann::json&)>;
    using UpdateFunc = std::function<nlohmann::json(const nlohmann::json&)>;

    /**
     * 初始化JSON存储器
     * 
     * @param file_path JSON文件路径
     * @param auto_create 文件不存在时是否自动创建
     * @param auto_backup 写入前是否自动备份
     * @param max_backups 最大备份数量
     * @param indent JSON缩进级别
     * @param encoding 文件编码
     * @param validate_func 数据验证函数
     */
    JSONStore(
        const std::string& file_path,
        bool auto_create = true,
        bool auto_backup = true,
        int max_backups = 5,
        int indent = 2,
        const std::string& encoding = "utf-8",
        ValidateFunc validate_func = nullptr
    );

    virtual ~JSONStore() = default;

    /**
     * 读取JSON数据
     * 
     * @param default_value 文件不存在时返回的默认值
     * @return 解析后的JSON数据
     * @throws JSONStoreError 读取或解析失败
     */
    nlohmann::json read(const nlohmann::json& default_value = nullptr);

    /**
     * 写入JSON数据（原子写入）
     * 
     * @param data 要写入的数据
     * @param validate 是否验证数据
     * @throws ValidationError 数据验证失败
     * @throws JSONStoreError 写入失败
     */
    void write(const nlohmann::json& data, bool validate = true);

    /**
     * 更新数据（读取-修改-写入）
     * 
     * @param update_func 更新函数，接收当前数据并返回新数据
     * @return 更新后的数据
     */
    nlohmann::json update(UpdateFunc update_func);

    /**
     * 删除JSON文件
     * 
     * @param create_backup 删除前是否备份
     * @return 是否成功删除
     */
    bool delete_file(bool create_backup = true);

    /**
     * 检查文件是否存在
     */
    bool exists() const;

    /**
     * 获取文件大小
     * 
     * @return 文件大小（字节）
     */
    size_t get_size() const;

    /**
     * 压缩JSON文件
     * 
     * @param output_path 输出路径，默认为原文件名+.gz
     * @return 压缩文件路径
     */
    std::string compress(const std::string& output_path = "");

    /**
     * 解压缩到当前文件
     * 
     * @param compressed_path 压缩文件路径
     */
    void decompress(const std::string& compressed_path);

protected:
    std::string file_path_;
    bool auto_create_;
    bool auto_backup_;
    int max_backups_;
    int indent_;
    std::string encoding_;
    ValidateFunc validate_func_;
    mutable std::mutex mutex_;

    void write_internal_(const nlohmann::json& data);
    std::string create_backup_();
    void cleanup_old_backups_();
};

// ============= DictJSONStore 类 =============

/**
 * 字典型JSON存储器 - 专门处理字典数据
 */
class DictJSONStore : public JSONStore {
public:
    explicit DictJSONStore(
        const std::string& file_path,
        const std::map<std::string, std::string>& kwargs = {}
    );

    /**
     * 获取指定键的值
     * 
     * @param key 键名
     * @param default_value 默认值
     * @return 键对应的值
     */
    nlohmann::json get(const std::string& key, const nlohmann::json& default_value = nullptr);

    /**
     * 设置键值对
     * 
     * @param key 键名
     * @param value 值
     */
    void set(const std::string& key, const nlohmann::json& value);

    /**
     * 删除指定键
     * 
     * @param key 键名
     * @return 是否成功删除
     */
    bool delete_key(const std::string& key);

    /**
     * 检查键是否存在
     * 
     * @param key 键名
     * @return 键是否存在
     */
    bool has_key(const std::string& key);

    /**
     * 获取所有键
     * 
     * @return 键列表
     */
    std::vector<std::string> keys();

    /**
     * 获取所有值
     * 
     * @return 值列表
     */
    std::vector<nlohmann::json> values();

    /**
     * 获取所有键值对
     * 
     * @return 键值对列表
     */
    std::vector<std::pair<std::string, nlohmann::json>> items();

    /**
     * 清空所有数据
     */
    void clear();

    /**
     * 合并字典数据
     * 
     * @param other 要合并的字典
     * @param overwrite 是否覆盖已存在的键
     */
    void merge(const nlohmann::json& other, bool overwrite = true);
};

// ============= ListJSONStore 类 =============

/**
 * 列表型JSON存储器 - 专门处理列表数据
 */
class ListJSONStore : public JSONStore {
public:
    using FilterFunc = std::function<bool(const nlohmann::json&)>;

    explicit ListJSONStore(
        const std::string& file_path,
        const std::map<std::string, std::string>& kwargs = {}
    );

    /**
     * 追加项目
     * 
     * @param item 要追加的项目
     */
    void append(const nlohmann::json& item);

    /**
     * 扩展列表
     * 
     * @param items 要添加的项目列表
     */
    void extend(const nlohmann::json& items);

    /**
     * 移除项目
     * 
     * @param item 要移除的项目
     * @return 是否成功移除
     */
    bool remove(const nlohmann::json& item);

    /**
     * 移除指定索引的项目
     * 
     * @param index 索引
     * @return 被移除的项目
     */
    nlohmann::json remove_at(int index);

    /**
     * 获取指定索引的项目
     * 
     * @param index 索引
     * @param default_value 默认值
     * @return 项目
     */
    nlohmann::json get_at(int index, const nlohmann::json& default_value = nullptr);

    /**
     * 获取列表长度
     * 
     * @return 列表长度
     */
    size_t length();

    /**
     * 清空列表
     */
    void clear();

    /**
     * 过滤列表项
     * 
     * @param filter_func 过滤函数
     */
    void filter(FilterFunc filter_func);

    friend class LogStore;
};

// ============= LogStore 类 =============

/**
 * 日志存储器 - 专门用于存储日志记录
 */
class LogStore {
public:
    using FilterFunc = std::function<bool(const nlohmann::json&)>;

    /**
     * 初始化日志存储器
     * 
     * @param directory 日志存储目录
     * @param prefix 文件名前缀
     * @param max_entries_per_file 每个文件最大日志条目数
     * @param auto_rotate 是否自动轮转
     */
    LogStore(
        const std::string& directory,
        const std::string& prefix = "log",
        int max_entries_per_file = 1000,
        bool auto_rotate = true
    );

    /**
     * 添加日志条目
     * 
     * @param log_entry 日志条目（JSON格式）
     */
    void add_log(nlohmann::json log_entry);

    /**
     * 获取日志记录
     * 
     * @param start_date 开始日期
     * @param end_date 结束日期
     * @param filter_func 过滤函数
     * @return 日志记录列表
     */
    std::vector<nlohmann::json> get_logs(
        const std::chrono::system_clock::time_point& start_date = std::chrono::system_clock::now(),
        const std::chrono::system_clock::time_point& end_date = std::chrono::system_clock::now(),
        FilterFunc filter_func = nullptr
    );

    /**
     * 清理旧日志
     * 
     * @param days 保留天数
     * @return 删除的文件数量
     */
    int clear_old_logs(int days = 30);

private:
    std::string directory_;
    std::string prefix_;
    int max_entries_per_file_;
    bool auto_rotate_;
    std::unique_ptr<ListJSONStore> current_store_;

    std::string get_current_file_path_();
    ListJSONStore* get_current_store_();
    void rotate_();
};

#endif // JSON_STORE_H
