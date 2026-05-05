import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const validateMobile = (value: string): boolean => {
    const digitsOnly = value.replace(/\D/g, '');
    return digitsOnly.length >= 10;
  };

  const validatePassword = (value: string): boolean => {
    return value.length >= 6;
  };

  const handleMobileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '');
    setMobile(value);
    setError('');
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPassword(e.target.value);
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!validateMobile(mobile)) {
      setError('Mobile number must be at least 10 digits');
      return;
    }

    if (!validatePassword(password)) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    try {
      const response = await apiService.login({ mobile, password });
      localStorage.setItem('token', response.access_token);
      navigate('/contacts');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const isMobileValid = mobile.length >= 10;
  const isPasswordValid = password.length >= 6;
  const isFormValid = isMobileValid && isPasswordValid;

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>Login</h1>
        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.formGroup}>
            <label htmlFor="mobile" style={styles.label}>
              Mobile Number
            </label>
            <input
              id="mobile"
              type="text"
              value={mobile}
              onChange={handleMobileChange}
              placeholder="Enter 10+ digit mobile number"
              style={styles.input}
              disabled={loading}
              data-testid="mobile-input"
            />
            {mobile && !isMobileValid && (
              <p style={styles.errorText} data-testid="mobile-error">
                Mobile number must be at least 10 digits
              </p>
            )}
          </div>

          <div style={styles.formGroup}>
            <label htmlFor="password" style={styles.label}>
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={handlePasswordChange}
              placeholder="Enter password (min 6 chars)"
              style={styles.input}
              disabled={loading}
              data-testid="password-input"
            />
            {password && !isPasswordValid && (
              <p style={styles.errorText} data-testid="password-error">
                Password must be at least 6 characters
              </p>
            )}
          </div>

          {error && (
            <div style={styles.errorBox} data-testid="error-message">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={!isFormValid || loading}
            style={{
              ...styles.button,
              ...((!isFormValid || loading) && styles.buttonDisabled)
            }}
            data-testid="submit-button"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
  },
  card: {
    backgroundColor: 'white',
    padding: '40px',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
    width: '100%',
    maxWidth: '400px',
  },
  title: {
    textAlign: 'center',
    marginBottom: '30px',
    color: '#333',
    fontSize: '24px',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  label: {
    fontWeight: '600',
    color: '#333',
    fontSize: '14px',
  },
  input: {
    padding: '10px 12px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '14px',
    fontFamily: 'inherit',
  },
  errorText: {
    color: '#d32f2f',
    fontSize: '12px',
    margin: '0',
  },
  errorBox: {
    backgroundColor: '#ffebee',
    color: '#d32f2f',
    padding: '12px',
    borderRadius: '4px',
    fontSize: '14px',
  },
  button: {
    padding: '12px',
    backgroundColor: '#1976d2',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
    marginTop: '10px',
  },
  buttonDisabled: {
    backgroundColor: '#ccc',
    cursor: 'not-allowed',
  },
};
