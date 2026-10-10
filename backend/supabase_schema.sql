-- Optional remote document store. Run in the project's Supabase SQL editor.
-- Actions, activity and reminder delivery still require a persistent DATA_DIR.
create table if not exists public.documents (
    id text primary key,
    user_id text not null,
    filename text not null,
    total_pages integer not null,
    file_size_bytes integer not null,
    word_count integer not null,
    file_path text not null,
    raw_text_json jsonb not null,
    created_at timestamptz not null default now()
);
create table if not exists public.analyses (
    id text primary key,
    user_id text not null,
    document_id text not null references public.documents(id) on delete cascade,
    result_json jsonb not null,
    engine_used text not null,
    risk_score integer not null,
    contract_type text not null,
    created_at timestamptz not null default now()
);
create index if not exists documents_user_idx on public.documents(user_id);
create index if not exists analyses_user_idx on public.analyses(user_id, created_at desc);
alter table public.documents enable row level security;
alter table public.analyses enable row level security;
-- The API uses the backend-only service key and applies an owner filter on every read.
-- Authenticated browser clients may read only their own rows; writes go through the API.
drop policy if exists "clauseguard_owner_read" on public.documents;
create policy "clauseguard_owner_read" on public.documents for select to authenticated
    using ((select auth.uid())::text = user_id);
drop policy if exists "clauseguard_owner_read" on public.analyses;
create policy "clauseguard_owner_read" on public.analyses for select to authenticated
    using ((select auth.uid())::text = user_id);
