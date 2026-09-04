# FASTA GC Content Calculator

> **Domain:** Bioinformatics & Genomic Sequence Analysis

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)

</div>

---

## Overview

FASTA GC Content Calculator is a Python tool for analyzing DNA sequences in FASTA format. It computes GC content, sliding window GC distribution, CpG observed/expected ratio, dinucleotide frequencies, N50 calculation, and masked vs unmasked content.

**Zero external dependencies for core functionality** — uses Python stdlib only. Optional `pydantic` dependency for the enterprise agent framework.

---

## Features

### Core Analysis Functions

- **`parse_fasta()`**: Parse FASTA format text into list of `{header, sequence}` dicts. Supports multi-sequence files and concatenates multi-line sequences.
- **`parse_fasta_file()`**: Parse a FASTA file from disk.
- **`gc_content()`**: Calculate GC content: `(G+C) / (A+T+G+C) × 100`, excluding N and ambiguous bases. Returns percentage (0-100).
- **`gc_content_detailed()`**: Detailed GC content analysis with base counts.
- **`sliding_window_gc()`**: Calculate GC content in sliding windows across a sequence.
- **`cpg_observed_expected()`**: Calculate CpG observed/expected ratio and detect CpG islands.
- **`dinucleotide_frequencies()`**: Count all 16 dinucleotide frequencies.
- **`masked_vs_unmasked()`**: Analyze soft-masked (lowercase) vs unmasked (uppercase) content.
- **`calculate_n50()`**: Calculate N50 from a list of sequence lengths.
- **`assembly_stats()`**: Calculate assembly statistics including N50.
- **`analyze_fasta()`**: Complete analysis of a FASTA file.
- **`process_batch()`**: Batch process sequences from CSV.

---

## Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/fasta-gc-calculator.git
cd fasta-gc-calculator

# No installation required for core functionality (Python 3.10+ stdlib only)
# For the agent framework, install optional dependencies:
pip install pydantic
```

---

## Usage

### CLI Commands

#### GC Content Analysis
```bash
# Analyze a sequence directly
python cli.py gc --sequence ATCGATCG

# Analyze a FASTA file
python cli.py gc --file sequences.fasta

# Read from stdin
echo ">seq1\nATCGATCG" | python cli.py gc
```

#### CpG Analysis
```bash
# Analyze CpG observed/expected ratio
python cli.py cpg --sequence ACGACG

# Analyze a FASTA file
python cli.py cpg --file sequences.fasta
```

#### Sliding Window GC
```bash
# Analyze GC distribution in sliding windows
python cli.py window --sequence ATCGATCGATCG --window-size 50 --step 10

# Analyze from file
python cli.py window --file sequences.fasta --window-size 100 --step 20
```

#### N50 Calculation
```bash
# Calculate N50 from comma-separated lengths
python cli.py n50 --lengths 100,200,300,400

# Calculate N50 from FASTA file
python cli.py n50 --file sequences.fasta
```

#### Batch Processing
```bash
# Process sequences from CSV (requires 'sequence' or 'seq' column)
python cli.py batch --input sequences.csv --output results.csv
```

### Python API
```python
from fasta_gc import parse_fasta, gc_content, calculate_n50

# Parse FASTA text
sequences = parse_fasta(">seq1\nATCGATCG\n>seq2\nGGCCAA\n")

# Calculate GC content
gc = gc_content("ATCGATCG")  # Returns 50.0

# Calculate N50
n50 = calculate_n50([100, 200, 300, 400])  # Returns 300
```

---

## Input Formats

### FASTA Format
```
>sequence_id Optional description
ATCGATCGATCGATCGATCG
ATCGATCGATCGATCGATCG
>another_sequence
GGCCGGCCGGCC
```

### Batch CSV Format
```csv
header,sequence
seq1,ATCGATCG
seq2,GGCCGGCC
```

---

## Testing

```bash
# Run all tests
pytest -v

# Run specific test files
pytest test_fasta_gc.py -v
pytest tests/test_fasta_gc_calculator.py -v
pytest tests/test_enrichment.py -v

# Run with coverage
pytest --cov=fasta_gc --cov=cli --cov=agents tests/ -v
```

---

## Project Structure

```
fasta-gc-calculator/
├── fasta_gc.py           # Core FASTA analysis functions
├── cli.py                # Command-line interface
├── test_fasta_gc.py      # Core functionality tests (36 tests)
├── enrichment.py         # Enrichment feature engines
├── simulator.py          # Throughput simulation
├── agents/               # Enterprise agent framework
│   ├── base.py           # Security, PHI guard, audit trail
│   ├── models.py         # Pydantic data models
│   ├── supervisor.py     # Multi-agent orchestrator
│   ├── workers.py        # Specialized analysis workers
│   ├── api.py            # FastAPI REST endpoints
│   ├── metrics.py        # Prometheus metrics
│   ├── learning.py       # Bayesian calibration engine
│   ├── llm_factory.py    # LLM provider abstraction
│   └── streamer.py       # WebSocket telemetry
├── tests/                # Test directory
│   ├── test_fasta_gc_calculator.py
│   └── test_enrichment.py
├── web/index.html        # Operations console UI
├── Dockerfile            # Container build
├── docker-compose.yml    # Container orchestration
├── benchmark_dataset.json # Golden benchmark test cases
└── sample.csv            # Sample batch input
```

---

## Security Features

- **Zero-PHI Outbound Guard:** Regex-based detection and blocking of SSNs, MRNs, phone numbers, emails, and patient identifiers in outbound data.
- **HMAC-SHA256 Audit Trail:** Cryptographic chained audit log for tamper-evident record keeping.
- **Docker Secrets:** Audit secret key configurable via environment variable (not hardcoded).

---

## Container Deployment

```bash
# Build and run with Docker
docker build -t fasta-gc-calculator .
docker run -e AUDIT_SECRET_KEY=$(openssl rand -hex 32) fasta-gc-calculator gc --sequence ATCG

# Or use docker-compose
AUDIT_SECRET_KEY=$(openssl rand -hex 32) docker-compose up
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.
