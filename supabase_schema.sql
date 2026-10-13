-- ==============================================================================
-- EduGenie Database Schema for Supabase
-- Paste this script into your Supabase SQL Editor:
-- https://supabase.com/dashboard/project/uynwotrrtcyrwkfhxdws/sql
-- ==============================================================================

-- 1. Create History Table for Questions, Explanations, Summaries, Quizzes & Roadmaps
CREATE TABLE IF NOT EXISTS public.edugenie_history (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    module_type VARCHAR(50) NOT NULL, -- 'qa', 'explain', 'summarize', 'quiz', 'roadmap'
    prompt_text TEXT NOT NULL,
    response_text TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- 2. Create Quiz Score Table for Student Assessment Tracking
CREATE TABLE IF NOT EXISTS public.quiz_scores (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    topic TEXT NOT NULL,
    score INT NOT NULL,
    total_questions INT NOT NULL,
    percentage NUMERIC(5, 2) GENERATED ALWAYS AS (ROUND((score::NUMERIC / NULLIF(total_questions, 0)) * 100, 2)) STORED
);

-- 3. Enable Row Level Security (RLS)
ALTER TABLE public.edugenie_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quiz_scores ENABLE ROW LEVEL SECURITY;

-- 4. Create Policies for Public Access
CREATE POLICY "Allow public read edugenie_history" ON public.edugenie_history
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert edugenie_history" ON public.edugenie_history
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public read quiz_scores" ON public.quiz_scores
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert quiz_scores" ON public.quiz_scores
    FOR INSERT WITH CHECK (true);

-- 5. Create Indices for Fast Lookup
CREATE INDEX IF NOT EXISTS idx_edugenie_history_module ON public.edugenie_history (module_type);
CREATE INDEX IF NOT EXISTS idx_edugenie_history_created ON public.edugenie_history (created_at DESC);
