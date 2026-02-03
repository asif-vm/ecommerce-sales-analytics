"""
=============================================================
STEP 3: LOAD DATA — S3 → RDS (MySQL)
=============================================================
Prerequisites:
  - Step 2 completed (aws_setup.py ran successfully)
  - db_config.json exists in the same folder as this script
  - pip install boto3 pandas pymysql
=============================================================
"""

import boto3
import pandas as pd
import pymysql
import json
import io
import time

# ─────────────────────────────────────────────
# LOAD CONFIG FROM STEP 2
# ─────────────────────────────────────────────
with open("db_config.json", "r") as f:
    config = json.load(f)

HOST     = config["host"]
PORT     = config["port"]
DATABASE = config["database"]
USERNAME = config["username"]
PASSWORD = config["password"]
BUCKET   = config["s3_bucket"]
REGION   = config["region"]


# ─────────────────────────────────────────────
# CONNECT TO S3 AND RDS
# ─────────────────────────────────────────────
def get_s3_client():
    return boto3.client("s3", region_name=REGION)

def get_db_connection():
    return pymysql.connect(
        host=HOST,
        port=PORT,
        user=USERNAME,
        password=PASSWORD,
        database=DATABASE
    )


# ─────────────────────────────────────────────
# READ CSV FROM S3 INTO A PANDAS DATAFRAME
# ─────────────────────────────────────────────
def read_csv_from_s3(s3, filename):
    key = f"raw/{filename}"
    print(f"  📥 Reading s3://{BUCKET}/{key} ...")
    obj = s3.get_object(Bucket=BUCKET, Key=key)
    df = pd.read_csv(io.StringIO(obj["Body"].read().decode("utf-8")))
    print(f"      → {len(df):,} rows loaded into memory")
    return df


# ─────────────────────────────────────────────
# INSERT FUNCTIONS (one per table)
# ─────────────────────────────────────────────
def insert_customers(cursor, df):
    sql = """
        INSERT INTO customers (customer_id, first_name, last_name, age, city, signup_date)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    rows = [tuple(row) for row in df.itertuples(index=False, name=None)]
    cursor.executemany(sql, rows)
    print(f"      ✅ Inserted {len(rows):,} rows into customers")


def insert_products(cursor, df):
    sql = """
        INSERT INTO products (product_id, product_name, category, price)
        VALUES (%s, %s, %s, %s)
    """
    rows = [tuple(row) for row in df.itertuples(index=False, name=None)]
    cursor.executemany(sql, rows)
    print(f"      ✅ Inserted {len(rows):,} rows into products")


def insert_orders(cursor, df):
    sql = """
        INSERT INTO orders (order_id, customer_id, order_date, status)
        VALUES (%s, %s, %s, %s)
    """
    rows = [tuple(row) for row in df.itertuples(index=False, name=None)]
    cursor.executemany(sql, rows)
    print(f"      ✅ Inserted {len(rows):,} rows into orders")


def insert_order_items(cursor, df):
    sql = """
        INSERT INTO order_items (order_item_id, order_id, product_id, quantity, discount_percent)
        VALUES (%s, %s, %s, %s, %s)
    """
    rows = [tuple(row) for row in df.itertuples(index=False, name=None)]
    cursor.executemany(sql, rows)
    print(f"      ✅ Inserted {len(rows):,} rows into order_items")


def insert_returns(cursor, df):
    sql = """
        INSERT INTO returns (return_id, order_item_id, order_id, return_date, reason)
        VALUES (%s, %s, %s, %s, %s)
    """
    rows = [tuple(row) for row in df.itertuples(index=False, name=None)]
    cursor.executemany(sql, rows)
    print(f"      ✅ Inserted {len(rows):,} rows into returns")


# ─────────────────────────────────────────────
# VERIFY: COUNT ROWS IN EACH TABLE
# ─────────────────────────────────────────────
def verify_data(cursor):
    tables = ["customers", "products", "orders", "order_items", "returns"]
    print("\n📊 Verification — Row counts in RDS:\n")
    print(f"  {'Table':<15} {'Rows':>8}")
    print(f"  {'─'*15} {'─'*8}")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table:<15} {count:>8,}")
    print()


# ─────────────────────────────────────────────
# MAIN — RUN IN ORDER (foreign keys matter!)
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  STEP 3: LOADING DATA FROM S3 → RDS")
    print("=" * 55)

    s3 = get_s3_client()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Order matters! customers & products first, then orders, then order_items, then returns
    load_order = [
        ("customers.csv",   insert_customers),
        ("products.csv",    insert_products),
        ("orders.csv",      insert_orders),
        ("order_items.csv", insert_order_items),
        ("returns.csv",     insert_returns),
    ]

    for filename, insert_fn in load_order:
        print(f"\n📦 Processing: {filename}")
        df = read_csv_from_s3(s3, filename)
        insert_fn(cursor, df)

    # Commit all changes
    conn.commit()
    print("\n💾 All data committed to RDS.\n")

    # Verify
    verify_data(cursor)

    conn.close()

    print("=" * 55)
    print("  ✅ STEP 3 COMPLETE — Data is live in RDS!")
    print("  Next up: Step 4 — SQL Queries")
    print("=" * 55)
