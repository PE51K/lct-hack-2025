import { useState } from 'react';
import type { CredentialsRequired } from '../services/api';

interface CredentialsFormProps {
  credentialsRequired: CredentialsRequired;
  onSubmit: (credentials: Record<string, unknown>) => void;
  onCancel: () => void;
}

function CredentialsForm({ credentialsRequired, onSubmit, onCancel }: CredentialsFormProps) {
  const [credentials, setCredentials] = useState<Record<string, unknown>>(() => {
    // Initialize with default values
    const initial: Record<string, unknown> = {};
    credentialsRequired.fields.forEach(field => {
      if (field.default !== undefined) {
        initial[field.name] = field.default;
      }
    });
    return initial;
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(credentials);
  };

  const handleChange = (fieldName: string, value: unknown) => {
    setCredentials(prev => ({ ...prev, [fieldName]: value }));
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '20px' }}>
      <h2>Target Database Credentials</h2>
      <p>
        The AI recommends using <strong>{credentialsRequired.target_type}</strong> as your target database.
        Please provide the connection credentials below.
      </p>

      <form onSubmit={handleSubmit}>
        {credentialsRequired.fields.map(field => (
          <div key={field.name} style={{ marginBottom: '15px' }}>
            <label htmlFor={field.name} style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              {field.label}
              {field.required && <span style={{ color: 'red' }}> *</span>}
            </label>
            <input
              type={field.type}
              id={field.name}
              name={field.name}
              placeholder={field.placeholder}
              required={field.required}
              value={credentials[field.name] as string || ''}
              onChange={(e) => {
                const value = field.type === 'number' ? Number(e.target.value) : e.target.value;
                handleChange(field.name, value);
              }}
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid #ccc',
                borderRadius: '4px',
                fontSize: '14px'
              }}
            />
          </div>
        ))}

        <div style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
          <button
            type="submit"
            style={{
              flex: 1,
              padding: '10px',
              backgroundColor: '#4CAF50',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            Create DAG
          </button>
          <button
            type="button"
            onClick={onCancel}
            style={{
              flex: 1,
              padding: '10px',
              backgroundColor: '#f44336',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

export default CredentialsForm;