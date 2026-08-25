#!/usr/bin/env python3
"""Tests for FASTA GC Content Calculator — 20+ real functional tests."""
import pytest
from fasta_gc import (
    parse_fasta,
    gc_content,
    gc_content_detailed,
    sliding_window_gc,
    cpg_observed_expected,
    dinucleotide_frequencies,
    masked_vs_unmasked,
    calculate_n50,
    assembly_stats,
    per_sequence_stats,
    process_batch,
)


# ---------------------------------------------------------------------------
# FASTA Parsing Tests
# ---------------------------------------------------------------------------

class TestFASTAParsing:
    def test_single_sequence(self):
        text = ">seq1\nATCGATCG\n"
        seqs = parse_fasta(text)
        assert len(seqs) == 1
        assert seqs[0]['header'] == 'seq1'
        assert seqs[0]['sequence'] == 'ATCGATCG'

    def test_multi_sequence(self):
        text = ">seq1\nATCG\n>seq2\nGGCC\n"
        seqs = parse_fasta(text)
        assert len(seqs) == 2
        assert seqs[1]['sequence'] == 'GGCC'

    def test_multiline_sequence(self):
        text = ">seq1\nATCG\nATCG\nATCG\n"
        seqs = parse_fasta(text)
        assert seqs[0]['sequence'] == 'ATCGATCGATCG'

    def test_empty_input(self):
        seqs = parse_fasta('')
        assert len(seqs) == 0

    def test_header_with_description(self):
        text = ">gi|123 Homo sapiens gene\nATCG\n"
        seqs = parse_fasta(text)
        assert 'Homo sapiens' in seqs[0]['header']


# ---------------------------------------------------------------------------
# GC Content Tests
# ---------------------------------------------------------------------------

class TestGCContent:
    def test_all_gc(self):
        assert gc_content('GGCC') == 100.0

    def test_all_at(self):
        assert gc_content('AATT') == 0.0

    def test_50_percent(self):
        assert gc_content('AAGGCCTT') == 50.0

    def test_excludes_n(self):
        # NN should be excluded from denominator
        result = gc_content('AANNGGCC')
        # A=2, G=2, C=2, T=0 -> GC = 4/6 * 100 = 66.67
        assert abs(result - 66.67) < 0.1

    def test_empty(self):
        assert gc_content('') == 0.0

    def test_lowercase(self):
        assert gc_content('aattggcc') == 50.0

    def test_detailed(self):
        result = gc_content_detailed('AATTGGCC')
        assert result['A'] == 2
        assert result['T'] == 2
        assert result['G'] == 2
        assert result['C'] == 2
        assert result['gc_content'] == 50.0


# ---------------------------------------------------------------------------
# Sliding Window Tests
# ---------------------------------------------------------------------------

class TestSlidingWindow:
    def test_basic_window(self):
        seq = 'A' * 50 + 'G' * 50  # 50% GC in second half
        windows = sliding_window_gc(seq, window_size=50, step=50)
        assert len(windows) == 2
        assert windows[0]['gc_content'] == 0.0
        assert windows[1]['gc_content'] == 100.0

    def test_window_size(self):
        seq = 'ATCG' * 25  # 100bp, 50% GC
        windows = sliding_window_gc(seq, window_size=20, step=20)
        for w in windows:
            assert w['gc_content'] == 50.0

    def test_short_sequence(self):
        seq = 'ATCG'
        windows = sliding_window_gc(seq, window_size=100, step=10)
        assert len(windows) == 0  # Sequence too short


# ---------------------------------------------------------------------------
# CpG Analysis Tests
# ---------------------------------------------------------------------------

class TestCpGAnalysis:
    def test_no_cpg(self):
        result = cpg_observed_expected('AATTAA')
        assert result['cpg_count'] == 0

    def test_cpg_present(self):
        result = cpg_observed_expected('ACGACG')
        assert result['cpg_count'] == 2

    def test_cpg_ratio(self):
        # Sequence: ACGT -> 1 CpG, C=1, G=1, len=4
        # CpG_OE = (1 * 4) / (1 * 1) = 4.0
        result = cpg_observed_expected('ACGT')
        assert result['cpg_oe_ratio'] == 4.0

    def test_cpg_island_detection(self):
        # Need: CpG_OE > 0.6, GC > 50%, length > 200bp
        # Build a GC-rich sequence with many CpGs
        seq = 'ACGACG' * 40  # 240bp, lots of CpG
        result = cpg_observed_expected(seq)
        assert result['length'] == 240
        assert result['is_cpg_island'] is True

    def test_not_cpg_island(self):
        # AT-rich, no CpG
        seq = 'AATT' * 60  # 240bp, no CpG
        result = cpg_observed_expected(seq)
        assert result['is_cpg_island'] is False


# ---------------------------------------------------------------------------
# Dinucleotide Frequency Tests
# ---------------------------------------------------------------------------

class TestDinucleotideFrequencies:
    def test_basic(self):
        dinucs = dinucleotide_frequencies('ATCG')
        assert dinucs['AT'] == 1
        assert dinucs['TC'] == 1
        assert dinucs['CG'] == 1
        assert dinucs['AA'] == 0

    def test_repeated(self):
        dinucs = dinucleotide_frequencies('AAAA')
        assert dinucs['AA'] == 3

    def test_all_dinucs_present(self):
        # All 16 dinucleotides should be in the dict
        dinucs = dinucleotide_frequencies('ATCG')
        assert len(dinucs) == 16


# ---------------------------------------------------------------------------
# Masked vs Unmasked Tests
# ---------------------------------------------------------------------------

class TestMaskedUnmasked:
    def test_all_unmasked(self):
        result = masked_vs_unmasked('ATCGATCG')
        assert result['masked_length'] == 0
        assert result['unmasked_length'] == 8

    def test_all_masked(self):
        result = masked_vs_unmasked('atcgatcg')
        assert result['masked_length'] == 8
        assert result['unmasked_length'] == 0

    def test_mixed(self):
        result = masked_vs_unmasked('ATCGatcg')
        assert result['masked_length'] == 4
        assert result['unmasked_length'] == 4

    def test_masked_fraction(self):
        result = masked_vs_unmasked('AAaa')
        assert result['masked_fraction'] == 50.0


# ---------------------------------------------------------------------------
# N50 Tests
# ---------------------------------------------------------------------------

class TestN50:
    def test_simple_n50(self):
        # Lengths: 100, 200, 300 -> total=600, half=300
        # Sorted: 300, 200, 100 -> cumulative: 300 >= 300 -> N50=300
        assert calculate_n50([100, 200, 300]) == 300

    def test_equal_lengths(self):
        assert calculate_n50([100, 100, 100]) == 100

    def test_single_sequence(self):
        assert calculate_n50([500]) == 500

    def test_empty(self):
        assert calculate_n50([]) == 0

    def test_n50_with_small_contigs(self):
        # 1000, 10, 10 -> total=1020, half=510
        # Sorted: 1000, 10, 10 -> cum: 1000 >= 510 -> N50=1000
        assert calculate_n50([10, 10, 1000]) == 1000


# ---------------------------------------------------------------------------
# Assembly Stats Tests
# ---------------------------------------------------------------------------

class TestAssemblyStats:
    def test_basic_stats(self):
        seqs = [{'header': 'a', 'sequence': 'ATCG' * 25},
                {'header': 'b', 'sequence': 'GCGC' * 25}]
        stats = assembly_stats(seqs)
        assert stats['num_sequences'] == 2
        assert stats['total_length'] == 200
        assert stats['n50'] == 100

    def test_empty(self):
        stats = assembly_stats([])
        assert stats['num_sequences'] == 0


# ---------------------------------------------------------------------------
# Per-Sequence Stats Tests
# ---------------------------------------------------------------------------

class TestPerSequenceStats:
    def test_basic(self):
        seqs = [{'header': 'seq1', 'sequence': 'ATCGATCG'}]
        results = per_sequence_stats(seqs)
        assert len(results) == 1
        assert results[0]['header'] == 'seq1'
        assert results[0]['gc_content'] == 50.0


# ---------------------------------------------------------------------------
# Batch Processing Tests
# ---------------------------------------------------------------------------

class TestBatchProcessing:
    def test_batch_csv(self, tmp_path):
        csv_in = tmp_path / 'in.csv'
        csv_out = tmp_path / 'out.csv'
        csv_in.write_text(
            'header,sequence\n'
            'seq1,ATCGATCG\n'
            'seq2,GGGGCCCC\n',
            encoding='utf-8'
        )
        results = process_batch(str(csv_in), str(csv_out))
        assert len(results) == 2
        assert csv_out.exists()
        assert 'gc_content' in results[0]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
