"""Build vending.db from schema.sql and seed.sql."""
import os
import sqlite3

DB_FILE = "vending.db"

if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

conn = sqlite3.connect(DB_FILE)
for script in ("schema.sql", "seed.sql"):
    with open(script) as f:
        conn.executescript(f.read())
conn.commit()
conn.close()
print(f"Created {DB_FILE}")
