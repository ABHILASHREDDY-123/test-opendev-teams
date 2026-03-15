import React, { useState } from 'react';

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true);
    // Call API to login
    setTimeout(() => {
      setIsLoading(false);
      if (username === 'admin' && password === 'password') {
        // Login success
      } else {
        setError('Invalid username or password');
      }
    }, 2000);
  };

  return (
    <div>
      <h1>Login Page</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Username:
          <input type="text" value={username} onChange={(event) => setUsername(event.target.value)} />
        </label>
        <br />
        <label>
          Password:
          <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
        </label>
        <br />
        <button type="submit" disabled={isLoading}>Login</button>
        {error && <div style={{ color: 'red' }}>{error}</div>}
        {isLoading && <div>Loading...</div>}
      </form>
    </div>
  );
};

export default LoginPage;
