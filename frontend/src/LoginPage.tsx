import React, { useState } from 'react';
import { login, storeToken } from './api';

interface LoginPageProps {
  onLoginSuccess: () => void;
}

/**
 * LoginPage Component
 * Handles user authentication with mobile number and password
 */
export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Validation errors
  const [mobileError, setMobileError] = useState('');
  const [passwordError, setPasswordError] = useState('');

  /**
   * Validate mobile number: digits only, minimum 10 characters
   */
  const validateMobile = (value: string): boolean => {
    if (!value) {
      setMobileError('Mobile number is required');
      return false;
    }
    if (!/^\d+$/.test(value)) {
      setMobileError('Mobile number must contain only digits');
      return false;
    }
    if (value.length < 10) {
      setMobileError('Mobile number must be at least 10 digits');
      return false;
    }
    setMobileError('');
    return true;
  };

  /**
   * Validate password: minimum 6 characters
   */
  const validatePassword = (value: string): boolean => {
    if (!value) {
      setPasswordError('Password is required');
      return false;
    }
    if (value.length < 6) {
      setPasswordError('Password must be at least 6 characters');
      return false;
    }
    setPasswordError('');
    return true;
  };

  /**
   * Handle mobile input change
   */
  const handleMobileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // Allow only digits
    const digitsOnly = value.replace(/\D/g, '');
    setMobile(digitsOnly);
    if (digitsOnly) {
      validateMobile(digitsOnly);
    } else {
      setMobileError('');
    }
  };

  /**
   * Handle password input change
   */
  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setPassword(value);
    if (value) {
      validatePassword(value);
    } else {
      setPasswordError('');
    }
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');

    // Validate inputs
    const mobileValid = validateMobile(mobile);
    const passwordValid = validatePassword(password);

    if (!mobileValid || !passwordValid) {
      return;
    }

    setLoading(true);
    try {
      const response = await login(mobile, password);
      storeToken(response.token);
      onLoginSuccess();
    } catch (err) {
      if (err instanceof Error) {
        if (err.message.includes('401')) {
          setError('Invalid credentials. Please try again.');
        } else {
          setError(err.message || 'Login failed. Please try again.');
        }
      } else {
        setError('Login failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>Contacts App</h1>
        <form onSubmit={handleSubmit} data-testid="login-form">
          <div className="form-group">
            <label htmlFor="mobile">Mobile Number</label>
            <input
              id="mobile"
              type="text"
              placeholder="Enter 10+ digit mobile number"
              value={mobile}
              onChange={handleMobileChange}
              disabled={loading}
              data-testid="mobile-input"
              maxLength={15}
            />
            {mobileError && (
              <span className="error-message" data-testid="mobile-error">
                {mobileError}
              </span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              placeholder="Enter password (6+ characters)"
              value={password}
              onChange={handlePasswordChange}
              disabled={loading}
              data-testid="password-input"
            />
            {passwordError && (
              <span className="error-message" data-testid="password-error">
                {passwordError}
              </span>
            )}
          </div>

          {error && (
            <div className="error-alert" data-testid="login-error">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            data-testid="login-button"
            className="submit-button"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  );
};
