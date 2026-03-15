import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const LoginPage = () => {
  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (event) => {
    event.preventDefault();
    // Call API to login
    navigate('/contacts');
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>Mobile:</label>
      <input type='text' value={mobile} onChange={(e) => setMobile(e.target.value)} />
      <label>Password:</label>
      <input type='password' value={password} onChange={(e) => setPassword(e.target.value)} />
      <button type='submit'>Login</button>
    </form>
  );
};

export default LoginPage;
