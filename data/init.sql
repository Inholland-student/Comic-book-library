-- Comic Library Database Schema

USE comic_library;

-- Users table with roles and passwords
CREATE TABLE IF NOT EXISTS users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(255) NOT NULL UNIQUE,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('super_admin', 'admin', 'friend') NOT NULL DEFAULT 'friend',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_username (username),
  INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Comics table
CREATE TABLE IF NOT EXISTS comics (
  id INT PRIMARY KEY AUTO_INCREMENT,
  serie VARCHAR(255) NOT NULL,
  number VARCHAR(50) NOT NULL,
  title VARCHAR(255) NOT NULL,
  created_by INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_serie (serie),
  INDEX idx_created_by (created_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create initial super_admin user (password: changeme)
-- Note: In production, this should be replaced by a proper admin creation flow
-- Password hash for "changeme" created with bcrypt (cost factor 12)
INSERT INTO users (username, email, password_hash, role) 
VALUES ('super_admin', 'super_admin@library.local', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lm', 'super_admin')
ON DUPLICATE KEY UPDATE username=username;
