import os
from datetime import date
from google.cloud import storage

BUCKET_NAME = "aleksandra-ecommerce-demo-2026"
LOCAL_DIR = "data/raw"

# Maps local file -> path inside the bucket
# Orders is dated so Composer can later pick up "today's file" specifically
today = date.today().isoformat()


FILES_TO_UPLOAD = {
    "customers.csv": "raw/customers/customers.csv",
    "products.csv": "raw/products/products.csv",
    "orders.csv": f"raw/orders/orders_{today}.csv",
}


def upload_file(client,  bucket, local_path, blob_path):
    blob = bucket.blob(blob_path) #path where object will be stored
    blob.upload_from_filename(local_path) #location from where upload
    print(f"Uploaded {local_path} -> gs://{bucket}/{blob_path}")


if __name__ == "__main__":
    client = storage.Client()  # picks up ADC credentials automatically
    bucket = client.bucket(BUCKET_NAME,)

    for local_filename, blob_path in FILES_TO_UPLOAD.items(): #customer.csv", "raw/customers/customers.csv"
        local_path = os.path.join(LOCAL_DIR, local_filename) #data/raw/customers.csv
        upload_file(client, bucket, local_path, blob_path)