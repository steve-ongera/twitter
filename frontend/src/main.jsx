import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import App from './App'
import { AuthProvider } from './context/AuthContext'
import './styles/main.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
        <Toaster
          position="bottom-center"
          toastOptions={{
            style: {
              background: '#1d9bf0',
              color: '#fff',
              borderRadius: '4px',
              fontWeight: 600,
              fontSize: '0.9rem',
            },
            duration: 3000,
          }}
        />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
)