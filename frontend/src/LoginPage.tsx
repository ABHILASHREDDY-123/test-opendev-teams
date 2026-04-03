import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from './api';
import { LoginForm } from './types';

const LoginPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<LoginForm>({ mobile: '', password: '' });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const result = await login(formData);
      localStorage.setItem('token', result.access_token);
      navigate('/contacts');
    } catch (err) {
      setError('Invalid credentials');
    } finally {
      setIsLoading(false);
    }
  };

  const validateMobile = (mobile: string) => {
    if (!/^[0-9]{10,}$/.test(mobile)) {
      return 'Invalid mobile number';
    }
    return '';
  };

  const validatePassword = (password: string) => {
    if (password.length < 6) {
      return 'Password must be at least 6 characters';
    }
    return '';
  };

  const mobileError = validateMobile(formData.mobile);
  const passwordError = validatePassword(formData.password);

  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Mobile:</label>
          <input
            type="text"
            value={formData.mobile}
            onChange={(e) => setFormData({ ...formData, mobile: e.target.value })}
          />
          {mobileError && <div style={{ color: 'red' }}>{mobileError}</div>}
        </div>
        <div>
          <label>Password:</label>
          <input
            type="password"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          />
          {passwordError && <div style={{ color: 'red' }}>{passwordError}</div>}
        </div>
        <button type="submit" disabled={isLoading || !!mobileError || !!passwordError}>
          {isLoading ? 'Loading...' : 'Login'}
        </button>
        {error && <div style={{ color: 'red' }}>{error}</div>}
      </form>
    </div>
  );
};

export default LoginPage;