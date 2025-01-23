import { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  IconButton,
  CircularProgress,
} from '@mui/material';
import { PlayArrow, Stop, Refresh } from '@mui/icons-material';
import { useQuery } from 'react-query';

interface Model {
  id: string;
  name: string;
  status: 'running' | 'stopped' | 'loading';
  type: 'rag' | 'processing' | 'embedding';
  memory_usage: number;
  port: number;
}

export default function Models() {
  const { data: models, isLoading, refetch } = useQuery<Model[]>(
    'models',
    async () => {
      const response = await fetch('/api/models');
      if (!response.ok) {
        throw new Error('Failed to fetch models');
      }
      return response.json();
    }
  );

  const handleModelAction = async (modelId: string, action: 'start' | 'stop') => {
    try {
      const response = await fetch(`/api/models/${modelId}/${action}`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`Failed to ${action} model`);
      }
      refetch();
    } catch (error) {
      console.error(error);
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Model Management</Typography>
        <IconButton onClick={() => refetch()}>
          <Refresh />
        </IconButton>
      </Box>

      <Grid container spacing={3}>
        {models?.map((model) => (
          <Grid item xs={12} md={6} lg={4} key={model.id}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {model.name}
                </Typography>
                <Box display="flex" alignItems="center" gap={1} mb={2}>
                  <Chip
                    label={model.status}
                    color={model.status === 'running' ? 'success' : 'default'}
                  />
                  <Chip label={model.type} color="primary" />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Memory Usage: {(model.memory_usage / 1024).toFixed(2)} GB
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Port: {model.port}
                </Typography>
                <Box display="flex" justifyContent="flex-end" mt={2}>
                  {model.status === 'running' ? (
                    <IconButton
                      color="error"
                      onClick={() => handleModelAction(model.id, 'stop')}
                    >
                      <Stop />
                    </IconButton>
                  ) : (
                    <IconButton
                      color="success"
                      onClick={() => handleModelAction(model.id, 'start')}
                    >
                      <PlayArrow />
                    </IconButton>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
