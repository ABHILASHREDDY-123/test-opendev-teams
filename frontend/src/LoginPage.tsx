import React, { useState } from 'react';
import { login, APIError } from './api';

interface LoginPageProps {
  onLoginSuccess: (token: string) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<{ mobile?: string; password?: string }>({});
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState('');

  const validateForm = (): boolean => {
    const newErrors: typeof errors = {};

    if (!mobile) {
      newErrors.mobile = 'Mobile number is required';
    } else if (!/^\d+$/.test(mobile)) {
      newErrors.mobile = 'Mobile number must contain only digits';
    } else if (mobile.length < 10) {
      newErrors.mobile = 'Mobile number must be at least 10 digits';
    }

    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError('');

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      const token = await login(mobile, password);
      localStorage.setItem('authToken', token);
      onLoginSuccess(token);
    } catch (error) {
      if (error instanceof APIError) {
        setApiError(error.message);
      } else {
        setApiError('An unexpected error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div data-testid="login-page" style={{ maxWidth: '400px', margin: '50px auto', padding: '20px' }}>
      <h1>Login</h1>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="mobile">Mobile Number:</label>
          <input
            id="mobile"
            type="text"
            value={mobile}
            onChange={(e) => {
              setMobile(e.target.value);
              setErrors((prev) => ({ ...prev, mobile: undefined }));
            }}
            placeholder="Enter 10+ digit mobile number"
            disabled={loading}
            data-testid="mobile-input"
          />
          {errors.mobile && (
            <div data-testid="mobile-error" style={{ color: 'red', fontSize: '12px', marginTop: '5px' }}>
              {errors.mobile}
            </div>
          )}
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="password">Password:</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              setErrors((prev) => ({ ...prev, password: undefined }));
            }}
            placeholder="Enter password (6+ characters)"
            disabled={loading}
            data-testid="password-input"
          />
          {errors.password && (
            <div data-testid="password-error" style={{ color: 'red', fontSize: '12px', marginTop: '5px' }}>
              {errors.password}
            </div>
          )}
        </div>

        {apiError && (
          <div data-testid="api-error" style={{ color: 'red', marginBottom: '15px', padding: '10px', backgroundColor: '#ffe0e0', borderRadius: '4px' }}>
            {apiError}
          </div>
        )}

        <button type="submit" disabled={loading} data-testid="login-button">
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
    </div>
  );
};
