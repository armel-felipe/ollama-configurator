import { afterEach, expect, test, vi } from "vitest";
import { getDiagnostics } from "./client";

afterEach(() => vi.restoreAllMocks());

test("explains how to recover when the local backend is unavailable", async () => {
  vi.spyOn(globalThis, "fetch").mockRejectedValue(new TypeError("Failed to fetch"));

  await expect(getDiagnostics()).rejects.toThrow(/backend local não está respondendo/i);
});
