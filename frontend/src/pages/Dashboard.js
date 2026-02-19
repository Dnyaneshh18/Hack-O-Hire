import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Grid, Paper, Typography, Card, CardContent, CircularProgress, Button, LinearProgress } from '@mui/material';
import { TrendingUp, Description, Warning, CheckCircle, Add, Visibility, Speed } from '@mui/icons-material';
import axiosInstance from '../api/axios';

function StatCard({ title, value, icon, color, subtitle }) {
  return (
    <Card className="hover-lift" sx={{ 
      height: '100%',
      position: 'relative',
      overflow: 'hidden',
      '&::before': {
        content: '""',
        position: 'absolute',
        top: 0,
        right: 0,
        width: '150px',
        height: '150px',
        background: `radial-gradient(circle, ${color}.light 0%, transparent 70%)`,
        opacity: 0.3,
      }
    }}>
      <CardContent sx={{ position: 'relative', zIndex: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box>
            <Typography color="text.secondary" gutterBottom variant="body2" sx={{ fontWeight: 600 }}>
              {title}
            </Typography>
            <Typography variant="h3" sx={{ fontWeight: 800, color: `${color}.main`, mb: 0.5 }}>
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="caption" color="text.secondary">
                {subtitle}
              </Typography>
            )}
          </Box>
          <Box sx={{ 
            bgcolor: `${color}.main`, 
            color: 'white', 
            p: 1.5, 
            borderRadius: 3,
            boxShadow: `0px 4px 12px ${color === 'primary' ? 'rgba(0, 174, 239, 0.3)' : 'rgba(0, 0, 0, 0.15)'}`,
          }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}

function QuickActionCard({ title, description, icon, color, onClick }) {
  return (
    <Card sx={{ 
      height: '100%',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      '&:hover': {
        transform: 'translateY(-8px)',
        boxShadow: '0px 12px 32px rgba(0, 0, 0, 0.15)',
      }
    }}
    onClick={onClick}
    >
      <CardContent>
        <Box sx={{ 
          display: 'inline-flex',
          p: 1.5,
          borderRadius: 2,
          bgcolor: `${color}.light`,
          color: `${color}.main`,
          mb: 2,
        }}>
          {icon}
        </Box>
        <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>
          {title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {description}
        </Typography>
      </CardContent>
    </Card>
  );
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axiosInstance.get('/analytics/dashboard')
      .then(res => setStats(res.data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <CircularProgress size={60} thickness={4} />
        <Typography variant="body1" color="text.secondary" sx={{ mt: 2 }}>
          Loading dashboard...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box className="slide-in-left" sx={{ mb: 4 }}>
        <Typography variant="h3" className="gradient-text" sx={{ fontWeight: 800, mb: 1 }}>
          Welcome Back! 👋
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Here's what's happening with your SAR compliance today
        </Typography>
      </Box>

      {/* Stats Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3} className="fade-in">
          <StatCard 
            title="Total SARs" 
            value={stats?.total_sars || 0} 
            icon={<Description sx={{ fontSize: 28 }} />} 
            color="primary"
            subtitle="All time"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3} className="fade-in" style={{ animationDelay: '0.1s' }}>
          <StatCard 
            title="Recent Activity" 
            value={stats?.recent_sars || 0} 
            icon={<TrendingUp sx={{ fontSize: 28 }} />} 
            color="success"
            subtitle="Last 30 days"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3} className="fade-in" style={{ animationDelay: '0.2s' }}>
          <StatCard 
            title="Approved SARs" 
            value={stats?.approved_sars || 0} 
            icon={<CheckCircle sx={{ fontSize: 28 }} />} 
            color="success"
            subtitle="Ready to file"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3} className="fade-in" style={{ animationDelay: '0.3s' }}>
          <StatCard 
            title="Avg Risk Score" 
            value={stats?.average_risk_score?.toFixed(1) || '0.0'} 
            icon={<Speed sx={{ fontSize: 28 }} />} 
            color="info"
            subtitle="Out of 100"
          />
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Typography variant="h5" className="gradient-text" sx={{ fontWeight: 700, mb: 3 }}>
        Quick Actions
      </Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6} className="fade-in">
          <QuickActionCard
            title="Generate New SAR"
            description="Create a new SAR narrative using AI-powered analysis"
            icon={<Add sx={{ fontSize: 28 }} />}
            color="primary"
            onClick={() => navigate('/generate')}
          />
        </Grid>
        <Grid item xs={12} md={6} className="fade-in" style={{ animationDelay: '0.1s' }}>
          <QuickActionCard
            title="View All SARs"
            description="Browse and manage all submitted SAR reports"
            icon={<Visibility sx={{ fontSize: 28 }} />}
            color="info"
            onClick={() => navigate('/sars')}
          />
        </Grid>
      </Grid>

      {/* System Status */}
      <Paper className="glass fade-in" sx={{ p: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
        <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
          System Status
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Box>
              <Typography variant="body2" sx={{ mb: 1, opacity: 0.9 }}>
                AI Model Status
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#00C389' }} />
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  Operational
                </Typography>
              </Box>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box>
              <Typography variant="body2" sx={{ mb: 1, opacity: 0.9 }}>
                Database Connection
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#00C389' }} />
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  Connected
                </Typography>
              </Box>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box>
              <Typography variant="body2" sx={{ mb: 1, opacity: 0.9 }}>
                Processing Speed
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#00C389' }} />
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  30-60 seconds
                </Typography>
              </Box>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
}
