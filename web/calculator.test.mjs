import test from "node:test";
import assert from "node:assert/strict";
import { parseFasta, analyzeSequence, analyzeRecords, calculateN50, slidingWindow, csvExport } from "./calculator.mjs";

test("multirecord FASTA and lowercase masking", () => {
  const records = parseFasta(">alpha\naCg\nTn\n>beta\nGGCC\n");
  assert.equal(records.length, 2);
  assert.equal(records[0].sequence, "aCgTn");
  const stats = analyzeSequence(records[0]);
  assert.equal(stats.masked, 3);
  assert.equal(stats.gcPercent, 50);
});

test("plain sequence input and empty input", () => {
  assert.equal(parseFasta("AATT").at(0).sequence, "AATT");
  assert.deepEqual(parseFasta(""), []);
});

test("invalid mixed FASTA raises instead of discarding bases", () => {
  assert.throws(() => parseFasta("ACG\n>seq\nGG"), /before/);
});

test("GC uses canonical bases rather than raw length", () => {
  const result = analyzeRecords(parseFasta(">a\nGN\n>b\nAT\n"));
  assert.equal(result.assembly.gcPercent, 100 / 3);
  assert.equal(result.assembly.n50, 2);
});

test("CpG ratio excludes ambiguous bases", () => {
  assert.equal(analyzeSequence({ header: "x", sequence: "ACGN" }).cpgOE, 3);
});

test("N50 validates input", () => {
  assert.equal(calculateN50([100, 200, 300]), 300);
  assert.equal(calculateN50([]), 0);
  assert.throws(() => calculateN50([-1, 5]), RangeError);
});

test("windows handle overlap, ambiguous bases and limits", () => {
  const windows = slidingWindow("AAGGNN", 2, 2);
  assert.deepEqual(windows.map(w => w.gcPercent), [0, 100, 0]);
  assert.equal(slidingWindow("ACGT", 2, 1, 1).length, 1);
  assert.throws(() => slidingWindow("AT", 1, 0), RangeError);
});

test("CSV export escapes spreadsheet formulas and quotes", () => {
  const rows = [analyzeSequence({ header: '=1+2",x', sequence: "GC" })];
  const csv = csvExport(rows);
  assert.match(csv, /"'=1\+2""/);
  assert.match(csv, /"100"/);
});
