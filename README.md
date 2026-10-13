# FASTA GC Calculator

A sequence-analysis tool for DNA FASTA files. Use the browser interface without installing anything, or run the Python command-line interface locally.

## Browser application

The repository includes a static calculator in `index.html` and `web/index.html`. It accepts pasted DNA sequences and FASTA files, displays assembly and per-sequence statistics, plots GC% in sliding windows, and exports a CSV table.

**Privacy:** Browser analysis runs entirely on your device, using JavaScript modules. Input sequences are not uploaded to a server. There is no remote API call or persistent browser storage in the calculator. Do not upload sensitive samples to a third-party instance of the optional API.

## Calculations

- **GC content:** `(G + C) / (A + T + G + C) × 100`. Ambiguous bases and N are excluded. A record without canonical bases reports 0%.
- **CpG observed/expected:** `CpG × canonical_base_count / (C × G)`. If C or G is absent, the ratio is zero. The CpG-island flag uses the illustrative heuristic GC > 50%, CpG O/E > 0.6, and more than 200 canonical bp; **it is not a validated CpG island caller**.
- **N50:** The contig length at which the cumulative sorted assembly length first reaches at least half the total bp count.
- **Masking:** Lowercase input bases are treated as soft-masked. Case is retained when parsing FASTA.
- **Sliding windows:** Configurable window width and step. In the browser, at most the first 300 windows of the longest sequence are displayed; the Python whole-file analysis returns at most the first 20 windows.
- **Dinucleotides:** Python counts the 16 canonical DNA dinucleotides, excluding ambiguous pairs.

## Command-line usage

Core calculation functions use **Python 3.10+** with no additional packages.

```bash
python cli.py gc --sequence ATCGATCG
python cli.py gc --file sequences.fasta
python cli.py cpg --file sequences.fasta
python cli.py window --sequence ATCGATCGATCG --window-size 4 --step 2
python cli.py n50 --lengths 100,200,300
python cli.py batch --input sequences.csv --output results.csv
```

Batch CSV files may contain a `sequence` or `seq` column and optional metadata columns; the output appends GC, length, CpG count, and CpG ratio. Spreadsheet formula-like cells are escaped in the generated CSV. FASTA headers can include spaces and descriptions.

Python use:

```python
from fasta_gc import parse_fasta, gc_content, assembly_stats

records = parse_fasta(">record1\nATCGnn\n>record2\nggcctt\n")
print(gc_content(records[0]["sequence"]))
print(assembly_stats(records))
```

## Testing

```bash
python -m pip install pytest "pydantic>=2,<3" "fastapi>=0.110,<1" "uvicorn>=0.30,<1"
python -m pytest -q
python -m compileall -q .
node --test web/calculator.test.mjs
```

The browser tests require Node.js 22+. GitHub Actions checks Python 3.10, 3.11 and 3.12 plus the browser module and entry-point scripts.

## Optional API and Docker

The `agents/` package contains a separate demo audit/supervisor API based on FastAPI and Pydantic. It is **not required** for the FASTA calculator, and its general-purpose thresholds are not genomic interpretation rules or validated clinical decision support. The regex-based identifier guard is not a comprehensive PHI detector. Audit chains are stored in memory; specify `AUDIT_SECRET_KEY` for a consistent deployment-specific HMAC key.

```bash
docker build -t fasta-gc-calculator .
docker run --rm fasta-gc-calculator gc --sequence ATCG
# Optional API, hosted locally on port 8000:
docker compose up --build
# Then open http://localhost:8000/docs
```

## Technology and compatibility

Python standard library for analysis, HTML/CSS and native JavaScript ES modules for the browser, and optional FastAPI/Pydantic/Uvicorn for the auxiliary API. Modern Chrome, Firefox, Edge and Safari browsers with ES module support are expected to work. No Pyodide/PyScript runtime is needed for the web calculator.

## License

[MIT](LICENSE).
