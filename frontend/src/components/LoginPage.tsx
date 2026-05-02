import React, { useState } from 'react';
import { apiClient } from '../services/apiClient';

interface LoginPageProps {
  onLoginSuccess: () => void;
}

interface ValidationErrors {
  mobile?: string;
  password?: string;
  general?: string;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<ValidationErrors>({});

  /**
   * Validate mobile number: 10+ digits, digits-only
   */
  const validateMobile = (value: string): boolean => {
    const digitsOnly = value.replace(/\D/g, '');
    return digitsOnly.length >= 10;
  };

  /**
   * Validate password: 6+ characters
   */
  const validatePassword = (value: string): boolean => {
    return value.length >= 6;
  };

  /**
   * Client-side validation before API call
   */
  const validate = (): boolean => {
    const newErrors: ValidationErrors = {};

    if (!mobile.trim()) {
      newErrors.mobile = 'Mobile number is required';
    } else if (!validateMobile(mobile)) {
      newErrors.mobile = 'Mobile number must be at least 10 digits';
    }

    if (!password) {
      newErrors.password = 'Password is required';
    } else if (!validatePassword(password)) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Handle login form submission
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    setLoading(true);
    setErrors({});

    try {
      const digitsOnly = mobile.replace(/\D/g, '');
      const result = await apiClient.login(digitsOnly, password);

      if (result.error) {
        setErrors({ general: result.error });
        setLoading(false);
        return;
      }

      // Store token and redirect
      if (result.data?.access_token) {
        apiClient.setToken(result.data.access_token);
        setLoading(false);
        onLoginSuccess();
      }
    } catch (error) {
      setErrors({ general: 'An unexpected error occurred' });
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h1>Login</h1>
      <form onSubmit={handleSubmit} className="login-form">
        <div className="form-group">
          <label htmlFor="mobile">Mobile Number</label>
          <input
            id="mobile"
            type="tel"
            value={mobile}
            onChange={(e) => setMobile(e.target.value)}
            placeholder="Enter 10+ digit mobile number"
            disabled={loading}
            className={errors.mobile ? 'input-error' : ''}
          />
          {errors.mobile && <span className="error-message">{errors.mobile}</span>}
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
            className={errors.password ? 'input-error' : ''}
          />
          {errors.password && <span className="error-message">{errors.password}</span>}
        </div>

        {errors.general && (
          <div className="error-box">
            <p>{errors.general}</p>
          </div>
        )}

        <button type="submit" disabled={loading} className="submit-button">
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
    </div>
  );
};
