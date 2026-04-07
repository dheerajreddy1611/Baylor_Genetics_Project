-- Gene Identification Database Schema
-- Part 2: SQL Schema and Queries

-- Create tables
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

-- Query 1: HGNC ID and disease connection
SELECT
    g.hgnc_id,
    g.gene_symbol,
    d.disease_name,
    d.source_context
FROM genes g
LEFT JOIN disease_associations d ON g.id = d.gene_id
ORDER BY g.hgnc_id;

-- Query 2: Gene name and all aliases
SELECT
    g.hgnc_id,
    g.gene_symbol,
    GROUP_CONCAT(a.alias, ' | ') AS all_aliases
FROM genes g
LEFT JOIN gene_aliases a ON g.id = a.gene_id
GROUP BY g.id, g.hgnc_id, g.gene_symbol
ORDER BY g.gene_symbol;

-- INSERT statements will be generated after running main.py and reading gene_output.csv
-- Example INSERT statements (replace with actual data):
/*
INSERT INTO genes (hgnc_id, gene_symbol, full_name, hg38_coordinates, hg19_coordinates) VALUES
('HGNC:11998', 'TP53', 'tumor protein p53', 'chr17:7571720-7590868', 'chr17:7571720-7590868');

INSERT INTO gene_aliases (gene_id, alias) VALUES
(1, 'P53'),
(1, 'LFS1');

INSERT INTO disease_associations (gene_id, disease_name, source_context) VALUES
(1, 'Cancer', 'TP53 mutations are associated with various cancers');
*/