import { useState, useCallback } from "react";
import type {
  SimulationFormData,
  BestResult as BestResultType,
} from "../types";
import { submitPermutations, getJobStatus, getBestResult } from "../network";
import { poll } from "../poller";

const POLL_INTERVAL = 2000;

export function useSimulation() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [expected, setExpected] = useState<number>(0);
  const [received, setReceived] = useState<number>(0);
  const [loading, setLoading] = useState(false);
  const [bestResult, setBestResult] = useState<BestResultType | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [complete, setComplete] = useState(false);

  const reset = useCallback(() => {
    setJobId(null);
    setExpected(0);
    setReceived(0);
    setLoading(false);
    setBestResult(null);
    setError(null);
    setComplete(false);
  }, []);

  const handleSubmit = useCallback(
    async (form: SimulationFormData) => {
      reset();
      setLoading(true);
      try {
        const { job_id, num_simulations } = await submitPermutations(form);
        setJobId(job_id);
        setExpected(num_simulations);
        setReceived(0);
        setComplete(false);
        // Use poller for job status
        try {
          await poll(
            async () => {
              const status = await getJobStatus(job_id);
              setReceived(status.received_results);
              return status;
            },
            (status) => status.complete,
            POLL_INTERVAL
          );
          setComplete(true);
          setLoading(false);
          // Fetch best result
          try {
            const best = await getBestResult(job_id);
            setBestResult(best);
          } catch {
            setError("Failed to fetch best result");
          }
        } catch {
          setError("Failed to fetch job status");
          setLoading(false);
        }
      } catch {
        setError("Failed to submit permutations");
        setLoading(false);
      }
    },
    [reset]
  );

  return {
    jobId,
    expected,
    received,
    loading,
    bestResult,
    error,
    complete,
    handleSubmit,
    reset,
  };
}
