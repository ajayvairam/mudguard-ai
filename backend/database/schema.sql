-- =====================================================================
-- MediGuard AI - Supabase PostgreSQL Database Schema & RLS Policies
-- =====================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Profiles Table (Holds user metadata & language preference, NO Profile UI page exists)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT,
    email TEXT,
    avatar_url TEXT,
    preferred_language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Prescriptions Table
CREATE TABLE IF NOT EXISTS public.prescriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    file_url TEXT,
    file_name TEXT NOT NULL,
    file_type VARCHAR(50),
    doctor_name TEXT,
    prescription_date DATE,
    raw_text TEXT,
    ocr_confidence NUMERIC(4, 2) DEFAULT 1.00,
    status VARCHAR(50) DEFAULT 'uploaded', -- uploaded, processing, analysed, failed
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Medicines Table
CREATE TABLE IF NOT EXISTS public.medicines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prescription_id UUID NOT NULL REFERENCES public.prescriptions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    original_name TEXT NOT NULL,
    normalized_name TEXT,
    generic_name TEXT,
    active_ingredient TEXT,
    strength VARCHAR(50),
    dosage VARCHAR(50),
    frequency VARCHAR(100),
    duration VARCHAR(50),
    route VARCHAR(50) DEFAULT 'oral',
    instructions TEXT,
    confidence NUMERIC(4, 2) DEFAULT 0.95,
    requires_verification BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Medication Analysis Table
CREATE TABLE IF NOT EXISTS public.medication_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    medicine_a_id UUID REFERENCES public.medicines(id) ON DELETE SET NULL,
    medicine_b_id UUID REFERENCES public.medicines(id) ON DELETE SET NULL,
    medicine_a_name TEXT,
    medicine_b_name TEXT,
    analysis_type VARCHAR(50) NOT NULL, -- duplicate, interaction, overlap, dosage_concern, conflict
    severity VARCHAR(20) DEFAULT 'LOW', -- LOW, MODERATE, HIGH, CRITICAL
    description TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    source TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Consolidated Medications Table
CREATE TABLE IF NOT EXISTS public.consolidated_medications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    analysis_id UUID,
    medicine_name TEXT NOT NULL,
    generic_name TEXT,
    strength VARCHAR(50),
    dosage VARCHAR(50),
    frequency VARCHAR(100),
    duration VARCHAR(50),
    instructions TEXT,
    status VARCHAR(50) DEFAULT 'active',
    requires_review BOOLEAN DEFAULT FALSE,
    review_reason TEXT,
    source_prescriptions TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Reminders Table
CREATE TABLE IF NOT EXISTS public.reminders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    medicine_id UUID REFERENCES public.medicines(id) ON DELETE SET NULL,
    medicine_name TEXT NOT NULL,
    dose VARCHAR(50) NOT NULL,
    time TIME NOT NULL,
    frequency VARCHAR(50) DEFAULT 'once_daily',
    start_date DATE DEFAULT CURRENT_DATE,
    end_date DATE,
    instructions TEXT,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. Reminder History Table
CREATE TABLE IF NOT EXISTS public.reminder_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reminder_id UUID NOT NULL REFERENCES public.reminders(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    scheduled_at TIMESTAMPTZ NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, taken, missed, skipped
    taken_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================================
-- Indexes for Performance
-- =====================================================================
CREATE INDEX IF NOT EXISTS idx_prescriptions_user ON public.prescriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_medicines_prescription ON public.medicines(prescription_id);
CREATE INDEX IF NOT EXISTS idx_medicines_user ON public.medicines(user_id);
CREATE INDEX IF NOT EXISTS idx_medication_analysis_user ON public.medication_analysis(user_id);
CREATE INDEX IF NOT EXISTS idx_consolidated_user ON public.consolidated_medications(user_id);
CREATE INDEX IF NOT EXISTS idx_reminders_user ON public.reminders(user_id);
CREATE INDEX IF NOT EXISTS idx_reminder_history_reminder ON public.reminder_history(reminder_id);

-- =====================================================================
-- Row Level Security (RLS) Policies
-- =====================================================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.prescriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.medicines ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.medication_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.consolidated_medications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reminders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reminder_history ENABLE ROW LEVEL SECURITY;

-- Profiles: Users can select and update their own profile
CREATE POLICY "Users can view own profile" ON public.profiles FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update own profile" ON public.profiles FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own profile" ON public.profiles FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Prescriptions
CREATE POLICY "Users can manage own prescriptions" ON public.prescriptions FOR ALL USING (auth.uid() = user_id);

-- Medicines
CREATE POLICY "Users can manage own medicines" ON public.medicines FOR ALL USING (auth.uid() = user_id);

-- Analysis
CREATE POLICY "Users can manage own analyses" ON public.medication_analysis FOR ALL USING (auth.uid() = user_id);

-- Consolidated
CREATE POLICY "Users can manage own consolidated plans" ON public.consolidated_medications FOR ALL USING (auth.uid() = user_id);

-- Reminders
CREATE POLICY "Users can manage own reminders" ON public.reminders FOR ALL USING (auth.uid() = user_id);

-- Reminder History
CREATE POLICY "Users can manage own reminder history" ON public.reminder_history FOR ALL USING (auth.uid() = user_id);

-- =====================================================================
-- Storage Bucket for Prescriptions
-- =====================================================================
INSERT INTO storage.buckets (id, name, public) 
VALUES ('prescriptions', 'prescriptions', false)
ON CONFLICT (id) DO NOTHING;

-- Storage RLS policy
CREATE POLICY "Users can upload own prescriptions" 
ON storage.objects FOR INSERT 
WITH CHECK (bucket_id = 'prescriptions' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can view own prescription files" 
ON storage.objects FOR SELECT 
USING (bucket_id = 'prescriptions' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can delete own prescription files" 
ON storage.objects FOR DELETE 
USING (bucket_id = 'prescriptions' AND auth.uid()::text = (storage.foldername(name))[1]);
