import React, { useState } from 'react';
import './LoginForm.css';

interface LoginFormProps {
  onSubmit: (username: string, password: string) => void;
}

const LoginForm: React.FC<LoginFormProps> = ({ onSubmit }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (username && password) {
      setIsLoading(true);
      onSubmit(username, password);
    } else {
      setError('Please fill in all fields');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Username:
        <input type="text" value={username} onChange={(event) => setUsername(event.target.value)} />
      </label>
      <label>
        Password:
        <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
      </label>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <button type="submit">{isLoading ? 'Loading...' : 'Login'}</button>
    </form>
  );
};

export default LoginForm;
