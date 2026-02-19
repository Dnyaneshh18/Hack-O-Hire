import { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Box, Drawer, AppBar, Toolbar, List, Typography, Divider, IconButton,
  ListItem, ListItemButton, ListItemIcon, ListItemText, Avatar, Menu, MenuItem,
} from '@mui/material';
import {
  Menu as MenuIcon, Dashboard as DashboardIcon, Description as DescriptionIcon,
  Add as AddIcon, Logout as LogoutIcon, Security, Notifications,
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';

const drawerWidth = 280;

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);

  const handleDrawerToggle = () => setMobileOpen(!mobileOpen);
  const handleMenu = (event) => setAnchorEl(event.currentTarget);
  const handleClose = () => setAnchorEl(null);
  const handleLogout = () => { logout(); navigate('/login'); };

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/', gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
    { text: 'Alert Data', icon: <Notifications />, path: '/alerts', gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
    { text: 'Generate SAR', icon: <AddIcon />, path: '/generate', gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
    { text: 'All SARs', icon: <DescriptionIcon />, path: '/sars', gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
  ];

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', bgcolor: '#FFFFFF' }}>
      {/* Logo Section */}
      <Box sx={{ 
        p: 3, 
        background: 'linear-gradient(135deg, #00AEEF 0%, #0088BD 100%)',
        color: 'white',
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
          <Security sx={{ fontSize: 32 }} />
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 800, lineHeight: 1.2 }}>
              AML Intelligence
            </Typography>
            <Typography variant="caption" sx={{ opacity: 0.9 }}>
              Platform
            </Typography>
          </Box>
        </Box>
      </Box>

      <Divider />

      {/* Navigation Menu */}
      <List sx={{ px: 2, py: 3, flexGrow: 1 }}>
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <ListItem key={item.text} disablePadding sx={{ mb: 1 }}>
              <ListItemButton 
                onClick={() => navigate(item.path)}
                sx={{
                  borderRadius: 2,
                  py: 1.5,
                  background: isActive ? 'linear-gradient(135deg, #00AEEF 0%, #0088BD 100%)' : 'transparent',
                  color: isActive ? 'white' : 'text.primary',
                  '&:hover': {
                    background: isActive 
                      ? 'linear-gradient(135deg, #0088BD 0%, #006A95 100%)'
                      : 'rgba(0, 174, 239, 0.08)',
                  },
                  transition: 'all 0.3s ease',
                  boxShadow: isActive ? '0px 4px 12px rgba(0, 174, 239, 0.3)' : 'none',
                }}
              >
                <ListItemIcon sx={{ 
                  color: isActive ? 'white' : 'primary.main',
                  minWidth: 40,
                }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={item.text} 
                  primaryTypographyProps={{ 
                    fontWeight: isActive ? 700 : 600,
                    fontSize: '0.95rem',
                  }} 
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      {/* User Info Section */}
      <Box sx={{ 
        p: 2, 
        borderTop: '1px solid',
        borderColor: 'divider',
        bgcolor: 'grey.50',
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Avatar sx={{ 
            width: 40, 
            height: 40, 
            background: 'linear-gradient(135deg, #00AEEF 0%, #0088BD 100%)',
            fontWeight: 700,
          }}>
            {user?.full_name?.charAt(0)}
          </Avatar>
          <Box sx={{ flexGrow: 1, minWidth: 0 }}>
            <Typography variant="body2" sx={{ fontWeight: 600, noWrap: true }}>
              {user?.full_name}
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'capitalize' }}>
              {user?.role}
            </Typography>
          </Box>
        </Box>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', width: '100%', minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* App Bar */}
      <AppBar 
        position="fixed" 
        elevation={0}
        sx={{ 
          width: { sm: `calc(100% - ${drawerWidth}px)` }, 
          ml: { sm: `${drawerWidth}px` },
          borderBottom: '1px solid',
          borderColor: 'divider',
          bgcolor: 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(20px)',
        }}
      >
        <Toolbar>
          <IconButton 
            color="primary" 
            edge="start" 
            onClick={handleDrawerToggle} 
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" noWrap sx={{ flexGrow: 1, color: 'white', fontWeight: 600 }}>
            AML Intelligence Platform
          </Typography>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box sx={{ display: { xs: 'none', md: 'block' } }}>
              <Typography variant="body2" sx={{ fontWeight: 600, color: 'white' }}>
                {user?.full_name}
              </Typography>
              <Typography variant="caption" sx={{ textTransform: 'capitalize', color: 'white' }}>
                {user?.role}
              </Typography>
            </Box>

            <IconButton onClick={handleMenu}>
              <Avatar sx={{ 
                width: 36, 
                height: 36, 
                background: 'linear-gradient(135deg, #00AEEF 0%, #0088BD 100%)',
                fontWeight: 700,
              }}>
                {user?.full_name?.charAt(0)}
              </Avatar>
            </IconButton>
          </Box>

          <Menu 
            anchorEl={anchorEl} 
            open={Boolean(anchorEl)} 
            onClose={handleClose}
            PaperProps={{
              sx: { borderRadius: 2, minWidth: 200, mt: 1 }
            }}
          >
            <MenuItem disabled>
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {user?.email}
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'capitalize' }}>
                  {user?.role}
                </Typography>
              </Box>
            </MenuItem>
            <Divider sx={{ my: 1 }} />
            <MenuItem onClick={handleLogout} sx={{ color: 'error.main' }}>
              <ListItemIcon>
                <LogoutIcon fontSize="small" color="error" />
              </ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Drawer */}
      <Box component="nav" sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}>
        <Drawer 
          variant="temporary" 
          open={mobileOpen} 
          onClose={handleDrawerToggle} 
          ModalProps={{ keepMounted: true }}
          sx={{ 
            display: { xs: 'block', sm: 'none' }, 
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth, border: 'none' } 
          }}
        >
          {drawer}
        </Drawer>
        <Drawer 
          variant="permanent" 
          sx={{ 
            display: { xs: 'none', sm: 'block' }, 
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth, border: 'none' } 
          }} 
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main Content */}
      <Box 
        component="main" 
        sx={{ 
          flexGrow: 1, 
          p: 4, 
          width: { sm: `calc(100% - ${drawerWidth}px)` }, 
          mt: 8,
          minHeight: 'calc(100vh - 64px)',
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
}
