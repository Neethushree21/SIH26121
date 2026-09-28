import React, { useState, useEffect } from "react";
import LoginPage from "./LoginPage";
import { isAuthenticated, getCurrentUser, clearAuth } from "../../utils/auth";

export default function ProtectedRoute({ children, onUserChange }) {
  const [authenticated, setAuthenticated] = useState(false);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const authStatus = isAuthenticated();
    setAuthenticated(authStatus);
    if (authStatus && onUserChange) {
      onUserChange(getCurrentUser());
    }
    setChecking(false);
  }, []);

  const handleLoginSuccess = (token, user) => {
    setAuthenticated(true);
    if (onUserChange) {
      onUserChange(user);
    }
  };

  const handleLogout = () => {
    clearAuth();
    setAuthenticated(false);
    if (onUserChange) {
      onUserChange(null);
    }
  };

  if (checking) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-amber-400 font-mono text-xs">
        <span className="animate-pulse">Validating Oil India Security Token...</span>
      </div>
    );
  }

  if (!authenticated) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  // Clone children or pass handleLogout down
  if (typeof children === "function") {
    return children({ onLogout: handleLogout, currentUser: getCurrentUser() });
  }

  return children;
}
