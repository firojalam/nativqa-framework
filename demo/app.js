const seedInput = document.getElementById("seed-input");
const dedupeInput = document.getElementById("dedupe-input");
const runBtn = document.getElementById("run-btn");
const clearBtn = document.getElementById("clear-btn");
const downloadBtn = document.getElementById("download-btn");
const preview = document.getElementById("jsonl-preview");
const statusEl = document.getElementById("status");

let currentJsonl = "";

function setStatus(message) {
  statusEl.textContent = message;
}

function buildJsonl(rawText, dedupeEnabled) {
  const lines = rawText
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);

  if (!lines.length) {
    return { jsonl: "", total: 0, unique: 0 };
  }

  const seen = new Set();
  const records = [];

  for (const line of lines) {
    const key = line.toLowerCase();
    if (dedupeEnabled && seen.has(key)) {
      continue;
    }
    seen.add(key);
    records.push({
      seed_query: line,
    });
  }

  const jsonl = records.map((record) => JSON.stringify(record)).join("\n");
  return { jsonl, total: lines.length, unique: records.length };
}

function runConversion() {
  const { jsonl, total, unique } = buildJsonl(seedInput.value, dedupeInput.checked);
  currentJsonl = jsonl;
  preview.value = jsonl;
  downloadBtn.disabled = !jsonl;

  if (!jsonl) {
    setStatus("No valid input found. Paste at least one non-empty line.");
    return;
  }

  const removed = total - unique;
  if (removed > 0) {
    setStatus(`Converted ${unique} queries to JSONL (${removed} duplicates removed).`);
    return;
  }

  setStatus(`Converted ${unique} queries to JSONL.`);
}

function clearAll() {
  seedInput.value = "";
  preview.value = "";
  currentJsonl = "";
  downloadBtn.disabled = true;
  setStatus("Cleared.");
}

function downloadJsonl() {
  if (!currentJsonl) {
    return;
  }

  const blob = new Blob([currentJsonl + "\n"], { type: "application/x-ndjson" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  const stamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, "-");
  a.href = url;
  a.download = `seed_queries_${stamp}.jsonl`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

runBtn.addEventListener("click", runConversion);
clearBtn.addEventListener("click", clearAll);
downloadBtn.addEventListener("click", downloadJsonl);
