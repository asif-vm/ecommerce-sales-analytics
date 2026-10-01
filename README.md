# 📊 E-Commerce Sales Analytics Dashboard

> End-to-end data analytics pipeline built with AWS (S3 + RDS), MySQL, Python, and Power BI

![Project Status](https://img.shields.io/badge/Status-Complete-success)
![AWS](https://img.shields.io/badge/AWS-S3%20%7C%20RDS-orange)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![MySQL](https://img.shields.io/badge/MySQL-8.0-blue)
![Power BI](https://img.shields.io/badge/Power%20BI-Desktop-yellow)

## 🎯 Project Overview

A complete data analytics solution that processes 2,000+ e-commerce transactions across 5 relational tables, deployed on AWS cloud infrastructure, and visualized through an interactive Power BI dashboard. This project demonstrates the full data pipeline from generation to insight delivery.

### Key Highlights
- ☁️ **Cloud-Native**: AWS S3 for data lake, RDS MySQL for structured storage
- 🔄 **ETL Pipeline**: Automated data extraction from S3 and loading into RDS
- 📈 **Advanced Analytics**: 10 complex SQL queries with window functions, CTEs, and multi-table JOINs
- 📊 **Interactive Dashboard**: Multi-page Power BI dashboard with KPIs and drill-down capabilities
- 💾 **Real Data Patterns**: Seasonal trends, geographic distribution, realistic return rates

---

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────────┐      ┌─────────────────┐
│  Python Script  │ ───> │   AWS S3     │ ───> │   Python ETL    │
│  (Data Gen)     │      │ (Raw CSVs)   │      │   (boto3)       │
└─────────────────┘      └──────────────┘      └────────┬────────┘
                                                         │
                                                         ▼
                         ┌──────────────────────────────────────┐
                         │        AWS RDS MySQL Database        │
                         │  ┌──────────┐  ┌──────────┐         │
                         │  │customers │  │ products │         │
                         │  └────┬─────┘  └─────┬────┘         │
                         │       │              │               │
                         │  ┌────▼──────────────▼────┐         │
                         │  │      orders            │         │
                         │  └────┬───────────────────┘         │
                         │       │                              │
                         │  ┌────▼──────────┐  ┌──────────┐   │
                         │  │ order_items   │  │ returns  │   │
                         │  └───────────────┘  └──────────┘   │
                         └─────────────┬────────────────────────┘
                                       │
                                       ▼
                         ┌──────────────────────────┐
                         │   SQL Queries (10)       │
                         │   - Revenue Analysis     │
                         │   - Customer Segments    │
                         │   - Return Analytics     │
                         └─────────────┬────────────┘
                                       │
                                       ▼
                         ┌──────────────────────────┐
                         │   Power BI Dashboard     │
                         │   - Overview             │
                         │   - Customers            │
                         │   - Returns              │
                         └──────────────────────────┘
```

---

## 📁 Dataset

| Table | Rows | Description |
|-------|------|-------------|
| **customers** | 500 | Customer demographics (name, age, city, signup date) |
| **products** | 40 | Product catalog across 5 categories with pricing |
| **orders** | 2,000 | Transaction records with dates and status |
| **order_items** | 3,497 | Line items detailing products per order |
| **returns** | 222 | Product returns with reasons (~10% return rate) |

**Realistic Patterns:**
- 📈 Seasonal spikes during October-December (festive season)
- 🌍 Geographic distribution across 15 Indian cities
- 💰 Variable discounts (0-30%)
- 🔄 Realistic return reasons and rates

---

## 🛠️ Tech Stack

### Data Generation & Processing
- **Python 3.11+**: Core programming language
- **Pandas & NumPy**: Data manipulation and analysis
- **Faker**: Realistic synthetic data generation
- **boto3**: AWS SDK for Python
- **pymysql**: MySQL database connector

### Cloud Infrastructure
- **AWS S3**: Object storage for raw CSV files
- **AWS RDS**: Managed MySQL 8.0 database instance (db.t3.micro)
- **AWS Security Groups**: Network access control

### Database & Analytics
- **MySQL 8.0**: Relational database with foreign key constraints
- **MySQL Workbench**: Query development and testing
- **SQL**: Advanced queries with window functions, CTEs, subqueries

### Visualization
- **Power BI Desktop**: Interactive dashboard creation
- **DAX**: Calculated measures and KPIs

---

## 📊 Key Insights

### Revenue Metrics
- **Total Revenue**: ₹11.2 Lakhs (Jan 2023 - Dec 2024)
- **Total Orders**: 2,000
- **Average Order Value**: ₹561
- **Top Category**: Electronics (₹3.1L revenue)

### Customer Analytics
- **Active Customers**: 500
- **Customer Segments**: High Value (46), Mid Value (142), Low Value (312)
- **Top Cities**: Bengaluru (₹2.84L), Mumbai (₹1.98L), Chennai (₹1.72L)

### Operational Metrics
- **Order Status**: 65% Delivered, 15% Shipped, 10% Pending, 10% Cancelled
- **Overall Return Rate**: 6.35%
- **Highest Return Category**: Electronics (12.4%)
- **Top Return Reason**: Defective product (26%)

---

## 🔍 SQL Queries Showcase

This project includes 10 production-ready SQL queries demonstrating:

1. **Multi-table JOINs** — Revenue aggregation across 3 tables
2. **Date Functions** — Monthly trend analysis with YEAR() and MONTH()
3. **Window Functions** — ROW_NUMBER() for ranking products by category
4. **Subqueries & CTEs** — Customer segmentation with CASE WHEN
5. **LEFT JOINs** — Return rate calculation handling missing data
6. **Running Totals** — Cumulative revenue using SUM() OVER()
7. **Aggregations** — Order status distribution with percentages
8. **Conditional Logic** — Dynamic customer tier assignment
9. **4-Table JOINs** — City-wise performance metrics
10. **Top N Analysis** — Identifying high-value customers

**Example Query: Customer Segmentation**
```sql
SELECT
    segment,
    COUNT(*) AS customer_count,
    ROUND(AVG(total_spent), 2) AS avg_spend
FROM (
    SELECT
        c.customer_id,
        ROUND(SUM(p.price * oi.quantity * (1 - oi.discount_percent / 100)), 2) AS total_spent,
        CASE
            WHEN SUM(p.price * oi.quantity * (1 - oi.discount_percent / 100)) >= 20000 THEN 'High Value'
            WHEN SUM(p.price * oi.quantity * (1 - oi.discount_percent / 100)) >= 8000 THEN 'Mid Value'
            ELSE 'Low Value'
        END AS segment
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    WHERE o.status = 'Delivered'
    GROUP BY c.customer_id
) AS customer_segments
GROUP BY segment
ORDER BY avg_spend DESC;
```

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.11+
- AWS Account (Free Tier eligible)
- Power BI Desktop
- MySQL Workbench (optional)

### Step 1: Clone Repository
```bash
git clone https://github.com/asif-vm/--E-Commerce-Sales-Analytics-Dashboard.git
cd --E-Commerce-Sales-Analytics-Dashboard
```

### Step 2: Install Dependencies
```bash
pip install boto3 pandas numpy faker pymysql
```

### Step 3: Configure AWS
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and Region (ap-south-1)

# PowerShell example: use a unique password and restrict access to your IP /32
$env:RDS_PASSWORD = "create-a-strong-password-locally"
$env:RDS_ALLOWED_CIDR = "203.0.113.5/32"
```

### Step 4: Generate Data
```bash
python generate_data.py
```
Creates 5 CSV files in `ecommerce_data/` folder.

### Step 5: Deploy to AWS
```bash
python aws_setup.py
```
- Creates S3 bucket and uploads CSVs
- Provisions RDS MySQL instance
- Configures security groups
- Creates database tables

`db_config.json` is generated locally and intentionally ignored by Git. Never commit credentials. Use `db_config.example.json` as the schema reference.

### Step 6: Load Data
```bash
python load_data.py
```
Reads CSVs from S3 and loads into RDS MySQL.

### Step 7: Build Dashboard
1. Open Power BI Desktop
2. Connect to RDS MySQL using credentials from `db_config.json`
3. Import tables or run SQL queries
4. Build visualizations following `STEP5_POWERBI_GUIDE.md`

---

## 📸 Dashboard Screenshots

### Overview Page
*[Screenshot: KPI cards, revenue by category, monthly trends, order status]*

### Customer Analytics
*[Screenshot: Top customers, segmentation, city performance]*

### Returns Analysis
*[Screenshot: Return rates, reasons breakdown]*

> **Note**: Add actual screenshots after completing the Power BI dashboard

---

## 📂 Project Structure

```
ecommerce-analytics-project/
│
├── generate_data.py              # Creates synthetic e-commerce data
├── aws_setup.py                  # AWS infrastructure deployment
├── fix_security_group.py         # Security group configuration
├── load_data.py                  # ETL pipeline (S3 → RDS)
├── queries.sql                   # 10 production SQL queries
│
├── ecommerce_data/               # Generated CSV files
│   ├── customers.csv
│   ├── products.csv
│   ├── orders.csv
│   ├── order_items.csv
│   └── returns.csv
│
├── db_config.json                # RDS connection details (git-ignored)
├── STEP2_GUIDE.md                # AWS setup instructions
├── STEP5_POWERBI_GUIDE.md        # Power BI setup instructions
├── dashboard_preview.jsx         # React preview of dashboard
│
└── README.md                     # This file
```

---

## 🎓 Skills Demonstrated

### Data Engineering
- ETL pipeline design and implementation
- Cloud infrastructure deployment (AWS S3, RDS)
- Data modeling with foreign key relationships
- Database schema design

### Data Analysis
- Advanced SQL (window functions, CTEs, subqueries)
- Data aggregation and transformation
- Business metrics calculation
- Statistical analysis

### Data Visualization
- Interactive dashboard design
- KPI identification and tracking
- Data storytelling
- User experience optimization

### Cloud & DevOps
- AWS services configuration
- Security group management
- Infrastructure as Code principles
- Cost optimization (Free Tier usage)

---

## 💡 Key Learnings

1. **Foreign Keys Matter**: Enforcing relationships at the database level prevents data inconsistencies
2. **Window Functions Are Powerful**: Running totals and rankings without GROUP BY collapse
3. **Security First**: Proper security group configuration is critical for cloud databases
4. **Query Optimization**: Pre-aggregated queries in Power BI improve dashboard performance
5. **Data Patterns**: Building realistic seasonal and geographic patterns makes insights more meaningful

---

## 🔮 Future Enhancements

- [ ] Add predictive analytics (ML model for return prediction)
- [ ] Implement automated data refresh using AWS Lambda
- [ ] Deploy dashboard to Power BI Service for web access
- [ ] Add real-time data streaming with AWS Kinesis
- [ ] Create Python Flask API for dashboard backend
- [ ] Add data quality monitoring and alerts
- [ ] Implement incremental data loading strategy

---

## 📧 Contact

**Asif V M**  
📧 asifvm15@gmail.com  
🔗 [LinkedIn](https://linkedin.com/in/asifvm1)  
💻 [GitHub](https://github.com/asifvm)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- Dataset patterns inspired by real-world e-commerce analytics
- AWS Free Tier for cloud infrastructure
- Power BI community for visualization best practices

---

**⭐ If you found this project helpful, please consider giving it a star!**
