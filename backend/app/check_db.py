import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "lab_booking.db"))

def check():
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Database file not found at: {DB_PATH}")
        return

    print("=" * 80)
    print(f" SQLite Database Inspector: {DB_PATH}")
    print(f" File Size: {os.path.getsize(DB_PATH):,} bytes")
    print("=" * 80)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tables = ["USERS", "LABORATORIES", "LAB_EQUIPMENT", "BOOKINGS", "APPROVALS"]

    for tbl in tables:
        print(f"\n" + "-" * 80)
        print(f" TABLE: {tbl}")
        print("-" * 80)

        cursor.execute(f"PRAGMA table_info({tbl})")
        cols = [col[1] for col in cursor.fetchall()]

        cursor.execute(f"SELECT * FROM {tbl}")
        rows = cursor.fetchall()

        if not rows:
            print("  (Table is currently empty)")
        else:
            # Print column headers
            header_str = " | ".join(cols[:6])
            print(f"  {header_str}")
            print("  " + "-" * len(header_str))
            for r in rows:
                row_str = " | ".join(str(val) if val is not None else "NULL" for val in r[:6])
                print(f"  {row_str}")

        print(f"  -> Total rows in {tbl}: {len(rows)}")

    conn.close()
    print("\n" + "=" * 80)
    print(" Inspection complete! All tables are active and persistent.")
    print("=" * 80)

if __name__ == "__main__":
    check()
