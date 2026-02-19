import { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  FormLabel,
  RadioGroup,
  Radio,
  Box,
  Typography,
  CircularProgress,
  Alert
} from '@mui/material';
import { Email, Send, Close } from '@mui/icons-material';

export default function EmailExportDialog({ open, onClose, onSend, caseId }) {
  const [recipientEmail, setRecipientEmail] = useState('');
  const [format, setFormat] = useState('pdf');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSend = async () => {
    // Validate email
    if (!recipientEmail || !recipientEmail.includes('@')) {
      setError('Please enter a valid email address');
      return;
    }

    setError('');
    setLoading(true);

    try {
      await onSend(recipientEmail, format);
      // Reset form
      setRecipientEmail('');
      setFormat('pdf');
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to send email');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setRecipientEmail('');
      setFormat('pdf');
      setError('');
      onClose();
    }
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleClose} 
      maxWidth="sm" 
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2,
          boxShadow: '0px 8px 24px rgba(0, 0, 0, 0.15)'
        }
      }}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: 1,
        bgcolor: 'primary.main',
        color: 'white',
        fontWeight: 700
      }}>
        <Email />
        Email SAR Export
      </DialogTitle>
      
      <DialogContent sx={{ mt: 2 }}>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Send SAR {caseId} export via email from dnyaneshwar.patil24@vit.edu
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <TextField
          fullWidth
          label="Recipient Email Address"
          type="email"
          value={recipientEmail}
          onChange={(e) => setRecipientEmail(e.target.value)}
          placeholder="recipient@example.com"
          required
          disabled={loading}
          sx={{ mb: 3 }}
          autoFocus
        />

        <FormControl component="fieldset" disabled={loading}>
          <FormLabel component="legend" sx={{ fontWeight: 600, mb: 1 }}>
            Export Format
          </FormLabel>
          <RadioGroup
            value={format}
            onChange={(e) => setFormat(e.target.value)}
          >
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center',
                p: 1.5,
                border: '1px solid',
                borderColor: format === 'pdf' ? 'primary.main' : 'divider',
                borderRadius: 1,
                bgcolor: format === 'pdf' ? 'primary.light' : 'transparent',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onClick={() => setFormat('pdf')}
              >
                <Radio value="pdf" />
                <Box>
                  <Typography variant="body1" fontWeight={600}>
                    PDF Format
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Professional report with full formatting
                  </Typography>
                </Box>
              </Box>

              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center',
                p: 1.5,
                border: '1px solid',
                borderColor: format === 'xml' ? 'primary.main' : 'divider',
                borderRadius: 1,
                bgcolor: format === 'xml' ? 'primary.light' : 'transparent',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onClick={() => setFormat('xml')}
              >
                <Radio value="xml" />
                <Box>
                  <Typography variant="body1" fontWeight={600}>
                    XML Format
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    FinCEN-compatible structured data
                  </Typography>
                </Box>
              </Box>

              <Box sx={{ 
                display: 'flex', 
                alignItems: 'center',
                p: 1.5,
                border: '1px solid',
                borderColor: format === 'csv' ? 'primary.main' : 'divider',
                borderRadius: 1,
                bgcolor: format === 'csv' ? 'primary.light' : 'transparent',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onClick={() => setFormat('csv')}
              >
                <Radio value="csv" />
                <Box>
                  <Typography variant="body1" fontWeight={600}>
                    CSV Format
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Spreadsheet-compatible data export
                  </Typography>
                </Box>
              </Box>
            </Box>
          </RadioGroup>
        </FormControl>
      </DialogContent>

      <DialogActions sx={{ p: 2.5, gap: 1 }}>
        <Button 
          onClick={handleClose} 
          disabled={loading}
          startIcon={<Close />}
          variant="outlined"
        >
          Cancel
        </Button>
        <Button 
          onClick={handleSend} 
          variant="contained"
          disabled={loading || !recipientEmail}
          startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <Send />}
          sx={{ minWidth: 120 }}
        >
          {loading ? 'Sending...' : 'Send Email'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
