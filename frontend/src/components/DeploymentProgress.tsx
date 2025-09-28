import React from 'react';

interface DeploymentProgressProps {
  messages: string[];
  isComplete: boolean;
  success?: boolean;
}

const DeploymentProgress: React.FC<DeploymentProgressProps> = ({ messages, isComplete, success }) => {
  return (
    <div>
      <h3>Deployment Progress</h3>
      <ul>
        {messages.map((msg, index) => (
          <li key={index}>{msg}</li>
        ))}
      </ul>
      {isComplete && (
        <p>{success ? 'Deployment Successful!' : 'Deployment Failed!'}</p>
      )}
    </div>
  );
};

export default DeploymentProgress;