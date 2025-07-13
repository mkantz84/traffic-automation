import type { JobStatus, BestResult } from "./types";

const API_BASE = "/api";

export async function submitPermutations(payload: {
  expected_I2: number;
  expected_I3: number;
  accel: number[];
  tau: number[];
  startupDelay: number[];
}): Promise<{ job_id: string; num_simulations: number }> {
  const resp = await fetch(`${API_BASE}/submit_permutations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!resp.ok) throw new Error("Failed to submit permutations");
  return await resp.json();
}

export async function getJobStatus(job_id: string): Promise<JobStatus> {
  const resp = await fetch(
    `${API_BASE}/job_status?job_id=${encodeURIComponent(job_id)}`
  );
  if (!resp.ok) throw new Error("Failed to fetch job status");
  return await resp.json();
}

export async function getBestResult(job_id: string): Promise<BestResult> {
  const resp = await fetch(
    `${API_BASE}/best_result?job_id=${encodeURIComponent(job_id)}`
  );
  if (!resp.ok) throw new Error("Failed to fetch best result");
  return await resp.json();
}
