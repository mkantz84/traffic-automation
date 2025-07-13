export interface SimulationFormData {
  accel: string;
  tau: string;
  startupDelay: string;
  expected_I2: string;
  expected_I3: string;
}

export interface JobStatus {
  job_id: string;
  received_results: number;
  expected_results: number;
  complete: boolean;
}

export interface BestResult {
  accel: number;
  tau: number;
  startupDelay: number;
  intersection_avg_delays: {
    I2: number;
    I3: number;
    [key: string]: number;
  };
  error?: number;
}
