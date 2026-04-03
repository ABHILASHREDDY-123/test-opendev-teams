import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './LoginPage';
import ContactsPage from './ContactsPage';

const App = () => {
  const [token, setToken] = useState(localStorage.getItem('token'));

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={token ? <Navigate to="/contacts" /> : <LoginPage />}
        />
        <Route
          path="/contacts"
          element={token ? <ContactsPage /> : <Navigate to="/login" />}
        />
        <Route path="*" element={<Navigate to={token ? '/contacts' : '/login'} />} />
      </Routes>
      {token && (
        <button onClick={handleLogout} style={{ position: 'absolute', top: 10, right: 10 }}>
          Logout
        </button>
      )}
    </BrowserRouter>
  );
};

export default App;