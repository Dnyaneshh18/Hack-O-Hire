import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Box, Paper, TextField, Button, Typography, Alert, CircularProgress, InputAdornment, IconButton, Grid } from '@mui/material';
import { Security, Visibility, VisibilityOff, LockOutlined, TrendingUp, Assessment, Shield, Speed } from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Grid container sx={{ minHeight: '100vh', width: '100%' }}>
      {/* Left Side - Login Form */}
      <Grid item xs={12} md={6} sx={{ 
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'white',
        p: { xs: 3, md: 5 },
      }}>
        <Box className="scale-in" sx={{ maxWidth: 450, width: '100%' }}>
          {/* Logo and Header */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Box sx={{ 
              display: 'inline-flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              width: 80, 
              height: 80, 
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #00AEEF 0%, #0088BD 100%)',
              mb: 2,
              boxShadow: '0px 8px 24px rgba(0, 174, 239, 0.3)',
            }}>
              <Security sx={{ fontSize: 40, color: 'white' }} />
            </Box>
            <Typography variant="h3" sx={{ 
              fontWeight: 800, 
              background: 'linear-gradient(135deg, #00AEEF 0%, #0088BD 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              mb: 1,
            }}>
              AML Intelligence
            </Typography>
            <Typography variant="h5" sx={{ fontWeight: 600, color: 'text.primary', mb: 0.5 }}>
              Platform
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
              <LockOutlined fontSize="small" /> Intelligent SAR Generation
            </Typography>
          </Box>

          {error && <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>{error}</Alert>}
          
          <Box component="form" onSubmit={handleSubmit}>
            <TextField 
              margin="normal" 
              required 
              fullWidth 
              label="Email Address" 
              autoFocus
              value={email} 
              onChange={(e) => setEmail(e.target.value)}
              sx={{ mb: 2 }}
            />
            <TextField 
              margin="normal" 
              required 
              fullWidth 
              label="Password" 
              type={showPassword ? 'text' : 'password'}
              value={password} 
              onChange={(e) => setPassword(e.target.value)}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={() => setShowPassword(!showPassword)} edge="end">
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              sx={{ mb: 3 }}
            />
            <Button 
              type="submit" 
              fullWidth 
              variant="contained" 
              size="large"
              className="hover-lift pulse"
              disabled={loading}
              sx={{ 
                py: 1.8, 
                fontSize: '1.1rem',
                fontWeight: 700,
                boxShadow: '0px 8px 24px rgba(0, 174, 239, 0.3)',
              }}
            >
              {loading ? <CircularProgress size={26} color="inherit" /> : 'Sign In Securely'}
            </Button>
          </Box>

          {/* Demo Credentials */}
          <Box sx={{ 
            mt: 4, 
            p: 2.5, 
            bgcolor: 'grey.50', 
            borderRadius: 2,
            border: '1px solid',
            borderColor: 'grey.200',
          }}>
            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, display: 'block', mb: 1 }}>
              Demo Credentials:
            </Typography>
            <Typography variant="body2" sx={{ fontFamily: 'monospace', color: 'primary.main', fontWeight: 600 }}>
              admin@barclays.com
            </Typography>
            <Typography variant="body2" sx={{ fontFamily: 'monospace', color: 'primary.main', fontWeight: 600 }}>
              Admin@123
            </Typography>
          </Box>

          {/* Footer */}
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', textAlign: 'center', mt: 3 }}>
            © 2024 AML Intelligence Platform. All rights reserved. | Secured by AI
          </Typography>
        </Box>
      </Grid>

      {/* Right Side - Feature Showcase */}
      <Grid item xs={12} md={6} sx={{ 
        background: 'linear-gradient(135deg, #00AEEF 0%, #0088BD 100%)',
        p: { xs: 4, md: 6 },
        display: { xs: 'none', md: 'flex' },
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        color: 'white',
      }}>
        <Box sx={{ maxWidth: 450, width: '100%' }}>
              <Box className="slide-in-left" sx={{ mb: 4 }}>
                <Typography variant="h4" sx={{ fontWeight: 800, mb: 2 }}>
                  AI-Powered SAR Generation
                </Typography>
                <Typography variant="body1" sx={{ opacity: 0.9, mb: 4 }}>
                  Transform suspicious activity reporting from hours to seconds with complete transparency and regulatory compliance.
                </Typography>
              </Box>

              {/* Feature Cards */}
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                <Box className="fade-in glass hover-lift" sx={{ 
                  display: 'flex', 
                  gap: 2, 
                  p: 3, 
                  bgcolor: 'rgba(255,255,255,0.1)', 
                  borderRadius: 2,
                  backdropFilter: 'blur(10px)',
                }}>
                  <Speed sx={{ fontSize: 40 }} />
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 700, mb: 0.5 }}>
                      99% Faster
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>
                      Generate SARs in 30-60 seconds instead of 5-6 hours
                    </Typography>
                  </Box>
                </Box>

                <Box className="fade-in glass hover-lift" style={{ animationDelay: '0.1s' }} sx={{ 
                  display: 'flex', 
                  gap: 2, 
                  p: 3, 
                  bgcolor: 'rgba(255,255,255,0.1)', 
                  borderRadius: 2,
                  backdropFilter: 'blur(10px)',
                }}>
                  <Assessment sx={{ fontSize: 40 }} />
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 700, mb: 0.5 }}>
                      16-Stage Analysis
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>
                      Complete audit trail with facts, red flags, and evidence mapping
                    </Typography>
                  </Box>
                </Box>

                <Box className="fade-in glass hover-lift" style={{ animationDelay: '0.2s' }} sx={{ 
                  display: 'flex', 
                  gap: 2, 
                  p: 3, 
                  bgcolor: 'rgba(255,255,255,0.1)', 
                  borderRadius: 2,
                  backdropFilter: 'blur(10px)',
                }}>
                  <Shield sx={{ fontSize: 40 }} />
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 700, mb: 0.5 }}>
                      Regulator-Ready
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>
                      FinCEN-compliant narratives with complete transparency
                    </Typography>
                  </Box>
                </Box>

                <Box className="fade-in glass hover-lift" style={{ animationDelay: '0.3s' }} sx={{ 
                  display: 'flex', 
                  gap: 2, 
                  p: 3, 
                  bgcolor: 'rgba(255,255,255,0.1)', 
                  borderRadius: 2,
                  backdropFilter: 'blur(10px)',
                }}>
                  <TrendingUp sx={{ fontSize: 40 }} />
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 700, mb: 0.5 }}>
                      $2.75M Savings
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>
                      Annual cost reduction with 50x capacity increase
                    </Typography>
                  </Box>
                </Box>
              </Box>
        </Box>
      </Grid>
    </Grid>
  );
}
