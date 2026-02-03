"""
Fix RDS Security Group - Add your IP to allow connection
Run this after aws_setup.py to fix the timeout error
"""

import boto3
import requests
import json
import pymysql

REGION = "ap-south-1"

# Load config
with open("db_config.json", "r") as f:
    config = json.load(f)

HOST = config["host"]
USERNAME = config["username"]
PASSWORD = config["password"]
DATABASE = config["database"]

print("=" * 55)
print("  FIXING SECURITY GROUP")
print("=" * 55)

# Get your public IP
print("\n🔍 Getting your public IP address...")
your_ip = requests.get("https://api.ipify.org").text
print(f"  ✅ Your IP: {your_ip}")

# Find the security group
ec2 = boto3.client("ec2", region_name=REGION)
rds = boto3.client("rds", region_name=REGION)

print("\n🔍 Finding RDS security group...")
response = rds.describe_db_instances(DBInstanceIdentifier="ecommerce-db")
vpc_sg_ids = response["DBInstances"][0]["VpcSecurityGroups"]
sg_id = vpc_sg_ids[0]["VpcSecurityGroupId"]
print(f"  ✅ Security Group ID: {sg_id}")

# Add your IP to the security group
print(f"\n🔐 Adding your IP ({your_ip}) to security group...")
try:
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpProtocol="tcp",
        FromPort=3306,
        ToPort=3306,
        CidrIp=f"{your_ip}/32"  # /32 means only your specific IP
    )
    print("  ✅ IP added to security group!")
except ec2.exceptions.ClientError as e:
    if "already exists" in str(e):
        print("  ℹ️  IP already in security group (this is fine)")
    else:
        raise

# Now try to create tables
print("\n🚀 Creating tables in RDS...")
try:
    conn = pymysql.connect(
        host=HOST,
        user=USERNAME,
        password=PASSWORD,
        database=DATABASE,
        connect_timeout=10
    )
    cursor = conn.cursor()

    # CUSTOMERS
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

    # PRODUCTS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id    INT PRIMARY KEY AUTO_INCREMENT,
            product_name  VARCHAR(150) NOT NULL,
            category      VARCHAR(100) NOT NULL,
            price         DECIMAL(10, 2) NOT NULL
        );
    """)
    print("  ✅ Table 'products' created")

    # ORDERS
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

    # ORDER ITEMS
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

    # RETURNS
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

    print("\n✅ All tables created successfully!")
    print("\n" + "=" * 55)
    print("  ✅ STEP 2 COMPLETE — Ready for Step 3 (load_data.py)")
    print("=" * 55)

except pymysql.err.OperationalError as e:
    print(f"\n❌ Still can't connect. Error: {e}")
    print("\nTroubleshooting:")
    print("1. Wait 2-3 minutes for the security group change to take effect")
    print("2. Make sure your internet connection is stable")
    print("3. Try running this script again")
