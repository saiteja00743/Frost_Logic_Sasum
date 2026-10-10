import React, { useState } from "react";
import { Shield, History, Settings, FileText, Sun, Moon, LogOut, ChevronDown } from "lucide-react";
import { useTheme } from "../context/ThemeContext";
import { useAuth } from "../context/AuthContext";

export default function Navbar({
  backendStatus,
  onOpenSettings,
  onOpenHistory,
  onReset,
  hasAnalysis,
}) {
  const { theme, toggleTheme } = useTheme();
  const { user, signOut } = useAuth();
  const isLight = theme === "light";
  const [profileOpen, setProfileOpen] = useState(false);

  const handleSignOut = async () => {
    setProfileOpen(false);
    try {
      await signOut();
    } catch (e) {
      console.error("Sign out error:", e);
    }
  };

  const avatar = user?.user_metadata?.avatar_url;
  const displayName = user?.user_metadata?.full_name || user?.email || "User";
  const shortName = displayName.split(" ")[0];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800 bg-slate-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div onClick={onReset} className="flex items-center gap-3 cursor-pointer group">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-sky-500 via-teal-400 to-emerald-400 p-[1px] shadow-lg shadow-teal-500/20 group-hover:shadow-teal-500/40 transition">
            <div className="h-full w-full bg-slate-950 rounded-[11px] flex items-center justify-center">
              <Shield className="w-5 h-5 text-teal-400 group-hover:scale-110 transition-transform" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg text-white tracking-tight">ClauseGuard</span>
              <span className="text-xs font-semibold px-1.5 py-0.5 rounded bg-teal-500/10 text-teal-400 border border-teal-500/20">
                AI
              </span>
            </div>
            <p className="text-[11px] text-slate-400 hidden sm:block">Legal Document &amp; Risk Intelligence</p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Health status badge */}
          <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-900 border border-slate-800 text-slate-300">
            <span
              className={`w-2 h-2 rounded-full ${
                backendStatus === "online"
                  ? "bg-emerald-400 animate-pulse"
                  : backendStatus === "checking"
                  ? "bg-amber-400"
                  : "bg-rose-400"
              }`}
            />
            <span>{backendStatus === "online" ? "Backend Ready" : "Connecting..."}</span>
          </div>

          {hasAnalysis && (
            <button
              onClick={onReset}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
            >
              <FileText className="w-3.5 h-3.5 text-teal-400" />
              <span>New Document</span>
            </button>
          )}

          <button
            onClick={onOpenHistory}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
            title="Analysis History"
          >
            <History className="w-3.5 h-3.5 text-sky-400" />
            <span className="hidden sm:inline">History</span>
          </button>

          <button
            onClick={onOpenSettings}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
            title="LLM &amp; Engine Settings"
          >
            <Settings className="w-3.5 h-3.5 text-amber-400" />
            <span className="hidden sm:inline">AI Settings</span>
          </button>

          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            id="theme-toggle-btn"
            title={isLight ? "Switch to Dark Mode" : "Switch to Light Mode"}
            className="theme-toggle-btn flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all duration-300"
            style={{ minWidth: "76px" }}
          >
            <span
              style={{
                display: "inline-flex",
                transition: "transform 0.3s ease, opacity 0.3s ease",
                transform: isLight ? "rotate(0deg) scale(1)" : "rotate(-20deg) scale(0.9)",
              }}
            >
              {isLight ? (
                <Sun className="w-3.5 h-3.5 text-amber-400" />
              ) : (
                <Moon className="w-3.5 h-3.5 text-sky-300" />
              )}
            </span>
            <span className="hidden sm:inline">{isLight ? "Light" : "Dark"}</span>
          </button>

          {/* ── User Profile Dropdown ───────────────────────── */}
          {user && (
            <div className="relative">
              <button
                id="profile-menu-btn"
                onClick={() => setProfileOpen((p) => !p)}
                className="flex items-center gap-2 px-2 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 border border-slate-700 transition"
                aria-label="User menu"
              >
                {avatar ? (
                  <img
                    src={avatar}
                    alt={displayName}
                    className="w-6 h-6 rounded-full ring-1 ring-teal-500/40"
                    referrerPolicy="no-referrer"
                  />
                ) : (
                  <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-teal-500 to-indigo-500 flex items-center justify-center text-[10px] font-bold text-white">
                    {shortName[0].toUpperCase()}
                  </div>
                )}
                <span className="text-xs text-slate-200 hidden sm:inline max-w-[80px] truncate">
                  {shortName}
                </span>
                <ChevronDown
                  className={`w-3 h-3 text-slate-400 transition-transform ${profileOpen ? "rotate-180" : ""}`}
                />
              </button>

              {profileOpen && (
                <>
                  {/* Backdrop */}
                  <div
                    className="fixed inset-0 z-40"
                    onClick={() => setProfileOpen(false)}
                  />
                  {/* Dropdown */}
                  <div className="absolute right-0 top-full mt-2 w-52 z-50 rounded-xl bg-slate-900 border border-slate-700 shadow-2xl shadow-black/40 overflow-hidden">
                    <div className="px-4 py-3 border-b border-slate-800">
                      {avatar && (
                        <img
                          src={avatar}
                          alt={displayName}
                          className="w-8 h-8 rounded-full mb-2"
                          referrerPolicy="no-referrer"
                        />
                      )}
                      <p className="text-sm font-semibold text-white truncate">{displayName}</p>
                      <p className="text-[11px] text-slate-400 truncate">{user.email}</p>
                    </div>
                    <button
                      id="sign-out-btn"
                      onClick={handleSignOut}
                      className="w-full flex items-center gap-2.5 px-4 py-3 text-xs text-rose-400 hover:bg-rose-500/10 hover:text-rose-300 transition"
                    >
                      <LogOut className="w-3.5 h-3.5" />
                      <span>Sign out</span>
                    </button>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
