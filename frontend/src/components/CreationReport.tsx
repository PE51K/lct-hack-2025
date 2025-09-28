import React from 'react';

interface CreationReportProps {
  extractConfig?: Record<string, unknown>;
  transformConfig?: Record<string, unknown>;
  loadConfig?: Record<string, unknown>;
  ddl?: Record<string, unknown>;
  dag?: Record<string, unknown>;
  onSatisfied: () => void;
  onNotSatisfied: () => void;
}

const CreationReport: React.FC<CreationReportProps> = ({
  extractConfig,
  transformConfig,
  loadConfig,
  ddl,
  dag,
  onSatisfied,
  onNotSatisfied,
}) => {
  return (
    <div>
      <h3>Creation Report</h3>
      {extractConfig && (
        <div>
          <h4>Extract Config</h4>
          <pre>{JSON.stringify(extractConfig, null, 2)}</pre>
        </div>
      )}
      {transformConfig && (
        <div>
          <h4>Transform Config</h4>
          <pre>{JSON.stringify(transformConfig, null, 2)}</pre>
        </div>
      )}
      {loadConfig && (
        <div>
          <h4>Load Config</h4>
          <pre>{JSON.stringify(loadConfig, null, 2)}</pre>
        </div>
      )}
      {ddl && (
        <div>
          <h4>DDL</h4>
          <pre>{JSON.stringify(ddl, null, 2)}</pre>
        </div>
      )}
      {dag && (
        <div>
          <h4>DAG</h4>
          <pre>{JSON.stringify(dag, null, 2)}</pre>
        </div>
      )}
      <button onClick={onSatisfied}>Satisfied</button>
      <button onClick={onNotSatisfied}>Not Satisfied</button>
    </div>
  );
};

export default CreationReport;