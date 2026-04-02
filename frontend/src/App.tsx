import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './LoginPage';
import ContactsPage from './ContactsPage';
import AddContactForm from './AddContactForm';

const App = () => {
  const token = localStorage.getItem('token');

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={!token ? <LoginPage /> : <Navigate to="/contacts" />} />
        <Route path="/contacts" element={token ? <ContactsPage /> : <Navigate to="/login" />} />
        <Route path="/add-contact" element={token ? <AddContactForm /> : <Navigate to="/login" />} />
        <Route path="*" element={<Navigate to={token ? '/contacts' : '/login'} />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;