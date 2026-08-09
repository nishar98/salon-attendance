-- Salon Attendance App — Database Schema
-- Run this in the Supabase SQL Editor to set up your tables.

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- USERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'associate' CHECK (role IN ('admin', 'associate')),
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'locked', 'inactive')),
    failed_login_attempts INT NOT NULL DEFAULT 0,
    locked_until TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================
-- SITE TABLE (Geofence configuration)
-- ============================================
CREATE TABLE IF NOT EXISTS site (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL DEFAULT 'Salon',
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    radius_m INT NOT NULL DEFAULT 10 CHECK (radius_m >= 5 AND radius_m <= 50),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================
-- PUNCH RECORDS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS punch_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(3) NOT NULL CHECK (type IN ('in', 'out')),
    server_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    gps_accuracy_m DECIMAL(6, 2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for fast history lookup per user
CREATE INDEX IF NOT EXISTS idx_punch_records_user_time
    ON punch_records (user_id, server_timestamp DESC);

-- ============================================
-- SEED DATA
-- ============================================

-- Insert default site (UPDATE these coordinates to your salon's actual GPS location!)
-- Example: Using a placeholder — replace with your salon's lat/lng from Google Maps.
INSERT INTO site (name, latitude, longitude, radius_m, updated_at)
VALUES ('Salon', 6.9271000, 79.8612000, 10, NOW())
ON CONFLICT DO NOTHING;

-- Insert initial Admin account
-- Password: Admin@1234 (hashed with bcrypt)
-- IMPORTANT: Change this password after first login!
INSERT INTO users (name, email, password_hash, role, status)
VALUES (
    'Salon Owner',
    'admin@salon.com',
    '$2b$12$0olMrciiiCPbwGceN6aOiOcGc2MA8JTFAdWHhx/IMFYCiIFm1ILdy',
    'admin',
    'active'
)
ON CONFLICT (email) DO NOTHING;
