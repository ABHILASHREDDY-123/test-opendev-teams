import React, { useState, useEffect } from 'react';
import { getToken } from './api';
import { LoginPage } from './LoginPage';
import { ContactsPage } from './ContactsPage';
import './App.css';

/**
 * Main App Component
 * Routes between Login and Contacts pages based on authentication state
 */
export const App: React.FC = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(true);

  /**
   * Check if user is already logged in on mount
   */
  useEffect(() => {
    const token = getToken();
    if (token) {
      setIsLoggedIn(true);
    }
    setLoading(false);
  }, []);

  if (loading) {
    return <div className="app-loading">Loading...</div>;
  }

  return (
    <div className="app">
      {isLoggedIn ? (
        <ContactsPage onLogout={() => setIsLoggedIn(false)} />
      ) : (
        <LoginPage onLoginSuccess={() => setIsLoggedIn(true)} />
      )}
    </div>
  );
};

export default App;
