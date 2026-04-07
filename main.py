#!/usr/bin/env python3
"""
Gene Identification System - Technical Assessment
Part 1: Gene Extraction & Metadata Retrieval

This script fetches a scientific paper (PMID: 38790019), extracts gene symbols,
validates them against HGNC, retrieves metadata, and outputs to CSV.
"""

import requests
import csv
import xml.etree.ElementTree as ET
import time
import re
import json
import sys
from typing import List, Dict, Optional, Tuple


class GeneExtractor:
    """Handles gene extraction and metadata retrieval."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GeneIdentificationScript/1.0 (mailto:your.email@example.com)'
        })

    def make_api_call(self, url: str, headers: Optional[Dict] = None, params: Optional[Dict] = None, retries: int = 1) -> Optional[requests.Response]:
        """Make API call with retry logic and rate limiting."""
        for attempt in range(retries + 1):
            try:
                time.sleep(0.5)  # Rate limiting
                response = self.session.get(url, headers=headers, params=params, timeout=10)
                if response.status_code == 200:
                    return response
                elif attempt < retries:
                    print(f"API call failed (status {response.status_code}), retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    print(f"API call failed after {retries + 1} attempts: {response.status_code}")
                    return None
            except Exception as e:
                if attempt < retries:
                    print(f"API call error: {e}, retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    print(f"API call failed after {retries + 1} attempts: {e}")
                    return None
        return None

    def fetch_paper_content(self, pmid: str) -> Optional[str]:
        """Fetch paper content from PubMed."""
        print(f"Fetching paper content for PMID: {pmid}")

        # Try to fetch full text first
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params = {
            "db": "pubmed",
            "id": pmid,
            "rettype": "xml",
            "retmode": "xml"
        }

        response = self.make_api_call(url, params=params)
        if not response:
            return None

        try:
            root = ET.fromstring(response.text)
            # Extract title and abstract
            title = ""
            abstract = ""

            for elem in root.iter():
                if elem.tag == 'ArticleTitle':
                    title = elem.text or ""
                elif elem.tag == 'AbstractText':
                    abstract += (elem.text or "") + " "

            content = f"{title} {abstract}".strip()
            print(f"Extracted content length: {len(content)} characters")
            return content if content else None

        except Exception as e:
            print(f"Error parsing XML: {e}")
            return None

    def extract_gene_candidates(self, text: str) -> List[str]:
        """Extract potential gene symbols using regex."""
        print("Extracting gene candidates from text...")

        # Pattern for gene symbols: uppercase letters and numbers, 2-8 characters
        pattern = r'\b[A-Z][A-Z0-9]{1,7}\b'
        candidates = re.findall(pattern, text)

        # Remove duplicates and filter common non-gene words
        common_words = {
            'THE', 'AND', 'FOR', 'FROM', 'THAT', 'WITH', 'THIS', 'WHICH', 'WERE', 'THEIR',
            'HAVE', 'BEEN', 'EACH', 'SUCH', 'THAN', 'BOTH', 'THROUGH', 'NOVEL', 'STUDY',
            'USING', 'BASED', 'RESULTS', 'METHODS', 'ANALYSIS', 'SHOWED', 'FINDINGS',
            'THESE', 'CELLS', 'MICE', 'HUMAN', 'DISEASE', 'ASSOCIATED', 'IDENTIFIED',
            'GENE', 'GENES', 'DATA', 'ABSTRACT', 'OBJECT', 'DOI', 'NCBI', 'PMID', 'NIH'
        }

        candidates = [c for c in set(candidates) if c not in common_words and len(c) >= 2]
        print(f"Found {len(candidates)} gene candidates: {candidates[:10]}...")
        return candidates

    def validate_gene_symbol(self, symbol: str) -> Optional[Dict]:
        """Validate gene symbol against HGNC API."""
        url = f"https://rest.genenames.org/search/symbol/{symbol}"
        headers = {"Accept": "application/json"}

        response = self.make_api_call(url, headers=headers)
        if not response:
            return None

        try:
            data = response.json()
            docs = data.get('response', {}).get('docs', [])
            if docs:
                return docs[0]  # Return first match
        except Exception as e:
            print(f"Error validating gene {symbol}: {e}")

        return None

    def get_gene_metadata(self, symbol: str) -> Optional[Dict]:
        """Get detailed gene metadata from HGNC."""
        url = f"https://rest.genenames.org/fetch/symbol/{symbol}"
        headers = {"Accept": "application/json"}

        response = self.make_api_call(url, headers=headers)
        if not response:
            return None

        try:
            data = response.json()
            docs = data.get('response', {}).get('docs', [])
            if docs:
                return docs[0]
        except Exception as e:
            print(f"Error getting metadata for {symbol}: {e}")

        return None

    def get_genomic_coordinates(self, symbol: str, assembly: str = "hg38") -> Optional[str]:
        """Get genomic coordinates from Ensembl."""
        base_url = "https://rest.ensembl.org" if assembly == "hg38" else "https://grch37.rest.ensembl.org"
        url = f"{base_url}/lookup/symbol/homo_sapiens/{symbol}"
        headers = {"Content-Type": "application/json"}

        response = self.make_api_call(url, headers=headers)
        if not response:
            return None

        try:
            data = response.json()
            if 'seq_region_name' in data and 'start' in data and 'end' in data:
                chrom = data['seq_region_name']
                start = data['start']
                end = data['end']
                return f"chr{chrom}:{start}-{end}"
        except Exception as e:
            print(f"Error getting {assembly} coordinates for {symbol}: {e}")

        return None

    def extract_disease_association(self, text: str, gene_symbol: str) -> Optional[str]:
        """Extract disease association context for a gene."""
        # Look for sentences containing the gene and disease keywords
        sentences = re.split(r'[.!?]+', text)
        disease_keywords = ['syndrome', 'disease', 'disorder', 'cancer', 'carcinoma', 'mutation', 'pathogenic']

        for sentence in sentences:
            if gene_symbol in sentence:
                for keyword in disease_keywords:
                    if keyword.lower() in sentence.lower():
                        # Extract disease name (simplified - look for capitalized words after keyword)
                        words = sentence.split()
                        for i, word in enumerate(words):
                            if keyword.lower() in word.lower():
                                # Look for disease name in next few words
                                for j in range(i+1, min(i+4, len(words))):
                                    if words[j][0].isupper():
                                        return words[j].strip('.,')
                        return keyword.capitalize()

        return None

    def process_paper(self, pmid: str) -> List[Dict]:
        """Main processing function."""
        print("=== Starting Gene Extraction Process ===")

        # Step 1: Fetch paper content
        content = self.fetch_paper_content(pmid)
        if not content:
            print("Failed to fetch paper content")
            return []

        # Step 2: Extract gene candidates
        candidates = self.extract_gene_candidates(content)
        if not candidates:
            print("No gene candidates found")
            return []

        # Step 3: Validate genes against HGNC
        validated_genes = []
        print("Validating gene symbols against HGNC...")

        for symbol in candidates[:20]:  # Limit to avoid too many API calls
            print(f"Validating: {symbol}")
            validation = self.validate_gene_symbol(symbol)
            if validation:
                validated_genes.append(symbol)
                print(f"✓ Valid gene: {symbol}")
            else:
                print(f"✗ Invalid gene: {symbol}")

            if len(validated_genes) >= 10:  # Get at least 10 genes
                break

        if len(validated_genes) < 5:
            print(f"Warning: Only found {len(validated_genes)} valid genes (need at least 5)")

        # Step 4: Get metadata for each validated gene
        results = []
        print("Retrieving metadata for validated genes...")

        for symbol in validated_genes:
            print(f"Processing gene: {symbol}")

            # Get HGNC metadata
            metadata = self.get_gene_metadata(symbol)
            if not metadata:
                print(f"Skipping {symbol} - no metadata found")
                continue

            hgnc_id = metadata.get('hgnc_id', 'Not available')
            gene_symbol = metadata.get('symbol', symbol)
            aliases = metadata.get('alias_symbol', [])
            alias_str = '|'.join(aliases) if aliases else 'None'
            full_name = metadata.get('name', 'Not available')

            # Get coordinates
            hg38_coords = self.get_genomic_coordinates(symbol, "hg38") or "Not available"
            hg19_coords = self.get_genomic_coordinates(symbol, "hg19") or "Not available"

            # Get disease association
            disease = self.extract_disease_association(content, symbol) or "Not specified"

            gene_data = {
                'hgnc_id': hgnc_id,
                'gene_symbol': gene_symbol,
                'gene_aliases': alias_str,
                'hg38_coordinates': hg38_coords,
                'hg19_coordinates': hg19_coords,
                'disease_association': disease
            }

            results.append(gene_data)
            print(f"✓ Processed: {symbol} -> {hgnc_id}")

        print(f"Successfully processed {len(results)} genes")
        return results

    def save_to_csv(self, data: List[Dict], filename: str = "gene_output.csv"):
        """Save results to CSV file."""
        if not data:
            print("No data to save")
            return

        print(f"Saving {len(data)} genes to {filename}")

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['hgnc_id', 'gene_symbol', 'gene_aliases', 'hg38_coordinates', 'hg19_coordinates', 'disease_association']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        print(f"Data saved to {filename}")


def main():
    """Main execution function."""
    extractor = GeneExtractor()
    results = extractor.process_paper("38790019")

    if results:
        extractor.save_to_csv(results)
        print("\n=== Process Complete ===")
        print(f"Extracted {len(results)} genes with metadata")
        print("Output saved to gene_output.csv")
    else:
        print("No genes were successfully processed")
        sys.exit(1)


if __name__ == "__main__":
    main()