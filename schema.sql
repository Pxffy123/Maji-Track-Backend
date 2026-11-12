-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'citizen',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Water Points Table
CREATE TABLE water_points (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    latitude DECIMAL(9, 6) NOT NULL,
    longitude DECIMAL(9, 6) NOT NULL,
    region VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'functional',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reports Table
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    water_point_id INT REFERENCES water_points(id) ON DELETE CASCADE,
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    issue_description TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Maintenance Table
CREATE TABLE maintenance (
    id SERIAL PRIMARY KEY,
    water_point_id INT REFERENCES water_points(id) ON DELETE CASCADE,
    technician_id INT REFERENCES users(id) ON DELETE SET NULL,
    action_taken TEXT NOT NULL,
    cost DECIMAL(10, 2),
    maintenance_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
