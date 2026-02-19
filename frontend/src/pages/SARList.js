import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Chip, IconButton, CircularProgress, TextField, InputAdornment, Checkbox, Button, Dialog, 
  DialogTitle, DialogContent, DialogContentText, DialogActions, Alert, Snackbar, Fade, Tooltip } from '@mui/material';
import { Visibility, Search, Delete, DeleteForever, FilterList, TrendingUp } from '@mui/icons-material';
import axiosInstance from '../api/axios';

export default function SARList() {
  const navigate = useNavigate();
  const [sars, setSars] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSARs, setSelectedSARs] = useState([]);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteAllDialogOpen, setDeleteAllDialogOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    loadSARs();
  }, []);

  const loadSARs = () => {
    setLoading(true);
    axiosInstance.get('/sars/')
      .then(res => setSars(res.data))
      .catch(err => {
        console.error(err);
        showSnackbar('Failed to load SARs', 'error');
      })
      .finally(() => setLoading(false));
  };

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleSelectAll = (event) => {
    if (event.target.checked) {
      setSelectedSARs(filteredSARs.map(s => s.id));
    } else {
      setSelectedSARs([]);
    }
  };

  const handleSelectOne = (sarId) => {
    setSelectedSARs(prev => 
      prev.includes(sarId) ? prev.filter(id => id !== sarId) : [...prev, sarId]
    );
  };

  const handleDeleteSelected = () => {
    if (selectedSARs.length === 0) {
      showSnackbar('Please select at least one SAR to delete', 'warning');
      return;
    }
    setDeleteDialogOpen(true);
  };

  const handleDeleteAll = () => {
    setDeleteAllDialogOpen(true);
  };

  const confirmDeleteSelected = async () => {
    setDeleting(true);
    try {
      const response = await axiosInstance.post('/sars/delete-multiple', {
        sar_ids: selectedSARs
      });
      showSnackbar(response.data.message, 'success');
      setSelectedSARs([]);
      loadSARs();
    } catch (error) {
      showSnackbar(error.response?.data?.detail || 'Failed to delete SARs', 'error');
    } finally {
      setDeleting(false);
      setDeleteDialogOpen(false);
    }
  };

  const confirmDeleteAll = async () => {
    setDeleting(true);
    try {
      const response = await axiosInstance.delete('/sars/delete-all');
      showSnackbar(response.data.message, 'success');
      setSelectedSARs([]);
      loadSARs();
    } catch (error) {
      showSnackbar(error.response?.data?.detail || 'Failed to delete all SARs', 'error');
    } finally {
      setDeleting(false);
      setDeleteAllDialogOpen(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = { 
      draft: 'default', 
      pending_review: 'warning', 
      approved: 'success', 
      rejected: 'error', 
      filed: 'info' 
    };
    return colors[status] || 'default';
  };

  const getRiskColor = (risk) => {
    const colors = { 
      low: 'success', 
      medium: 'warning', 
      high: 'error', 
      critical: 'error' 
    };
    return colors[risk] || 'default';
  };

  const filteredSARs = sars.filter(s => 
    s.case_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.customer_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <CircularProgress size={60} thickness={4} />
        <Typography variant="body1" color="text.secondary" sx={{ mt: 2 }}>
          Loading SARs...
        </Typography>
      </Box>
    );
  }

  return (
    <Fade in={true} timeout={800}>
      <Box>
        {/* Header Section */}
        <Box className="slide-in-left" sx={{ mb: 4 }}>
          <Typography variant="h3" className="gradient-text" sx={{ fontWeight: 800, mb: 1 }}>
            SAR Repository 📋
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage and review all Suspicious Activity Reports
          </Typography>
        </Box>

        {/* Stats Bar */}
        <Box className="fade-in" sx={{ 
          display: 'flex', 
          gap: 2, 
          mb: 3, 
          flexWrap: 'wrap',
        }}>
          <Paper className="hover-lift" sx={{ 
            px: 3, 
            py: 2, 
            display: 'flex', 
            alignItems: 'center', 
            gap: 2,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
          }}>
            <TrendingUp sx={{ fontSize: 32 }} />
            <Box>
              <Typography variant="h4" sx={{ fontWeight: 800 }}>
                {sars.length}
              </Typography>
              <Typography variant="caption">
                Total SARs
              </Typography>
            </Box>
          </Paper>

          {selectedSARs.length > 0 && (
            <Paper sx={{ 
              px: 3, 
              py: 2, 
              display: 'flex', 
              alignItems: 'center', 
              gap: 2,
              background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
              color: 'white',
            }}>
              <Box>
                <Typography variant="h4" sx={{ fontWeight: 800 }}>
                  {selectedSARs.length}
                </Typography>
                <Typography variant="caption">
                  Selected
                </Typography>
              </Box>
            </Paper>
          )}
        </Box>

        {/* Action Bar */}
        <Paper sx={{ p: 2, mb: 3, display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
          <TextField 
            size="small" 
            placeholder="Search by Case ID or Customer..." 
            value={searchTerm} 
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{ 
              startAdornment: (
                <InputAdornment position="start">
                  <Search color="primary" />
                </InputAdornment>
              ) 
            }} 
            sx={{ flexGrow: 1, minWidth: 300 }} 
          />
          
          {selectedSARs.length > 0 && (
            <Button 
              variant="contained" 
              color="error" 
              startIcon={<Delete />}
              onClick={handleDeleteSelected}
              sx={{ 
                boxShadow: '0px 4px 12px rgba(255, 59, 48, 0.3)',
              }}
            >
              Delete Selected ({selectedSARs.length})
            </Button>
          )}
          
          <Button 
            variant="outlined" 
            color="error" 
            startIcon={<DeleteForever />}
            onClick={handleDeleteAll}
            disabled={sars.length === 0}
          >
            Delete All
          </Button>
        </Paper>

        {/* Table */}
        <TableContainer component={Paper} sx={{ 
          borderRadius: 3,
          overflow: 'hidden',
          boxShadow: '0px 4px 20px rgba(0, 0, 0, 0.08)',
        }}>
          <Table>
            <TableHead>
              <TableRow sx={{ 
                background: 'linear-gradient(135deg, #00AEEF 0%, #0088BD 100%)',
              }}>
                <TableCell padding="checkbox">
                  <Checkbox
                    indeterminate={selectedSARs.length > 0 && selectedSARs.length < filteredSARs.length}
                    checked={filteredSARs.length > 0 && selectedSARs.length === filteredSARs.length}
                    onChange={handleSelectAll}
                    sx={{ color: 'white', '&.Mui-checked': { color: 'white' } }}
                  />
                </TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 700 }}>Case ID</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 700 }}>Customer</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 700 }}>Risk Level</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 700 }}>Status</TableCell>
                <TableCell sx={{ color: 'white', fontWeight: 700 }}>Created</TableCell>
                <TableCell align="center" sx={{ color: 'white', fontWeight: 700 }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredSARs.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Box sx={{ py: 8 }}>
                      <Typography variant="h6" color="text.secondary" sx={{ mb: 1 }}>
                        No SARs found
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {searchTerm ? 'Try adjusting your search' : 'Generate your first SAR to get started'}
                      </Typography>
                    </Box>
                  </TableCell>
                </TableRow>
              ) : (
                filteredSARs.map((sar, index) => (
                  <TableRow 
                    key={sar.id} 
                    hover
                    selected={selectedSARs.includes(sar.id)}
                    sx={{
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        backgroundColor: 'rgba(0, 174, 239, 0.04)',
                        transform: 'scale(1.01)',
                      },
                      animation: `fadeIn 0.5s ease ${index * 0.05}s both`,
                      '@keyframes fadeIn': {
                        from: { opacity: 0, transform: 'translateY(10px)' },
                        to: { opacity: 1, transform: 'translateY(0)' },
                      },
                    }}
                  >
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={selectedSARs.includes(sar.id)}
                        onChange={() => handleSelectOne(sar.id)}
                        color="primary"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 700, color: 'primary.main' }}>
                        {sar.case_id}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {sar.customer_name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        ID: {sar.customer_id}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={sar.risk_level || 'N/A'} 
                        color={getRiskColor(sar.risk_level)} 
                        size="small"
                        sx={{ fontWeight: 700, textTransform: 'uppercase' }}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={sar.status.replace('_', ' ')} 
                        color={getStatusColor(sar.status)} 
                        size="small"
                        sx={{ fontWeight: 600, textTransform: 'capitalize' }}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {new Date(sar.created_at).toLocaleDateString('en-US', { 
                          month: 'short', 
                          day: 'numeric', 
                          year: 'numeric' 
                        })}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(sar.created_at).toLocaleTimeString('en-US', { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        })}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Tooltip title="View Details" arrow>
                        <IconButton 
                          size="small" 
                          onClick={() => navigate(`/sars/${sar.id}`)} 
                          sx={{
                            color: 'primary.main',
                            '&:hover': {
                              background: 'linear-gradient(135deg, #00AEEF 0%, #0088BD 100%)',
                              color: 'white',
                            }
                          }}
                        >
                          <Visibility />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Delete Selected Confirmation Dialog */}
        <Dialog 
          open={deleteDialogOpen} 
          onClose={() => !deleting && setDeleteDialogOpen(false)}
          PaperProps={{
            sx: { borderRadius: 3, minWidth: 400 }
          }}
        >
          <DialogTitle sx={{ fontWeight: 700, fontSize: '1.5rem' }}>
            Confirm Deletion
          </DialogTitle>
          <DialogContent>
            <DialogContentText>
              Are you sure you want to delete <strong>{selectedSARs.length}</strong> selected SAR(s)? 
              <br /><br />
              This action cannot be undone and will permanently remove the data from the database.
            </DialogContentText>
          </DialogContent>
          <DialogActions sx={{ p: 2 }}>
            <Button onClick={() => setDeleteDialogOpen(false)} disabled={deleting}>
              Cancel
            </Button>
            <Button 
              onClick={confirmDeleteSelected} 
              color="error" 
              variant="contained" 
              disabled={deleting}
              sx={{ minWidth: 100 }}
            >
              {deleting ? <CircularProgress size={20} color="inherit" /> : 'Delete'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Delete All Confirmation Dialog */}
        <Dialog 
          open={deleteAllDialogOpen} 
          onClose={() => !deleting && setDeleteAllDialogOpen(false)}
          PaperProps={{
            sx: { borderRadius: 3, minWidth: 400 }
          }}
        >
          <DialogTitle sx={{ color: 'error.main', fontWeight: 700, fontSize: '1.5rem' }}>
            ⚠️ Warning: Delete All SARs
          </DialogTitle>
          <DialogContent>
            <DialogContentText>
              <strong>This will permanently delete ALL {sars.length} SAR(s) from the database!</strong>
              <br /><br />
              This action is irreversible and will remove all SAR data, narratives, and analysis. 
              Are you absolutely sure you want to proceed?
            </DialogContentText>
          </DialogContent>
          <DialogActions sx={{ p: 2 }}>
            <Button onClick={() => setDeleteAllDialogOpen(false)} disabled={deleting}>
              Cancel
            </Button>
            <Button 
              onClick={confirmDeleteAll} 
              color="error" 
              variant="contained" 
              disabled={deleting}
              sx={{ minWidth: 100 }}
            >
              {deleting ? <CircularProgress size={20} color="inherit" /> : 'Delete All'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Snackbar for notifications */}
        <Snackbar 
          open={snackbar.open} 
          autoHideDuration={4000} 
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert 
            onClose={() => setSnackbar({ ...snackbar, open: false })} 
            severity={snackbar.severity}
            sx={{ borderRadius: 2, boxShadow: 3 }}
          >
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Box>
    </Fade>
  );
}
