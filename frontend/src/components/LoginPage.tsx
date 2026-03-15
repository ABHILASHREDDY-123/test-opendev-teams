import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import axios from 'axios';

interface LoginForm {
  email: string;
  password: string;
}

const LoginPage = () => {
  const { register, handleSubmit, errors } = useForm<LoginForm>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const onSubmit = async (data: LoginForm) => {
    setLoading(true);
    try {
      const response = await axios.post('/api/auth/login', data);
      // Handle login success
      console.log(response);
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
        <button type="submit">{loading ? 'Loading...' : 'Login'}</button>
        {error && <div>{error}</div>}
      </form>
    </div>
  );
};

export default LoginPage;
