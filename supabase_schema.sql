-- ==============================================================================
-- MediGuard AI — Supabase Database Schema
-- Run this in your Supabase SQL Editor: Dashboard -> SQL Editor -> New Query
-- ==============================================================================

-- 1. Profiles Table
CREATE TABLE IF NOT EXISTS public.profiles (
    id TEXT PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL,
    full_name TEXT,
    email TEXT,
    avatar_url TEXT,
    preferred_language TEXT DEFAULT 'en',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 2. Prescriptions Table
CREATE TABLE IF NOT EXISTS public.prescriptions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    file_url TEXT,
    file_name TEXT NOT NULL,
    file_type TEXT,
    doctor_name TEXT,
    prescription_date TEXT,
    raw_text TEXT,
    ocr_confidence REAL DEFAULT 1.0,
    status TEXT DEFAULT 'uploaded',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 3. Medicines Table
CREATE TABLE IF NOT EXISTS public.medicines (
    id TEXT PRIMARY KEY,
    prescription_id TEXT NOT NULL REFERENCES public.prescriptions(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    original_name TEXT NOT NULL,
    normalized_name TEXT,
    generic_name TEXT,
    active_ingredient TEXT,
    strength TEXT,
    dosage TEXT,
    frequency TEXT,
    duration TEXT,
    route TEXT DEFAULT 'oral',
    instructions TEXT,
    confidence REAL DEFAULT 0.95,
    requires_verification BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 4. Medication Safety Analysis Warnings Table
CREATE TABLE IF NOT EXISTS public.medication_analysis (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    medicine_a_id TEXT,
    medicine_b_id TEXT,
    medicine_a_name TEXT,
    medicine_b_name TEXT,
    analysis_type TEXT NOT NULL,
    severity TEXT DEFAULT 'LOW',
    description TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    source TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 5. Consolidated Medications Review Table
CREATE TABLE IF NOT EXISTS public.consolidated_medications (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    analysis_id TEXT,
    medicine_name TEXT NOT NULL,
    generic_name TEXT,
    strength TEXT,
    dosage TEXT,
    frequency TEXT,
    duration TEXT,
    instructions TEXT,
    status TEXT DEFAULT 'active',
    requires_review BOOLEAN DEFAULT false,
    review_reason TEXT,
    source_prescriptions JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 6. Reminders Table
CREATE TABLE IF NOT EXISTS public.reminders (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    medicine_id TEXT,
    medicine_name TEXT NOT NULL,
    dose TEXT NOT NULL,
    time TEXT NOT NULL,
    frequency TEXT DEFAULT 'once_daily',
    start_date TEXT,
    end_date TEXT,
    instructions TEXT,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 7. Reminder History Table
CREATE TABLE IF NOT EXISTS public.reminder_history (
    id TEXT PRIMARY KEY,
    reminder_id TEXT NOT NULL REFERENCES public.reminders(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    scheduled_at TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    taken_at TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Enable Row Level Security (RLS) and permissive access for the service role & authenticated users
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.prescriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.medicines ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.medication_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.consolidated_medications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reminders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reminder_history ENABLE ROW LEVEL SECURITY;

-- Allow read/write for all application operations
CREATE POLICY "Allow public read access" ON public.profiles FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public read access" ON public.prescriptions FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public read access" ON public.medicines FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public read access" ON public.medication_analysis FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public read access" ON public.consolidated_medications FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public read access" ON public.reminders FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow public read access" ON public.reminder_history FOR ALL USING (true) WITH CHECK (true);
