#!/usr/bin/env python3
"""
CLI for FASTA GC Content Calculator.

Subcommands:
  gc        — Calculate GC content for a sequence or FASTA file
  cpg       — CpG observed/expected analysis
  window    — Sliding window GC distribution
  n50       — Calculate N50 from sequence lengths
  batch     — Batch process sequences from CSV
"""
import argparse
import json
import sys

from fasta_gc import (
    gc_content,
    gc_content_detailed,
    cpg_observed_expected,
    sliding_window_gc,
    dinucleotide_frequencies,
    masked_vs_unmasked,
    calculate_n50,
    assembly_stats,
    per_sequence_stats,
    analyze_fasta,
    parse_fasta,
    process_batch,
)


def cmd_gc(args):
    """Calculate GC content."""
    if args.file:
        result = analyze_fasta(args.file)
        print(json.dumps(result['assembly'], indent=2))
    elif args.sequence:
        result = gc_content_detailed(args.sequence)
        print(json.dumps(result, indent=2))
    else:
        # Read from stdin
        seq = sys.stdin.read().strip()
        lines = seq.split('\n')
        seq = ''.join(l.strip() for l in lines if not l.startswith('>'))
        result = gc_content_detailed(seq)
        print(json.dumps(result, indent=2))


def cmd_cpg(args):
    """CpG observed/expected analysis."""
    if args.file:
        from fasta_gc import parse_fasta_file
        seqs = parse_fasta_file(args.file)
        results = []
        for s in seqs:
            cpg = cpg_observed_expected(s['sequence'])
            cpg['header'] = s['header']
            results.append(cpg)
        print(json.dumps(results, indent=2))
    elif args.sequence:
        result = cpg_observed_expected(args.sequence)
        print(json.dumps(result, indent=2))


def cmd_window(args):
    """Sliding window GC distribution."""
    if args.file:
        from fasta_gc import parse_fasta_file
        seqs = parse_fasta_file(args.file)
        seq = seqs[0]['sequence'] if seqs else ''
    elif args.sequence:
        seq = args.sequence
    else:
        print("Provide --file or --sequence", file=sys.stderr)
        sys.exit(1)

    windows = sliding_window_gc(seq, args.window_size, args.step)
    print(json.dumps(windows, indent=2))


def cmd_n50(args):
    """Calculate N50 from sequence lengths."""
    if args.lengths:
        lengths = [int(x) for x in args.lengths.split(',')]
    elif args.file:
        from fasta_gc import parse_fasta_file
        seqs = parse_fasta_file(args.file)
        lengths = [len(s['sequence']) for s in seqs]
    else:
        print("Provide --lengths or --file", file=sys.stderr)
        sys.exit(1)

    n50 = calculate_n50(lengths)
    print(json.dumps({'n50': n50, 'num_sequences': len(lengths),
                       'total_length': sum(lengths)}, indent=2))


def cmd_batch(args):
    """Batch process sequences from CSV."""
    results = process_batch(args.input, args.output)
    print(f"Processed {len(results)} sequences -> {args.output}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog='fasta-gc-calculator',
        description='FASTA GC Content Calculator — GC, CpG, N50, sliding window analysis'
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # gc
    p_gc = subparsers.add_parser('gc', help='Calculate GC content')
    p_gc.add_argument('--sequence', '-s', help='DNA sequence')
    p_gc.add_argument('--file', '-f', help='FASTA file')
    p_gc.set_defaults(func=cmd_gc)

    # cpg
    p_cpg = subparsers.add_parser('cpg', help='CpG observed/expected analysis')
    p_cpg.add_argument('--sequence', '-s', help='DNA sequence')
    p_cpg.add_argument('--file', '-f', help='FASTA file')
    p_cpg.set_defaults(func=cmd_cpg)

    # window
    p_win = subparsers.add_parser('window', help='Sliding window GC')
    p_win.add_argument('--sequence', '-s', help='DNA sequence')
    p_win.add_argument('--file', '-f', help='FASTA file')
    p_win.add_argument('--window-size', '-w', type=int, default=100, help='Window size')
    p_win.add_argument('--step', type=int, default=10, help='Step size')
    p_win.set_defaults(func=cmd_window)

    # n50
    p_n50 = subparsers.add_parser('n50', help='Calculate N50')
    p_n50.add_argument('--lengths', help='Comma-separated sequence lengths')
    p_n50.add_argument('--file', '-f', help='FASTA file')
    p_n50.set_defaults(func=cmd_n50)

    # batch
    p_batch = subparsers.add_parser('batch', help='Batch process from CSV')
    p_batch.add_argument('-i', '--input', required=True, help='Input CSV')
    p_batch.add_argument('-o', '--output', default='results.csv', help='Output CSV')
    p_batch.set_defaults(func=cmd_batch)

    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == '__main__':
    main()
