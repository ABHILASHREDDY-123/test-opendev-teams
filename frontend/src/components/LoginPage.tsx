import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import axios from 'axios';

interface LoginForm {
  username: string;
  password: string;
}

const LoginPage = () => {
  const { register, handleSubmit, errors } = useForm<LoginForm>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const onSubmit = async (data: LoginForm) => {
    setLoading(true);
    try {
      const response = await axios.post('/api/login', data);
      // Handle successful login
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Login Page</h1>
      <form onSubmit={handleSubmit(onSubmit)}>
        <label>Username:</label>
        <input {...register('username')} />
        {errors.username && <div>{errors.username.message}</div>}
        <label>Password:</label>
        <input {...register('password')} />
        {errors.password && <div>{errors.password.message}</div>}
        <button type='submit'>Login</button>
        {loading && <div>Loading...</div>}
        {error && <div>{error}</div>}
      </form>
    </div>
  );
};

export default LoginPage;
