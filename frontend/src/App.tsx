import React from 'react';
import LoginForm from './components/LoginForm';
import './App.css';

function App() {
 const handleSubmit = (username: string, password: string) => {
 console.log(`Username: ${username}, Password: ${password}`);
 };

 return (
 <div className="App">
 <header className="App-header">
 <LoginForm onSubmit={handleSubmit} />
 </header>
 </div>
 );
}

export default App;
