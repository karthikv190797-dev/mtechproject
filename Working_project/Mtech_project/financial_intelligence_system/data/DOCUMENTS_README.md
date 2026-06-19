# Knowledge Base Document Storage

This directory holds financial documents for the RAG pipeline knowledge base.

## 📁 Directory Structure

```
data/
├── sec_filings/              # SEC 10-K/10-Q filings
│   ├── apple_10k_2023.txt
│   ├── microsoft_10k_2023.txt
│   └── tesla_10k_2023.txt
├── earnings_calls/           # Earnings call transcripts
│   ├── apple_earnings_q4_2023.txt
│   └── microsoft_earnings_q4_2023.txt
├── financial_reports/        # Annual & quarterly reports
│   ├── apple_annual_report_2023.pdf
│   └── amazon_quarterly_report_q4_2023.txt
├── news_articles/           # Financial news & press releases
│   └── samsung_expansion_announcement_2024.txt
└── metadata.json            # Index of all documents (auto-generated)
```

## 📝 Supported Formats

- **Text files** (`.txt`) — plain text financial documents
- **JSON files** (`.json`) — structured document batches
- **Markdown files** (`.md`) — formatted documentation
- **PDF** (`.pdf`) — requires PDF parsing library (optional)

## 🔧 Adding Documents

### Option 1: Manual Text Files
Place `.txt` files in the appropriate subdirectory:
```bash
cp apple_10k_2023.txt data/sec_filings/
cp earnings_transcript.txt data/earnings_calls/
```

### Option 2: Using the Python API
```python
from src.ingestion import LocalFileSource

loader = LocalFileSource(base_dir="data/")
documents = loader.fetch_documents()  # Auto-scans all subdirs
```

### Option 3: Using Batch JSON
Create `data/documents_batch.json`:
```json
[
  {
    "id": "apple_10k_2023",
    "title": "Apple Inc. 10-K Filing 2023",
    "content": "Form 10-K filed with SEC...",
    "source": "SEC_EDGAR",
    "company": "AAPL",
    "financial_year": 2023,
    "metadata": {"filing_type": "10-K"}
  },
  {
    "id": "msft_earnings_q4_2023",
    "title": "Microsoft Q4 2023 Earnings",
    "content": "Earnings call transcript...",
    "source": "INVESTOR_RELATIONS",
    "company": "MSFT",
    "metadata": {"quarter": 4, "year": 2023}
  }
]
```

## 🔍 Document Format Best Practices

Each document should ideally contain:
- **Company name** (in title or metadata)
- **Filing type** (10-K, 10-Q, earnings call, etc.)
- **Year/Quarter** (fiscal year and quarter if applicable)
- **Clear content sections** (MD&A, financial statements, risks, etc.)

**Example document structure:**
```
Apple Inc. 10-K Filing for 2023

Company: Apple Inc.
Filing Type: Form 10-K
Fiscal Year: 2023
CIK: 0000320193

1. BUSINESS
   Apple Inc. designs, manufactures, and markets smartphones, personal computers...

2. RISK FACTORS
   The Company faces risks in supply chain disruptions, macroeconomic conditions...

3. FINANCIAL STATEMENTS
   Revenue: $383.3 billion
   Gross Margin: 44.1%
   Net Income: $96.7 billion
   ...
```

## ⚙️ Auto-Indexing

The system will automatically:
1. Scan all subdirectories when the backend starts
2. Create embeddings for each document
3. Store metadata in `data/metadata.json`
4. Index documents in the retrieval system (FAISS/BM25)

## 📊 Sample Documents

Sample documents are available in:
- `examples/sample_data/` — ready-to-use examples
- Use these to test the pipeline before adding production data

## 🔐 Privacy & Security

- Store sensitive documents in a `.gitignore`'d directory (already configured)
- Use environment variables for accessing external document sources
- Review document content before indexing

## 📞 Troubleshooting

- **Documents not loading?** Check file permissions: `chmod 644 data/**/*.txt`
- **Encoding issues?** Ensure UTF-8 encoding: `file data/sec_filings/*.txt`
- **Slow indexing?** Large files slow embedding — split into sections
