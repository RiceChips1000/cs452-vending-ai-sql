"""Ask questions about the vending machine database in plain English.

Flow: question -> GPT (with schema) -> SQL -> SQLite -> GPT -> plain-English answer

Usage:
    python app.py                       # zero-shot (default)
    python app.py --strategy few-shot   # include example question/SQL pairs
"""
import argparse
import os
import sqlite3

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

MODEL = "gpt-4o-mini"
DB_FILE = "vending.db"

# Strategy 1 (zero-shot): the schema is all the model gets.
# Foreign keys are in the schema text, and sample rows are added below.
FEW_SHOT_EXAMPLES = """
Q: Which machines are currently active?
SQL: SELECT name, location FROM vending_machine WHERE status = 'active';

Q: How much money has each machine made?
SQL: SELECT vm.name, SUM(s.price_sold_at) / 100.0 AS total_dollars
     FROM sale s JOIN vending_machine vm ON vm.vending_machine_id = s.vending_machine_id
     GROUP BY vm.vending_machine_id;

Q: What is the profit on each product sold?
SQL: SELECT p.name, SUM(s.price_sold_at - p.buy_price) / 100.0 AS profit_dollars
     FROM sale s JOIN product p ON p.product_id = s.product_id
     GROUP BY p.product_id;
"""


def get_schema_and_samples(conn):
    """Schema text (with foreign keys) plus 3 sample rows per table."""
    parts = []
    tables = conn.execute("SELECT name, sql FROM sqlite_master WHERE type='table'").fetchall()
    for name, create_sql in tables:
        parts.append(create_sql + ";")
        rows = conn.execute(f"SELECT * FROM {name} LIMIT 3").fetchall()
        parts.append(f"-- sample rows from {name}: {rows}")
    return "\n".join(parts)


def ask_gpt(system, user):
    resp = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
    )
    return resp.choices[0].message.content.strip()


def question_to_sql(question, schema, strategy):
    system = (
        "You write SQLite queries. Given the database schema, reply with ONE SQL "
        "SELECT query and nothing else (no markdown, no explanation). "
        "Prices are stored in cents."
    )
    user = f"Schema:\n{schema}\n"
    if strategy == "few-shot":
        user += f"\nExamples:\n{FEW_SHOT_EXAMPLES}\n"
    user += f"\nQ: {question}\nSQL:"
    sql = ask_gpt(system, user)
    return sql.replace("```sql", "").replace("```", "").strip()


def run_sql(conn, sql):
    # Only allow reads
    if not sql.lstrip().lower().startswith("select"):
        raise ValueError("Refusing to run non-SELECT query")
    cur = conn.execute(sql)
    cols = [c[0] for c in cur.description]
    return cols, cur.fetchall()


def answer_in_english(question, sql, cols, rows):
    system = "You answer questions about a vending machine business in friendly plain English. Prices in the data are in cents; show dollars."
    user = f"Question: {question}\nSQL used: {sql}\nColumns: {cols}\nRows: {rows}\n\nAnswer the question."
    return ask_gpt(system, user)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", choices=["zero-shot", "few-shot"], default="zero-shot")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_FILE)
    schema = get_schema_and_samples(conn)
    print(f"Vending machine assistant ({args.strategy}). Type 'quit' to exit.")

    while True:
        question = input("\nAsk a question: ").strip()
        if question.lower() in ("quit", "exit", ""):
            break
        sql = question_to_sql(question, schema, args.strategy)
        print(f"\nSQL: {sql}")
        try:
            cols, rows = run_sql(conn, sql)
        except Exception as e:
            print(f"SQL failed: {e}")
            continue
        print(f"Rows: {rows}")
        print(f"\nAnswer: {answer_in_english(question, sql, cols, rows)}")


if __name__ == "__main__":
    main()
