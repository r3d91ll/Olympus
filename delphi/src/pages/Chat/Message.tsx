import { Box, Paper, Typography } from '@mui/material';
import { formatDistanceToNow } from 'date-fns';

interface MessageProps {
  message: {
    role: 'user' | 'assistant';
    content: string;
    timestamp: number;
  };
}

export function Message({ message }: MessageProps) {
  const isAssistant = message.role === 'assistant';

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isAssistant ? 'flex-start' : 'flex-end',
        mb: 2,
      }}
    >
      <Paper
        elevation={1}
        sx={{
          maxWidth: '70%',
          p: 2,
          backgroundColor: isAssistant ? 'background.paper' : 'primary.dark',
          borderRadius: 2,
        }}
      >
        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
          {message.content}
        </Typography>
        <Typography
          variant="caption"
          sx={{
            display: 'block',
            mt: 1,
            color: 'text.secondary',
            textAlign: 'right',
          }}
        >
          {formatDistanceToNow(message.timestamp, { addSuffix: true })}
        </Typography>
      </Paper>
    </Box>
  );
}
