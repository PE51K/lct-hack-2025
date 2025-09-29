import React, { useState } from 'react';
import type { Feedback } from '../services/api';

interface FeedbackFormProps {
  onSubmit: (feedback: Feedback) => void;
  onCancel: () => void;
}

const FeedbackForm: React.FC<FeedbackFormProps> = ({ onSubmit, onCancel }) => {
  const [overall, setOverall] = useState('');
  const [items, setItems] = useState<{ area: string; message: string; suggestion: string }[]>([]);

  const addItem = () => {
    setItems([...items, { area: '', message: '', suggestion: '' }]);
  };

  const updateItem = (index: number, field: string, value: string) => {
    const newItems = [...items];
    newItems[index] = { ...newItems[index], [field]: value };
    setItems(newItems);
  };

  const removeItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      overall: overall || undefined,
      items: items.filter(item => item.area && item.message),
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <h3>Feedback</h3>
      <div>
        <label>Overall Comment:</label>
        <textarea
          value={overall}
          onChange={(e) => setOverall(e.target.value)}
        />
      </div>
      <div>
        <h4>Feedback Items</h4>
        {items.map((item, index) => (
          <div key={index}>
            <input
              type="text"
              placeholder="Area (e.g., extract)"
              value={item.area}
              onChange={(e) => updateItem(index, 'area', e.target.value)}
            />
            <input
              type="text"
              placeholder="Message"
              value={item.message}
              onChange={(e) => updateItem(index, 'message', e.target.value)}
            />
            <input
              type="text"
              placeholder="Suggestion (optional)"
              value={item.suggestion}
              onChange={(e) => updateItem(index, 'suggestion', e.target.value)}
            />
            <button type="button" onClick={() => removeItem(index)}>Remove</button>
          </div>
        ))}
        <button type="button" onClick={addItem}>Add Item</button>
      </div>
      <button type="submit">Submit Feedback</button>
      <button type="button" onClick={onCancel}>Cancel</button>
    </form>
  );
};

export default FeedbackForm;