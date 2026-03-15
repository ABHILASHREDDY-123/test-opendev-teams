// Implement the LoginPage component with proper testing and validation
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import axios from 'axios';

const schema = yup.object().shape({
  email: yup.string().email('Invalid email').required('Email is required'),
  password: yup.string().min(8, 'Password must be at least 8 characters').required('Password is required'),
});

const LoginPage = () => {
  const { register, handleSubmit, errors } = useForm({
    resolver: yupResolver(schema),
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const onSubmit = async (data) => {
    try {
      setIsLoading(true);
      const response = await axios.post('/api/login', data);
      setSuccess(response.data);
    } catch (err) {
      setError(err.response.data);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h1>Login Page</h1>
      <form onSubmit={handleSubmit(onSubmit)}>
        <label>Email:</label>
        <input type='email' {...register('email')} />
        {errors.email && <div>{errors.email.message}</div>}
        <label>Password:</label>
        <input type='password' {...register('password')} />
        {errors.password && <div>{errors.password.message}</div>}
        <button type='submit'>Login</button>
        {isLoading && <div>Loading...</div>}
        {error && <div style={{ color: 'red' }}>{error.message}</div>}
        {success && <div style={{ color: 'green' }}>{success.message}</div>}
      </form>
    </div>
  );
};

export default LoginPage;
