-- ============================================================
-- VerifiKlaim — Patch Migration (ADDITIVE ONLY)
-- Schema utama sudah dibuat oleh dashboard-web migration.
-- File ini HANYA menambahkan:
--   1. Kolom tambahan di scoring_history (kalau belum ada)
--   2. Tabel app_users (belum ada di schema sebelumnya)
--   3. RLS service_role bypass untuk FastAPI backend
-- ============================================================

-- ── 1. Patch scoring_history — tambah kolom yang belum ada ────────
ALTER TABLE scoring_history ADD COLUMN IF NOT EXISTS source           TEXT DEFAULT 'single';
ALTER TABLE scoring_history ADD COLUMN IF NOT EXISTS batch_id         TEXT;
ALTER TABLE scoring_history ADD COLUMN IF NOT EXISTS claim_id         TEXT;
ALTER TABLE scoring_history ADD COLUMN IF NOT EXISTS facility         TEXT;
ALTER TABLE scoring_history ADD COLUMN IF NOT EXISTS amount           FLOAT8;
ALTER TABLE scoring_history ADD COLUMN IF NOT EXISTS los              FLOAT8;
ALTER TABLE scoring_history ADD COLUMN IF NOT EXISTS patient_category TEXT;
ALTER TABLE scoring_history ADD COLUMN IF NOT EXISTS claim_type       TEXT;
ALTER TABLE scoring_history ADD COLUMN IF NOT EXISTS diagnosis_group  TEXT;

-- ── 2. app_users — tabel baru, belum ada di schema sebelumnya ─────
CREATE TABLE IF NOT EXISTS public.app_users (
  id          TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  name        TEXT NOT NULL,
  email       TEXT UNIQUE NOT NULL,
  role        TEXT NOT NULL DEFAULT 'verifier',
  org         TEXT DEFAULT '',
  status      TEXT DEFAULT 'Active',
  last_active TIMESTAMPTZ DEFAULT NOW(),
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ── 3. Patch tabel claims dari schema lama ─────────────────────────
-- Schema baru punya UUID id, kita tambah kolom yg dibutuhkan backend
ALTER TABLE public.claims ADD COLUMN IF NOT EXISTS risk_score   NUMERIC  DEFAULT 0;
ALTER TABLE public.claims ADD COLUMN IF NOT EXISTS risk_percent NUMERIC  DEFAULT 0;
ALTER TABLE public.claims ADD COLUMN IF NOT EXISTS priority     TEXT     DEFAULT 'Low';
ALTER TABLE public.claims ADD COLUMN IF NOT EXISTS status       TEXT     DEFAULT 'New';
ALTER TABLE public.claims ADD COLUMN IF NOT EXISTS reviewer     TEXT     DEFAULT '';
ALTER TABLE public.claims ADD COLUMN IF NOT EXISTS top_factors  JSONB    DEFAULT '[]'::jsonb;
ALTER TABLE public.claims ADD COLUMN IF NOT EXISTS source       TEXT     DEFAULT 'single';
ALTER TABLE public.claims ADD COLUMN IF NOT EXISTS last_note    TEXT     DEFAULT '';
ALTER TABLE public.claims ADD COLUMN IF NOT EXISTS facility_name_text TEXT;
ALTER TABLE public.claims ADD COLUMN IF NOT EXISTS org_name_text      TEXT;

-- ── 4. Patch batch_uploads — tambah kolom summary ─────────────────
ALTER TABLE public.batch_uploads ADD COLUMN IF NOT EXISTS high   INT DEFAULT 0;
ALTER TABLE public.batch_uploads ADD COLUMN IF NOT EXISTS medium INT DEFAULT 0;
ALTER TABLE public.batch_uploads ADD COLUMN IF NOT EXISTS low    INT DEFAULT 0;

-- ── 5. Patch audit_events — tambah kolom text untuk backend ───────
-- Schema baru pakai actor_id (UUID) + detail (jsonb)
-- Kita tambah kolom text agar backend bisa insert tanpa auth.uid()
ALTER TABLE public.audit_events ADD COLUMN IF NOT EXISTS actor_name_text TEXT;
ALTER TABLE public.audit_events ADD COLUMN IF NOT EXISTS category        TEXT DEFAULT 'claim';
ALTER TABLE public.audit_events ADD COLUMN IF NOT EXISTS "timestamp"     TIMESTAMPTZ DEFAULT NOW();

-- ── 6. RLS — service_role bypass untuk FastAPI backend ────────────
-- FastAPI pakai service_role key → perlu policy yang allow all

ALTER TABLE public.app_users        ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scoring_history  ENABLE ROW LEVEL SECURITY;

-- scoring_history
DROP POLICY IF EXISTS "service_all_scoring_history" ON public.scoring_history;
DROP POLICY IF EXISTS "anon_select_scoring_history"  ON public.scoring_history;
CREATE POLICY "service_all_scoring_history"
  ON public.scoring_history FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "anon_select_scoring_history"
  ON public.scoring_history FOR SELECT TO anon USING (true);

-- claims — tambah service_role policy di atas policy auth yang sudah ada
DROP POLICY IF EXISTS "service_all_claims" ON public.claims;
CREATE POLICY "service_all_claims"
  ON public.claims FOR ALL TO service_role USING (true) WITH CHECK (true);

-- batch_uploads
DROP POLICY IF EXISTS "service_all_batch_uploads" ON public.batch_uploads;
CREATE POLICY "service_all_batch_uploads"
  ON public.batch_uploads FOR ALL TO service_role USING (true) WITH CHECK (true);

-- audit_events
DROP POLICY IF EXISTS "service_all_audit_events" ON public.audit_events;
CREATE POLICY "service_all_audit_events"
  ON public.audit_events FOR ALL TO service_role USING (true) WITH CHECK (true);

-- app_users
DROP POLICY IF EXISTS "service_all_app_users" ON public.app_users;
DROP POLICY IF EXISTS "anon_select_app_users"  ON public.app_users;
CREATE POLICY "service_all_app_users"
  ON public.app_users FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "anon_select_app_users"
  ON public.app_users FOR SELECT TO anon USING (true);

-- ── 7. Seed — app_users ───────────────────────────────────────────
INSERT INTO public.app_users (id, name, email, role, org, status, last_active) VALUES
  ('usr-001', 'Sari Wulandari', 'sari.w@rsharapan.co.id',     'verifier', 'RS Harapan Sehat',            'Active',   NOW() - INTERVAL '2 hours'),
  ('usr-002', 'Dimas Rahardjo', 'dimas.r@rsudcitra.go.id',     'verifier', 'RSUD Citra Medika',           'Active',   NOW() - INTERVAL '1 hour'),
  ('usr-003', 'Reza Hermawan',  'reza.h@bpjs-kesehatan.go.id', 'auditor',  'BPJS Cabang Jakarta Selatan', 'Active',   NOW() - INTERVAL '3 hours'),
  ('usr-004', 'Anita Pertiwi',  'anita.p@kliniksehat.co.id',   'verifier', 'Klinik Sehat Bersama',        'Active',   NOW() - INTERVAL '16 hours'),
  ('usr-005', 'Budi Santoso',   'budi.s@jkn-regional.go.id',   'auditor',  'JKN Regional Review Unit',    'Active',   NOW() - INTERVAL '2 hours'),
  ('usr-006', 'Admin Sistem',   'admin@verifiklaim.id',         'admin',    'Platform Admin',              'Active',   NOW() - INTERVAL '15 hours'),
  ('usr-007', 'Hendra Gunawan', 'hendra.g@rsudmedan.go.id',    'verifier', 'RSUD Kota Medan',             'Inactive', NOW() - INTERVAL '12 days'),
  ('usr-008', 'Fitri Andriani', 'fitri.a@bpjs-bandung.go.id',  'auditor',  'BPJS Cabang Bandung',         'Pending',  NOW())
ON CONFLICT (id) DO NOTHING;

-- ── 8. Seed — audit_events ────────────────────────────────────────
INSERT INTO public.audit_events (id, actor_name, actor_role, action, entity_type, entity_id, category, detail, created_at) VALUES
  (gen_random_uuid(), 'Sari W.',    'Verifier', 'Review status changed',    'Claim', 'CLM-2026-01482', 'review',  '{"note":"Status changed from New to Needs Review"}'::jsonb, NOW() - INTERVAL '5 hours'),
  (gen_random_uuid(), 'Sari W.',    'Verifier', 'Batch uploaded',           'Batch', 'BTH-2026-0521',  'batch',   '{"note":"48 claims ingested for processing"}'::jsonb,        NOW() - INTERVAL '15 hours'),
  (gen_random_uuid(), 'Reza H.',    'Auditor',  'Claim escalated',          'Claim', 'CLM-2026-01510', 'review',  '{"note":"Escalated - score 0.84, surgical high-value"}'::jsonb, NOW() - INTERVAL '6 hours'),
  (gen_random_uuid(), 'Admin User', 'Admin',    'User role changed',        'User',  'usr-005',        'user',    '{"note":"Role changed: Verifier to Auditor"}'::jsonb,         NOW() - INTERVAL '1 day'),
  (gen_random_uuid(), 'System',     'System',   'Artifact version updated', 'Model', 'artifact-v031',  'system',  '{"note":"Model artifact updated to v0.3.1"}'::jsonb,          NOW() - INTERVAL '7 days');
