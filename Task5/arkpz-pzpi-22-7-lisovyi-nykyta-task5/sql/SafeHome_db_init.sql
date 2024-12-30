IF EXISTS (SELECT * FROM sys.databases WHERE name = 'SafeHome')
BEGIN
    DROP DATABASE SafeHome;
END;
GO

CREATE DATABASE SafeHome;
GO

USE SafeHome;
GO

CREATE TABLE role (
    role_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    role_name NVARCHAR(100) NOT NULL,
    description NVARCHAR(255) NULL
);

CREATE TABLE subscription_plan (
    plan_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    name NVARCHAR(100) NOT NULL,
    max_homes INT NOT NULL,
    max_sensors INT NOT NULL,
    price FLOAT NOT NULL,
    duration_days INT NOT NULL
);

CREATE TABLE default_security_mode (
    mode_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    mode_name NVARCHAR(100) NOT NULL,
    description NVARCHAR(255) NULL
);

-- Переименована таблица с 'user' в 'users'
CREATE TABLE users (  -- Переименована таблица
    user_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    role_id UNIQUEIDENTIFIER NOT NULL,
    name NVARCHAR(100) NOT NULL,
    birthday DATE NULL,
    email NVARCHAR(120) UNIQUE NOT NULL,
    password NVARCHAR(256) NULL,
    google_id NVARCHAR(128) NULL,
    google_refresh_token TEXT NULL,
    created_at DATETIME DEFAULT GETUTCDATE(),
    email_confirmed BIT DEFAULT 0,
    FOREIGN KEY (role_id) REFERENCES role(role_id) ON DELETE CASCADE
);

CREATE TABLE subscription (
    subscription_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    user_id UNIQUEIDENTIFIER NOT NULL,
    plan_id UNIQUEIDENTIFIER NOT NULL,
    start_date DATETIME DEFAULT GETUTCDATE() NOT NULL,
    end_date DATETIME NULL,
    is_active BIT DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,  -- Обновлено имя таблицы
    FOREIGN KEY (plan_id) REFERENCES subscription_plan(plan_id) ON DELETE CASCADE
);

CREATE TABLE home (
    home_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    user_id UNIQUEIDENTIFIER NOT NULL,
    default_mode_id UNIQUEIDENTIFIER NOT NULL,
    name NVARCHAR(100) NOT NULL,
    address NVARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT GETUTCDATE(),
    is_archived BIT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,  -- Обновлено имя таблицы
    FOREIGN KEY (default_mode_id) REFERENCES default_security_mode(mode_id) ON DELETE CASCADE
);

CREATE TABLE mobile_device (
    user_device_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    user_id UNIQUEIDENTIFIER NOT NULL,
    device_token TEXT NOT NULL,
    device_info VARCHAR(256) NULL,
    created_at DATETIME DEFAULT GETUTCDATE(),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE  -- Обновлено имя таблицы
);

CREATE TABLE sensor (
    sensor_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    home_id UNIQUEIDENTIFIER NOT NULL,
    user_id UNIQUEIDENTIFIER NULL,
    name NVARCHAR(100) NOT NULL,
    type NVARCHAR(50) NOT NULL,
    is_closed BIT DEFAULT 0,
    is_active BIT DEFAULT 0,
    is_security_breached BIT DEFAULT 0,
    is_archived BIT DEFAULT 0,
    created_at DATETIME DEFAULT GETUTCDATE(),
    FOREIGN KEY (home_id) REFERENCES home(home_id) ON DELETE CASCADE
);

CREATE TABLE security_user_notifications (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    home_id UNIQUEIDENTIFIER NOT NULL,
    sensor_id UNIQUEIDENTIFIER NULL,
    user_id UNIQUEIDENTIFIER NOT NULL,
    title NVARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    importance NVARCHAR(50) NOT NULL CHECK (importance IN ('low', 'medium', 'high')),
    created_at DATETIME DEFAULT GETUTCDATE(),
    type NVARCHAR(50) NOT NULL,
    data NVARCHAR(MAX) NULL,
    FOREIGN KEY (home_id) REFERENCES home(home_id) ON DELETE CASCADE
);

CREATE TABLE general_user_notifications (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    user_id UNIQUEIDENTIFIER NOT NULL,
    title NVARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    importance NVARCHAR(50) NOT NULL CHECK (importance IN ('low', 'medium', 'high')),
    created_at DATETIME DEFAULT GETUTCDATE(),
    type NVARCHAR(50) NOT NULL,
    data NVARCHAR(MAX) NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE  -- Обновлено имя таблицы
);

-- Вставка данных в таблицу role
INSERT INTO role (role_name, description)
VALUES
    ('user', NULL),
    ('admin', NULL);

-- Вставка данных в таблицу subscription_plan
INSERT INTO subscription_plan (name, max_homes, max_sensors, price, duration_days)
VALUES
    ('premium', 5, 20, 10, 30),
    ('basic', 1, 4, 0, 365);

-- Вставка данных в таблицу default_security_mode
INSERT INTO default_security_mode (mode_name, description)
VALUES
    ('security', 'all sensors on'),
    ('custom', 'user changed default security mode'),
    ('safety', 'all sensors off');

-- Получение ID роли 'admin' для вставки в таблицу users
DECLARE @admin_role_id UNIQUEIDENTIFIER;
SELECT @admin_role_id = role_id FROM role WHERE role_name = 'admin';

-- Вставка данных в таблицу users с указанием role_id
INSERT INTO users (email, password, email_confirmed, role_id)
VALUES
    ('admin@safehome.com', 'admin', 1, @admin_role_id);
