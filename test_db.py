import sqlite3
import os

def audit_full_database():
    db_path = "enterprise_decision_system.db"
    size_bytes = os.path.getsize(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tables = [r[0] for r in cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';").fetchall()]

    total_rows = 0
    print("=" * 80)
    print(f"DATABASE FILE:   {os.path.abspath(db_path)}")
    print(f"FILE SIZE:       {size_bytes:,} bytes ({size_bytes / 1024:.2f} KB)")
    print(f"TOTAL TABLES:    {len(tables)}")
    print("=" * 80)

    for i, t in enumerate(tables, 1):
        cnt = cursor.execute(f"SELECT COUNT(*) FROM {t};").fetchone()[0]
        total_rows += cnt
        cols = [col[1] for col in cursor.execute(f"PRAGMA table_info({t});").fetchall()]
        print(f"{i:2d}. {t.ljust(35)} | {cnt:5d} records | Columns: {len(cols)}")

    print("=" * 80)
    print(f"TOTAL ROWS PERSISTED IN SQLITE: {total_rows:,} ROWS")
    print("=" * 80)
    conn.close()

if __name__ == "__main__":
    audit_full_database()
