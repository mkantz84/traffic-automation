import React from "react";
import type { BestResult as BestResultType } from "../../types";
import "./BestResult.css";

type Props = {
  result: BestResultType | null;
};

const BestResult: React.FC<Props> = ({ result }) => {
  if (!result) return null;
  return (
    <div className="best-result">
      <h2>Best Result:</h2>
      <pre className="best-result__json">{JSON.stringify(result, null, 2)}</pre>
    </div>
  );
};

export default BestResult;
