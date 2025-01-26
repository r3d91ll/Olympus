import { useState, useEffect, useRef } from 'react';
import { Box, TextField, IconButton, Paper, Typography, Divider } from '@mui/material';
import { Send } from '@mui/icons-material';
import { useMcpConnection } from '../../hooks/useMcpConnection';
import { Message } from './Message';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

export default function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { sendMessage, lastMessage, connectionStatus } = useMcpConnection();

  useEffect(() => {
    if (lastMessage) {
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: lastMessage,
        timestamp: Date.now()
      }]);
    }
  }, [lastMessage]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMessage]);
    sendMessage(input);
    setInput('');
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <Box sx={{ height: 'calc(100vh - 100px)', display: 'flex', flexDirection: 'column' }}>
      <Paper 
        elevation={3} 
        sx={{ 
          flex: 1, 
          mb: 2, 
          overflow: 'auto',
          p: 2,
          backgroundColor: 'background.paper' 
        }}
      >
        {messages.map((message) => (
          <Message key={message.id} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </Paper>

      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask HADES..."
          sx={{ backgroundColor: 'background.paper' }}
        />
        <IconButton 
          onClick={handleSend} 
          color="primary" 
          sx={{ alignSelf: 'flex-end' }}
        >
          <Send />
        </IconButton>
      </Box>

      {connectionStatus !== 'connected' && (
        <Typography 
          color="error" 
          variant="caption" 
          sx={{ mt: 1 }}
        >
          {connectionStatus === 'connecting' ? 'Connecting...' : 'Disconnected'}
        </Typography>
      )}
    </Box>
  );
}
