import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Box, Paper, Typography, Button, Chip, Grid, CircularProgress, Alert, Accordion, AccordionSummary, AccordionDetails, Fade, Card, CardContent, Dialog, DialogTitle, DialogContent, DialogActions, TextField, Snackbar, Menu, MenuItem, ListItemIcon, ListItemText } from '@mui/material';
import { ArrowBack, ExpandMore, CheckCircle, Warning, Info, Timeline, Assessment, Security, Flag, TrendingUp, Lightbulb, Lock, Psychology, NavigateNext, Edit, Check, Close, Save, Cancel, PictureAsPdf, Code, TableChart, Email, FileDownload } from '@mui/icons-material';
import axiosInstance from '../api/axios';
import { useAuth } from '../context/AuthContext';
import EmailExportDialog from '../components/EmailExportDialog';

function AnalysisSection({ title, content, icon, color = 'primary', defaultExpanded = false }) {
  if (!content) return null;
  
  return (
    <Accordion defaultExpanded={defaultExpanded} sx={{ 
      borderRadius: 2,
      '&:before': { display: 'none' },
      boxShadow: '0px 2px 12px rgba(0, 0, 0, 0.08)',
      mb: 2,
      border: '1px solid',
      borderColor: 'divider',
      transition: 'all 0.3s ease',
      '&:hover': {
        boxShadow: '0px 4px 20px rgba(0, 0, 0, 0.12)',
      }
    }}>
      <AccordionSummary 
        expandIcon={<ExpandMore />}
        sx={{ 
          '& .MuiAccordionSummary-content': { 
            display: 'flex', 
            alignItems: 'center', 
            gap: 1.5,
            my: 1.5,
          },
          bgcolor: `${color}.50`,
          borderRadius: 2,
          '&:hover': {
            bgcolor: `${color}.100`,
          }
        }}
      >
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          width: 40,
          height: 40,
          borderRadius: 2,
          bgcolor: `${color}.main`,
          color: 'white',
          boxShadow: `0px 4px 12px ${color === 'primary' ? 'rgba(0, 174, 239, 0.3)' : 'rgba(0, 0, 0, 0.15)'}`,
        }}>
          {icon}
        </Box>
        <Typography sx={{ fontWeight: 700, fontSize: '1.05rem', color: 'text.primary' }}>
          {title}
        </Typography>
      </AccordionSummary>
      <AccordionDetails sx={{ p: 3, bgcolor: 'background.paper' }}>
        <Typography sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.9, color: 'text.secondary' }}>
          {content}
        </Typography>
      </AccordionDetails>
    </Accordion>
  );
}

export default function SARDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [sar, setSar] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Edit state
  const [editMode, setEditMode] = useState(false);
  const [editedNarrative, setEditedNarrative] = useState('');
  const [saving, setSaving] = useState(false);
  
  // Approve/Reject state
  const [approveDialogOpen, setApproveDialogOpen] = useState(false);
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false);
  const [comments, setComments] = useState('');
  const [processing, setProcessing] = useState(false);
  
  // Export state
  const [exportAnchorEl, setExportAnchorEl] = useState(null);
  const [exporting, setExporting] = useState(false);
  const [exportType, setExportType] = useState('');
  
  // Email dialog state
  const [emailDialogOpen, setEmailDialogOpen] = useState(false);
  
  // Snackbar
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    loadSAR();
  }, [id]);

  const loadSAR = () => {
    setLoading(true);
    axiosInstance.get(`/sars/${id}`)
      .then(res => {
        setSar(res.data);
        setEditedNarrative(res.data.narrative);
      })
      .catch(err => setError('Failed to load SAR'))
      .finally(() => setLoading(false));
  };

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleEditClick = () => {
    setEditMode(true);
  };

  const handleCancelEdit = () => {
    setEditMode(false);
    setEditedNarrative(sar.narrative);
  };

  const handleSaveEdit = async () => {
    setSaving(true);
    try {
      await axiosInstance.put(`/sars/${id}`, {
        narrative: editedNarrative,
        status: sar.status
      });
      showSnackbar('SAR narrative updated successfully');
      setEditMode(false);
      loadSAR();
    } catch (err) {
      showSnackbar('Failed to update SAR', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleApprove = async () => {
    setProcessing(true);
    try {
      await axiosInstance.post(`/sars/${id}/approve`, null, {
        params: { comments }
      });
      showSnackbar('SAR approved successfully', 'success');
      setApproveDialogOpen(false);
      setComments('');
      loadSAR();
    } catch (err) {
      showSnackbar(err.response?.data?.detail || 'Failed to approve SAR', 'error');
    } finally {
      setProcessing(false);
    }
  };

  const handleReject = async () => {
    setProcessing(true);
    try {
      await axiosInstance.post(`/sars/${id}/reject`, null, {
        params: { comments }
      });
      showSnackbar('SAR rejected', 'warning');
      setRejectDialogOpen(false);
      setComments('');
      loadSAR();
    } catch (err) {
      showSnackbar(err.response?.data?.detail || 'Failed to reject SAR', 'error');
    } finally {
      setProcessing(false);
    }
  };

  const handleExportPDF = async () => {
    setExportAnchorEl(null);
    setExporting(true);
    setExportType('PDF');
    
    try {
      const response = await axiosInstance.get(`/sars/${id}/export/pdf`, {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `SAR_${sar.case_id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      showSnackbar(`Successfully exported ${sar.case_id} as PDF`, 'success');
    } catch (err) {
      showSnackbar('Failed to export PDF', 'error');
    } finally {
      setExporting(false);
      setExportType('');
    }
  };

  const handleExportXML = async () => {
    setExportAnchorEl(null);
    setExporting(true);
    setExportType('XML');
    
    try {
      const response = await axiosInstance.get(`/sars/${id}/export/xml`, {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `SAR_${sar.case_id}.xml`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      showSnackbar(`Successfully exported ${sar.case_id} as XML`, 'success');
    } catch (err) {
      showSnackbar('Failed to export XML', 'error');
    } finally {
      setExporting(false);
      setExportType('');
    }
  };

  const handleExportCSV = async () => {
    setExportAnchorEl(null);
    setExporting(true);
    setExportType('CSV');
    
    try {
      const response = await axiosInstance.get(`/sars/${id}/export/csv`, {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `SAR_${sar.case_id}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      showSnackbar(`Successfully exported ${sar.case_id} as CSV`, 'success');
    } catch (err) {
      showSnackbar('Failed to export CSV', 'error');
    } finally {
      setExporting(false);
      setExportType('');
    }
  };

  const handleEmailExport = () => {
    setExportAnchorEl(null);
    setEmailDialogOpen(true);
  };

  const handleSendEmail = async (recipientEmail, format) => {
    try {
      await axiosInstance.post(`/sars/${id}/export/email`, {
        recipient_email: recipientEmail,
        format: format
      });
      
      showSnackbar(`Successfully sent ${sar.case_id} as ${format.toUpperCase()} to ${recipientEmail}`, 'success');
    } catch (err) {
      throw new Error(err.response?.data?.detail || 'Failed to send email');
    }
  };

  const canEdit = () => {
    if (!user || !sar) return false;
    // Analysts can edit their own SARs, supervisors/admins can edit any
    return user.role === 'admin' || user.role === 'supervisor' || 
           (user.role === 'analyst' && sar.created_by === user.id);
  };

  const canApprove = () => {
    if (!user) return false;
    return user.role === 'admin' || user.role === 'supervisor';
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <CircularProgress size={60} thickness={4} />
        <Typography variant="body1" color="text.secondary" sx={{ mt: 2 }}>
          Loading SAR details...
        </Typography>
      </Box>
    );
  }

  if (error || !sar) {
    return (
      <Box>
        <Alert severity="error" sx={{ borderRadius: 2, mb: 2 }}>
          {error || 'SAR not found'}
        </Alert>
        <Button startIcon={<ArrowBack />} onClick={() => navigate('/sars')}>
          Back to List
        </Button>
      </Box>
    );
  }

  const getRiskColor = (level) => {
    const colors = { low: 'success', medium: 'warning', high: 'error', critical: 'error' };
    return colors[level] || 'default';
  };

  return (
    <Fade in={true} timeout={800}>
      <Box>
        {/* Back Button */}
        <Button 
          startIcon={<ArrowBack />} 
          onClick={() => navigate('/sars')} 
          sx={{ mb: 3, fontWeight: 600 }}
        >
          Back to SAR List
        </Button>
        
        {/* Export Button - Above Blue Panel */}
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
          <Button
            className="pulse hover-lift"
            variant="contained"
            size="large"
            startIcon={exporting ? <CircularProgress size={20} color="inherit" /> : <FileDownload />}
            onClick={(e) => setExportAnchorEl(e.currentTarget)}
            disabled={exporting}
            sx={{
              bgcolor: '#FF6B35',
              color: 'white',
              fontWeight: 700,
              px: 4,
              py: 1.5,
              fontSize: '1rem',
              boxShadow: '0px 4px 12px rgba(255, 107, 53, 0.3)',
              '&:hover': {
                bgcolor: '#E85A2A',
                boxShadow: '0px 6px 16px rgba(255, 107, 53, 0.4)',
              },
              '&.Mui-disabled': {
                bgcolor: 'grey.400',
                color: 'grey.600',
              }
            }}
          >
            {exporting ? `Exporting ${exportType}...` : 'Export SAR'}
          </Button>
          
          {/* Export Menu */}
          <Menu
            anchorEl={exportAnchorEl}
            open={Boolean(exportAnchorEl)}
            onClose={() => setExportAnchorEl(null)}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            PaperProps={{
              sx: {
                mt: 1,
                minWidth: 240,
                boxShadow: '0px 8px 24px rgba(0, 0, 0, 0.15)',
                borderRadius: 2,
              }
            }}
          >
            <MenuItem 
              onClick={handleExportPDF}
              sx={{ 
                py: 1.5, 
                px: 2,
                '&:hover': { bgcolor: 'error.light', color: 'error.dark' }
              }}
            >
              <ListItemIcon>
                <PictureAsPdf fontSize="medium" sx={{ color: '#D32F2F' }} />
              </ListItemIcon>
              <ListItemText 
                primary="Export as PDF"
                secondary="Professional report"
                primaryTypographyProps={{ fontWeight: 600 }}
              />
            </MenuItem>
            <MenuItem 
              onClick={handleExportXML}
              sx={{ 
                py: 1.5, 
                px: 2,
                '&:hover': { bgcolor: 'primary.light', color: 'primary.dark' }
              }}
            >
              <ListItemIcon>
                <Code fontSize="medium" sx={{ color: '#1976D2' }} />
              </ListItemIcon>
              <ListItemText 
                primary="Export as XML"
                secondary="FinCEN filing"
                primaryTypographyProps={{ fontWeight: 600 }}
              />
            </MenuItem>
            <MenuItem 
              onClick={handleExportCSV}
              sx={{ 
                py: 1.5, 
                px: 2,
                '&:hover': { bgcolor: 'success.light', color: 'success.dark' }
              }}
            >
              <ListItemIcon>
                <TableChart fontSize="medium" sx={{ color: '#2E7D32' }} />
              </ListItemIcon>
              <ListItemText 
                primary="Export as CSV"
                secondary="Data analysis"
                primaryTypographyProps={{ fontWeight: 600 }}
              />
            </MenuItem>
            <MenuItem 
              onClick={handleEmailExport}
              sx={{ 
                py: 1.5, 
                px: 2,
                '&:hover': { bgcolor: 'secondary.light', color: 'secondary.dark' }
              }}
            >
              <ListItemIcon>
                <Email fontSize="medium" sx={{ color: '#9C27B0' }} />
              </ListItemIcon>
              <ListItemText 
                primary="Email Export"
                secondary="Send via email"
                primaryTypographyProps={{ fontWeight: 600 }}
              />
            </MenuItem>
          </Menu>
        </Box>
        
        {/* Header Card */}
        <Paper className="slide-in-left" sx={{ 
          p: 4, 
          mb: 3,
          background: 'linear-gradient(135deg, #00AEEF 0%, #0088BD 100%)',
          color: 'white',
        }}>
          <Typography variant="h3" className="gradient-text" sx={{ fontWeight: 800, mb: 2, color: 'white !important', WebkitTextFillColor: 'white !important' }}>
            {sar.case_id}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1.5, flexWrap: 'wrap' }}>
            <Chip 
              label={sar.status.replace('_', ' ')} 
              sx={{ 
                bgcolor: 'white', 
                color: 'primary.main', 
                fontWeight: 700,
                textTransform: 'capitalize',
                fontSize: '0.9rem',
              }} 
            />
            <Chip 
              label={`Risk: ${sar.risk_level}`} 
              color={getRiskColor(sar.risk_level)}
              sx={{ 
                fontWeight: 700,
                textTransform: 'uppercase',
                fontSize: '0.9rem',
              }} 
            />
            <Chip 
              label={`Score: ${sar.risk_score}/100`} 
              sx={{ 
                bgcolor: 'white', 
                color: 'primary.main', 
                fontWeight: 700,
                fontSize: '0.9rem',
              }} 
            />
            <Box 
              sx={{ 
                bgcolor: 'white', 
                color: 'primary.main', 
                fontWeight: 700,
                fontSize: '0.9rem',
                px: 2,
                py: 1,
                borderRadius: '16px',
                display: 'inline-block',
                maxWidth: '100%',
              }} 
            >
              <Typography variant="body2" sx={{ fontWeight: 700, fontSize: '0.9rem', wordWrap: 'break-word' }}>
                Typology: {sar.typology || 'Unknown'}
              </Typography>
            </Box>
          </Box>
        </Paper>

        {/* Customer Info Grid */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={6}>
            <Card className="fade-in hover-lift">
              <CardContent>
                <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                  Customer Name
                </Typography>
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  {sar.customer_name}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card className="fade-in hover-lift" style={{ animationDelay: '0.1s' }}>
              <CardContent>
                <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                  Customer ID
                </Typography>
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  {sar.customer_id}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card className="fade-in hover-lift" style={{ animationDelay: '0.2s' }}>
              <CardContent>
                <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                  Created Date
                </Typography>
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  {new Date(sar.created_at).toLocaleString('en-US', {
                    month: 'long',
                    day: 'numeric',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card className="fade-in hover-lift" style={{ animationDelay: '0.3s' }}>
              <CardContent>
                <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                  Money Laundering Typology
                </Typography>
                <Typography variant="h6" sx={{ fontWeight: 700, textTransform: 'capitalize' }}>
                  {sar.typology || 'Not Specified'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Executive Summary */}
        {sar.executive_summary && (
          <Paper className="scale-in glass" sx={{ p: 4, mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              <Info sx={{ fontSize: 32 }} />
              <Typography variant="h5" sx={{ fontWeight: 700 }}>
                Executive Summary
              </Typography>
            </Box>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.9, fontSize: '1.05rem' }}>
              {sar.executive_summary}
            </Typography>
          </Paper>
        )}

        {/* SAR Narrative */}
        <Paper className="fade-in" sx={{ p: 4, mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h5" className="gradient-text" sx={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
              <Security color="primary" />
              Official SAR Narrative
            </Typography>
            {!editMode && canEdit() && sar.status === 'draft' && (
              <Button 
                variant="outlined" 
                startIcon={<Edit />}
                onClick={handleEditClick}
                size="small"
              >
                Edit Narrative
              </Button>
            )}
          </Box>
          
          {editMode ? (
            <Box>
              <TextField
                fullWidth
                multiline
                rows={12}
                value={editedNarrative}
                onChange={(e) => setEditedNarrative(e.target.value)}
                variant="outlined"
                sx={{ mb: 2 }}
              />
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<Save />}
                  onClick={handleSaveEdit}
                  disabled={saving}
                >
                  {saving ? 'Saving...' : 'Save Changes'}
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Cancel />}
                  onClick={handleCancelEdit}
                  disabled={saving}
                >
                  Cancel
                </Button>
              </Box>
            </Box>
          ) : (
            <Paper variant="outlined" sx={{ 
              p: 3, 
              bgcolor: 'grey.50',
              borderRadius: 2,
              border: '2px solid',
              borderColor: 'primary.light',
            }}>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.9, fontSize: '1.05rem' }}>
                {sar.narrative}
              </Typography>
            </Paper>
          )}
        </Paper>

        {/* Comprehensive Analysis */}
        <Paper className="fade-in" sx={{ p: 4, mb: 3 }}>
          <Typography variant="h5" className="gradient-text" sx={{ fontWeight: 700, mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
            <Assessment color="primary" />
            Comprehensive AI Analysis (16 Stages)
          </Typography>

          <AnalysisSection 
            title="Extracted Facts" 
            content={sar.facts}
            icon={<CheckCircle />}
            color="primary"
            defaultExpanded={true}
          />

          <AnalysisSection 
            title="Red Flags Detected" 
            content={sar.red_flags}
            icon={<Flag />}
            color="error"
          />

          <AnalysisSection 
            title="Event Timeline" 
            content={sar.timeline}
            icon={<Timeline />}
            color="secondary"
          />

          <AnalysisSection 
            title="Typology Confidence Analysis" 
            content={sar.typology_confidence}
            icon={<TrendingUp />}
            color="success"
          />

          <AnalysisSection 
            title="Evidence Mapping" 
            content={sar.evidence_map}
            icon={<NavigateNext />}
            color="info"
          />

          <AnalysisSection 
            title="Quality Assessment" 
            content={sar.quality_check}
            icon={<CheckCircle />}
            color="success"
          />

          <AnalysisSection 
            title="Contradiction Detection" 
            content={sar.contradictions}
            icon={<Warning />}
            color="warning"
          />

          <AnalysisSection 
            title="Regulatory Highlights" 
            content={sar.regulatory_highlights}
            icon={<Security />}
            color="primary"
          />

          <AnalysisSection 
            title="Recommended Next Actions" 
            content={sar.next_actions}
            icon={<NavigateNext />}
            color="info"
          />

          <AnalysisSection 
            title="Suggested Improvements" 
            content={sar.improvements}
            icon={<Lightbulb />}
            color="secondary"
          />

          <AnalysisSection 
            title="PII Leakage Check" 
            content={sar.pii_check}
            icon={<Lock />}
            color="success"
          />

          <AnalysisSection 
            title="Detailed Reasoning Trace" 
            content={sar.reasoning_trace_detailed}
            icon={<Psychology />}
            color="primary"
          />
        </Paper>

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button 
            variant="outlined" 
            size="large"
            onClick={() => navigate('/sars')}
            sx={{ px: 4, py: 1.5 }}
          >
            Back to List
          </Button>
          
          {canApprove() && (sar.status === 'draft' || sar.status === 'pending_review') && (
            <>
              <Button 
                variant="contained" 
                size="large"
                color="success"
                startIcon={<Check />}
                onClick={() => setApproveDialogOpen(true)}
                sx={{ px: 4, py: 1.5 }}
              >
                Approve SAR
              </Button>
              <Button 
                variant="outlined" 
                size="large"
                color="error"
                startIcon={<Close />}
                onClick={() => setRejectDialogOpen(true)}
                sx={{ px: 4, py: 1.5 }}
              >
                Reject SAR
              </Button>
            </>
          )}
        </Box>

        {/* Approve Dialog */}
        <Dialog open={approveDialogOpen} onClose={() => setApproveDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Approve SAR</DialogTitle>
          <DialogContent>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Are you sure you want to approve this SAR? This action will mark it as approved and ready for filing.
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Comments (Optional)"
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              placeholder="Add any approval comments..."
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setApproveDialogOpen(false)} disabled={processing}>
              Cancel
            </Button>
            <Button 
              onClick={handleApprove} 
              variant="contained" 
              color="success"
              disabled={processing}
            >
              {processing ? 'Approving...' : 'Approve'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Reject Dialog */}
        <Dialog open={rejectDialogOpen} onClose={() => setRejectDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Reject SAR</DialogTitle>
          <DialogContent>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Are you sure you want to reject this SAR? Please provide a reason for rejection.
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Rejection Reason (Required)"
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              placeholder="Explain why this SAR is being rejected..."
              required
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setRejectDialogOpen(false)} disabled={processing}>
              Cancel
            </Button>
            <Button 
              onClick={handleReject} 
              variant="contained" 
              color="error"
              disabled={processing || !comments.trim()}
            >
              {processing ? 'Rejecting...' : 'Reject'}
            </Button>
          </DialogActions>
        </Dialog>

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

        {/* Email Export Dialog */}
        <EmailExportDialog
          open={emailDialogOpen}
          onClose={() => setEmailDialogOpen(false)}
          onSend={handleSendEmail}
          caseId={sar?.case_id}
        />
      </Box>
    </Fade>
  );
}
