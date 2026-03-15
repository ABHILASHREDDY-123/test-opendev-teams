import React, { useState } from 'react';
import { login } from '../api';

const LoginPage = () => {
 const [mobile, setMobile] = useState('');
 const [password, setPassword] = useState('');
 const [error, setError] = useState(null);
 const [isLoading, setIsLoading] = useState(false);

 const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
 event.preventDefault();
 setIsLoading(true);
 try {
 const data = await login(mobile, password);
 // Handle login success
 } catch (error) {
 setError(error.message);
 }
 finally {
 setIsLoading(false);
 }
 };

 return (
 <form onSubmit={handleSubmit}>
 <label>
 Mobile:
 <input type="text" value={mobile} onChange={(event) => setMobile(event.target.value)} />
 </label>
 <label>
 Password:
 <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
 </label>
 <button type="submit" disabled={isLoading}>Login</button>
 {error && <div style={{ color: 'red' }}>{error}</div>}
 {isLoading && <div>Loading...</div>}
 </form>
 );
};

export default LoginPage;
