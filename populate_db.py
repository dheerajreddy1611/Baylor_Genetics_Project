#!/usr/bin/env python3
"""
Populate Database with Gene Data
Reads gene_output.csv and inserts data into SQLite database
"""

import sqlite3
import csv
import os


def create_database():
    """Create the database and tables."""
    conn = sqlite3.connect('gene_identification.db')
    cursor = conn.cursor()

    # Read and execute schema.sql
    with open('schema.sql', 'r') as f:
        schema_sql = f.read()

    # Execute only the CREATE TABLE statements (ignore queries and comments)
    statements = []
    current_statement = []
    in_multiline_comment = False

    for line in schema_sql.split('\n'):
        line = line.strip()
        if not line or line.startswith('--'):
            continue
        if line.startswith('/*'):
            in_multiline_comment = True
            continue
        if line.startswith('*/'):
            in_multiline_comment = False
            continue
        if in_multiline_comment:
            continue

        current_statement.append(line)
        if line.endswith(';'):
            statements.append(' '.join(current_statement))
            current_statement = []

    for statement in statements:
        if statement.upper().startswith('CREATE TABLE'):
            cursor.execute(statement)

    conn.commit()
    return conn


def populate_database(conn, csv_file='gene_output.csv'):
    """Populate database with data from CSV."""
    cursor = conn.cursor()

    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found. Run main.py first.")
        return

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        genes_data = list(reader)

    print(f"Loading {len(genes_data)} genes from {csv_file}")

    # Insert genes
    for gene in genes_data:
        try:
            cursor.execute('''
                INSERT INTO genes (hgnc_id, gene_symbol, full_name, hg38_coordinates, hg19_coordinates)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                gene['hgnc_id'],
                gene['gene_symbol'],
                'Not available',  # We don't have full name in CSV
                gene['hg38_coordinates'],
                gene['hg19_coordinates']
            ))

            gene_id = cursor.lastrowid

            # Insert aliases
            if gene['gene_aliases'] != 'None':
                aliases = gene['gene_aliases'].split('|')
                for alias in aliases:
                    if alias.strip():
                        cursor.execute('''
                            INSERT INTO gene_aliases (gene_id, alias)
                            VALUES (?, ?)
                        ''', (gene_id, alias.strip()))

            # Insert disease associations
            if gene['disease_association'] != 'Not specified':
                cursor.execute('''
                    INSERT INTO disease_associations (gene_id, disease_name, source_context)
                    VALUES (?, ?, ?)
                ''', (gene_id, gene['disease_association'], 'Extracted from paper'))

        except sqlite3.IntegrityError as e:
            print(f"Skipping duplicate gene {gene['gene_symbol']}: {e}")
        except Exception as e:
            print(f"Error inserting gene {gene['gene_symbol']}: {e}")

    conn.commit()
    print("Database populated successfully")


def run_queries(conn):
    """Run the required queries and display results."""
    cursor = conn.cursor()

    print("\n=== Query 1: HGNC ID and disease connection ===")
    cursor.execute('''
        SELECT
            g.hgnc_id,
            g.gene_symbol,
            d.disease_name,
            d.source_context
        FROM genes g
        LEFT JOIN disease_associations d ON g.id = d.gene_id
        ORDER BY g.hgnc_id
    ''')

    results = cursor.fetchall()
    for row in results:
        print(row)

    print("\n=== Query 2: Gene name and all aliases ===")
    cursor.execute('''
        SELECT
            g.hgnc_id,
            g.gene_symbol,
            GROUP_CONCAT(a.alias, ' | ') AS all_aliases
        FROM genes g
        LEFT JOIN gene_aliases a ON g.id = a.gene_id
        GROUP BY g.id, g.hgnc_id, g.gene_symbol
        ORDER BY g.gene_symbol
    ''')

    results = cursor.fetchall()
    for row in results:
        print(row)


def main():
    """Main execution."""
    if not os.path.exists('gene_output.csv'):
        print("gene_output.csv not found. Please run main.py first.")
        return

    conn = create_database()
    populate_database(conn)
    run_queries(conn)
    conn.close()

    print("\nDatabase created and populated successfully!")
    print("File: gene_identification.db")


if __name__ == "__main__":
    main()