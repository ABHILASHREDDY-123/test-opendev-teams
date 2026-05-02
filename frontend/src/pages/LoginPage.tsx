import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../api';
import { validateMobile, validatePassword } from '../utils/validation';

const LoginPage: React.FC = () => {
  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');
  const [mobileError, setMobileError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [loginError, setLoginError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleMobileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, ''); // Remove non-digits
    setMobile(value);
    setMobileError('');
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPassword(e.target.value);
    setPasswordError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError('');
    setMobileError('');
    setPasswordError('');

    // Validate inputs
    const mobileValidation = validateMobile(mobile);
    if (!mobileValidation.valid) {
      setMobileError(mobileValidation.error || 'Invalid mobile');
      return;
    }

    const passwordValidation = validatePassword(password);
    if (!passwordValidation.valid) {
      setPasswordError(passwordValidation.error || 'Invalid password');
      return;
    }

    setLoading(true);
    try {
      const token = await authAPI.login(mobile, password);
      localStorage.setItem('jwt_token', token);
      navigate('/contacts');
    } catch (error: any) {
      if (error.response?.status === 401) {
        setLoginError('Invalid mobile or password');
      } else {
        setLoginError('Login failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h1>Login</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="mobile">Mobile Number</label>
          <input
            id="mobile"
            type="text"
            placeholder="Enter 10+ digit mobile number"
            value={mobile}
            onChange={handleMobileChange}
            disabled={loading}
            maxLength={15}
          />
          {mobileError && <span className="error">{mobileError}</span>}
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
          />
          {passwordError && <span className="error">{passwordError}</span>}
        </div>

        {loginError && <div className="error-message">{loginError}</div>}

        <button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
    </div>
  );
};

export default LoginPage;
