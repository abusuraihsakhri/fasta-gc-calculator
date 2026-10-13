// Zero-dependency, client-side FASTA analysis. No network calls.
const NUCLEOTIDES = new Set(["A", "C", "G", "T"]);

export function parseFasta(input) {
  if (typeof input !== "string") throw new TypeError("FASTA input must be text");
  const text = input.replace(/^\uFEFF/, "");
  const lines = text.split(/\r?\n/);
  const records = [];
  let header = null;
  let chunks = [];
  let sawData = false;
  const save = () => {
    if (header !== null) records.push({ header, sequence: chunks.join("") });
  };
  for (const raw of lines) {
    const line = raw.trim();
    if (!line) continue;
    if (line.startsWith(">")) {
      save();
      header = line.slice(1).trim() || `sequence_${records.length + 1}`;
      chunks = [];
    } else {
      if (header === null) {
        if (line.startsWith(";")) continue;
        sawData = true;
        chunks.push(line.replace(/\s+/g, ""));
      } else {
        chunks.push(line.replace(/\s+/g, ""));
      }
    }
  }
  save();
  if (!records.length && sawData) {
    const sequence = chunks.join("");
    if (sequence.startsWith(">")) throw new Error("Invalid FASTA header");
    records.push({ header: "sequence_1", sequence });
  } else if (records.length && sawData) {
    throw new Error("Sequence data before the first FASTA header");
  }
  for (const record of records) {
    if (!/^[A-Za-z*.-]*$/.test(record.sequence)) {
      throw new Error(`Invalid nucleotide symbols in ${record.header}`);
    }
  }
  return records;
}

export function analyzeSequence(record) {
  const seq = record.sequence || "";
  const counts = { A: 0, T: 0, G: 0, C: 0, N: 0, other: 0 };
  let masked = 0, cpg = 0;
  for (let i = 0; i < seq.length; i++) {
    const base = seq[i].toUpperCase();
    if (Object.hasOwn(counts, base) && base !== "other") counts[base]++;
    else counts.other++;
    if (/[a-z]/.test(seq[i])) masked++;
    if (base === "C" && seq[i + 1]?.toUpperCase() === "G") cpg++;
  }
  const canonical = counts.A + counts.T + counts.G + counts.C;
  const gc = counts.G + counts.C;
  const gcPercent = canonical ? 100 * gc / canonical : 0;
  const cpgOE = counts.C && counts.G ? (cpg * canonical) / (counts.C * counts.G) : 0;
  return {
    header: record.header, length: seq.length, ...counts, canonical,
    gcPercent, cpg, cpgOE, masked,
    maskedPercent: seq.length ? 100 * masked / seq.length : 0,
    isCpgIsland: seq.length > 200 && gcPercent > 50 && cpgOE > 0.6
  };
}

export function calculateN50(lengths) {
  if (lengths.some(n => !Number.isSafeInteger(n) || n < 0)) {
    throw new RangeError("Lengths must be nonnegative integers");
  }
  const ordered = [...lengths].sort((a, b) => b - a);
  const total = ordered.reduce((s, n) => s + n, 0);
  if (!total) return 0;
  let cumulative = 0;
  for (const length of ordered) {
    cumulative += length;
    if (cumulative >= total / 2) return length;
  }
  return 0;
}

export function analyzeRecords(records) {
  const stats = records.map(analyzeSequence);
  const sum = key => stats.reduce((acc, rec) => acc + rec[key], 0);
  const valid = sum("canonical");
  return {
    stats,
    assembly: {
      records: stats.length, length: sum("length"), canonical: valid,
      gcPercent: valid ? 100 * (sum("G") + sum("C")) / valid : 0,
      n50: calculateN50(stats.map(x => x.length)),
      ambiguous: sum("N") + sum("other")
    }
  };
}

export function slidingWindow(sequence, windowSize = 100, step = 10, limit = 300) {
  if (!Number.isSafeInteger(windowSize) || windowSize <= 0 ||
      !Number.isSafeInteger(step) || step <= 0 ||
      !Number.isSafeInteger(limit) || limit < 0) {
    throw new RangeError("Window size and step must be positive integers");
  }
  const output = [];
  const seq = sequence.toUpperCase();
  // A rolling total avoids re-scanning each overlapping window.
  let valid = 0, gc = 0;
  for (let i = 0; i < seq.length; i++) {
    if (NUCLEOTIDES.has(seq[i])) valid++;
    if (seq[i] === "G" || seq[i] === "C") gc++;
    if (i >= windowSize) {
      const old = seq[i - windowSize];
      if (NUCLEOTIDES.has(old)) valid--;
      if (old === "G" || old === "C") gc--;
    }
    const start = i - windowSize + 1;
    if (start >= 0 && start % step === 0) {
      if (output.length >= limit) break;
      output.push({ start, end: i + 1, gcPercent: valid ? 100 * gc / valid : 0 });
    }
  }
  return output;
}

export function csvExport(rows) {
  const columns = ["header", "length", "gcPercent", "A", "T", "G", "C",
                   "N", "other", "cpg", "cpgOE", "maskedPercent", "isCpgIsland"];
  const safe = value => {
    let data = typeof value === "number" ? String(Math.round(value * 10000) / 10000) : String(value ?? "");
    if (/^\s*[=+@-]/.test(data)) data = "'" + data;
    return '"' + data.replaceAll('"', '""') + '"';
  };
  return [columns.join(","), ...rows.map(row => columns.map(k => safe(row[k])).join(","))].join("\r\n") + "\r\n";
}
