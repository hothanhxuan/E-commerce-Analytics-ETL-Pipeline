import sys
import os
import gc

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orchestration.pipeline_orchestrator import PipelineOrchestrator
from utils.logger import setup_logger

def update_rfm_only():
    """
    Lightweight script to update ONLY the RFM segmentation in BigQuery.
    Skips cart events (3M+ rows), order items, and payments to avoid memory crashes.
    """
    logger = setup_logger("RFM_Updater")
    logger.info("==============================================")
    logger.info("Starting FAST RFM Update (Memory Safe Mode)...")
    logger.info("==============================================")
    
    orch = PipelineOrchestrator()
    
    try:
        # Step 1: Extract and Transform Customers
        logger.info("1. Extracting customers...")
        customers = orch.sapo_extractor.extract_customers()
        orch.transformed["dim_customers"] = orch.dim_transformer.transform_dim_customers(customers)
        del customers
        gc.collect()
        
        # Step 2: Extract and Transform Orders (needed to calculate RFM)
        logger.info("2. Extracting orders...")
        shopify_orders = orch.shopify_extractor.extract_orders()
        online_orders = orch.sapo_extractor.extract_online_orders()
        sapo_orders = orch.sapo_extractor.extract_orders()
        
        orch.transformed["fact_orders"] = orch.fact_transformer.transform_fact_orders(
            shopify_orders, sapo_orders, online_orders
        )
        del shopify_orders, online_orders, sapo_orders
        gc.collect()
        
        # Step 3: Update Aggregates (Calculates RFM and uploads dim_customers to BQ)
        logger.info("3. Calculating new RFM and uploading to BigQuery...")
        orch._step_update_aggregates()
        
        logger.info("==============================================")
        logger.info("✅ SUCCESS! RFM has been updated in BigQuery.")
        logger.info("You can now click 'Refresh' in Power BI.")
        logger.info("==============================================")
        
    except Exception as e:
        logger.error(f"❌ FAILED: {e}")

if __name__ == "__main__":
    update_rfm_only()
