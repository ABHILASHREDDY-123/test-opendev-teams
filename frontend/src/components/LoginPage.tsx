import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import axios from 'axios';

interface LoginForm {
  username: string;
  password: string;
}

const LoginPage = () => {
  const { register, handleSubmit, errors } = useForm<LoginForm>();
  const [loginError, setLoginError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const onSubmit = async (data: LoginForm) => {
    try {
      setIsLoading(true);
      const response = await axios.post('/api/login', data);
      // Handle successful login
      console.log(response);
    } catch (error) {
      setLoginError('Invalid username or password');
    } finally {
      setIsLoading(false);
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
        <input type='password' {...register('password')} />
        {errors.password && <div>{errors.password.message}</div>}
        <button type='submit' disabled={isLoading}>Login</button>
        {loginError && <div style={{ color: 'red' }}>{loginError}</div>}
      </form>
    </div>
  );
};

export default LoginPage;
