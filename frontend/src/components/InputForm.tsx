import { useState, useEffect } from 'react';
import type { CreateETLRequest } from '../services/api';

const generateRandomId = () => Math.random().toString(36).substring(2, 15);

interface InputFormProps {
  onSubmit: (request: CreateETLRequest) => void;
}

const InputForm: React.FC<InputFormProps> = ({ onSubmit }) => {
  const [userPrompt, setUserPrompt] = useState('');
  const [threadId, setThreadId] = useState('');
  const [userId, setUserId] = useState('');

  useEffect(() => {
    setThreadId(generateRandomId());
    setUserId(generateRandomId());
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      user_prompt: userPrompt,
      ids: {
        thread_id: threadId,
        user_id: userId,
      },
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>User Prompt:</label>
        <textarea
          value={userPrompt}
          onChange={(e) => setUserPrompt(e.target.value)}
          required
          rows={4}
          placeholder="Describe your ETL requirements..."
        />
      </div>
      <div>
        <label>Thread ID:</label>
        <input
          type="text"
          value={threadId}
          onChange={(e) => setThreadId(e.target.value)}
          required
        />
      </div>
      <div>
        <label>User ID:</label>
        <input
          type="text"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          required
        />
      </div>
      <button type="submit">Create ETL</button>
    </form>
  );
};

export default InputForm;