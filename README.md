# FASTA GC Content Calculator

Analyze FASTA sequences for GC content, CpG islands, dinucleotide frequencies, N50, and more.

## Features

- **GC Content**: `(G+C) / (A+T+G+C) × 100` excluding N bases
- **Sliding Window GC**: GC distribution across sequence in configurable windows
- **CpG Analysis**: Observed/expected ratio, CpG island detection
- **Dinucleotide Frequencies**: All 16 dinucleotide counts
- **N50 Calculation**: Assembly contiguity metric
- **Masked vs Unmasked**: Soft-masked (lowercase) content analysis
- **Multi-Sequence Support**: Per-sequence and whole-file statistics

## Installation

Zero dependencies — Python 3.8+ stdlib only.

```bash
cd fasta-gc-calculator
```

## Usage

### CLI

```bash
# GC content from sequence
python cli.py gc -s "ATCGATCGATCG"

# GC content from FASTA file
python cli.py gc -f genome.fasta

# CpG analysis
python cli.py cpg -s "ACGACGACGACG"

# Sliding window GC
python cli.py window -f genome.fasta --window-size 200 --step 50

# N50 calculation
python cli.py n50 --lengths "1000,500,200,100"

# Batch process from CSV
python cli.py batch -i sequences.csv -o results.csv
```

### Python API

```python
from fasta_gc import (
    gc_content,
    cpg_observed_expected,
    sliding_window_gc,
    calculate_n50,
    parse_fasta,
)

# GC content
gc = gc_content('ATCGATCG')  # 50.0

# CpG analysis
cpg = cpg_observed_expected('ACGACGACG')
print(f"CpG O/E: {cpg['cpg_oe_ratio']}, Island: {cpg['is_cpg_island']}")

# Parse FASTA
seqs = parse_fasta(">seq1\nATCG\n>seq2\nGGCC\n")

# N50
n50 = calculate_n50([1000, 500, 200, 100])
```

## Formulas

### GC Content
GC% = (G + C) / (A + T + G + C) × 100 (N bases excluded)

### CpG Observed/Expected
CpG_OE = (CpG_count × len) / (C_count × G_count)

### CpG Island Criteria
- CpG_OE > 0.6
- GC > 50%
- Length > 200 bp

### N50
The length such that sequences ≥ this length cover ≥ 50% of total assembly.

## Tests

```bash
python -m pytest test_fasta_gc.py -v
```

## License

MIT
