import React, { useState } from "react";
import {
  Flame,
  Lock,
  Mail,
  User,
  ShieldCheck,
  Compass,
  ArrowRight,
  AlertCircle,
  Eye,
  EyeOff,
  CheckCircle2,
  HardDrive
} from "lucide-react";
import { loginUser, registerUser } from "../../utils/api";
import { setToken, setCurrentUser } from "../../utils/auth";

export default function LoginPage({ onLoginSuccess }) {
  const [activeTab, setActiveTab] = useState("login"); // "login" or "register"
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  // Login form state
  const [loginEmail, setLoginEmail] = useState("engineer@oilindia.in");
  const [loginPassword, setLoginPassword] = useState("OilIndia@2026");

  // Registration form state
  const [regFullName, setRegFullName] = useState("");
  const [regEmail, setRegEmail] = useState("");
  const [regPassword, setRegPassword] = useState("");
  const [regRole, setRegRole] = useState("Drilling Engineer");
  const [regField, setRegField] = useState("Nahorkatiya Field");

  // Quick fill demo credentials
  const handleQuickFill = (email, pwd) => {
    setLoginEmail(email);
    setLoginPassword(pwd);
    setErrorMsg("");
  };

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    if (!loginEmail.trim() || !loginPassword.trim()) {
      setErrorMsg("Please enter both email and password.");
      return;
    }

    setLoading(true);
    setErrorMsg("");

    try {
      const data = await loginUser(loginEmail, loginPassword);
      setToken(data.access_token);
      setCurrentUser(data.user);
      if (onLoginSuccess) {
        onLoginSuccess(data.access_token, data.user);
      }
    } catch (err) {
      setErrorMsg(err.message || "Invalid email or password.");
    } finally {
      setLoading(false);
    }
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    if (!regEmail.trim() || !regPassword.trim() || !regFullName.trim()) {
      setErrorMsg("Please fill in all required fields.");
      return;
    }
    if (regPassword.length < 6) {
      setErrorMsg("Password must be at least 6 characters.");
      return;
    }

    setLoading(true);
    setErrorMsg("");

    try {
      const data = await registerUser({
        email: regEmail,
        password: regPassword,
        full_name: regFullName,
        role: regRole,
        asset_field: regField
      });
      setToken(data.access_token);
      setCurrentUser(data.user);
      setSuccessMsg("Account successfully registered! Loading dashboard...");
      setTimeout(() => {
        if (onLoginSuccess) {
          onLoginSuccess(data.access_token, data.user);
        }
      }, 500);
    } catch (err) {
      setErrorMsg(err.message || "Registration failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-center items-center p-4 selection:bg-amber-500 selection:text-black">
      {/* Background Decorative Gradient Orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-amber-500/5 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-sky-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* Main Login Container Card */}
      <div className="relative w-full max-w-md bg-slate-900/90 border border-slate-800 rounded-2xl shadow-2xl p-6 sm:p-8 backdrop-blur-md z-10">
        
        {/* Header Branding */}
        <div className="flex flex-col items-center text-center mb-6">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500 to-amber-700 flex items-center justify-center shadow-lg shadow-amber-500/20 mb-3">
            <Flame className="w-7 h-7 text-black font-black" />
          </div>
          <div className="flex items-center space-x-2 mb-1">
            <span className="text-[10px] uppercase font-extrabold tracking-wider px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
              OIL INDIA LIMITED
            </span>
            <span className="text-[10px] font-mono text-slate-400">SIH26121</span>
          </div>
          <h1 className="text-xl font-bold tracking-tight text-white">
            NWIS Control Room
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-xs font-mono">
            Nearby Wells Intelligence & Decision Support System
          </p>
        </div>

        {/* Tab Switcher: Sign In vs Request Access */}
        <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800 mb-5">
          <button
            type="button"
            onClick={() => {
              setActiveTab("login");
              setErrorMsg("");
            }}
            className={`flex-1 py-2 rounded-lg text-xs font-bold transition flex items-center justify-center space-x-1.5 ${
              activeTab === "login"
                ? "bg-amber-500 text-black shadow-md shadow-amber-500/20"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <Lock className="w-3.5 h-3.5" />
            <span>Sign In</span>
          </button>
          <button
            type="button"
            onClick={() => {
              setActiveTab("register");
              setErrorMsg("");
            }}
            className={`flex-1 py-2 rounded-lg text-xs font-bold transition flex items-center justify-center space-x-1.5 ${
              activeTab === "register"
                ? "bg-amber-500 text-black shadow-md shadow-amber-500/20"
                : "text-slate-400 hover:text-white"
            }`}
          >
            <User className="w-3.5 h-3.5" />
            <span>Request Access</span>
          </button>
        </div>

        {/* Error / Success Notifications */}
        {errorMsg && (
          <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center space-x-2 text-xs text-red-300">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}
        {successMsg && (
          <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center space-x-2 text-xs text-emerald-300">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{successMsg}</span>
          </div>
        )}

        {/* TAB 1: SIGN IN FORM */}
        {activeTab === "login" ? (
          <form onSubmit={handleLoginSubmit} className="space-y-4">
            <div>
              <label className="block text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                Work Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
                <input
                  type="email"
                  required
                  placeholder="engineer@oilindia.in"
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700/80 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  placeholder="••••••••••••"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700/80 rounded-xl pl-9 pr-10 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-2.5 text-slate-500 hover:text-slate-300"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 px-4 rounded-xl bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-black font-bold text-xs flex items-center justify-center space-x-2 transition shadow-lg shadow-amber-500/20"
            >
              {loading ? (
                <span>Authenticating with PostGIS & JWT...</span>
              ) : (
                <>
                  <span>Authenticate & Enter Control Room</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>

            {/* Quick-Fill Demo Accounts */}
            <div className="pt-4 border-t border-slate-800">
              <span className="block text-[10px] font-mono text-slate-400 uppercase tracking-wider mb-2">
                Quick Demo Credentials (One-Click):
              </span>
              <div className="grid grid-cols-2 gap-2 text-[10px]">
                <button
                  type="button"
                  onClick={() => handleQuickFill("engineer@oilindia.in", "OilIndia@2026")}
                  className="p-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 border border-slate-800 text-amber-400/90 text-left font-mono truncate transition"
                >
                  Drilling Engineer
                </button>
                <button
                  type="button"
                  onClick={() => handleQuickFill("superintendent@oilindia.in", "OilIndia@2026")}
                  className="p-1.5 rounded-lg bg-slate-950 hover:bg-slate-800 border border-slate-800 text-sky-400/90 text-left font-mono truncate transition"
                >
                  Superintendent
                </button>
              </div>
            </div>
          </form>
        ) : (
          /* TAB 2: REQUEST ACCESS / REGISTRATION FORM */
          <form onSubmit={handleRegisterSubmit} className="space-y-3.5">
            <div>
              <label className="block text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1">
                Full Name & Title
              </label>
              <div className="relative">
                <User className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
                <input
                  type="text"
                  required
                  placeholder="Er. Pranjal Baruah"
                  value={regFullName}
                  onChange={(e) => setRegFullName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700/80 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1">
                Oil India Work Email
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
                <input
                  type="email"
                  required
                  placeholder="pbaruah@oilindia.in"
                  value={regEmail}
                  onChange={(e) => setRegEmail(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700/80 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-[10px] font-semibold uppercase tracking-wider text-slate-400 mb-1">
                  Operational Role
                </label>
                <select
                  value={regRole}
                  onChange={(e) => setRegRole(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-2.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                >
                  <option value="Drilling Engineer">Drilling Engineer</option>
                  <option value="Drilling Superintendent">Superintendent</option>
                  <option value="Wellsite Geologist">Wellsite Geologist</option>
                  <option value="Operations Analyst">Operations Analyst</option>
                </select>
              </div>

              <div>
                <label className="block text-[10px] font-semibold uppercase tracking-wider text-slate-400 mb-1">
                  Assigned Asset
                </label>
                <select
                  value={regField}
                  onChange={(e) => setRegField(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-2.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                >
                  <option value="Nahorkatiya Field">Nahorkatiya Field</option>
                  <option value="Baghjan Field">Baghjan Field</option>
                  <option value="Moran Field">Moran Field</option>
                  <option value="Jorajan Field">Jorajan Field</option>
                  <option value="Assam Shelf Asset">Assam Shelf Asset</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1">
                Password (min 6 chars)
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  placeholder="••••••••••••"
                  value={regPassword}
                  onChange={(e) => setRegPassword(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700/80 rounded-xl pl-9 pr-10 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-amber-500"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-2.5 text-slate-500 hover:text-slate-300"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 px-4 rounded-xl bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-black font-bold text-xs flex items-center justify-center space-x-2 transition shadow-lg shadow-amber-500/20 mt-2"
            >
              {loading ? (
                <span>Registering Account...</span>
              ) : (
                <>
                  <span>Create Account & Enter Dashboard</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        )}

        {/* Security & Regulatory Notice */}
        <div className="mt-5 text-center text-[10px] text-slate-500 font-mono flex items-center justify-center space-x-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
          <span>Secured by JWT & PostGIS Spatial Isolation</span>
        </div>

      </div>
    </div>
  );
}
