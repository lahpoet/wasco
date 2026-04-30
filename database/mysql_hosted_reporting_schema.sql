-- Hosted MySQL schema for WASCO reporting/fragment database
-- Run this on Railway MySQL before using the admin Sync Now button.

SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS districts (
    district_id INT AUTO_INCREMENT PRIMARY KEY,
    district_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS branches (
    branch_id INT AUTO_INCREMENT PRIMARY KEY,
    branch_name VARCHAR(100) NOT NULL UNIQUE,
    district_id INT NOT NULL,
    location TEXT NOT NULL,
    phone VARCHAR(30),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (district_id) REFERENCES districts(district_id)
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    account_number VARCHAR(50) NOT NULL UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    phone VARCHAR(30),
    email VARCHAR(100),
    address TEXT NOT NULL,
    district_id INT NOT NULL,
    branch_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (district_id) REFERENCES districts(district_id),
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('customer','admin','manager') NOT NULL,
    branch_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

CREATE TABLE IF NOT EXISTS billing_rates (
    rate_id INT AUTO_INCREMENT PRIMARY KEY,
    rate_tier VARCHAR(50) NOT NULL,
    min_usage DECIMAL(10,2) NOT NULL,
    max_usage DECIMAL(10,2),
    cost_per_unit DECIMAL(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS meter_readings (
    reading_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    reading_month VARCHAR(20) NOT NULL,
    previous_reading DECIMAL(10,2) NOT NULL,
    current_reading DECIMAL(10,2) NOT NULL,
    usage_units DECIMAL(10,2) GENERATED ALWAYS AS (current_reading - previous_reading) STORED,
    reading_date DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS bills (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    reading_id INT NOT NULL,
    billing_month VARCHAR(20) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_status ENUM('unpaid','partial','paid') DEFAULT 'unpaid',
    due_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (reading_id) REFERENCES meter_readings(reading_id)
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    bill_id INT NOT NULL,
    customer_id INT NOT NULL,
    amount_paid DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50),
    payment_reference VARCHAR(100),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bill_id) REFERENCES bills(bill_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    bill_id INT,
    message TEXT NOT NULL,
    notification_type VARCHAR(50),
    status VARCHAR(30) DEFAULT 'pending',
    sent_at TIMESTAMP NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (bill_id) REFERENCES bills(bill_id)
);

CREATE TABLE IF NOT EXISTS leakage_reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    location TEXT NOT NULL,
    description TEXT,
    report_status VARCHAR(30) DEFAULT 'reported',
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

SET FOREIGN_KEY_CHECKS = 1;
