import React from 'react';

interface DeploymentReportProps {
  success: boolean;
  messages: string[];
}

const DeploymentReport: React.FC<DeploymentReportProps> = ({ success, messages }) => {
  return (
    <div>
      <h3>Deployment Report</h3>
      <p>Status: {success ? 'Success' : 'Failure'}</p>
      <ul>
        {messages.map((msg, index) => (
          <li key={index}>{msg}</li>
        ))}
      </ul>
    </div>
  );
};

export default DeploymentReport;