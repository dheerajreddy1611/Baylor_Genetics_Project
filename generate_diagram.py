#!/usr/bin/env python3
"""
Generate ER Diagram for Gene Identification Database Schema
Part 3: Schema Diagram Code
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch


def create_er_diagram():
    """Create ER diagram using matplotlib."""

    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Colors
    table_color = '#E3F2FD'
    pk_color = '#FFF3E0'
    fk_color = '#F3E5F5'

    # Table 1: genes
    genes_box = FancyBboxPatch((1, 5), 3, 2, boxstyle="round,pad=0.05",
                              facecolor=table_color, edgecolor='black', linewidth=2)
    ax.add_patch(genes_box)
    ax.text(2.5, 6.5, 'genes', ha='center', va='center', fontsize=12, fontweight='bold')
    ax.text(1.2, 6.0, 'id (PK)', ha='left', va='center', fontsize=10, bbox=dict(boxstyle="round,pad=0.2", facecolor=pk_color))
    ax.text(1.2, 5.7, 'hgnc_id', ha='left', va='center', fontsize=10)
    ax.text(1.2, 5.4, 'gene_symbol', ha='left', va='center', fontsize=10)
    ax.text(1.2, 5.1, 'full_name', ha='left', va='center', fontsize=10)

    # Table 2: gene_aliases
    aliases_box = FancyBboxPatch((5.5, 5), 3, 2, boxstyle="round,pad=0.05",
                                facecolor=table_color, edgecolor='black', linewidth=2)
    ax.add_patch(aliases_box)
    ax.text(7, 6.5, 'gene_aliases', ha='center', va='center', fontsize=12, fontweight='bold')
    ax.text(5.7, 6.0, 'id (PK)', ha='left', va='center', fontsize=10, bbox=dict(boxstyle="round,pad=0.2", facecolor=pk_color))
    ax.text(5.7, 5.7, 'gene_id (FK)', ha='left', va='center', fontsize=10, bbox=dict(boxstyle="round,pad=0.2", facecolor=fk_color))
    ax.text(5.7, 5.4, 'alias', ha='left', va='center', fontsize=10)

    # Table 3: disease_associations
    disease_box = FancyBboxPatch((1, 1.5), 3, 2, boxstyle="round,pad=0.05",
                                facecolor=table_color, edgecolor='black', linewidth=2)
    ax.add_patch(disease_box)
    ax.text(2.5, 3.0, 'disease_associations', ha='center', va='center', fontsize=12, fontweight='bold')
    ax.text(1.2, 2.5, 'id (PK)', ha='left', va='center', fontsize=10, bbox=dict(boxstyle="round,pad=0.2", facecolor=pk_color))
    ax.text(1.2, 2.2, 'gene_id (FK)', ha='left', va='center', fontsize=10, bbox=dict(boxstyle="round,pad=0.2", facecolor=fk_color))
    ax.text(1.2, 1.9, 'disease_name', ha='left', va='center', fontsize=10)
    ax.text(1.2, 1.6, 'source_context', ha='left', va='center', fontsize=10)

    # Relationships
    # genes -> gene_aliases
    con1 = ConnectionPatch((4, 6), (5.5, 6), "data", "data",
                          arrowstyle="->", shrinkA=5, shrinkB=5,
                          mutation_scale=15, fc="black", color="black")
    ax.add_artist(con1)
    ax.text(4.75, 6.2, '1:N', ha='center', va='center', fontsize=10, fontweight='bold')

    # genes -> disease_associations
    con2 = ConnectionPatch((2.5, 5), (2.5, 3.5), "data", "data",
                          arrowstyle="->", shrinkA=5, shrinkB=5,
                          mutation_scale=15, fc="black", color="black")
    ax.add_artist(con2)
    ax.text(2.7, 4.25, '1:N', ha='center', va='center', fontsize=10, fontweight='bold')

    # Title
    ax.text(6, 7.5, 'Gene Identification Database ER Diagram', ha='center', va='center',
            fontsize=16, fontweight='bold')

    # Legend
    ax.text(9, 7, 'Legend:', ha='left', va='center', fontsize=12, fontweight='bold')
    ax.text(9, 6.5, 'PK = Primary Key', ha='left', va='center', fontsize=10)
    ax.text(9, 6.2, 'FK = Foreign Key', ha='left', va='center', fontsize=10)
    ax.text(9, 5.9, '1:N = One to Many', ha='left', va='center', fontsize=10)

    plt.tight_layout()
    plt.savefig('schema_diagram.png', dpi=300, bbox_inches='tight')
    print("ER diagram saved as schema_diagram.png")


if __name__ == "__main__":
    create_er_diagram()