import React, { useState, useEffect } from 'react';

interface Message {
  id: string;
  content: string;
  type: string;
  toolCalls?: any[];
}

const CalculatorChat: React.FC = () => {
  const [userId, setUserId] = useState('');
  const [threadId, setThreadId] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);

  useEffect(() => {
    // Generate random IDs on mount
    setUserId(Math.random().toString(36).substring(2, 15));
    setThreadId(Math.random().toString(36).substring(2, 15));
  }, []);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      content: input,
      type: 'user',
    };
    setMessages(prev => [...prev, newMessage]);
    setInput('');
    setIsStreaming(true);

    try {
      const formData = new FormData();
      formData.append('message', input);
      formData.append('thread_id', threadId);
      formData.append('user_id', userId);

      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/chat/calculator`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Failed to send message');

      const reader = response.body?.getReader();
      if (!reader) return;

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim()) {
            try {
              const data = JSON.parse(line);
              const msg = data.message;
              if (msg.type === 'AIMessageChunk') {
                setMessages(prev => {
                  const last = prev[prev.length - 1];
                  if (last && last.type === 'ai' && last.id === msg.id) {
                    return [...prev.slice(0, -1), { ...last, content: last.content + msg.content }];
                  } else {
                    return [...prev, { id: msg.id, content: msg.content, type: 'ai', toolCalls: msg.tool_call_chunks }];
                  }
                });
              } else if (msg.type === 'tool') {
                setMessages(prev => [...prev, { id: msg.id, content: `Tool result: ${msg.content}`, type: 'tool' }]);
              }
            } catch (e) {
              console.error('Failed to parse line:', line);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, { id: Date.now().toString(), content: 'Error sending message', type: 'error' }]);
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Calculator Chat</h1>
      <div>
        <label>User ID: <input value={userId} onChange={e => setUserId(e.target.value)} /></label>
        <label>Thread ID: <input value={threadId} onChange={e => setThreadId(e.target.value)} /></label>
      </div>
      <div style={{ height: '400px', overflowY: 'scroll', border: '1px solid #ccc', padding: '10px', margin: '10px 0' }}>
        {messages.map(msg => (
          <div key={msg.id} style={{ marginBottom: '10px' }}>
            <strong>{msg.type === 'user' ? 'You' : msg.type === 'ai' ? 'AI' : 'Tool'}:</strong> {msg.content}
            {msg.toolCalls && msg.toolCalls.length > 0 && (
              <div>Tool calls: {JSON.stringify(msg.toolCalls)}</div>
            )}
          </div>
        ))}
        {isStreaming && <div>AI is thinking...</div>}
      </div>
      <div>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && sendMessage()}
          placeholder="Type your message..."
          style={{ width: '70%', padding: '10px' }}
        />
        <button onClick={sendMessage} disabled={isStreaming} style={{ padding: '10px' }}>Send</button>
      </div>
    </div>
  );
};

export default CalculatorChat;