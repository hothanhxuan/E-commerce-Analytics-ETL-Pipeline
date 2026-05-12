import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.join(__file__, ".."))))
from loaders.bigquery_loader import BigQueryLoader

if __name__ == "__main__":
    print("Updating BigQuery Views...")
    loader = BigQueryLoader()
    loader.create_views()
    print("Successfully updated views!")
