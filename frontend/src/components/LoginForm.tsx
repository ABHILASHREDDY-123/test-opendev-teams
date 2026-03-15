import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import axios from 'axios';

const schema = yup.object().shape({
  email: yup.string().email().required(),
  password: yup.string().required(),
});

const LoginForm = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: yupResolver(schema),
  });

  const onSubmit = async (data) => {
    try {
      setLoading(true);
      const response = await axios.post('/api/login', data);
      // Handle login success
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <label>
        Email:
        <input {...register('email')} />
        {errors.email && <div>{errors.email.message}</div>}
      </label>
      <label>
        Password:
        <input {...register('password')} />
        {errors.password && <div>{errors.password.message}</div>}
      </label>
      <button type="submit" disabled={loading}>Login</button>
      {loading && <div>Loading...</div>}
      {error && <div>{error}</div>}
    </form>
  );
};

export default LoginForm;
