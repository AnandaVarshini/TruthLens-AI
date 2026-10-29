export const CATEGORY_ORDER = ["Real", "Misleading", "Partially False", "Fake"];

export const CATEGORY_META = {
  Real: {
    color: "#22c55e",
    soft: "rgba(34, 197, 94, 0.14)",
    description: "Accurate — the evidence supports the claim.",
  },
  Misleading: {
    color: "#f59e0b",
    soft: "rgba(245, 158, 11, 0.14)",
    description: "Mostly accurate but missing context or overstated.",
  },
  "Partially False": {
    color: "#f97316",
    soft: "rgba(249, 115, 22, 0.14)",
    description: "Part of the claim is true and part is false or unsupported.",
  },
  Fake: {
    color: "#ef4444",
    soft: "rgba(239, 68, 68, 0.14)",
    description: "False or fabricated — the evidence contradicts the claim.",
  },
};

export const LABEL_MAPPING_ROWS = [
  ["true", "Real"],
  ["mostly-true", "Misleading"],
  ["half-true", "Partially False"],
  ["barely-true", "Partially False"],
  ["false", "Fake"],
  ["pants-fire", "Fake"],
];

export function formatDate(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatPercent(value, digits = 1) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `${(Number(value) * 100).toFixed(digits)}%`;
}
