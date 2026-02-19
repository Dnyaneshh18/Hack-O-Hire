import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Box, Paper, Typography, TextField, Button, Grid, Alert, CircularProgress, Chip, LinearProgress, Backdrop } from '@mui/material';
import { Person, Receipt, Flag, CheckCircle, Rocket } from '@mui/icons-material';
import axiosInstance from '../api/axios';

export default function SARGenerator() {
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [generatedSAR, setGeneratedSAR] = useState(null);
  const [customerData, setCustomerData] = useState({ customer_id: '', name: '', account_number: '' });
  const [transactionData, setTransactionData] = useState('');
  const [alertReason, setAlertReason] = useState('');
  const [progress, setProgress] = useState(0);
  const [alertId, setAlertId] = useState(null);

  // Prevent page refresh/close during SAR generation
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (loading) {
        e.preventDefault();
        e.returnValue = 'SAR generation in progress. Are you sure you want to leave?';
        return e.returnValue;
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [loading]);

  // Pre-fill data from Alert Data if available
  useEffect(() => {
    if (location.state?.alertData) {
      const alert = location.state.alertData;
      setAlertId(alert.id);
      setCustomerData({
        customer_id: alert.customer_id,
        name: alert.customer_name,
        account_number: alert.account_number,
      });
      
      // Convert transaction data to CSV format
      if (alert.transaction_data && alert.transaction_data.length > 0) {
        const csvData = alert.transaction_data.map(t => 
          `${t.date || t.Date}, ${t.amount || t.Amount}, ${t.counterparty || t.Counterparty}, ${t.description || t.Description}`
        ).join('\n');
        setTransactionData(csvData);
      }
      
      setAlertReason(alert.alert_reason);
    }
  }, [location.state]);

  const handleGenerate = async () => {
    setLoading(true);
    setError('');
    setProgress(0);
    
    try {
      // Validate inputs
      if (!customerData.customer_id || !customerData.name || !customerData.account_number) {
        setError('Please fill in all customer fields');
        setLoading(false);
        return;
      }
      if (!transactionData.trim()) {
        setError('Please enter transaction data');
        setLoading(false);
        return;
      }
      if (!alertReason.trim()) {
        setError('Please enter alert reason');
        setLoading(false);
        return;
      }

      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 3000);

      const transactions = transactionData.split('\n').filter(l => l.trim()).map((line, i) => {
        const parts = line.split(',').map(p => p.trim());
        return { 
          transaction_id: `TXN-${i+1}`, 
          date: parts[0] || new Date().toISOString().split('T')[0],
          amount: parseFloat(parts[1]) || 0, 
          counterparty: parts[2] || 'Unknown', 
          description: parts[3] || 'Transaction' 
        };
      });

      const response = await axiosInstance.post('/sars/generate', {
        customer_data: customerData, 
        transaction_data: transactions,
        kyc_data: { expected_activity: '', source_of_funds: '', business_purpose: '' }, 
        alert_reason: alertReason
      });
      
      clearInterval(progressInterval);
      setProgress(100);
      setGeneratedSAR(response.data);
      
      // If this SAR was generated from an alert, mark the alert as processed
      if (alertId) {
        try {
          await axiosInstance.put(`/alerts/${alertId}`, {
            is_processed: true,
            sar_id: response.data.id
          });
        } catch (err) {
          console.error('Failed to update alert status:', err);
        }
      }
    } catch (err) {
      console.error('SAR Generation Error:', err);
      if (err.response) {
        setError(err.response.data?.detail || `Error: ${err.response.status} - ${err.response.statusText}`);
      } else if (err.request) {
        setError('No response from server. Please check if backend is running.');
      } else {
        setError(err.message || 'Failed to generate SAR');
      }
    } finally {
      setLoading(false);
    }
  };

  if (generatedSAR) {
    return (
      <Box>
        {/* Success Header */}
        <Paper className="bounce-in" sx={{ 
          p: 4, 
          mb: 3, 
          background: 'linear-gradient(135deg, #00C389 0%, #009B6B 100%)',
          color: 'white',
          textAlign: 'center',
        }}>
          <CheckCircle sx={{ fontSize: 64, mb: 2 }} />
          <Typography variant="h3" sx={{ fontWeight: 800, mb: 1 }}>
            SAR Generated Successfully! 🎉
          </Typography>
          <Typography variant="body1" sx={{ opacity: 0.9 }}>
            Your AI-powered SAR narrative is ready for review
          </Typography>
        </Paper>

        {/* SAR Details */}
        <Paper className="fade-in" sx={{ p: 4, mb: 3 }}>
          <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
            <Chip 
              className="scale-in"
              label={`Case ID: ${generatedSAR.case_id}`} 
              color="primary" 
              sx={{ fontWeight: 700, fontSize: '0.95rem', py: 2.5 }}
            />
            <Chip 
              label={`Risk: ${generatedSAR.risk_level}`} 
              color={generatedSAR.risk_level === 'high' || generatedSAR.risk_level === 'critical' ? 'error' : 'warning'} 
              sx={{ fontWeight: 700, fontSize: '0.95rem', py: 2.5, textTransform: 'uppercase' }}
            />
            <Chip 
              label={`Score: ${generatedSAR.risk_score}/100`} 
              color="info"
              sx={{ fontWeight: 700, fontSize: '0.95rem', py: 2.5 }}
            />
            <Chip 
              label={`Typology: ${generatedSAR.typology || 'Unknown'}`} 
              sx={{ fontWeight: 700, fontSize: '0.95rem', py: 2.5 }}
            />
          </Box>

          <Typography variant="h6" sx={{ fontWeight: 700, mb: 2, color: 'primary.main' }}>
            Generated Narrative
          </Typography>
          <Paper variant="outlined" sx={{ 
            p: 3, 
            bgcolor: 'grey.50',
            borderRadius: 2,
            border: '2px solid',
            borderColor: 'primary.light',
          }}>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.9, fontSize: '1.05rem' }}>
              {generatedSAR.narrative}
            </Typography>
          </Paper>
        </Paper>

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button 
            variant="contained" 
            size="large"
            onClick={() => navigate(`/sars/${generatedSAR.id}`)}
            sx={{ 
              px: 4,
              py: 1.5,
              fontSize: '1rem',
              fontWeight: 700,
            }}
          >
            View Full Analysis
          </Button>
          <Button 
            variant="outlined" 
            size="large"
            onClick={() => navigate('/sars')}
            sx={{ px: 4, py: 1.5 }}
          >
            View All SARs
          </Button>
          <Button 
            size="large"
            onClick={() => window.location.reload()}
            sx={{ px: 4, py: 1.5 }}
          >
            Generate Another
          </Button>
        </Box>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box className="slide-in-left" sx={{ mb: 4 }}>
        <Typography variant="h3" className="gradient-text" sx={{ fontWeight: 800, mb: 1 }}>
          Generate SAR Narrative
        </Typography>
        <Typography variant="body1" color="text.secondary">
          AI-powered analysis with comprehensive 16-stage processing
        </Typography>
      </Box>

      {/* Process Steps */}
      <Paper className="glass fade-in" sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
        <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
          How It Works
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={3}>
            <Box className="hover-lift" sx={{ textAlign: 'center' }}>
              <Person sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                1. Enter Customer Data
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={3}>
            <Box className="hover-lift" sx={{ textAlign: 'center' }}>
              <Receipt sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                2. Add Transactions
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={3}>
            <Box className="hover-lift" sx={{ textAlign: 'center' }}>
              <Rocket sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                3. AI Analysis
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={3}>
            <Box className="hover-lift" sx={{ textAlign: 'center' }}>
              <CheckCircle sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                4. Review & Submit
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
          {error}
        </Alert>
      )}

      {/* Input Form */}
      <Paper className="glass scale-in" sx={{ p: 4 }}>
        <Grid container spacing={3}>
          {/* Customer Information */}
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Person color="primary" />
              <Typography variant="h6" sx={{ fontWeight: 700 }}>
                Customer Information
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField 
              fullWidth 
              label="Customer ID" 
              value={customerData.customer_id}
              onChange={(e) => setCustomerData({...customerData, customer_id: e.target.value})} 
              required
              placeholder="e.g., CUST-12345"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField 
              fullWidth 
              label="Customer Name" 
              value={customerData.name}
              onChange={(e) => setCustomerData({...customerData, name: e.target.value})} 
              required
              placeholder="e.g., John Doe"
            />
          </Grid>

          <Grid item xs={12}>
            <TextField 
              fullWidth 
              label="Account Number" 
              value={customerData.account_number}
              onChange={(e) => setCustomerData({...customerData, account_number: e.target.value})} 
              required
              placeholder="e.g., ACC-98765"
            />
          </Grid>

          {/* Transaction Data */}
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2, mt: 2 }}>
              <Receipt color="primary" />
              <Typography variant="h6" sx={{ fontWeight: 700 }}>
                Transaction Data
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12}>
            <TextField 
              fullWidth 
              multiline 
              rows={8} 
              label="Transaction Details" 
              value={transactionData}
              onChange={(e) => setTransactionData(e.target.value)}
              placeholder="Enter one transaction per line in format: Date, Amount, Counterparty, Description&#10;Example:&#10;2024-01-15, 9500, ABC Corp, Wire transfer&#10;2024-01-16, 9800, XYZ Ltd, Wire transfer&#10;2024-01-17, 9200, DEF Inc, Wire transfer"
              required
              helperText="Format: Date, Amount, Counterparty, Description (one per line)"
            />
          </Grid>

          {/* Alert Reason */}
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2, mt: 2 }}>
              <Flag color="primary" />
              <Typography variant="h6" sx={{ fontWeight: 700 }}>
                Alert Reason
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12}>
            <TextField 
              fullWidth 
              multiline 
              rows={3} 
              label="Why is this activity suspicious?" 
              value={alertReason}
              onChange={(e) => setAlertReason(e.target.value)} 
              required
              placeholder="e.g., Multiple transactions just below reporting threshold, rapid fund movement, unusual pattern for customer profile"
            />
          </Grid>
        </Grid>

        {/* Generate Button */}
        <Box sx={{ mt: 4 }}>
          <Button 
            className="pulse hover-lift btn-gradient"
            variant="contained" 
            size="large" 
            fullWidth
            onClick={handleGenerate} 
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <Rocket />}
            sx={{ 
              py: 2,
              fontSize: '1.1rem',
              fontWeight: 700,
              boxShadow: '0px 8px 24px rgba(0, 174, 239, 0.3)',
            }}
          >
            {loading ? 'Generating SAR Narrative...' : 'Generate SAR Narrative with AI'}
          </Button>

          {loading && (
            <Box sx={{ mt: 3 }}>
              <LinearProgress variant="determinate" value={progress} sx={{ height: 8, borderRadius: 4, mb: 2 }} />
              <Typography variant="body2" color="text.secondary" align="center">
                {progress < 30 && '🔍 Analyzing transaction patterns...'}
                {progress >= 30 && progress < 60 && '🧠 AI is extracting facts and detecting red flags...'}
                {progress >= 60 && progress < 90 && '📝 Generating professional SAR narrative...'}
                {progress >= 90 && '✅ Finalizing comprehensive analysis...'}
              </Typography>
              <Typography variant="caption" color="text.secondary" align="center" display="block" sx={{ mt: 1 }}>
                This typically takes 30-60 seconds. Please wait...
              </Typography>
            </Box>
          )}
        </Box>
      </Paper>

      {/* Info Box */}
      <Paper sx={{ p: 3, mt: 3, bgcolor: 'info.light', border: '2px solid', borderColor: 'info.main' }}>
        <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
          💡 Pro Tip
        </Typography>
        <Typography variant="body2">
          The AI will perform 16-stage comprehensive analysis including fact extraction, red flag detection, 
          typology identification, evidence mapping, quality checks, and regulatory compliance review.
        </Typography>
      </Paper>

      {/* Loading Backdrop */}
      <Backdrop
        sx={{ 
          color: '#fff', 
          zIndex: (theme) => theme.zIndex.drawer + 1,
          flexDirection: 'column',
          gap: 3,
        }}
        open={loading}
      >
        <CircularProgress size={80} thickness={4} />
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>
            Generating SAR Narrative...
          </Typography>
          <Typography variant="body1" sx={{ mb: 3, opacity: 0.9 }}>
            Please wait, do not navigate away
          </Typography>
          <LinearProgress 
            variant="determinate" 
            value={progress} 
            sx={{ 
              width: 400, 
              height: 8, 
              borderRadius: 4,
              bgcolor: 'rgba(255,255,255,0.2)',
              '& .MuiLinearProgress-bar': {
                bgcolor: '#00AEEF'
              }
            }} 
          />
          <Typography variant="body2" sx={{ mt: 2, opacity: 0.8 }}>
            {progress < 30 && '🔍 Analyzing transaction patterns...'}
            {progress >= 30 && progress < 60 && '🧠 Generating AI narrative...'}
            {progress >= 60 && progress < 90 && '✅ Performing quality checks...'}
            {progress >= 90 && '🎉 Finalizing SAR report...'}
          </Typography>
        </Box>
      </Backdrop>
    </Box>
  );
}
