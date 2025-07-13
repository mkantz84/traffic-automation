import React from "react";
import SimulationForm from "./components/SimulationForm";
import SimulationProgress from "./components/SimulationProgress";
import BestResult from "./components/BestResult";
import Loader from "./components/Loader";
import { useSimulation } from "./hooks/useSimulation";

const App: React.FC = () => {
  const {
    jobId,
    expected,
    received,
    loading,
    bestResult,
    error,
    complete,
    handleSubmit,
  } = useSimulation();

  return (
    <div className="container">
      <h1>Run SUMO Delay Simulations</h1>
      <SimulationForm onSubmit={handleSubmit} disabled={loading} />
      {error && <div className="error">{error}</div>}
      {jobId && (
        <SimulationProgress
          received={received}
          expected={expected}
          loading={loading && !complete}
        />
      )}
      {loading && !complete && <Loader />}
      {bestResult && <BestResult result={bestResult} />}
    </div>
  );
};

export default App;
