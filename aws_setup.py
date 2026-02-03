"""
=============================================================
STEP 2: AWS SETUP — S3 + RDS (PostgreSQL)
=============================================================
Prerequisites:
  1. Install dependencies:
       pip install boto3 psycopg2-binary
  2. Configure AWS CLI:
       aws configure
       (Enter your Access Key, Secret Key, Region: ap-south-1)
  3. Make sure your CSVs are in a folder called 'ecommerce_data'
     in the same directory as this script.
=============================================================
"""

import boto3
import os
import time
import json

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
REGION = "ap-south-1"                        # Mumbai region (closest to Bengaluru)
BUCKET_NAME = "ecommerce-raw-data-asif"      # Change this to something unique
RDS_INSTANCE_ID = "ecommerce-db"
RDS_DB_NAME = "ecomdb"
RDS_USERNAME = "dbadmin"
RDS_PASSWORD = "SecurePass123!"              # Change this to something strong
RDS_INSTANCE_CLASS = "db.t3.micro"           # Free tier eligible
CSV_FOLDER = "ecommerce_data"                # folder with your CSVs

# ─────────────────────────────────────────────
# STEP 2A: CREATE S3 BUCKET & UPLOAD CSVs
# ─────────────────────────────────────────────
def setup_s3():
    print("\n🚀 Setting up S3 Bucket...")
    s3 = boto3.client("s3", region_name=REGION)

    # Create bucket
    try:
        s3.create_bucket(
            Bucket=BUCKET_NAME,
            CreateBucketConfiguration={"LocationConstraint": REGION}
        )
        print(f"✅ Bucket '{BUCKET_NAME}' created successfully.")
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"ℹ️  Bucket '{BUCKET_NAME}' already exists. Skipping creation.")
    except Exception as e:
        print(f"❌ Error creating bucket: {e}")
        return False

    # Upload CSVs
    csv_files = ["customers.csv", "products.csv", "orders.csv", "order_items.csv", "returns.csv"]
    for file in csv_files:
        local_path = os.path.join(CSV_FOLDER, file)
        s3_key = f"raw/{file}"  # Store inside a 'raw/' prefix for organisation
        if os.path.exists(local_path):
            s3.upload_file(local_path, BUCKET_NAME, s3_key)
            print(f"  📤 Uploaded: {file} → s3://{BUCKET_NAME}/{s3_key}")
        else:
            print(f"  ⚠️  File not found: {local_path}")

    print("✅ S3 setup complete!\n")
    return True


# ─────────────────────────────────────────────
# STEP 2B: CREATE RDS POSTGRESQL INSTANCE
# ─────────────────────────────────────────────
def setup_rds():
    print("🚀 Setting up RDS (PostgreSQL)...")
    rds = boto3.client("rds", region_name=REGION)
    ec2 = boto3.client("ec2", region_name=REGION)

    # --- Create a Security Group that allows PostgreSQL (port 5432) from your IP ---
    # We'll open it to 0.0.0.0/0 for simplicity during dev (restrict later in production)
    sg_response = ec2.create_security_group(
        GroupName="ecommerce-rds-sg",
        Description="Security group for ecommerce RDS"
    )
    sg_id = sg_response["GroupId"]
    print(f"  🔐 Security Group created: {sg_id}")

    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpProtocol="tcp",
        FromPort=5432,
        ToPort=5432,
        CidrIp="0.0.0.0/0"  # ⚠️ For dev only. Lock down in production!
    )
    print("  🔐 Ingress rule added for port 5432")

    # --- Create RDS Instance ---
    try:
        rds.create_db_instance(
            DBInstanceIdentifier=RDS_INSTANCE_ID,
            DBInstanceClass=RDS_INSTANCE_CLASS,
            Engine="mysql",                          # Using MySQL (free tier friendly)
            MasterUsername=RDS_USERNAME,
            MasterUserPassword=RDS_PASSWORD,
            DBName=RDS_DB_NAME,
            AllocatedStorage=20,                     # 20 GB (free tier max)
            Port=3306,
            VpcSecurityGroupIds=[sg_id],
            BackupRetentionPeriod=0,                 # Disable backups for free tier
            MultiAZ=False,
            PubliclyAccessible=True,                 # So we can connect locally
            StorageType="gp2"
        )
        print(f"  ✅ RDS instance '{RDS_INSTANCE_ID}' is being created...")
        print("  ⏳ This takes 3-5 minutes. Waiting...\n")

    except rds.exceptions.DBInstanceAlreadyExistsFault:
        print(f"  ℹ️  RDS instance '{RDS_INSTANCE_ID}' already exists. Skipping creation.")

    # --- Wait for RDS to be available ---
    waiter = rds.get_waiter("db_instance_available")
    waiter.wait(DBInstanceIdentifier=RDS_INSTANCE_ID)
    print("  ✅ RDS instance is now AVAILABLE!\n")

    # --- Get the endpoint ---
    response = rds.describe_db_instances(DBInstanceIdentifier=RDS_INSTANCE_ID)
    endpoint = response["DBInstances"][0]["Endpoint"]["Address"]
    print(f"  🌐 RDS Endpoint: {endpoint}")
    print(f"  👤 Username:     {RDS_USERNAME}")
    print(f"  🔑 Password:     {RDS_PASSWORD}")
    print(f"  🗄️  Database:     {RDS_DB_NAME}\n")

    # Save endpoint to a config file for the next step
    config = {
        "host": endpoint,
        "port": 3306,
        "database": RDS_DB_NAME,
        "username": RDS_USERNAME,
        "password": RDS_PASSWORD,
        "s3_bucket": BUCKET_NAME,
        "region": REGION
    }
    with open("db_config.json", "w") as f:
        json.dump(config, f, indent=2)
    print("  💾 Config saved to db_config.json (use this in Step 3)")

    print("✅ RDS setup complete!\n")
    return True


# ─────────────────────────────────────────────
# STEP 2C: CREATE TABLES IN RDS (MySQL)
# ─────────────────────────────────────────────
def create_tables(endpoint):
    import pymysql  # pip install pymysql

    print("🚀 Creating tables in RDS...")
    conn = pymysql.connect(
        host=endpoint,
        user=RDS_USERNAME,
        password=RDS_PASSWORD,
        database=RDS_DB_NAME
    )
    cursor = conn.cursor()

    # --- CUSTOMERS ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id   INT PRIMARY KEY AUTO_INCREMENT,
            first_name    VARCHAR(100) NOT NULL,
            last_name     VARCHAR(100) NOT NULL,
            age           INT,
            city          VARCHAR(100),
            signup_date   DATE
        );
    """)
    print("  ✅ Table 'customers' created")

    # --- PRODUCTS ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id    INT PRIMARY KEY AUTO_INCREMENT,
            product_name  VARCHAR(150) NOT NULL,
            category      VARCHAR(100) NOT NULL,
            price         DECIMAL(10, 2) NOT NULL
        );
    """)
    print("  ✅ Table 'products' created")

    # --- ORDERS ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id      INT PRIMARY KEY AUTO_INCREMENT,
            customer_id   INT NOT NULL,
            order_date    DATE NOT NULL,
            status        VARCHAR(50) NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );
    """)
    print("  ✅ Table 'orders' created")

    # --- ORDER ITEMS ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id   INT PRIMARY KEY AUTO_INCREMENT,
            order_id        INT NOT NULL,
            product_id      INT NOT NULL,
            quantity        INT NOT NULL,
            discount_percent DECIMAL(5, 2) DEFAULT 0,
            FOREIGN KEY (order_id)   REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );
    """)
    print("  ✅ Table 'order_items' created")

    # --- RETURNS ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS returns (
            return_id       INT PRIMARY KEY AUTO_INCREMENT,
            order_item_id   INT NOT NULL,
            order_id        INT NOT NULL,
            return_date     DATE,
            reason          VARCHAR(200),
            FOREIGN KEY (order_item_id) REFERENCES order_items(order_item_id),
            FOREIGN KEY (order_id)      REFERENCES orders(order_id)
        );
    """)
    print("  ✅ Table 'returns' created")

    conn.commit()
    conn.close()
    print("\n✅ All tables created successfully!\n")


# ─────────────────────────────────────────────
# RUN EVERYTHING
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  E-COMMERCE PROJECT — AWS SETUP (S3 + RDS)")
    print("=" * 55)

    # Step 2A
    s3_ok = setup_s3()

    # Step 2B
    rds_ok = setup_rds()

    # Step 2C — Create tables (runs after RDS is ready)
    if rds_ok:
        # Read endpoint from saved config
        with open("db_config.json", "r") as f:
            config = json.load(f)
        create_tables(config["host"])

    print("=" * 55)
    print("  ✅ STEP 2 COMPLETE — Ready for Step 3 (Data Load)")
    print("=" * 55)
