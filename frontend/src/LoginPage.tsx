<!-- LoginPage.tsx -->
import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';

const LoginPage = () => {
  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');
  const history = useHistory();

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    // Call API to login
    console.log(`Login with mobile: ${mobile} and password: ${password}`);
    history.push('/contacts');
  };

  return (
    <div>
      <h1>Login Page</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Mobile:
          <input type="text" value={mobile} onChange={(event) => setMobile(event.target.value)} />
        </label>
        <br />
        <label>
          Password:
          <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
        </label>
        <br />
        <button type="submit">Login</button>
      </form>
    </div>
  );
};

export default LoginPage;
