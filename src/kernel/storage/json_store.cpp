/**
 * JSON 存储模块 (C++ 实现)
 * 
 * 提供统一的JSON本地持久化操作，支持CRUD、原子写入、备份、压缩等功能
 */

#include "json_store.h"
#include <fstream>
#include <sstream>
#include <filesystem>
#include <iostream>
#include <chrono>
#include <algorithm>
#include <cstring>
#include <zlib.h>

namespace fs = std::filesystem;

// ============= JSONStoreError 异常类 =============

JSONStoreError::JSONStoreError(const std::string& message) 
    : std::runtime_error(message) {}

FileNotFoundError::FileNotFoundError(const std::string& message)
    : JSONStoreError(message) {}

ValidationError::ValidationError(const std::string& message)
    : JSONStoreError(message) {}

// ============= JSONStore 类实现 =============

JSONStore::JSONStore(
    const std::string& file_path,
    bool auto_create,
    bool auto_backup,
    int max_backups,
    int indent,
    const std::string& encoding,
    ValidateFunc validate_func
)
    : file_path_(file_path),
      auto_create_(auto_create),
      auto_backup_(auto_backup),
      max_backups_(max_backups),
      indent_(indent),
      encoding_(encoding),
      validate_func_(validate_func) {
    
    // 确保目录存在
    fs::path dir = fs::path(file_path).parent_path();
    if (!dir.empty()) {
        fs::create_directories(dir);
    }
    
    // 如果文件不存在且允许自动创建，创建空文件
    if (!fs::exists(file_path) && auto_create) {
        nlohmann::json empty = nlohmann::json::object();
        write_internal_(empty);
    }
}

nlohmann::json JSONStore::read(const nlohmann::json& default_value) {
    std::lock_guard<std::mutex> lock(mutex_);
    
    try {
        if (!fs::exists(file_path_)) {
            if (!default_value.is_null()) {
                return default_value;
            }
            throw FileNotFoundError("文件不存在: " + file_path_);
        }
        
        std::ifstream file(file_path_);
        if (!file.is_open()) {
            throw JSONStoreError("无法打开文件: " + file_path_);
        }
        
        nlohmann::json data;
        file >> data;
        return data;
    }
    catch (const nlohmann::json::exception& e) {
        throw JSONStoreError("JSON解析失败: " + std::string(e.what()));
    }
    catch (const std::exception& e) {
        throw JSONStoreError("读取文件失败: " + std::string(e.what()));
    }
}

void JSONStore::write(const nlohmann::json& data, bool validate) {
    std::lock_guard<std::mutex> lock(mutex_);
    
    // 验证数据
    if (validate && validate_func_) {
        if (!validate_func_(data)) {
            throw ValidationError("数据验证失败");
        }
    }
    
    // 备份旧文件
    if (auto_backup_ && fs::exists(file_path_)) {
        create_backup_();
    }
    
    // 原子写入
    write_internal_(data);
}

void JSONStore::write_internal_(const nlohmann::json& data) {
    try {
        std::string temp_file = file_path_ + ".tmp";
        
        // 写入临时文件
        std::ofstream file(temp_file);
        if (!file.is_open()) {
            throw JSONStoreError("无法创建临时文件: " + temp_file);
        }
        
        file << std::setw(indent_) << data << std::endl;
        file.close();
        
        // 原子重命名
        fs::rename(temp_file, file_path_);
    }
    catch (const std::exception& e) {
        std::string temp_file = file_path_ + ".tmp";
        try {
            if (fs::exists(temp_file)) {
                fs::remove(temp_file);
            }
        }
        catch (...) {}
        throw JSONStoreError("写入文件失败: " + std::string(e.what()));
    }
}

nlohmann::json JSONStore::update(UpdateFunc update_func) {
    std::lock_guard<std::mutex> lock(mutex_);
    
    // 读取当前数据
    nlohmann::json data = nlohmann::json::object();
    if (fs::exists(file_path_)) {
        std::ifstream file(file_path_);
        if (file.is_open()) {
            file >> data;
        }
    }
    
    // 应用更新
    nlohmann::json new_data = update_func(data);
    
    // 写入新数据
    write_internal_(new_data);
    
    return new_data;
}

bool JSONStore::delete_file(bool create_backup) {
    std::lock_guard<std::mutex> lock(mutex_);
    
    try {
        if (!fs::exists(file_path_)) {
            return false;
        }
        
        if (create_backup) {
            create_backup_();
        }
        
        fs::remove(file_path_);
        return true;
    }
    catch (const std::exception& e) {
        throw JSONStoreError("删除文件失败: " + std::string(e.what()));
    }
}

bool JSONStore::exists() const {
    return fs::exists(file_path_);
}

size_t JSONStore::get_size() const {
    if (!fs::exists(file_path_)) {
        return 0;
    }
    return fs::file_size(file_path_);
}

std::string JSONStore::create_backup_() {
    if (!fs::exists(file_path_)) {
        return "";
    }
    
    // 生成备份文件名
    auto now = std::chrono::system_clock::now();
    auto time = std::chrono::system_clock::to_time_t(now);
    struct tm* tm_info = localtime(&time);
    
    char timestamp[20];
    strftime(timestamp, sizeof(timestamp), "%Y%m%d_%H%M%S", tm_info);
    
    fs::path p(file_path_);
    std::string backup_name = p.stem().string() + "_backup_" + timestamp + p.extension().string();
    fs::path backup_path = p.parent_path() / backup_name;
    
    // 复制文件
    fs::copy_file(file_path_, backup_path, fs::copy_options::overwrite_existing);
    
    // 清理旧备份
    cleanup_old_backups_();
    
    return backup_path.string();
}

void JSONStore::cleanup_old_backups_() {
    fs::path p(file_path_);
    std::string pattern = p.stem().string() + "_backup_";
    
    std::vector<fs::path> backups;
    for (const auto& entry : fs::directory_iterator(p.parent_path())) {
        if (entry.path().filename().string().find(pattern) != std::string::npos) {
            backups.push_back(entry.path());
        }
    }
    
    // 按修改时间排序
    std::sort(backups.begin(), backups.end(), 
        [](const fs::path& a, const fs::path& b) {
            return fs::last_write_time(a) > fs::last_write_time(b);
        }
    );
    
    // 删除超过最大数量的备份
    for (size_t i = max_backups_; i < backups.size(); ++i) {
        try {
            fs::remove(backups[i]);
        }
        catch (...) {}
    }
}

std::string JSONStore::compress(const std::string& output_path) {
    if (!fs::exists(file_path_)) {
        throw FileNotFoundError("文件不存在: " + file_path_);
    }
    
    std::string final_output = output_path.empty() 
        ? file_path_ + ".gz"
        : output_path;
    
    try {
        std::ifstream source(file_path_, std::ios::binary);
        gzFile dest = gzopen(final_output.c_str(), "wb");
        
        if (!source.is_open() || !dest) {
            throw JSONStoreError("无法打开文件进行压缩");
        }
        
        char buffer[1024];
        while (source.read(buffer, sizeof(buffer))) {
            gzwrite(dest, buffer, source.gcount());
        }
        
        source.close();
        gzclose(dest);
        
        return final_output;
    }
    catch (const std::exception& e) {
        throw JSONStoreError("压缩文件失败: " + std::string(e.what()));
    }
}

void JSONStore::decompress(const std::string& compressed_path) {
    if (!fs::exists(compressed_path)) {
        throw FileNotFoundError("压缩文件不存在: " + compressed_path);
    }
    
    try {
        gzFile source = gzopen(compressed_path.c_str(), "rb");
        std::ofstream dest(file_path_, std::ios::binary);
        
        if (!source || !dest.is_open()) {
            throw JSONStoreError("无法打开文件进行解压缩");
        }
        
        char buffer[1024];
        int bytes;
        while ((bytes = gzread(source, buffer, sizeof(buffer))) > 0) {
            dest.write(buffer, bytes);
        }
        
        gzclose(source);
        dest.close();
    }
    catch (const std::exception& e) {
        throw JSONStoreError("解压缩文件失败: " + std::string(e.what()));
    }
}

// ============= DictJSONStore 类实现 =============

DictJSONStore::DictJSONStore(const std::string& file_path, 
    const std::map<std::string, std::string>& kwargs)
    : JSONStore(file_path) {
    // 解析 kwargs 中的参数
}

nlohmann::json DictJSONStore::get(const std::string& key, const nlohmann::json& default_value) {
    nlohmann::json data = read(nlohmann::json::object());
    if (data.contains(key)) {
        return data[key];
    }
    return default_value;
}

void DictJSONStore::set(const std::string& key, const nlohmann::json& value) {
    auto update_func = [&](nlohmann::json data) {
        if (!data.is_object()) {
            data = nlohmann::json::object();
        }
        data[key] = value;
        return data;
    };
    update(update_func);
}

bool DictJSONStore::delete_key(const std::string& key) {
    auto update_func = [&](nlohmann::json data) {
        if (data.is_object() && data.contains(key)) {
            data.erase(key);
        }
        return data;
    };
    update(update_func);
    return true;
}

bool DictJSONStore::has_key(const std::string& key) {
    nlohmann::json data = read(nlohmann::json::object());
    return data.is_object() && data.contains(key);
}

std::vector<std::string> DictJSONStore::keys() {
    nlohmann::json data = read(nlohmann::json::object());
    std::vector<std::string> result;
    if (data.is_object()) {
        for (const auto& [k, v] : data.items()) {
            result.push_back(k);
        }
    }
    return result;
}

std::vector<nlohmann::json> DictJSONStore::values() {
    nlohmann::json data = read(nlohmann::json::object());
    std::vector<nlohmann::json> result;
    if (data.is_object()) {
        for (const auto& [k, v] : data.items()) {
            result.push_back(v);
        }
    }
    return result;
}

std::vector<std::pair<std::string, nlohmann::json>> DictJSONStore::items() {
    nlohmann::json data = read(nlohmann::json::object());
    std::vector<std::pair<std::string, nlohmann::json>> result;
    if (data.is_object()) {
        for (const auto& [k, v] : data.items()) {
            result.push_back({k, v});
        }
    }
    return result;
}

void DictJSONStore::clear() {
    write(nlohmann::json::object());
}

void DictJSONStore::merge(const nlohmann::json& other, bool overwrite) {
    auto update_func = [&](nlohmann::json data) {
        if (!data.is_object()) {
            data = nlohmann::json::object();
        }
        
        if (overwrite) {
            data.update(other);
        }
        else {
            for (const auto& [k, v] : other.items()) {
                if (!data.contains(k)) {
                    data[k] = v;
                }
            }
        }
        return data;
    };
    update(update_func);
}

// ============= ListJSONStore 类实现 =============

ListJSONStore::ListJSONStore(const std::string& file_path,
    const std::map<std::string, std::string>& kwargs)
    : JSONStore(file_path) {
}

void ListJSONStore::append(const nlohmann::json& item) {
    auto update_func = [&](nlohmann::json data) {
        if (!data.is_array()) {
            data = nlohmann::json::array();
        }
        data.push_back(item);
        return data;
    };
    update(update_func);
}

void ListJSONStore::extend(const nlohmann::json& items) {
    auto update_func = [&](nlohmann::json data) {
        if (!data.is_array()) {
            data = nlohmann::json::array();
        }
        if (items.is_array()) {
            for (const auto& item : items) {
                data.push_back(item);
            }
        }
        return data;
    };
    update(update_func);
}

bool ListJSONStore::remove(const nlohmann::json& item) {
    auto update_func = [&](nlohmann::json data) {
        if (data.is_array()) {
            auto it = std::find(data.begin(), data.end(), item);
            if (it != data.end()) {
                data.erase(it);
            }
        }
        return data;
    };
    update(update_func);
    return true;
}

nlohmann::json ListJSONStore::remove_at(int index) {
    nlohmann::json removed_item = nlohmann::json::null();
    
    auto update_func = [&](nlohmann::json data) {
        if (data.is_array() && index >= 0 && index < data.size()) {
            removed_item = data[index];
            data.erase(index);
        }
        return data;
    };
    update(update_func);
    
    return removed_item;
}

nlohmann::json ListJSONStore::get_at(int index, const nlohmann::json& default_value) {
    nlohmann::json data = read(nlohmann::json::array());
    if (data.is_array() && index >= 0 && index < data.size()) {
        return data[index];
    }
    return default_value;
}

size_t ListJSONStore::length() {
    nlohmann::json data = read(nlohmann::json::array());
    if (data.is_array()) {
        return data.size();
    }
    return 0;
}

void ListJSONStore::clear() {
    write(nlohmann::json::array());
}

void ListJSONStore::filter(FilterFunc filter_func) {
    auto update_func = [&](nlohmann::json data) {
        if (data.is_array()) {
            nlohmann::json filtered = nlohmann::json::array();
            for (const auto& item : data) {
                if (filter_func(item)) {
                    filtered.push_back(item);
                }
            }
            return filtered;
        }
        return data;
    };
    update(update_func);
}

// ============= LogStore 类实现 =============

LogStore::LogStore(
    const std::string& directory,
    const std::string& prefix,
    int max_entries_per_file,
    bool auto_rotate
)
    : directory_(directory),
      prefix_(prefix),
      max_entries_per_file_(max_entries_per_file),
      auto_rotate_(auto_rotate) {
    fs::create_directories(directory);
}

std::string LogStore::get_current_file_path_() {
    auto now = std::chrono::system_clock::now();
    auto time = std::chrono::system_clock::to_time_t(now);
    struct tm* tm_info = localtime(&time);
    
    char timestamp[10];
    strftime(timestamp, sizeof(timestamp), "%Y%m%d", tm_info);
    
    fs::path dir(directory_);
    return (dir / (prefix_ + "_" + timestamp + ".json")).string();
}

ListJSONStore* LogStore::get_current_store_() {
    std::string file_path = get_current_file_path_();
    
    if (current_store_ == nullptr || current_store_->file_path_ != file_path) {
        current_store_ = std::make_unique<ListJSONStore>(file_path);
    }
    
    // 检查是否需要轮转
    if (auto_rotate_) {
        size_t length = current_store_->length();
        if (length >= max_entries_per_file_) {
            rotate_();
        }
    }
    
    return current_store_.get();
}

void LogStore::rotate_() {
    auto now = std::chrono::system_clock::now();
    auto time = std::chrono::system_clock::to_time_t(now);
    struct tm* tm_info = localtime(&time);
    
    char timestamp[20];
    strftime(timestamp, sizeof(timestamp), "%Y%m%d_%H%M%S", tm_info);
    
    fs::path dir(directory_);
    std::string new_path = (dir / (prefix_ + "_" + timestamp + ".json")).string();
    current_store_ = std::make_unique<ListJSONStore>(new_path);
}

void LogStore::add_log(nlohmann::json log_entry) {
    // 自动添加时间戳
    if (!log_entry.contains("timestamp")) {
        auto now = std::chrono::system_clock::now();
        auto duration = now.time_since_epoch();
        log_entry["timestamp"] = duration.count();
    }
    
    ListJSONStore* store = get_current_store_();
    store->append(log_entry);
}

std::vector<nlohmann::json> LogStore::get_logs(
    const std::chrono::system_clock::time_point& start_date,
    const std::chrono::system_clock::time_point& end_date,
    FilterFunc filter_func) {
    
    std::vector<nlohmann::json> logs;
    
    // 获取所有日志文件
    fs::path dir(directory_);
    std::string pattern = prefix_ + "_";
    
    std::vector<fs::path> log_files;
    for (const auto& entry : fs::directory_iterator(dir)) {
        if (entry.path().filename().string().find(pattern) != std::string::npos) {
            log_files.push_back(entry.path());
        }
    }
    
    // 排序日志文件
    std::sort(log_files.begin(), log_files.end());
    
    // 读取所有日志
    for (const auto& file_path : log_files) {
        ListJSONStore store(file_path.string());
        nlohmann::json data = store.read(nlohmann::json::array());
        
        if (data.is_array()) {
            for (const auto& item : data) {
                logs.push_back(item);
            }
        }
    }
    
    // 自定义过滤
    if (filter_func) {
        std::vector<nlohmann::json> filtered;
        for (const auto& log : logs) {
            if (filter_func(log)) {
                filtered.push_back(log);
            }
        }
        return filtered;
    }
    
    return logs;
}

int LogStore::clear_old_logs(int days) {
    auto cutoff_time = std::time(nullptr) - (days * 24 * 3600);
    int deleted_count = 0;
    
    fs::path dir(directory_);
    std::string pattern = prefix_ + "_";
    
    for (const auto& entry : fs::directory_iterator(dir)) {
        if (entry.path().filename().string().find(pattern) != std::string::npos) {
            auto write_time = fs::last_write_time(entry.path());
            auto sctp = std::chrono::time_point_cast<std::chrono::seconds>(write_time);
            auto time_t_val = std::chrono::system_clock::to_time_t(sctp);
            
            if (time_t_val < cutoff_time) {
                try {
                    fs::remove(entry.path());
                    deleted_count++;
                }
                catch (...) {}
            }
        }
    }
    
    return deleted_count;
}
