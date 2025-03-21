-- 等待MySQL初始化完成
SELECT 1 FROM DUAL;

-- 創建數據庫
CREATE DATABASE IF NOT EXISTS blog_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- 使用新創建的數據庫
USE blog_db;

-- 確保我們有足夠的權限
SELECT CURRENT_USER();

-- 授予權限給blog_user (如果需要)
GRANT ALL PRIVILEGES ON blog_db.* TO 'blog_user'@'%';

-- 刷新權限
FLUSH PRIVILEGES;
