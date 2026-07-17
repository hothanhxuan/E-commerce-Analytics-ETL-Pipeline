"""
Pipeline Orchestrator - Coordinates the full ETL pipeline execution.
Manages extract → transform → load workflow with proper dependency ordering.

Memory-optimized: processes data in stages and releases memory between steps
to support machines with limited RAM (8GB).
"""

import gc
import time
from datetime import datetime
from utils.logger import setup_logger

# Extractors
from extractors.shopify_extractor import ShopifyExtractor
from extractors.sapo_extractor import SapoExtractor
from extractors.payment_extractor import PaymentExtractor
from extractors.tracking_extractor import TrackingExtractor

# Transformers
from transformers.dimension_transformer import DimensionTransformer
from transformers.fact_transformer import FactTransformer

# Loaders
from loaders.bigquery_loader import BigQueryLoader


def _log_memory():
    """Log approximate memory usage (best-effort, won't fail if psutil missing)."""
    try:
        import psutil
        process = psutil.Process()
        mem_mb = process.memory_info().rss / (1024 * 1024)
        return f" [RAM: {mem_mb:.0f} MB]"
    except ImportError:
        return ""


def _force_gc():
    """Force garbage collection to release memory."""
    gc.collect()


def _lower_process_priority():
    """Lower this process's priority so the desktop stays responsive.
    
    Sets priority to BELOW_NORMAL on Windows, or 'nice' on Linux/Mac.
    This prevents the ETL from starving Explorer, VS Code, and other apps.
    """
    import os
    import sys
    try:
        if sys.platform == "win32":
            import ctypes
            # BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
            handle = ctypes.windll.kernel32.GetCurrentProcess()
            ctypes.windll.kernel32.SetPriorityClass(handle, 0x00004000)
        else:
            os.nice(10)  # Lower priority on Unix
    except Exception:
        pass  # Non-critical — best effort


def _check_memory_safety(logger, threshold_pct=85):
    """Warn if system memory usage is above threshold.
    
    Args:
        logger: Logger instance.
        threshold_pct: Memory usage percentage that triggers a warning.
        
    Returns:
        True if memory is safe, False if dangerously high.
    """
    try:
        import psutil
        mem = psutil.virtual_memory()
        used_pct = mem.percent
        avail_mb = mem.available / (1024 * 1024)
        if used_pct > threshold_pct:
            logger.warning(
                f"⚠ HIGH MEMORY: {used_pct:.0f}% used, "
                f"only {avail_mb:.0f} MB available. "
                f"Consider closing other applications."
            )
            return False
        return True
    except ImportError:
        return True  # Can't check without psutil — assume OK


class PipelineOrchestrator:
    """Orchestrates the full ETL pipeline for TechStore Vietnam.
    
    Memory-optimized: each data source is extracted, transformed, loaded,
    and then freed from memory before moving to the next source.
    """

    def __init__(self):
        """Initialize pipeline orchestrator with all components."""
        self.logger = setup_logger("PipelineOrchestrator")
        self.start_time = None

        # Initialize components lazily — extractors create GCS clients
        self._shopify_extractor = None
        self._sapo_extractor = None
        self._payment_extractor = None
        self._tracking_extractor = None

        self.dim_transformer = DimensionTransformer()
        self.fact_transformer = FactTransformer()

        self.loader = BigQueryLoader()

        # Storage for transformed DataFrames (kept lightweight)
        self.transformed = {}
        self._row_counts = {}  # Track row counts for summary without holding DFs

    # ── Lazy extractor initialization ──
    @property
    def shopify_extractor(self):
        if self._shopify_extractor is None:
            self._shopify_extractor = ShopifyExtractor()
        return self._shopify_extractor

    @property
    def sapo_extractor(self):
        if self._sapo_extractor is None:
            self._sapo_extractor = SapoExtractor()
        return self._sapo_extractor

    @property
    def payment_extractor(self):
        if self._payment_extractor is None:
            self._payment_extractor = PaymentExtractor()
        return self._payment_extractor

    @property
    def tracking_extractor(self):
        if self._tracking_extractor is None:
            self._tracking_extractor = TrackingExtractor()
        return self._tracking_extractor

    def run_full_pipeline(self):
        """
        Execute the complete ETL pipeline (memory-optimized):
        1. Extract & transform dimensions → load → free
        2. Extract & transform facts (orders, payments) → load → free  
        3. Extract & transform cart_events in chunks → load → free
        4. Extract & transform bank transactions → load → free
        5. Update aggregates & create views
        """
        self.start_time = time.time()
        self.logger.info("=" * 60)
        self.logger.info("STARTING FULL ETL PIPELINE (Memory-Optimized)")
        self.logger.info(f"Timestamp: {datetime.now().isoformat()}")
        self.logger.info("=" * 60)

        # Lower process priority so the desktop stays responsive
        _lower_process_priority()
        self.logger.info("Process priority lowered to BELOW_NORMAL (desktop-safe mode)")

        try:
            # Step 1: Create BigQuery dataset
            self._step_create_dataset()

            # ────────────────────────────────────
            # PHASE A: Dimensions (small data)
            # ────────────────────────────────────
            self.logger.info("─" * 40)
            self.logger.info(f"PHASE A: DIMENSIONS{_log_memory()}")

            # Extract shared data
            customers = self.sapo_extractor.extract_customers()
            products = self.sapo_extractor.extract_products()
            locations = self.sapo_extractor.extract_locations()

            # We need sapo_orders for dim_staff AND for fact_orders later
            # Extract once, keep reference for facts
            sapo_orders = self.sapo_extractor.extract_orders()

            # Transform dimensions
            self.transformed["dim_customers"] = self.dim_transformer.transform_dim_customers(customers)
            del customers; _force_gc()

            self.transformed["dim_products"] = self.dim_transformer.transform_dim_products(products)
            del products; _force_gc()

            self.transformed["dim_locations"] = self.dim_transformer.transform_dim_locations(locations)
            del locations; _force_gc()

            self.transformed["dim_staff"] = self.dim_transformer.transform_dim_staff(sapo_orders)
            self.transformed["dim_date"] = self.dim_transformer.transform_dim_date()

            # Load dimensions
            self._load_tables({
                "dim_customers": {"partition_field": "created_at"},
                "dim_products": {},
                "dim_locations": {},
                "dim_staff": {},
                "dim_date": {},
            }, label="Dimensions")

            self.logger.info(f"Phase A complete.{_log_memory()}")

            # Free dimension DataFrames no longer needed (keep dim_customers for Phase F)
            for key in ["dim_products", "dim_locations", "dim_staff", "dim_date"]:
                self.transformed.pop(key, None)
            _force_gc()
            self.logger.info(f"  Freed dimension DataFrames{_log_memory()}")

            # ────────────────────────────────────
            # PHASE B: Order facts (medium data)
            # ────────────────────────────────────
            self.logger.info("─" * 40)
            _check_memory_safety(self.logger)
            self.logger.info(f"PHASE B: ORDER FACTS{_log_memory()}")

            shopify_orders = self.shopify_extractor.extract_orders()
            online_orders = self.sapo_extractor.extract_online_orders()

            # Transform order facts
            self.transformed["fact_orders"] = self.fact_transformer.transform_fact_orders(
                shopify_orders, sapo_orders, online_orders
            )
            self.transformed["fact_order_items"] = self.fact_transformer.transform_fact_order_items(
                shopify_orders, sapo_orders, online_orders
            )

            # ────────────────────────────────────
            # DATA QUALITY: Drop Orphan Orders
            # ────────────────────────────────────
            self.logger.info("Applying strict referential integrity filters...")
            
            # 1. Identify valid customers (allow -1 for unknown/walk-in)
            valid_customers = set(self.transformed["dim_customers"]["customer_id"])
            valid_customers.add(-1)

            # 2. Filter fact_orders
            fact_orders = self.transformed["fact_orders"]
            initial_orders_count = len(fact_orders)
            fact_orders = fact_orders[fact_orders["customer_id"].isin(valid_customers)]
            self.transformed["fact_orders"] = fact_orders
            
            dropped_orders = initial_orders_count - len(fact_orders)
            if dropped_orders > 0:
                self.logger.warning(f"  Dropped {dropped_orders:,} orphan orders (customer_id not in dim_customers)")

            # 3. Filter fact_order_items (must match valid order_keys)
            fact_order_items = self.transformed["fact_order_items"]
            initial_items_count = len(fact_order_items)
            valid_orders = set(fact_orders["order_key"])
            fact_order_items = fact_order_items[fact_order_items["order_key"].isin(valid_orders)]
            self.transformed["fact_order_items"] = fact_order_items
            
            dropped_items = initial_items_count - len(fact_order_items)
            if dropped_items > 0:
                self.logger.warning(f"  Dropped {dropped_items:,} orphan order items")


            # Free raw order data
            del shopify_orders, sapo_orders, online_orders
            _force_gc()

            # Load order facts
            self._load_tables({
                "fact_orders": {
                    "partition_field": "order_date",
                    "clustering_fields": ["customer_id", "channel"],
                },
                "fact_order_items": {
                    "partition_field": "order_date",
                    "clustering_fields": ["product_id"],
                },
            }, label="Order facts")

            self.logger.info(f"Phase B complete.{_log_memory()}")

            # Free large fact_order_items (2M+ rows) — only fact_orders needed for Phase F
            self.transformed.pop("fact_order_items", None)
            _force_gc()
            self.logger.info(f"  Freed fact_order_items{_log_memory()}")

            # ────────────────────────────────────
            # PHASE C: Payment facts (small-medium)
            # ────────────────────────────────────
            self.logger.info("─" * 40)
            self.logger.info(f"PHASE C: PAYMENT FACTS{_log_memory()}")

            paypal = self.payment_extractor.extract_paypal()
            momo = self.payment_extractor.extract_momo()
            zalopay = self.payment_extractor.extract_zalopay()

            self.transformed["fact_payments"] = self.fact_transformer.transform_fact_payments(
                paypal, momo, zalopay
            )
            del paypal, momo, zalopay
            _force_gc()

            self._load_tables({
                "fact_payments": {
                    "partition_field": "payment_date",
                    "clustering_fields": ["customer_id", "payment_gateway"],
                },
            }, label="Payment facts")

            self.logger.info(f"Phase C complete.{_log_memory()}")

            # Free payment facts
            self.transformed.pop("fact_payments", None)
            _force_gc()

            # ────────────────────────────────────
            # PHASE D: Cart events (LARGE — stream-to-BQ, never holds full DF)
            # ────────────────────────────────────
            self.logger.info("─" * 40)
            _check_memory_safety(self.logger)
            self.logger.info(f"PHASE D: CART EVENTS (stream-to-BigQuery mode){_log_memory()}")

            # Stream each chunk directly to BigQuery to avoid holding the
            # entire cart events DataFrame in RAM (the #1 crash cause).
            # Chunk size reduced to 20,000 for safer peak memory.
            cart_chunks = self.tracking_extractor.extract_cart_events_chunked(chunk_size=20000)
            total_cart_rows = 0
            chunk_num = 0

            for chunk in cart_chunks:
                chunk_num += 1
                self.logger.info(f"  Cart chunk {chunk_num}: transforming {len(chunk)} records...{_log_memory()}")

                # Transform this single chunk
                chunk_df = self.fact_transformer.transform_fact_cart_events(chunk)
                del chunk
                _force_gc()

                if chunk_df.empty:
                    continue

                # Load directly to BigQuery:
                # First chunk truncates (resets table), subsequent chunks append.
                disposition = "WRITE_TRUNCATE" if chunk_num == 1 else "WRITE_APPEND"
                self.loader.load_dataframe(
                    table_name="fact_cart_events",
                    df=chunk_df,
                    write_disposition=disposition,
                    partition_field="event_timestamp",
                    clustering_fields=["customer_id", "session_id", "event_type"],
                )
                total_cart_rows += len(chunk_df)
                self.logger.info(f"  Cart chunk {chunk_num} loaded ({len(chunk_df)} rows). Total: {total_cart_rows:,}{_log_memory()}")

                del chunk_df
                _force_gc()

            self._row_counts["fact_cart_events"] = total_cart_rows
            self.logger.info(f"Phase D complete. Total cart events: {total_cart_rows:,}{_log_memory()}")

            # ────────────────────────────────────
            # PHASE E: Bank transactions (small)
            # ────────────────────────────────────
            self.logger.info("─" * 40)
            self.logger.info(f"PHASE E: BANK TRANSACTIONS{_log_memory()}")

            mercury_transactions = self.payment_extractor.extract_mercury_transactions()
            # Also extract accounts (not used in transform but extracted for completeness)
            mercury_accounts = self.payment_extractor.extract_mercury_accounts()
            del mercury_accounts
            _force_gc()

            self.transformed["fact_bank_transactions"] = self.fact_transformer.transform_fact_bank_transactions(
                mercury_transactions
            )
            del mercury_transactions
            _force_gc()

            self._load_tables({
                "fact_bank_transactions": {
                    "partition_field": "transaction_date",
                },
            }, label="Bank transaction facts")

            self.logger.info(f"Phase E complete.{_log_memory()}")

            # Free bank transaction facts
            self.transformed.pop("fact_bank_transactions", None)
            _force_gc()

            # ────────────────────────────────────
            # PHASE F: Aggregates & Views
            # ────────────────────────────────────
            self.logger.info("─" * 40)
            self.logger.info(f"PHASE F: AGGREGATES & VIEWS{_log_memory()}")

            self._step_update_aggregates()
            self._step_create_views()

            # Final summary
            self._print_summary()

        except Exception as e:
            elapsed = time.time() - self.start_time
            self.logger.error(f"PIPELINE FAILED after {elapsed:.1f}s: {e}")
            raise

    def run_extract_only(self):
        """Extract data from GCS without loading."""
        self.start_time = time.time()
        self.logger.info("Running EXTRACT ONLY mode...")

        raw_data = {}
        raw_data["shopify_orders"] = self.shopify_extractor.extract_orders()
        raw_data["customers"] = self.sapo_extractor.extract_customers()
        raw_data["products"] = self.sapo_extractor.extract_products()
        raw_data["locations"] = self.sapo_extractor.extract_locations()
        raw_data["sapo_orders"] = self.sapo_extractor.extract_orders()
        raw_data["online_orders"] = self.sapo_extractor.extract_online_orders()
        raw_data["paypal"] = self.payment_extractor.extract_paypal()
        raw_data["momo"] = self.payment_extractor.extract_momo()
        raw_data["zalopay"] = self.payment_extractor.extract_zalopay()
        raw_data["mercury_accounts"] = self.payment_extractor.extract_mercury_accounts()
        raw_data["mercury_transactions"] = self.payment_extractor.extract_mercury_transactions()
        raw_data["cart_events"] = self.tracking_extractor.extract_cart_events()

        self.logger.info(f"Extraction completed in {time.time() - self.start_time:.1f}s")
        for key, data in raw_data.items():
            count = len(data) if isinstance(data, list) else "N/A"
            self.logger.info(f"  {key}: {count} records")
        return raw_data

    def run_transform_only(self):
        """Extract and transform without loading to BigQuery (memory-optimized)."""
        self.start_time = time.time()
        self.logger.info("Running EXTRACT + TRANSFORM mode (memory-optimized)...")

        # Dimensions
        customers = self.sapo_extractor.extract_customers()
        self.transformed["dim_customers"] = self.dim_transformer.transform_dim_customers(customers)
        del customers; _force_gc()

        products = self.sapo_extractor.extract_products()
        self.transformed["dim_products"] = self.dim_transformer.transform_dim_products(products)
        del products; _force_gc()

        locations = self.sapo_extractor.extract_locations()
        self.transformed["dim_locations"] = self.dim_transformer.transform_dim_locations(locations)
        del locations; _force_gc()

        sapo_orders = self.sapo_extractor.extract_orders()
        self.transformed["dim_staff"] = self.dim_transformer.transform_dim_staff(sapo_orders)
        self.transformed["dim_date"] = self.dim_transformer.transform_dim_date()

        # Facts
        shopify_orders = self.shopify_extractor.extract_orders()
        online_orders = self.sapo_extractor.extract_online_orders()

        self.transformed["fact_orders"] = self.fact_transformer.transform_fact_orders(
            shopify_orders, sapo_orders, online_orders
        )
        self.transformed["fact_order_items"] = self.fact_transformer.transform_fact_order_items(
            shopify_orders, sapo_orders, online_orders
        )
        del shopify_orders, sapo_orders, online_orders; _force_gc()

        paypal = self.payment_extractor.extract_paypal()
        momo = self.payment_extractor.extract_momo()
        zalopay = self.payment_extractor.extract_zalopay()
        self.transformed["fact_payments"] = self.fact_transformer.transform_fact_payments(
            paypal, momo, zalopay
        )
        del paypal, momo, zalopay; _force_gc()

        cart_events = self.tracking_extractor.extract_cart_events()
        self.transformed["fact_cart_events"] = self.fact_transformer.transform_fact_cart_events(
            cart_events
        )
        del cart_events; _force_gc()

        mercury_transactions = self.payment_extractor.extract_mercury_transactions()
        self.transformed["fact_bank_transactions"] = self.fact_transformer.transform_fact_bank_transactions(
            mercury_transactions
        )
        del mercury_transactions; _force_gc()

        self.logger.info(f"Transform completed in {time.time() - self.start_time:.1f}s")
        return self.transformed

    # ──────────────────────────────────────────────
    # Helper methods
    # ──────────────────────────────────────────────

    def _load_tables(self, table_configs: dict, label: str = ""):
        """Load multiple transformed tables to BigQuery, then free their memory."""
        self.logger.info(f"Loading {label} to BigQuery...")
        for table_name, config in table_configs.items():
            df = self.transformed.get(table_name)
            if df is not None and not df.empty:
                self._row_counts[table_name] = len(df)
                self.loader.load_dataframe(
                    table_name=table_name,
                    df=df,
                    write_disposition="WRITE_TRUNCATE",
                    partition_field=config.get("partition_field"),
                    clustering_fields=config.get("clustering_fields"),
                )
            else:
                self.logger.warning(f"Skipping empty table: {table_name}")
                self._row_counts[table_name] = 0

    # ──────────────────────────────────────────────
    # Pipeline Steps
    # ──────────────────────────────────────────────

    def _step_create_dataset(self):
        """Step: Create BigQuery dataset."""
        self.logger.info("─" * 40)
        self.logger.info("STEP: Creating BigQuery dataset...")
        self.loader.create_dataset_if_not_exists()

    def _step_update_aggregates(self):
        """Step: Update customer aggregates from fact tables."""
        self.logger.info("Updating customer aggregates...")

        fact_orders = self.transformed.get("fact_orders")
        dim_customers = self.transformed.get("dim_customers")

        if fact_orders is not None and dim_customers is not None:
            updated_customers = self.dim_transformer.update_customer_aggregates(
                dim_customers, fact_orders
            )
            # Reload updated dim_customers
            self.loader.load_dataframe(
                table_name="dim_customers",
                df=updated_customers,
                write_disposition="WRITE_TRUNCATE",
                partition_field="created_at",
            )
            self.logger.info("Customer aggregates updated and reloaded")
        else:
            self.logger.warning("Cannot update aggregates: missing data")

    def _step_create_views(self):
        """Step: Create analytical views."""
        self.logger.info("Creating analytical views...")
        self.loader.create_views()

    def _print_summary(self):
        """Print final pipeline execution summary."""
        elapsed = time.time() - self.start_time
        self.logger.info("=" * 60)
        self.logger.info("PIPELINE EXECUTION SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Total execution time: {elapsed:.1f}s ({elapsed/60:.1f}min)")
        self.logger.info("")
        self.logger.info("Tables loaded:")

        all_tables = [
            "dim_customers", "dim_products", "dim_locations",
            "dim_staff", "dim_date",
            "fact_orders", "fact_order_items", "fact_payments",
            "fact_cart_events", "fact_bank_transactions"
        ]

        for table in all_tables:
            rows = self._row_counts.get(table, 0)
            self.logger.info(f"  {table}: {rows:,} rows")

        # Data quality summary
        quality_reports = {}
        quality_reports.update(self.dim_transformer.get_quality_report())
        quality_reports.update(self.fact_transformer.get_quality_report())

        if quality_reports:
            self.logger.info("")
            self.logger.info("Data Quality Issues:")
            for issue, count in quality_reports.items():
                self.logger.info(f"  ⚠ {issue}: {count}")

        self.logger.info("")
        self.logger.info("Views created: vw_customer_journey, vw_cashflow_daily, vw_payment_status")
        self.logger.info("=" * 60)
        self.logger.info(f"PIPELINE COMPLETED SUCCESSFULLY{_log_memory()}")
        self.logger.info("=" * 60)
