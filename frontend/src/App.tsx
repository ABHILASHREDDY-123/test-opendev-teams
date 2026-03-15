import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './LoginPage';
import ContactsPage from './ContactsPage';

const App: React.FC = () => {
  const token = localStorage.getItem('token');

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/contacts"
          element={token ? <ContactsPage /> : <Navigate to="/login" replace />}
        />
        <Route path="*" element={<Navigate to={token ? '/contacts' : '/login'} replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;