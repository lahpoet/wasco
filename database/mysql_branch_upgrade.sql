-- MySQL branch upgrade for wasco_fragment_db

INSERT IGNORE INTO districts (district_name) VALUES
('Maseru'),
('Berea'),
('Leribe'),
('Butha-Buthe'),
('Mokhotlong'),
('Thaba-Tseka'),
('Mafeteng'),
('Mohale''s Hoek'),
('Quthing'),
('Qacha''s Nek');

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

INSERT IGNORE INTO branches (branch_name, district_id, location, phone, email)
SELECT 'Maseru Branch', district_id, 'Maseru', '22210001', 'maseru@wasco.co.ls'
FROM districts WHERE district_name = 'Maseru';

INSERT IGNORE INTO branches (branch_name, district_id, location, phone, email)
SELECT 'Berea Branch', district_id, 'Teyateyaneng', '22210002', 'berea@wasco.co.ls'
FROM districts WHERE district_name = 'Berea';

INSERT IGNORE INTO branches (branch_name, district_id, location, phone, email)
SELECT 'Leribe Branch', district_id, 'Hlotse', '22210003', 'leribe@wasco.co.ls'
FROM districts WHERE district_name = 'Leribe';

INSERT IGNORE INTO branches (branch_name, district_id, location, phone, email)
SELECT 'Butha-Buthe Branch', district_id, 'Butha-Buthe', '22210004', 'bb@wasco.co.ls'
FROM districts WHERE district_name = 'Butha-Buthe';

INSERT IGNORE INTO branches (branch_name, district_id, location, phone, email)
SELECT 'Mafeteng Branch', district_id, 'Mafeteng', '22210007', 'mafeteng@wasco.co.ls'
FROM districts WHERE district_name = 'Mafeteng';

ALTER TABLE customers ADD COLUMN branch_id INT NULL;
ALTER TABLE users ADD COLUMN branch_id INT NULL;

-- If the foreign key already exists, MySQL may raise duplicate constraint error.
-- Only run these once if they are not already added.
ALTER TABLE customers
ADD CONSTRAINT fk_customers_branch
FOREIGN KEY (branch_id) REFERENCES branches(branch_id);

ALTER TABLE users
ADD CONSTRAINT fk_users_branch
FOREIGN KEY (branch_id) REFERENCES branches(branch_id);

UPDATE customers c
JOIN branches br ON br.district_id = c.district_id
SET c.branch_id = br.branch_id
WHERE c.branch_id IS NULL;

UPDATE users
SET branch_id = (SELECT branch_id FROM branches WHERE branch_name = 'Maseru Branch' LIMIT 1)
WHERE username = 'manager';