import os
import time
import random
import argparse
import logging
from datetime import date, timedelta

from dotenv import load_dotenv, find_dotenv
from faker import Faker
import psycopg

# Завантажуємо .env з кореня проєкту незалежно від поточної теки
load_dotenv(find_dotenv())

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
fake = Faker()


def build_dsn(args) -> str:
    """Визначаємо DSN у пріоритеті: аргумент командного рядка → DB_DSN → POSTGRES_*."""
    if args.dsn:
        return args.dsn

    dsn = os.getenv("DB_DSN")
    if dsn:
        return dsn

    user = os.getenv("POSTGRES_USER", "metrics")
    password = os.getenv("POSTGRES_PASSWORD", "metrics_pass")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "55432")  # << наш новий порт за замовчуванням
    db = os.getenv("POSTGRES_DB", "metrics_db")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


# ---------------- db ops ----------------
def ensure_min_seed(conn, min_resources: int = 5):
    with conn.cursor() as cur:
        cur.execute("select count(*) from resources")
        (cnt,) = cur.fetchone()
    need = max(0, min_resources - cnt)
    for _ in range(need):
        insert_resource(conn)
    if need:
        logging.info("Seeded %d resources", need)


def random_date_between(start_year=2018, end_year=2025) -> date:
    y = random.randint(start_year, end_year)
    m = random.randint(1, 12)
    d = random.randint(1, 28)
    return date(y, m, d)


def insert_resource(conn) -> int:
    name = f"{fake.word().title()} {fake.word().title()} Resource"
    author = fake.name()
    annotation = fake.paragraph(nb_sentences=3)
    kind = random.choice(["article", "dataset", "video", "tool", "guide"])
    purpose = random.choice(["education", "research", "publication", "lab"])
    open_date = random_date_between()
    expiry_date = open_date + timedelta(days=random.randint(180, 1500))
    usage_conditions = random.choice(["internal", "public", "students-only", "staff-only"])
    url = fake.url()

    with conn.cursor() as cur:
        cur.execute(
            """
            insert into resources (name, author, annotation, kind, purpose, open_date, expiry_date, usage_conditions, url)
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            returning id
            """,
            (name, author, annotation, kind, purpose, open_date, expiry_date, usage_conditions, url),
        )
        (rid,) = cur.fetchone()
    conn.commit()
    logging.info("INSERT resource id=%s (%s)", rid, name)
    return rid


def update_resource(conn) -> int:
    with conn.cursor() as cur:
        cur.execute("select id from resources order by random() limit 1")
        row = cur.fetchone()
    if not row:
        return insert_resource(conn)

    rid = row[0]
    new_annot = fake.paragraph(nb_sentences=2)
    new_kind = random.choice(["article", "dataset", "video", "tool", "guide"])
    with conn.cursor() as cur:
        cur.execute(
            """
            update resources
               set annotation = %s,
                   kind = %s
             where id = %s
            """,
            (new_annot, new_kind, rid),
        )
    conn.commit()
    logging.info("UPDATE resource id=%s", rid)
    return rid


def delete_resource(conn, min_keep: int = 10):
    with conn.cursor() as cur:
        cur.execute("select count(*) from resources")
        (cnt,) = cur.fetchone()
        if cnt <= min_keep:
            logging.info("DELETE skipped (only %d resources, min_keep=%d)", cnt, min_keep)
            return None
        cur.execute("select id from resources order by random() limit 1")
        (rid,) = cur.fetchone()
        cur.execute("delete from resources where id = %s", (rid,))
    conn.commit()
    logging.info("DELETE resource id=%s", rid)
    return rid


def simulate_usage(conn, bursts: int = 3):
    with conn.cursor() as cur:
        cur.execute("select id from app_users")
        users = [r[0] for r in cur.fetchall()]
        cur.execute("select id from resources")
        resources = [r[0] for r in cur.fetchall()]
    if not users or not resources:
        return

    for _ in range(bursts):
        uid = random.choice(users)
        rid = random.choice(resources)
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into usage_stats (resource_id, user_id, usage_count, last_access)
                values (%s,%s,1, now())
                on conflict (resource_id, user_id)
                do update set usage_count = usage_stats.usage_count + 1,
                              last_access  = excluded.last_access
                """,
                (rid, uid),
            )
        conn.commit()
        logging.info("USAGE resource=%s user=%s (+1)", rid, uid)


def run_once(conn, weights=(0.6, 0.3, 0.1)):
    op = random.choices(["insert", "update", "delete"], weights=weights, k=1)[0]
    if op == "insert":
        insert_resource(conn)
    elif op == "update":
        update_resource(conn)
    else:
        delete_resource(conn)
    simulate_usage(conn, bursts=random.randint(1, 4))


def main():
    parser = argparse.ArgumentParser(description="DB activity generator (PostgreSQL)")
    parser.add_argument("--dsn", help="Postgres DSN, напр.: postgresql://user:pass@host:port/db")
    parser.add_argument("--mode", choices=["burst", "continuous"], default="burst")
    parser.add_argument("--ops", type=int, default=50, help="operations in burst mode")
    parser.add_argument("--sleep", type=float, default=1.0, help="delay (s) in continuous mode")
    args = parser.parse_args()

    dsn = build_dsn(args)
    logging.info("Connecting to %s", dsn)

    with psycopg.connect(dsn) as conn:
        ensure_min_seed(conn, min_resources=5)
        if args.mode == "burst":
            for _ in range(args.ops):
                run_once(conn)
            logging.info("Done (burst mode).")
        else:
            logging.info("Continuous mode started. Ctrl+C to stop.")
            try:
                while True:
                    run_once(conn)
                    time.sleep(args.sleep)
            except KeyboardInterrupt:
                logging.info("Stopped by user.")

if __name__ == "__main__":
    main()
