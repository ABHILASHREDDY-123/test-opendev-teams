import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './LoginPage';
import ContactsPage from './ContactsPage';
import AddContactForm from './AddContactForm';

const App = () => {
  const [token, setToken] = React.useState(localStorage.getItem('token'));

  const handleLogin = (newToken: string) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={<LoginPage onLogin={handleLogin} />}
        />
        <Route
          path="/contacts"
          element={token ? <ContactsPage /> : <Navigate to="/login" />}
        />
        <Route
          path="/add-contact"
          element={token ? <AddContactForm /> : <Navigate to="/login" />}
        />
        <Route path="*" element={<Navigate to={token ? '/contacts' : '/login'} />} />
      </Routes>
      {token && <button onClick={handleLogout}>Logout</button>}
    </BrowserRouter>
  );
};

export default App;