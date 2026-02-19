import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Chip, IconButton, CircularProgress, TextField, InputAdornment, Alert, Snackbar, Tooltip } from '@mui/material';
import { Search, Send } from '@mui/icons-material';
import axiosInstance from '../api/axios';

export default function AlertData() {
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = () => {
    setLoading(true);
    axiosInstance.get('/alerts/')
      .then(res => setAlerts(res.data))
      .catch(err => {
        console.error(err);
        showSnackbar('Failed to load alerts', 'error');
      })
      .finally(() => setLoading(false));
  };

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleInsertToSAR = (alert) => {
    // Navigate to SAR Generator with alert data
    navigate('/generate', { state: { alertData: alert } });
  };

  const getPriorityColor = (priority) => {
    const colors = { low: 'success', medium: 'warning', high: 'error', critical: 'error' };
    return colors[priority] || 'default';
  };

  const filteredAlerts = alerts.filter(alert =>
    alert.customer_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    alert.customer_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    alert.alert_id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box className="slide-in-left" sx={{ mb: 4 }}>
        <Typography variant="h4" className="gradient-text" sx={{ fontWeight: 700, mb: 1 }}>
          Alert Data Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Incoming alerts waiting for SAR generation
        </Typography>
      </Box>

      {/* Actions Bar */}
      <Paper className="fade-in" sx={{ p: 3, mb: 3 }}>
        <TextField
          placeholder="Search by customer name, ID, or alert ID..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          fullWidth
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
        />
      </Paper>

      {/* Alerts Table */}
      <TableContainer component={Paper} className="scale-in">
        <Table>
          <TableHead>
            <TableRow sx={{ bgcolor: 'grey.50' }}>
              <TableCell sx={{ fontWeight: 700 }}>Alert ID</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Customer</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Account</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Alert Type</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Priority</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Transactions</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Created</TableCell>
              <TableCell sx={{ fontWeight: 700 }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredAlerts.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center" sx={{ py: 8 }}>
                  <Typography variant="body1" color="text.secondary">
                    No alerts found
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              filteredAlerts.map((alert) => (
                <TableRow 
                  key={alert.id}
                  hover
                  sx={{ '&:hover': { bgcolor: 'action.hover' } }}
                >
                  <TableCell>
                    <Typography variant="body2" sx={{ fontWeight: 600, fontFamily: 'monospace' }}>
                      {alert.alert_id}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {alert.customer_name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      ID: {alert.customer_id}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                      {alert.account_number}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {alert.alert_type || 'General'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={alert.priority.toUpperCase()} 
                      color={getPriorityColor(alert.priority)}
                      size="small"
                      sx={{ fontWeight: 600 }}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {alert.transaction_data?.length || 0} transactions
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {new Date(alert.created_at).toLocaleDateString()}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Tooltip title="Insert to SAR Generator">
                      <IconButton 
                        color="primary"
                        onClick={() => handleInsertToSAR(alert)}
                        size="small"
                      >
                        <Send />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={() => setSnackbar({ ...snackbar, open: false })} 
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}
