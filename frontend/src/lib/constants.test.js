import { describe, expect, it } from "vitest";
import {
  CATEGORY_META,
  CATEGORY_ORDER,
  LABEL_MAPPING_ROWS,
  formatDate,
  formatPercent,
} from "./constants";

describe("category helpers", () => {
  it("defines exactly the four project categories", () => {
    expect(CATEGORY_ORDER).toEqual(["Real", "Misleading", "Partially False", "Fake"]);
  });

  it("gives every category a colour and description", () => {
    for (const label of CATEGORY_ORDER) {
      expect(CATEGORY_META[label].color).toMatch(/^#/);
      expect(CATEGORY_META[label].description.length).toBeGreaterThan(10);
    }
  });

  it("maps the six LIAR ratings onto four categories", () => {
    expect(LABEL_MAPPING_ROWS).toHaveLength(6);
    const mapped = new Set(LABEL_MAPPING_ROWS.map(([, value]) => value));
    expect([...mapped].sort()).toEqual([...CATEGORY_ORDER].sort());
  });
});

describe("formatters", () => {
  it("formats probabilities as percentages", () => {
    expect(formatPercent(0.3784)).toBe("37.8%");
    expect(formatPercent(null)).toBe("—");
  });

  it("returns a placeholder for missing dates", () => {
    expect(formatDate(undefined)).toBe("—");
    expect(formatDate("not-a-date")).toBe("not-a-date");
  });
});
