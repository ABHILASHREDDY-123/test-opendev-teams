import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';

const LoginPage = () => {
  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');
  const history = useHistory();

  const handleSubmit = (event) => {
    event.preventDefault();
    // Call API to login
    history.push('/contacts');
  };

  return (
    <div>
      <h1>Login Page</h1>
      <form onSubmit={handleSubmit}>
        <label>Mobile:</label>
        <input type='text' value={mobile} onChange={(event) => setMobile(event.target.value)} />
        <br />
        <label>Password:</label>
        <input type='password' value={password} onChange={(event) => setPassword(event.target.value)} />
        <br />
        <button type='submit'>Login</button>
      </form>
    </div>
  );
};

export default LoginPage;
