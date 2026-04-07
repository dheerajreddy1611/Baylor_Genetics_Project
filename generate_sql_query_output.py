#!/usr/bin/env python3
"""Generate actual SQL query outputs from the populated database."""

import sqlite3
from pathlib import Path


def main():
    db_path = Path('gene_identification.db')
    if not db_path.exists():
        raise FileNotFoundError('gene_identification.db not found. Run populate_db.py first.')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    queries = [
        (
            'Query 1: HGNC ID and disease connection',
            '''
SELECT
    g.hgnc_id,
    g.gene_symbol,
    d.disease_name,
    d.source_context
FROM genes g
LEFT JOIN disease_associations d ON g.id = d.gene_id
ORDER BY g.hgnc_id;
''',
        ),
        (
            'Query 2: Gene name and all aliases',
            '''
SELECT
    g.hgnc_id,
    g.gene_symbol,
    GROUP_CONCAT(a.alias, ' | ') AS all_aliases
FROM genes g
LEFT JOIN gene_aliases a ON g.id = a.gene_id
GROUP BY g.id, g.hgnc_id, g.gene_symbol
ORDER BY g.gene_symbol;
''',
        ),
    ]

    output_lines = []
    for title, query in queries:
        output_lines.append(title)
        output_lines.append('-' * len(title))
        output_lines.append(query.strip())
        output_lines.append('RESULTS:')
        cursor.execute(query)
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                output_lines.append(str(row))
        else:
            output_lines.append('No results')
        output_lines.append('')

    target = Path('sql_query_output.txt')
    target.write_text('\n'.join(output_lines), encoding='utf-8')
    conn.close()
    print(f'Wrote SQL output to {target}')


if __name__ == '__main__':
    main()
