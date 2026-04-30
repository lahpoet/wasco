-- PostgreSQL branch upgrade for wasco_main_db
-- Run this after your existing tables are already created.

-- 1) Make sure all Lesotho districts exist.
INSERT INTO districts (district_name) VALUES
('Maseru'),
('Berea'),
('Leribe'),
('Butha-Buthe'),
('Mokhotlong'),
('Thaba-Tseka'),
('Mafeteng'),
('Mohale''s Hoek'),
('Quthing'),
('Qacha''s Nek')
ON CONFLICT (district_name) DO NOTHING;

-- 2) Create branches table.
CREATE TABLE IF NOT EXISTS branches (
    branch_id SERIAL PRIMARY KEY,
    branch_name VARCHAR(100) NOT NULL UNIQUE,
    district_id INT NOT NULL,
    location TEXT NOT NULL,
    phone VARCHAR(30),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (district_id) REFERENCES districts(district_id)
);

-- 3) Insert branches safely using district names instead of guessed IDs.
INSERT INTO branches (branch_name, district_id, location, phone, email)
SELECT 'Maseru Branch', district_id, 'Maseru', '22210001', 'maseru@wasco.co.ls'
FROM districts WHERE district_name = 'Maseru'
ON CONFLICT (branch_name) DO NOTHING;

INSERT INTO branches (branch_name, district_id, location, phone, email)
SELECT 'Berea Branch', district_id, 'Teyateyaneng', '22210002', 'berea@wasco.co.ls'
FROM districts WHERE district_name = 'Berea'
ON CONFLICT (branch_name) DO NOTHING;

INSERT INTO branches (branch_name, district_id, location, phone, email)
SELECT 'Leribe Branch', district_id, 'Hlotse', '22210003', 'leribe@wasco.co.ls'
FROM districts WHERE district_name = 'Leribe'
ON CONFLICT (branch_name) DO NOTHING;

INSERT INTO branches (branch_name, district_id, location, phone, email)
SELECT 'Butha-Buthe Branch', district_id, 'Butha-Buthe', '22210004', 'bb@wasco.co.ls'
FROM districts WHERE district_name = 'Butha-Buthe'
ON CONFLICT (branch_name) DO NOTHING;

INSERT INTO branches (branch_name, district_id, location, phone, email)
SELECT 'Mafeteng Branch', district_id, 'Mafeteng', '22210007', 'mafeteng@wasco.co.ls'
FROM districts WHERE district_name = 'Mafeteng'
ON CONFLICT (branch_name) DO NOTHING;

-- 4) Add branch_id to customers and users.
ALTER TABLE customers ADD COLUMN IF NOT EXISTS branch_id INT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS branch_id INT;

-- 5) Add constraints safely.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_customers_branch'
    ) THEN
        ALTER TABLE customers
        ADD CONSTRAINT fk_customers_branch
        FOREIGN KEY (branch_id) REFERENCES branches(branch_id);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_users_branch'
    ) THEN
        ALTER TABLE users
        ADD CONSTRAINT fk_users_branch
        FOREIGN KEY (branch_id) REFERENCES branches(branch_id);
    END IF;
END $$;

-- 6) Assign old customers to matching branches by district.
UPDATE customers c
SET branch_id = br.branch_id
FROM branches br
WHERE c.district_id = br.district_id
AND c.branch_id IS NULL;

-- 7) Assign manager to Maseru Branch if manager exists.
UPDATE users
SET branch_id = (SELECT branch_id FROM branches WHERE branch_name = 'Maseru Branch' LIMIT 1)
WHERE username = 'manager';

-- 8) Useful branch performance view.
CREATE OR REPLACE VIEW vw_branch_performance AS
SELECT 
    br.branch_id,
    br.branch_name,
    d.district_name,
    COUNT(DISTINCT c.customer_id) AS total_customers,
    COUNT(DISTINCT b.bill_id) AS total_bills,
    COALESCE(SUM(m.usage_units), 0) AS total_usage,
    COALESCE(SUM(b.total_amount), 0) AS total_billed,
    COALESCE(SUM(p.amount_paid), 0) AS total_paid,
    COALESCE(SUM(b.total_amount), 0) - COALESCE(SUM(p.amount_paid), 0) AS outstanding_balance
FROM branches br
JOIN districts d ON d.district_id = br.district_id
LEFT JOIN customers c ON c.branch_id = br.branch_id
LEFT JOIN bills b ON b.customer_id = c.customer_id
LEFT JOIN meter_readings m ON m.reading_id = b.reading_id
LEFT JOIN payments p ON p.bill_id = b.bill_id
GROUP BY br.branch_id, br.branch_name, d.district_name;