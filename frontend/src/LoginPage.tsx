import React, { useState } from 'react';
import { apiClient } from './api';
import './LoginPage.css';

interface LoginPageProps {
  onLoginSuccess: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [generalError, setGeneralError] = useState('');

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Validate mobile
    if (!mobile) {
      newErrors.mobile = 'Mobile number is required';
    } else if (!/^\d+$/.test(mobile)) {
      newErrors.mobile = 'Mobile number must contain only digits';
    } else if (mobile.length < 10) {
      newErrors.mobile = 'Mobile number must be at least 10 digits';
    }

    // Validate password
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
    setGeneralError('');

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      const token = await apiClient.login(mobile, password);
      localStorage.setItem('jwt_token', token);
      onLoginSuccess();
    } catch (error) {
      setGeneralError(error instanceof Error ? error.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>Contacts Login</h1>
        
        {generalError && <div className="error-message">{generalError}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="mobile">Mobile Number</label>
            <input
              id="mobile"
              type="text"
              value={mobile}
              onChange={(e) => setMobile(e.target.value)}
              placeholder="Enter 10+ digit mobile number"
              disabled={loading}
              aria-invalid={!!errors.mobile}
              aria-describedby={errors.mobile ? 'mobile-error' : undefined}
            />
            {errors.mobile && (
              <span id="mobile-error" className="field-error">
                {errors.mobile}
              </span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password (6+ characters)"
              disabled={loading}
              aria-invalid={!!errors.password}
              aria-describedby={errors.password ? 'password-error' : undefined}
            />
            {errors.password && (
              <span id="password-error" className="field-error">
                {errors.password}
              </span>
            )}
          </div>

          <button type="submit" disabled={loading} className="submit-button">
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  );
};
