# Fasta Gc Calculator

> **Domain:** Clinical Decision Support & Biomedical Computing  
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

FASTA GC Content Calculator — Real Implementation

Parses FASTA files (multi-sequence), computes GC content, sliding window
GC distribution, CpG observed/expected ratio, dinucleotide frequencies,
N50 calculation, and masked vs unmasked content.

Zero external dependencies — Python stdlib only.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Analytical Functions

- **`parse_fasta()`**: Parse FASTA format text into list of {header, sequence} dicts.

Supports multi-sequence files. Concatenates multi-line sequences.
- **`parse_fasta_file()`**: Parse a FASTA file from disk.
- **`gc_content()`**: Calculate GC content: (G+C) / (A+T+G+C) × 100, excluding N and ambiguous bases.

Returns percentage (0-100).
- **`gc_content_detailed()`**: Detailed GC content analysis of a sequence.
- **`sliding_window_gc()`**: Calculate GC content in sliding windows across a sequence.

Args:
    sequence: DNA sequence.
    window_size: Size of each window (default 100).
    step: Step size between windows (default 10).

Returns:
    List of dicts with position, gc_content, window_size.

---

## 📐 Mathematical Formulation & Logic

```text
  return (g + c) / total * 100.0
  """Calculate GC content in sliding windows across a sequence.
  """Calculate CpG observed/expected ratio.
  Calculate observed/expected
  """Calculate N50 from a list of sequence lengths.
```

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py --file <value> --sequence <value> --lengths <value> --window-size <value>
```

### Parameter Reference
- `--file`: Specifies input measurement or parameter value.
- `--sequence`: Specifies input measurement or parameter value.
- `--lengths`: Specifies input measurement or parameter value.
- `--window-size`: Specifies input measurement or parameter value.
- `--step`: Specifies input measurement or parameter value.
- `--input`: Specifies input measurement or parameter value.
- `--output`: Specifies input measurement or parameter value.

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `query` | Parameter / observation metric | Required |
| `name` | Parameter / observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

```bash
docker build -t fasta-gc-calculator .
docker run -p 8000:8000 fasta-gc-calculator
```
