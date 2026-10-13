"""Regression tests for FASTA calculations and audit integrity."""
import csv

import pytest

from fasta_gc import (
    analyze_fasta, assembly_stats, calculate_n50, cpg_observed_expected,
    masked_vs_unmasked, parse_fasta, process_batch, sliding_window_gc,
)
from agents.base import AuditTrail
from cli import main


def test_fasta_preserves_soft_masking():
    records = parse_fasta(">record\naTgC\nca\n")
    assert records[0]["sequence"] == "aTgCca"
    assert masked_vs_unmasked(records[0]["sequence"])["masked_length"] == 4


def test_assembly_gc_ignores_ambiguous_bases_across_contigs():
    records = parse_fasta(">one\nGN\n>two\nAT\n")
    assert assembly_stats(records)["gc_content"] == 33.33


def test_cpg_excludes_ambiguous_bases_from_normalization():
    assert cpg_observed_expected("ACGN")["cpg_oe_ratio"] == 3.0


@pytest.mark.parametrize("window,step", [(0, 1), (-1, 1), (1, 0), (1, -1)])
def test_invalid_windows_raise(window, step):
    with pytest.raises(ValueError):
        sliding_window_gc("ATGC", window, step)


def test_window_bound():
    result = sliding_window_gc("ATGC" * 500, 20, 1, max_windows=5)
    assert len(result) == 5
    assert sliding_window_gc("ATGC", 1, 1, max_windows=0) == []


def test_analyze_fasta_limits_windows(tmp_path):
    path = tmp_path / "input.fa"
    path.write_text(">seq\n" + "GC" * 500)
    assert len(analyze_fasta(str(path), window_size=20, step=1)["sliding_window"]) == 20


@pytest.mark.parametrize("lengths", [[-1, 100], [2.5, 4], ["3", 4]])
def test_invalid_n50_lengths(lengths):
    with pytest.raises(ValueError):
        calculate_n50(lengths)


def test_empty_contigs_n50():
    assert calculate_n50([0, 0]) == 0


def test_csv_escaping_and_existing_result_columns(tmp_path):
    source = tmp_path / "input.csv"
    dest = tmp_path / "output.csv"
    source.write_text("header,seq,gc_content\n=1+2,GC,999\n")
    values = process_batch(str(source), str(dest))
    assert values[0]["header"] == "=1+2"
    with dest.open(newline="") as handle:
        parsed = list(csv.DictReader(handle))
    assert parsed[0]["header"] == "'=1+2"
    assert parsed[0]["gc_content"] == "100.0"


def test_empty_fasta_cli_is_reported(tmp_path):
    source = tmp_path / "empty.fa"
    source.write_text("")
    assert main(["gc", "--file", str(source)]) == 2


def test_audit_hmac_detects_tampering():
    trail = AuditTrail("test-only-secret")
    original = trail.log("worker", "service", "done", {"status": "ok"})
    assert trail.verify_integrity()
    original["event_type"] = "changed"
    assert not trail.verify_integrity()


def test_audit_trail_defensive_copy():
    trail = AuditTrail("test-only-secret")
    trail.log("worker", "service", "done", {})
    trail.get_trail()[0]["actor"] = "modified"
    assert trail.verify_integrity()
