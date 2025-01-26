import { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  CircularProgress,
} from '@mui/material';
import { useQuery } from 'react-query';

interface MemoryStats {
  elysium: {
    size: number;
    count: number;
  };
  asphodel: {
    size: number;
    count: number;
  };
  tartarus: {
    size: number;
    count: number;
  };
  lethe: {
    archived: number;
  };
}

export default function Memory() {
  const [activeTab, setActiveTab] = useState(0);

  const { data: memoryStats, isLoading } = useQuery<MemoryStats>(
    'memoryStats',
    async () => {
      const response = await fetch('/api/memory/stats');
      if (!response.ok) {
        throw new Error('Failed to fetch memory stats');
      }
      return response.json();
    },
    {
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  );

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Memory Management
      </Typography>

      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          variant="fullWidth"
        >
          <Tab label="Elysium" />
          <Tab label="Asphodel" />
          <Tab label="Tartarus" />
          <Tab label="Lethe" />
        </Tabs>
      </Paper>

      <Box role="tabpanel" hidden={activeTab !== 0}>
        {activeTab === 0 && (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Active Memory (Elysium)
            </Typography>
            <Typography>
              Total Items: {memoryStats?.elysium.count}
            </Typography>
            <Typography>
              Size: {(memoryStats?.elysium.size || 0 / 1024 / 1024).toFixed(2)} MB
            </Typography>
          </Paper>
        )}
      </Box>

      {/* Similar panels for other memory tiers */}
    </Box>
  );
}
