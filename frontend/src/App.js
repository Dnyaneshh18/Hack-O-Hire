import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box, ThemeProvider, CssBaseline } from '@mui/material';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import SARGenerator from './pages/SARGenerator';
import SARList from './pages/SARList';
import SARDetail from './pages/SARDetail';
import AlertData from './pages/AlertData';
import Layout from './components/Layout';
import { AuthProvider, useAuth } from './context/AuthContext';
import theme from './theme';

function PrivateRoute({ children }) {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/"
              element={
                <PrivateRoute>
                  <Layout />
                </PrivateRoute>
              }
            >
              <Route index element={<Dashboard />} />
              <Route path="alerts" element={<AlertData />} />
              <Route path="generate" element={<SARGenerator />} />
              <Route path="sars" element={<SARList />} />
              <Route path="sars/:id" element={<SARDetail />} />
            </Route>
          </Routes>
        </Box>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
