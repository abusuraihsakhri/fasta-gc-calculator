#!/usr/bin/env python3
"""
FASTA GC Content Calculator — Real Implementation

Parses FASTA files (multi-sequence), computes GC content, sliding window
GC distribution, CpG observed/expected ratio, dinucleotide frequencies,
N50 calculation, and masked vs unmasked content.

Zero external dependencies — Python stdlib only.
"""

import csv
import math
import sys
from typing import Dict, Any, List, Optional, Tuple


# ---------------------------------------------------------------------------
# FASTA Parsing
# ---------------------------------------------------------------------------

def parse_fasta(text: str) -> List[Dict[str, str]]:
    """Parse FASTA format text into list of {header, sequence} dicts.

    Supports multi-sequence files. Concatenates multi-line sequences.
    """
    sequences = []
    current_header = None
    current_seq = []

    for line in text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('>'):
            if current_header is not None:
                sequences.append({
                    'header': current_header,
                    'sequence': ''.join(current_seq).upper(),
                })
            current_header = line[1:].strip()
            current_seq = []
        else:
            current_seq.append(line)

    # Don't forget the last sequence
    if current_header is not None:
        sequences.append({
            'header': current_header,
            'sequence': ''.join(current_seq).upper(),
        })

    return sequences


def parse_fasta_file(filepath: str) -> List[Dict[str, str]]:
    """Parse a FASTA file from disk."""
    with open(filepath, 'r') as f:
        return parse_fasta(f.read())


# ---------------------------------------------------------------------------
# GC Content
# ---------------------------------------------------------------------------

def gc_content(sequence: str) -> float:
    """Calculate GC content: (G+C) / (A+T+G+C) × 100, excluding N and ambiguous bases.

    Returns percentage (0-100).
    """
    seq = sequence.upper()
    g = seq.count('G')
    c = seq.count('C')
    a = seq.count('A')
    t = seq.count('T')
    total = a + t + g + c
    if total == 0:
        return 0.0
    return (g + c) / total * 100.0


def gc_content_detailed(sequence: str) -> Dict[str, Any]:
    """Detailed GC content analysis of a sequence."""
    seq = sequence.upper()
    a = seq.count('A')
    t = seq.count('T')
    g = seq.count('G')
    c = seq.count('C')
    n = seq.count('N')
    other = len(seq) - a - t - g - c - n
    atgc = a + t + g + c

    gc = (g + c) / atgc * 100.0 if atgc > 0 else 0.0

    return {
        'length': len(seq),
        'A': a, 'T': t, 'G': g, 'C': c,
        'N': n, 'other': other,
        'atgc_count': atgc,
        'gc_content': round(gc, 2),
    }


# ---------------------------------------------------------------------------
# Sliding Window GC
# ---------------------------------------------------------------------------

def sliding_window_gc(sequence: str, window_size: int = 100,
                       step: int = 10) -> List[Dict[str, Any]]:
    """Calculate GC content in sliding windows across a sequence.

    Args:
        sequence: DNA sequence.
        window_size: Size of each window (default 100).
        step: Step size between windows (default 10).

    Returns:
        List of dicts with position, gc_content, window_size.
    """
    seq = sequence.upper()
    results = []

    for start in range(0, len(seq) - window_size + 1, step):
        window = seq[start:start + window_size]
        gc = gc_content(window)
        results.append({
            'start': start,
            'end': start + window_size,
            'gc_content': round(gc, 2),
            'window_size': window_size,
        })

    return results


# ---------------------------------------------------------------------------
# CpG Analysis
# ---------------------------------------------------------------------------

def cpg_observed_expected(sequence: str) -> Dict[str, Any]:
    """Calculate CpG observed/expected ratio.

    CpG_OE = (CpG_count × len) / (C_count × G_count)

    CpG islands: CpG_OE > 0.6, GC > 50%, length > 200bp.
    """
    seq = sequence.upper()
    length = len(seq)

    c_count = seq.count('C')
    g_count = seq.count('G')

    # Count CpG dinucleotides
    cpg_count = 0
    for i in range(length - 1):
        if seq[i] == 'C' and seq[i + 1] == 'G':
            cpg_count += 1

    # Calculate observed/expected
    if c_count == 0 or g_count == 0:
        cpg_oe = 0.0
    else:
        cpg_oe = (cpg_count * length) / (c_count * g_count)

    gc = gc_content(seq)

    is_cpg_island = cpg_oe > 0.6 and gc > 50.0 and length > 200

    return {
        'length': length,
        'cpg_count': cpg_count,
        'c_count': c_count,
        'g_count': g_count,
        'cpg_oe_ratio': round(cpg_oe, 4),
        'gc_content': round(gc, 2),
        'is_cpg_island': is_cpg_island,
    }


# ---------------------------------------------------------------------------
# Dinucleotide Frequencies
# ---------------------------------------------------------------------------

def dinucleotide_frequencies(sequence: str) -> Dict[str, int]:
    """Count all dinucleotide frequencies in a sequence."""
    seq = sequence.upper()
    bases = ['A', 'T', 'G', 'C']
    dinucs = {}

    # Initialize all possible dinucleotides
    for b1 in bases:
        for b2 in bases:
            dinucs[b1 + b2] = 0

    # Count
    for i in range(len(seq) - 1):
        dinuc = seq[i:i + 2]
        if dinuc in dinucs:
            dinucs[dinuc] += 1

    return dinucs


# ---------------------------------------------------------------------------
# Masked vs Unmasked Content
# ---------------------------------------------------------------------------

def masked_vs_unmasked(sequence: str) -> Dict[str, Any]:
    """Analyze masked (lowercase) vs unmasked (uppercase) content.

    In FASTA, lowercase = soft-masked (repeats), uppercase = unmasked.
    """
    masked_bases = []
    unmasked_bases = []

    for base in sequence:
        if base.islower():
            masked_bases.append(base.upper())
        elif base.isalpha():
            unmasked_bases.append(base)

    masked_str = ''.join(masked_bases)
    unmasked_str = ''.join(unmasked_bases)

    masked_gc = gc_content(masked_str)
    unmasked_gc = gc_content(unmasked_str)

    return {
        'total_length': len(sequence),
        'masked_length': len(masked_bases),
        'unmasked_length': len(unmasked_bases),
        'masked_fraction': round(len(masked_bases) / len(sequence) * 100, 2) if sequence else 0.0,
        'masked_gc': round(masked_gc, 2),
        'unmasked_gc': round(unmasked_gc, 2),
    }


# ---------------------------------------------------------------------------
# N50 Calculation
# ---------------------------------------------------------------------------

def calculate_n50(lengths: List[int]) -> int:
    """Calculate N50 from a list of sequence lengths.

    N50 is the length such that sequences of this length or longer cover
    at least 50% of the total assembly length.
    """
    if not lengths:
        return 0

    sorted_lengths = sorted(lengths, reverse=True)
    total = sum(sorted_lengths)
    half = total / 2.0
    cumulative = 0

    for length in sorted_lengths:
        cumulative += length
        if cumulative >= half:
            return length

    return sorted_lengths[-1]


def assembly_stats(sequences: List[Dict[str, str]]) -> Dict[str, Any]:
    """Calculate assembly statistics including N50."""
    lengths = [len(s['sequence']) for s in sequences]

    if not lengths:
        return {'num_sequences': 0, 'total_length': 0, 'n50': 0}

    n50 = calculate_n50(lengths)
    gc_vals = [gc_content(s['sequence']) for s in sequences]
    weighted_gc = sum(len(s['sequence']) * gc_content(s['sequence'])
                      for s in sequences)
    total_len = sum(lengths)
    avg_gc = weighted_gc / total_len if total_len > 0 else 0.0

    return {
        'num_sequences': len(sequences),
        'total_length': total_len,
        'min_length': min(lengths),
        'max_length': max(lengths),
        'mean_length': round(total_len / len(lengths), 1),
        'n50': n50,
        'gc_content': round(avg_gc, 2),
    }


# ---------------------------------------------------------------------------
# Per-Sequence Statistics
# ---------------------------------------------------------------------------

def per_sequence_stats(sequences: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Calculate statistics for each sequence in a FASTA file."""
    results = []
    for s in sequences:
        detail = gc_content_detailed(s['sequence'])
        cpg = cpg_observed_expected(s['sequence'])
        results.append({
            'header': s['header'],
            'length': detail['length'],
            'gc_content': detail['gc_content'],
            'A': detail['A'], 'T': detail['T'],
            'G': detail['G'], 'C': detail['C'],
            'N': detail['N'],
            'cpg_count': cpg['cpg_count'],
            'cpg_oe_ratio': cpg['cpg_oe_ratio'],
            'is_cpg_island': cpg['is_cpg_island'],
        })
    return results


# ---------------------------------------------------------------------------
# Whole-File Analysis
# ---------------------------------------------------------------------------

def analyze_fasta(filepath: str, window_size: int = 100,
                   step: int = 10) -> Dict[str, Any]:
    """Complete analysis of a FASTA file."""
    sequences = parse_fasta_file(filepath)

    if not sequences:
        return {'error': 'No sequences found'}

    assembly = assembly_stats(sequences)
    per_seq = per_sequence_stats(sequences)

    # Aggregate dinucleotide frequencies
    all_dinucs = {}
    for s in sequences:
        dinucs = dinucleotide_frequencies(s['sequence'])
        for k, v in dinucs.items():
            all_dinucs[k] = all_dinucs.get(k, 0) + v

    # Sliding window on longest sequence
    longest = max(sequences, key=lambda s: len(s['sequence']))
    windows = sliding_window_gc(longest['sequence'], window_size, step)

    # Masked/unmasked analysis
    masked = masked_vs_unmasked(longest['sequence'])

    return {
        'assembly': assembly,
        'per_sequence': per_seq,
        'dinucleotide_frequencies': all_dinucs,
        'sliding_window': windows[:20],  # First 20 windows
        'masked_analysis': masked,
    }


# ---------------------------------------------------------------------------
# Batch Processing
# ---------------------------------------------------------------------------

def process_batch(input_csv: str, output_csv: str) -> List[Dict[str, Any]]:
    """Process a CSV of sequences and calculate GC content.

    Expected CSV columns: sequence (required), header/name (optional).
    """
    with open(input_csv, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    out_fields = fieldnames + ['gc_content', 'length', 'cpg_count', 'cpg_oe_ratio']
    out_rows = []

    for r in rows:
        seq = r.get('sequence', r.get('seq', ''))
        detail = gc_content_detailed(seq)
        cpg = cpg_observed_expected(seq)

        row_dict = dict(r)
        row_dict['gc_content'] = detail['gc_content']
        row_dict['length'] = detail['length']
        row_dict['cpg_count'] = cpg['cpg_count']
        row_dict['cpg_oe_ratio'] = cpg['cpg_oe_ratio']
        out_rows.append(row_dict)

    with open(output_csv, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(out_rows)

    return out_rows
