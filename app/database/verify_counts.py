"""Script to execute raw SQL queries on the actual database and display table counts."""

import sqlite3
import os


def verify_database():
    db_file = "hospital_ops.db"
    if not os.path.exists(db_file):
        print(f"Database file '{db_file}' not found.")
        return

    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [r[0] for r in cur.fetchall()]
    print(f"Actual Database Tables ({len(tables)}):")
    for t in sorted(tables):
        print(f"  - {t}")

    print("\nActual Database Record Counts via Raw SQL:")
    for t in sorted(tables):
        cur.execute(f"SELECT count(*) FROM {t}")
        cnt = cur.fetchone()[0]
        print(f"  - {t}: {cnt}")

    print("\nInventory Breakdown by Hospital:")
    cur.execute(
        "SELECT h.name, h.city, count(i.id) "
        "FROM inventory_items i "
        "JOIN hospitals h ON i.hospital_id = h.id "
        "GROUP BY h.id, h.name, h.city"
    )
    for name, city, count in cur.fetchall():
        print(f"  - {name} ({city}): {count} inventory items")

    conn.close()


if __name__ == "__main__":
    verify_database()
