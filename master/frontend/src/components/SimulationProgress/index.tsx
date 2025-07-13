import React from "react";
import "./SimulationProgress.css";

type Props = {
  received: number;
  expected: number;
  loading: boolean;
};

const SimulationProgress: React.FC<Props> = ({
  received,
  expected,
  loading,
}) => {
  return (
    <div className="simulation-progress">
      {loading && (
        <span className="simulation-progress__loader">Loading... </span>
      )}
      <span>
        {received} out of {expected} simulations completed.
      </span>
    </div>
  );
};

export default SimulationProgress;
