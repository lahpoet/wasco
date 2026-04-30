DROP TABLE IF EXISTS leakage_reports, notifications, payments, bills, meter_readings, billing_rates, users, customers, districts CASCADE;

CREATE TABLE districts (
    district_id SERIAL PRIMARY KEY,
    district_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    account_number VARCHAR(50) NOT NULL UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    phone VARCHAR(30),
    email VARCHAR(100),
    address TEXT NOT NULL,
    district_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (district_id) REFERENCES districts(district_id)
);

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    customer_id INT,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(30) NOT NULL CHECK (role IN ('customer', 'admin', 'manager')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE billing_rates (
    rate_id SERIAL PRIMARY KEY,
    rate_tier VARCHAR(50) NOT NULL,
    min_usage DECIMAL(10,2) NOT NULL,
    max_usage DECIMAL(10,2),
    cost_per_unit DECIMAL(10,2) NOT NULL
);

CREATE TABLE meter_readings (
    reading_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    reading_month VARCHAR(20) NOT NULL,
    previous_reading DECIMAL(10,2) NOT NULL,
    current_reading DECIMAL(10,2) NOT NULL,
    usage_units DECIMAL(10,2) GENERATED ALWAYS AS (current_reading - previous_reading) STORED,
    reading_date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE bills (
    bill_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    reading_id INT NOT NULL,
    billing_month VARCHAR(20) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_status VARCHAR(30) DEFAULT 'unpaid'
        CHECK (payment_status IN ('unpaid', 'partial', 'paid')),
    due_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (reading_id) REFERENCES meter_readings(reading_id)
);

CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    bill_id INT NOT NULL,
    customer_id INT NOT NULL,
    amount_paid DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50),
    payment_reference VARCHAR(100),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bill_id) REFERENCES bills(bill_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE notifications (
    notification_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    bill_id INT,
    message TEXT NOT NULL,
    notification_type VARCHAR(50),
    status VARCHAR(30) DEFAULT 'pending',
    sent_at TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (bill_id) REFERENCES bills(bill_id)
);

CREATE TABLE leakage_reports (
    report_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    location TEXT NOT NULL,
    description TEXT,
    report_status VARCHAR(30) DEFAULT 'reported',
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

INSERT INTO districts (district_name) VALUES
('Maseru'),('Berea'),('Leribe'),('Butha-Buthe'),('Mokhotlong'),('Thaba-Tseka'),('Mafeteng'),('Mohale''s Hoek'),('Quthing'),('Qacha''s Nek');

INSERT INTO customers (account_number, full_name, phone, email, address, district_id) VALUES
('WS-10001','Thabo Mokoena','62000001','thabo.mokoena@example.com','Maseru West, Maseru',1),
('WS-10002','Lerato Nkosi','62000002','lerato.nkosi@example.com','Hlotse, Leribe',3),
('WS-10003','Kabelo Sello','62000003','kabelo.sello@example.com','Teyateyaneng, Berea',2);

INSERT INTO billing_rates (rate_tier, min_usage, max_usage, cost_per_unit) VALUES
('Lifeline',0,10,2.50),
('Domestic Standard',11,30,3.50),
('High Consumption',31,NULL,5.00);

INSERT INTO meter_readings (customer_id, reading_month, previous_reading, current_reading) VALUES
(1,'January 2026',100,120),
(2,'January 2026',200,240),
(3,'January 2026',150,180),
(1,'February 2026',120,137),
(2,'February 2026',240,263);

INSERT INTO bills (customer_id, reading_id, billing_month, total_amount, payment_status, due_date) VALUES
(1,1,'January 2026',70.00,'paid','2026-02-10'),
(2,2,'January 2026',150.00,'partial','2026-02-10'),
(3,3,'January 2026',105.00,'unpaid','2026-02-10'),
(1,4,'February 2026',59.50,'unpaid','2026-03-10'),
(2,5,'February 2026',80.50,'unpaid','2026-03-10');

INSERT INTO payments (bill_id, customer_id, amount_paid, payment_method, payment_reference) VALUES
(1,1,70.00,'Mobile Money','PAY-10001'),
(2,2,50.00,'Bank Transfer','PAY-10002');

INSERT INTO leakage_reports (customer_id, location, description) VALUES
(1,'Maseru West Main Road','Visible pipe leakage near the service line.'),
(3,'Teyateyaneng Market Area','Continuous water flow near public tap.');

-- Passwords:
-- admin / Admin@2026
-- manager / Manager@2026
-- customer / Customer@2026
INSERT INTO users (customer_id, username, password_hash, role) VALUES
(NULL,'admin','scrypt:32768:8:1$RC8rPMuhAi7aZG3a$03490f0340c03a127ebf706291d1dbd88d7471e3e89396ed100deeb9101c620000535a636fdd491735ebcffcb8671441784c43e5762be13763a27cae679cddbb','admin'),
(NULL,'manager','scrypt:32768:8:1$seXkOE0FSJNODa7X$22c7e9bec8f087b0393580089e975e6f611537263a6f378b4df1d09a8f0d69f565777ad5f3cd8afc13a3ad01cc4d5fcae4e7f94437a5f80af1e01e1a','manager'),
(1,'customer','scrypt:32768:8:1$BU1WeUYmoCi8K5XI$8d5f45e16fc80e6b3a10bed89059ff5812f7d3a6f5477ded549de0290c87a3461b8f98eb0d8cc73be5f265fa382f2ba7ca35dc05752ec8f8fdcb700a6317f','customer');