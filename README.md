# Ecommerce

**Goal:** get clean data into BigQuery and calculate total revenue per customer

# Architecture diagram
<img width="2320" height="488" alt="image" src="https://github.com/user-attachments/assets/cbdd0940-8521-43c0-b399-1e0f53e4f2e8" />

Data was generated with the Faker library in generate_data.py, which creates 3 files: customers.csv, orders.csv, products.csv.

# Project Setup

**Create a virtual environment in Visual Studio Code**

A virtual environment helps avoid future conflicts between package versions.

`python3 -m venv venv`

`source venv/bin/activate`

**Google Cloud Storage (GCS)**
- A GCS bucket was created with default settings
  - Region: europe-west3, the closest one. The goal is to keep the GCS bucket and the Data Fusion pipeline in one region to avoid slow cross-region data transfer and charges.
  - Storage class: Standard. No retrieval fees, but the highest price per GB. There was no plan to store the data for a long time.
  - Access Control: Uniform. Permissions are set at the bucket level - every object in the bucket inherits the same access rules.
- A service account was created
  - Given roles: BigQuery Job User, Cloud Data Fusion Runner, Dataproc Worker, Storage Admin
- Authentication for GCS through terminal
  - https://cloud.google.com/sdk/docs/install - download the official Google Cloud SDK installer
    - Unzip
    - `./google-cloud-sdk/install.sh` - run the installer
    - Add to PATH
  - `gcloud auth application-default login` - log in
  - `gcloud config set project YOUR_PROJECT_ID` - set the project
    - `gcloud projects list` - find the project ID
- Install GCS library: `pip install google-cloud-storage`

**Data Fusion**
- Create a Data Fusion instance with default settings
  - Set the same region: europe-west3

**BigQuery**

- Create a dataset
  - Set the same location: europe-west3
- Manage access for this dataset: share it with the service account and grant the BigQuery Data Editor role.


# Project Steps
**generate_data.py**
- `pip install faker` - run the command in the terminal
- `python generate_data.py`

**upload_to_gcs.py**
- `python upload_to_gcs.py`

The folder with data will appear in GCS.

**Data Fusion**

The pipeline was built: GCS -> Wrangler -> BigQuery

After reviewing the data, I found that the "order_date" column has inconsistent date formats. Data Fusion doesn't have an easy way to fix this, so I decided to write a Python function for it.

The date issue is fixed in "transform_order_date.py". The data was uploaded to GCS again, passed through Wrangler to parse the schema correctly, and then loaded into BigQuery. The same step was applied to the other files, so all three tables (customers.csv, orders.csv, products.csv) were loaded into BigQuery.

**BigQuery**

I noticed an inconsistency in the "country" column of the customers table: it contained values like "US", "USA", etc. I decided to clean the data inside BigQuery and create a silver layer where all data is consistent.

```sql
CREATE OR REPLACE TABLE ecommerce_demo.customers_silver AS
SELECT
  customer_id,
  name,
  email,
  signup_date,
  CASE
    WHEN TRIM(country) IN ('US', 'USA') THEN 'United States'
    WHEN TRIM(country) IN ('DE', 'Germany') THEN 'Germany'
    ELSE TRIM(country)
  END AS country
FROM ecommerce_demo.customers_bronze
```

A data integrity issue was found: not all products in the orders table exist in the products table, so the price of some products is unknown. I decided to exclude these orders, because calculating revenue per customer requires the price.

Final query:

```sql
SELECT 
  customer.customer_id,
  ROUND(SUM(orders.quantity*products.unit_price), 2) AS revenue
from ecommerce_demo.customers_silver AS customer
INNER JOIN ecommerce_demo.orders_clean AS orders ON customer.customer_id = orders.customer_id
INNER JOIN ecommerce_demo.products AS products ON orders.product_id = products.product_id
GROUP BY customer.customer_id
```




