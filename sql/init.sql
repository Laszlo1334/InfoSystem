create table if not exists resources (
  id            bigserial primary key,
  name          text        not null,
  author        text,
  annotation    text,
  kind          text,
  purpose       text,
  open_date     date,
  expiry_date   date,
  usage_conditions text,
  url           text,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

create table if not exists app_users (
  id         bigserial primary key,
  full_name  text not null,
  email      text unique
);

create table if not exists usage_stats (
  id           bigserial primary key,
  resource_id  bigint not null references resources(id) on delete cascade,
  user_id      bigint not null references app_users(id) on delete cascade,
  usage_count  integer not null default 0,
  last_access  timestamptz,
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now(),
  unique(resource_id, user_id)
);

create or replace function set_updated_at() returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists trg_resources_updated on resources;
create trigger trg_resources_updated
before update on resources
for each row execute function set_updated_at();

drop trigger if exists trg_usage_stats_updated on usage_stats;
create trigger trg_usage_stats_updated
before update on usage_stats
for each row execute function set_updated_at();

insert into app_users (full_name, email) values
  ('Admin User', 'admin@example.com'),
  ('Student One', 'student1@example.com'),
  ('Student Two', 'student2@example.com')
on conflict do nothing;

create index if not exists idx_resources_updated_at on resources (updated_at desc);
create index if not exists idx_usage_stats_res on usage_stats (resource_id);
create index if not exists idx_usage_stats_user on usage_stats (user_id);
