import React from 'react';

interface ProgressBarProps {
  messages: string[];
  isComplete: boolean;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ messages, isComplete }) => {
  return (
    <div>
      <h3>Progress</h3>
      <ul>
        {messages.map((msg, index) => (
          <li key={index}>{msg}</li>
        ))}
      </ul>
      {isComplete && <p>Complete!</p>}
    </div>
  );
};

export default ProgressBar;