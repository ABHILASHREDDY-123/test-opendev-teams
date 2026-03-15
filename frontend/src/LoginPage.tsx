import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from './api';
import { LoginForm } from './types';

const LoginPage = () => {
  const [formData, setFormData] = useState<LoginForm>({ mobile: '', password: '' });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      await login(formData);
      navigate('/contacts');
    } catch (err) {
      setError('Invalid credentials');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Mobile"
        value={formData.mobile}
        onChange={(e) => setFormData({ ...formData, mobile: e.target.value })}
      />
      <input
        type="password"
        placeholder="Password"
        value={formData.password}
        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
      />
      <button type="submit" disabled={isLoading}>{isLoading ? 'Loading...' : 'Login'}</button>
      {error && <div style={{ color: 'red' }}>{error}</div>}
    </form>
  );
};

export default LoginPage;