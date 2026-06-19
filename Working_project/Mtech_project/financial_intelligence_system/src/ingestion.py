# Data Ingestion Module - Handles SEC filings and Snowflake data
import logging
import os
from typing import List, Dict, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json
import uuid

# Load .env automatically so env-vars are available everywhere
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"), override=False)
except ImportError:
    pass

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Financial document representation"""
    id: str
    title: str
    content: str
    source: str
    financial_year: Optional[int] = None
    company: Optional[str] = None
    metadata: Dict = None


class DataSource(ABC):
    """Abstract base for data sources"""
    
    @abstractmethod
    def fetch_documents(self, **kwargs) -> List[Document]:
        """Fetch documents from source"""
        pass


class SECFilingSource(DataSource):
    """SEC 10-K filing data source"""
    
    def __init__(self, cache_dir: str = "./data/sec_filings"):
        self.cache_dir = cache_dir
        logger.info(f"Initialized SEC filing source with cache: {cache_dir}")
    
    def fetch_documents(self, company: str = None, year: int = None) -> List[Document]:
        """
        Fetch SEC 10-K filings
        
        Args:
            company: Company ticker/name
            year: Financial year
            
        Returns:
            List of Document objects
        """
        documents = []
        logger.info(f"Fetching SEC filings for {company} ({year})")
        
        # Placeholder: In production, use SEC EDGAR API
        # Mock document for demonstration
        if company and year:
            doc = Document(
                id=f"sec_10k_{company}_{year}",
                title=f"{company} 10-K Filing {year}",
                content=f"This is a mock 10-K filing for {company} for the year {year}. "
                       f"It contains financial statements, risk disclosures, and MD&A.",
                source="SEC_EDGAR",
                financial_year=year,
                company=company,
                metadata={
                    "filing_type": "10-K",
                    "cik": "0000000000",
                    "accession_number": "0000000000-24-000000"
                }
            )
            documents.append(doc)
            logger.info(f"Fetched {len(documents)} SEC documents")
        
        return documents


class LocalFileSource(DataSource):
    """Load documents from local file system (data/ directory)"""
    
    def __init__(self, base_dir: str = "./data"):
        """
        Initialize local file source
        
        Args:
            base_dir: Base directory to scan for documents (default: ./data)
        """
        self.base_dir = os.path.abspath(base_dir)
        logger.info(f"Initialized local file source with base dir: {self.base_dir}")
    
    def fetch_documents(self, **kwargs) -> List[Document]:
        """
        Fetch documents from local filesystem
        
        Scans subdirectories for .txt, .json, .md files
        Supports directory structure: data/sec_filings/, data/earnings_calls/, etc.
        
        Returns:
            List of Document objects
        """
        documents = []
        
        if not os.path.exists(self.base_dir):
            logger.warning(f"Base directory does not exist: {self.base_dir}")
            return documents
        
        # Scan all subdirectories for documents
        for root, dirs, files in os.walk(self.base_dir):
            for file in files:
                if file.startswith('.'):
                    continue  # Skip hidden files
                
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, self.base_dir)
                
                try:
                    # Handle text files
                    if file.endswith(('.txt', '.md')):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Extract title from filename or first line
                        title = os.path.splitext(file)[0].replace('_', ' ').title()
                        if content:
                            first_line = content.split('\n')[0]
                            if len(first_line) < 200:
                                title = first_line
                        
                        doc = Document(
                            id=f"local_{relative_path.replace('/', '_')}",
                            title=title,
                            content=content,
                            source=f"LOCAL_FILE:{relative_path}",
                            metadata={"file_path": relative_path, "file_type": "text"}
                        )
                        documents.append(doc)
                        logger.debug(f"Loaded text document: {relative_path}")
                    
                    # Handle JSON batch files
                    elif file.endswith('.json'):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Support both single document and batch formats
                        if isinstance(data, list):
                            for item in data:
                                doc = Document(
                                    id=item.get('id', f"json_{uuid.uuid4()}"),
                                    title=item.get('title', 'Untitled'),
                                    content=item.get('content', ''),
                                    source=item.get('source', f"LOCAL_FILE:{relative_path}"),
                                    financial_year=item.get('financial_year'),
                                    company=item.get('company'),
                                    metadata=item.get('metadata', {})
                                )
                                documents.append(doc)
                        elif isinstance(data, dict):
                            doc = Document(
                                id=data.get('id', f"json_{uuid.uuid4()}"),
                                title=data.get('title', 'Untitled'),
                                content=data.get('content', ''),
                                source=data.get('source', f"LOCAL_FILE:{relative_path}"),
                                financial_year=data.get('financial_year'),
                                company=data.get('company'),
                                metadata=data.get('metadata', {})
                            )
                            documents.append(doc)
                        logger.debug(f"Loaded JSON documents: {relative_path}")
                
                except Exception as e:
                    logger.error(f"Error loading document {relative_path}: {e}")
        
        logger.info(f"Loaded {len(documents)} documents from local filesystem")
        return documents


class SnowflakeSource(DataSource):
    """Snowflake data warehouse source — reads credentials from environment variables."""

    # Tables to discover automatically when no explicit query/table is given
    DEFAULT_TABLES = [
        "FINANCIAL_REPORTS",
        "EARNINGS_CALLS",
        "SEC_FILINGS",
        "COMPANY_METRICS",
        "MARKET_DATA",
        "BALANCE_SHEETS",
        "INCOME_STATEMENTS",
        "CASH_FLOW_STATEMENTS",
    ]

    def __init__(self, connection_config: Dict = None):
        """
        Initialise Snowflake source.

        Credentials are resolved in priority order:
          1. Values passed in connection_config
          2. Environment variables (SNOWFLAKE_*)
        """
        cfg = connection_config or {}
        self.config = {
            "account":   cfg.get("account")   or os.environ.get("SNOWFLAKE_ACCOUNT", ""),
            "user":      cfg.get("user")       or os.environ.get("SNOWFLAKE_USER", ""),
            "password":  cfg.get("password")   or os.environ.get("SNOWFLAKE_PASSWORD", ""),
            "warehouse": cfg.get("warehouse")  or os.environ.get("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
            "database":  cfg.get("database")   or os.environ.get("SNOWFLAKE_DATABASE", "FINANCIAL_DB"),
            "schema":    cfg.get("schema")     or os.environ.get("SNOWFLAKE_SCHEMA", "RAW_DATA"),
        }
        self.connection = None
        logger.info(
            f"Initialised Snowflake source — account={self.config['account']}, "
            f"db={self.config['database']}, schema={self.config['schema']}"
        )

    # ── Connection ───────────────────────────────────────────────────────────

    def connect(self):
        """Establish (or reuse) a Snowflake connection."""
        if self.connection:
            try:
                self.connection.cursor().execute("SELECT 1")
                return  # already alive
            except Exception:
                self.connection = None

        import snowflake.connector
        self.connection = snowflake.connector.connect(
            account=self.config["account"],
            user=self.config["user"],
            password=self.config["password"],
            warehouse=self.config["warehouse"],
            database=self.config["database"],
            schema=self.config["schema"],
        )
        logger.info("Connected to Snowflake successfully")

    def disconnect(self):
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
            self.connection = None

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _execute(self, sql: str, params=None) -> List[Dict]:
        """Run a SQL statement and return rows as list-of-dicts."""
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute(sql, params or ())
        columns = [d[0].upper() for d in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def _available_tables(self) -> List[str]:
        """Return table names that actually exist in the current schema."""
        rows = self._execute(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
            "WHERE TABLE_SCHEMA = CURRENT_SCHEMA() AND TABLE_TYPE = 'BASE TABLE'"
        )
        return [r["TABLE_NAME"] for r in rows]

    @staticmethod
    def _row_to_text(row: Dict, table: str) -> str:
        """Convert a DB row to a human-readable text passage for the RAG index."""
        parts = [f"[Source: Snowflake / {table}]"]

        # ── Special handling for OHLCV / market-data tables ──────────────
        ohlcv_keys = {"OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"}
        row_upper = {k.upper(): v for k, v in row.items()}
        if ohlcv_keys.issubset(row_upper):
            date  = row_upper.get("DATE", "")
            open_ = row_upper.get("OPEN");  close = row_upper.get("CLOSE")
            high  = row_upper.get("HIGH");  low   = row_upper.get("LOW")
            vol   = row_upper.get("VOLUME")
            # Infer company from table name (e.g. APPLE_FIN_US_2025 → Apple)
            company_hint = table.split("_")[0].title() if table else "Company"
            parts.append(
                f"{company_hint} stock on {date}: "
                f"Open={open_}, High={high}, Low={low}, Close={close}, Volume={vol}."
            )
            return " ".join(parts)

        # ── Generic fallback ──────────────────────────────────────────────
        priority = ["COMPANY", "TICKER", "COMPANY_NAME", "YEAR", "FISCAL_YEAR",
                    "PERIOD", "REPORT_DATE", "METRIC", "TITLE", "DESCRIPTION",
                    "CONTENT", "TEXT", "SUMMARY", "NOTES"]
        ordered = {}
        rest = {}
        for k, v in row.items():
            if k.upper() in [p.upper() for p in priority]:
                ordered[k] = v
            else:
                rest[k] = v
        for k, v in {**ordered, **rest}.items():
            if v is not None and str(v).strip():
                parts.append(f"{k}: {v}")
        return ". ".join(parts)

    # ── Public API ───────────────────────────────────────────────────────────

    def fetch_documents(
        self,
        query: str = None,
        table: str = None,
        limit: int = 500,
    ) -> List[Document]:
        """
        Fetch documents from Snowflake.

        Priority:
          1. Raw SQL `query` if provided
          2. Named `table` with a SELECT … LIMIT
          3. Auto-discover tables from DEFAULT_TABLES that exist in the schema
        """
        documents: List[Document] = []

        try:
            self.connect()

            if query:
                rows = self._execute(query)
                source_label = "custom_query"
                for idx, row in enumerate(rows):
                    documents.append(Document(
                        id=f"sf_query_{idx}",
                        title=f"Snowflake result row {idx + 1}",
                        content=self._row_to_text(row, "QUERY"),
                        source="SNOWFLAKE",
                        company=row.get("COMPANY") or row.get("TICKER"),
                        metadata={"source_label": source_label, "row_index": idx, **row},
                    ))

            else:
                tables_to_fetch: List[str] = []
                if table:
                    tables_to_fetch = [table.upper()]
                else:
                    available = set(self._available_tables())
                    tables_to_fetch = [t for t in self.DEFAULT_TABLES if t in available]
                    if not tables_to_fetch:
                        # Fall back: fetch everything available
                        tables_to_fetch = list(available)

                for tbl in tables_to_fetch:
                    try:
                        rows = self._execute(
                            f'SELECT * FROM "{tbl}" LIMIT %s', (limit,)
                        )
                        for idx, row in enumerate(rows):
                            company = (row.get("COMPANY") or row.get("TICKER")
                                       or row.get("COMPANY_NAME"))
                            year = (row.get("YEAR") or row.get("FISCAL_YEAR")
                                    or row.get("PERIOD"))
                            documents.append(Document(
                                id=f"sf_{tbl}_{idx}",
                                title=f"{tbl} record {idx + 1}"
                                      + (f" – {company}" if company else "")
                                      + (f" ({year})" if year else ""),
                                content=self._row_to_text(row, tbl),
                                source="SNOWFLAKE",
                                financial_year=int(year) if str(year).isdigit() else None,
                                company=str(company) if company else None,
                                metadata={"table": tbl, "row_index": idx, **row},
                            ))
                        logger.info(f"Fetched {len(rows)} rows from {tbl}")
                    except Exception as e:
                        logger.warning(f"Could not fetch table {tbl}: {e}")

            logger.info(f"Total Snowflake documents fetched: {len(documents)}")
        except Exception as e:
            logger.error(f"Snowflake fetch failed: {e}")
        finally:
            self.disconnect()

        return documents


class DataIngestionPipeline:
    """Orchestrates data ingestion from multiple sources"""
    
    def __init__(self):
        self.sources: Dict[str, DataSource] = {}
        self.documents: List[Document] = []
    
    def register_source(self, name: str, source: DataSource):
        """Register a data source"""
        self.sources[name] = source
        logger.info(f"Registered data source: {name}")
    
    def ingest(self, source_name: str, **kwargs) -> List[Document]:
        """
        Ingest data from a specific source
        
        Args:
            source_name: Name of registered source
            **kwargs: Source-specific parameters
            
        Returns:
            List of ingested documents
        """
        if source_name not in self.sources:
            logger.error(f"Source not found: {source_name}")
            return []
        
        source = self.sources[source_name]
        documents = source.fetch_documents(**kwargs)
        self.documents.extend(documents)
        
        logger.info(f"Ingested {len(documents)} documents from {source_name}")
        return documents
    
    def ingest_all(self, source_configs: Dict[str, Dict]) -> List[Document]:
        """
        Ingest from multiple sources
        
        Args:
            source_configs: Dict mapping source names to their configs
            
        Returns:
            All ingested documents
        """
        for source_name, config in source_configs.items():
            if source_name in self.sources:
                self.ingest(source_name, **config)
        
        logger.info(f"Total documents ingested: {len(self.documents)}")
        return self.documents
    
    def get_documents(self) -> List[Document]:
        """Get all ingested documents"""
        return self.documents
