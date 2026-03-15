import React, { useState } from 'react';
import { login } from './api';
import { useNavigate } from 'react-router-dom';

interface Props {}

const LoginPage: React.FC<Props> = () => {
  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const data = await login(mobile, password);
      localStorage.setItem('token', data.token);
      navigate('/contacts');
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={mobile}
        onChange={(e) => setMobile(e.target.value)}
        placeholder="Mobile number"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <button type="submit" disabled={loading}>{loading ? 'Loading...' : 'Login'}</button>
    </form>
  );
};

export default LoginPage;