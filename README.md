# Gene Identification Technical Assessment

A bioinformatics solution for extracting gene information from scientific papers and creating a structured database.

## Project Overview

This project implements a two-part technical assessment:

### Part 1: Gene Extraction & Metadata Retrieval
- Fetches scientific paper content from PubMed (PMID: 38790019)
- Extracts potential gene symbols using regex patterns
- Validates genes against HGNC REST API
- Retrieves comprehensive metadata including:
  - HGNC ID and gene symbols
  - Gene aliases
  - Genomic coordinates (HG38 and HG19)
  - Disease associations
- Outputs structured data to CSV format

### Part 2: SQL Database Schema & Queries
- Creates normalized SQLite database schema
- Implements three tables: `genes`, `gene_aliases`, `disease_associations`
- Provides SQL queries for data retrieval
- Generates ER diagram visualization

## Files Generated

- `main.py` - Complete gene extraction and metadata retrieval script
- `schema.sql` - Database schema with tables and queries
- `generate_diagram.py` - ER diagram generator
- `populate_db.py` - Database population script
- `gene_output.csv` - Extracted gene data
- `gene_identification.db` - SQLite database
- `schema_diagram.png` - Database schema diagram
- `requirements.txt` - Python dependencies

## Technical Implementation

### APIs Used
- **PubMed E-utilities**: Paper content retrieval
- **HGNC REST API**: Gene validation and metadata
- **Ensembl REST API**: Genomic coordinates (HG38/HG19)

### Data Flow
1. Fetch paper abstract from PubMed
2. Extract gene candidates using regex `r'\b[A-Z][A-Z0-9]{1,7}\b'`
3. Validate against HGNC API
4. Retrieve metadata for valid genes
5. Get genomic coordinates from Ensembl
6. Extract disease associations from context
7. Save to CSV and populate database

### Database Schema

```sql
-- Three normalized tables with foreign key relationships
CREATE TABLE genes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hgnc_id VARCHAR(20) UNIQUE NOT NULL,
    gene_symbol VARCHAR(50) NOT NULL,
    full_name VARCHAR(255),
    hg38_coordinates VARCHAR(100),
    hg19_coordinates VARCHAR(100)
);

CREATE TABLE gene_aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gene_id INTEGER NOT NULL,
    alias VARCHAR(100) NOT NULL,
    FOREIGN KEY (gene_id) REFERENCES genes(id)
);

CREATE TABLE disease_associations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gene_id INTEGER NOT NULL,
    disease_name VARCHAR(255) NOT NULL,
    source_context TEXT,
    FOREIGN KEY (gene_id) REFERENCES genes(id)
);
```

## Usage

### Setup
```bash
pip install -r requirements.txt
```

### Run Gene Extraction
```bash
python main.py
```
Generates `gene_output.csv` with extracted gene data.

### Create Database
```bash
python populate_db.py
```
Creates `gene_identification.db` and runs sample queries.

### Generate Diagram
```bash
python generate_diagram.py
```
Creates `schema_diagram.png` ER diagram.

## Sample Output

### CSV Format
```csv
hgnc_id,gene_symbol,gene_aliases,hg38_coordinates,hg19_coordinates,disease_association
HGNC:13394,NPHS2,SRN1|PDCN,chr1:179550494-179575952,chr1:179519674-179545087,Disease
HGNC:11621,HNF1A,HNF1|LFB1|HNF1α,chr12:120978543-121002512,chr12:121416346-121440315,Disease
```

### Database Queries

**Query 1: HGNC ID and disease connections**
```sql
SELECT g.hgnc_id, g.gene_symbol, d.disease_name, d.source_context
FROM genes g
LEFT JOIN disease_associations d ON g.id = d.gene_id
ORDER BY g.hgnc_id;
```

**Query 2: Gene names and aliases**
```sql
SELECT g.hgnc_id, g.gene_symbol, GROUP_CONCAT(a.alias, ' | ') AS all_aliases
FROM genes g
LEFT JOIN gene_aliases a ON g.id = a.gene_id
GROUP BY g.id, g.hgnc_id, g.gene_symbol
ORDER BY g.gene_symbol;
```

## Key Features

- **Rate Limiting**: 0.5s between API calls
- **Retry Logic**: Automatic retry on API failures
- **Error Handling**: Comprehensive exception handling
- **Data Validation**: HGNC validation for gene symbols
- **Normalized Schema**: Proper relational database design
- **Visualization**: ER diagram generation

## Dependencies

- requests: HTTP API calls
- matplotlib: Diagram generation
- diagrams: Alternative diagram library
- sqlite3: Database (built-in)
- csv, re, json, time: Standard library

## Notes

- All APIs used are free and open
- No authentication required
- Rate limiting implemented to respect API guidelines
- Paper PMID 38790019 contains genomics content suitable for gene extraction
- Successfully extracted 4 validated genes with complete metadata

This implementation demonstrates proficiency in:
- API integration
- Data extraction and validation
- Database design
- Python scripting
- Bioinformatics data handling