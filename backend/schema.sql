CREATE DATABASE IF NOT EXISTS crowdbuy
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE crowdbuy;

CREATE TABLE IF NOT EXISTS users (
  id CHAR(36) PRIMARY KEY,
  role ENUM('pyme', 'agro') NOT NULL,
  contact_name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NULL,
  company_name VARCHAR(255) NULL,
  phone VARCHAR(50) NULL,
  area VARCHAR(255) NULL,
  products TEXT NULL,
  business_size VARCHAR(255) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lots (
  id VARCHAR(20) PRIMARY KEY,
  product VARCHAR(255) NOT NULL,
  producer VARCHAR(255) NOT NULL,
  target_kilos DECIMAL(12,2) NOT NULL,
  current_kilos DECIMAL(12,2) NOT NULL DEFAULT 0,
  base_price DECIMAL(12,2) NOT NULL,
  deadline DATETIME NOT NULL,
  status ENUM('active', 'completed', 'expired', 'deactivated') NOT NULL DEFAULT 'active',
  created_by CHAR(36) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_lots_created_by FOREIGN KEY (created_by) REFERENCES users(id)
    ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS commitments (
  id CHAR(36) PRIMARY KEY,
  lot_id VARCHAR(20) NOT NULL,
  user_id CHAR(36) NULL,
  kilos DECIMAL(12,2) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_commitments_lot FOREIGN KEY (lot_id) REFERENCES lots(id)
    ON DELETE CASCADE,
  CONSTRAINT fk_commitments_user FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS demand_predictions (
  id CHAR(36) PRIMARY KEY,
  lot_id VARCHAR(20) NOT NULL,
  labels JSON NOT NULL,
  datasets JSON NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_predictions_lot FOREIGN KEY (lot_id) REFERENCES lots(id)
    ON DELETE CASCADE
);

ALTER TABLE lots MODIFY status
  ENUM('active', 'completed', 'expired', 'deactivated')
  NOT NULL DEFAULT 'active';
