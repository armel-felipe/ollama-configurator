import { afterEach, expect, test, vi } from "vitest";
import { getDiagnostics, saveGatewayTailscaleIp } from "./client";

afterEach(() => vi.restoreAllMocks());

test("explains how to recover when the local backend is unavailable", async () => {
  vi.spyOn(globalThis, "fetch").mockRejectedValue(new TypeError("Failed to fetch"));

  await expect(getDiagnostics()).rejects.toThrow(/backend local não está respondendo/i);
});

test("persists the Tailscale client IP", async () => {
  const response = {
    host: "0.0.0.0",
    effective_host: "0.0.0.0",
    port: 11435,
    pending_restart: false,
    options: [],
    tailscale_ip: "100.87.71.48",
  };
  vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(JSON.stringify(response), { status: 200 }),
  );

  await expect(saveGatewayTailscaleIp("100.87.71.48")).resolves.toEqual(response);
  expect(fetch).toHaveBeenCalledWith("/api/gateway/tailscale-ip", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tailscale_ip: "100.87.71.48" }),
  });
});
