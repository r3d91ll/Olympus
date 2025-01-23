import { useState, useEffect, useCallback } from 'react';

type ConnectionStatus = 'connected' | 'connecting' | 'disconnected';

export function useMcpConnection() {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [lastMessage, setLastMessage] = useState<string>('');
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected');

  const connect = useCallback(() => {
    if (ws?.readyState === WebSocket.OPEN) return;

    setConnectionStatus('connecting');
    const websocket = new WebSocket('ws://localhost:8000/mcp');

    websocket.onopen = () => {
      setConnectionStatus('connected');
    };

    websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'response') {
          setLastMessage(data.content);
        }
      } catch (error) {
        console.error('Failed to parse message:', error);
      }
    };

    websocket.onclose = () => {
      setConnectionStatus('disconnected');
      setTimeout(connect, 5000); // Reconnect after 5 seconds
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      websocket.close();
    };

    setWs(websocket);
  }, [ws]);

  useEffect(() => {
    connect();
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [connect]);

  const sendMessage = useCallback((content: string) => {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'request',
        content,
        timestamp: Date.now()
      }));
    }
  }, [ws]);

  return {
    sendMessage,
    lastMessage,
    connectionStatus
  };
}
