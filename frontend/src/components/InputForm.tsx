import { useState, useEffect } from 'react';
import type { GenerateETLRequest } from '../services/api';

const generateRandomId = () => Math.random().toString(36).substring(2, 15);

interface InputFormProps {
  onSubmit: (request: GenerateETLRequest) => void;
}

const InputForm: React.FC<InputFormProps> = ({ onSubmit }) => {
  const [dataUri, setDataUri] = useState('');
  const [threadId, setThreadId] = useState('');
  const [userId, setUserId] = useState('');

  useEffect(() => {
    setThreadId(generateRandomId());
    setUserId(generateRandomId());
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      data_uri: dataUri,
      ids: {
        thread_id: threadId,
        user_id: userId,
      },
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Data URI:</label>
        <input
          type="text"
          value={dataUri}
          onChange={(e) => setDataUri(e.target.value)}
          required
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
      <button type="submit">Generate ETL</button>
    </form>
  );
};

export default InputForm;