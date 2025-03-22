-- 等待MySQL初始化完成
SELECT 1 FROM DUAL;

-- 創建數據庫
CREATE DATABASE IF NOT EXISTS blog_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- 使用新創建的數據庫
USE blog_db;

-- 禁用主機緩存
SET GLOBAL host_cache_size=0;

-- 設置認證策略
SET GLOBAL authentication_policy='caching_sha2_password';

-- 確保我們有足夠的權限
SELECT CURRENT_USER();

-- 授予權限給blog_user
CREATE USER IF NOT EXISTS 'blog_user'@'%' IDENTIFIED WITH caching_sha2_password BY 'yourpassword';
GRANT ALL PRIVILEGES ON blog_db.* TO 'blog_user'@'%';

-- 刷新權限
FLUSH PRIVILEGES;

-- 設置時區
SET GLOBAL time_zone = '+00:00';
