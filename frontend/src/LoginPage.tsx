import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const LoginPage = () => {
  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const response = await axios.post('/api/auth/login', { mobile, password });
      navigate('/contacts');
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Mobile:
        <input type='text' value={mobile} onChange={(event) => setMobile(event.target.value)} />
      </label>
      <label>
        Password:
        <input type='password' value={password} onChange={(event) => setPassword(event.target.value)} />
      </label>
      <button type='submit'>Login</button>
    </form>
  );
};

export default LoginPage;
