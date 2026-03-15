import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import axios from 'axios';

const schema = yup.object().shape({
  email: yup.string().email().required(),
  password: yup.string().min(8).required(),
});

const LoginPage = () => {
  const { register, handleSubmit, errors } = useForm({
    resolver: yupResolver(schema),
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const onSubmit = async (data) => {
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
        <label>Email:</label>
        <input {...register('email')} />
        {errors.email && <div>{errors.email.message}</div>}
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
