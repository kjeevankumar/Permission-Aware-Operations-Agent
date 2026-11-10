import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  BotMessageSquare,
  Package,
  FileText,
  ShieldCheck,
  History,
  LogOut,
  Building2,
  Lock,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { name: 'Overview', to: '/', icon: LayoutDashboard },
    { name: 'AI Assistant', to: '/assistant', icon: BotMessageSquare, highlight: true },
    { name: 'Inventory', to: '/inventory', icon: Package },
    { name: 'Bills', to: '/bills', icon: FileText },
    { name: 'User Access', to: '/access', icon: ShieldCheck },
    { name: 'Audit Logs', to: '/audit', icon: History },
  ];

  const primaryRole = user?.active_roles?.[0] || 'User';

  return (
    <aside className="w-64 bg-navy-900 text-slate-300 flex flex-col justify-between shrink-0 min-h-screen border-r border-navy-800 shadow-xl">
      <div>
        {/* Brand Header */}
        <div className="h-16 flex items-center px-6 gap-3 border-b border-navy-800/80 bg-navy-900/50">
          <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-lg shadow-md shadow-blue-500/20">
            H
          </div>
          <div>
            <h1 className="font-bold text-white tracking-tight leading-none text-base">
              Hextgen<span className="text-blue-400">AI</span>
            </h1>
            <p className="text-[10px] text-slate-400 font-medium tracking-wider uppercase mt-0.5">
              Operations Agent
            </p>
          </div>
        </div>

        {/* Tenant Hospital Badge */}
        <div className="mx-4 my-4 p-3 rounded-lg bg-navy-800/70 border border-navy-700/60 flex items-center gap-3">
          <div className="p-2 rounded-md bg-navy-700/80 text-blue-400">
            <Building2 className="w-4 h-4" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-[10px] uppercase font-semibold text-slate-400 tracking-wider">
              Hospital Tenant
            </p>
            <p className="text-xs font-semibold text-white truncate">
              {user?.username?.includes('metro')
                ? 'Metro Health General'
                : user?.username?.includes('jude')
                ? 'St. Jude Memorial'
                : 'Hospital Operations'}
            </p>
          </div>
        </div>

        {/* Navigation Menu */}
        <nav className="px-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30 font-semibold'
                      : 'text-slate-300 hover:bg-navy-800 hover:text-white'
                  }`
                }
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span className="flex-1">{item.name}</span>
                {item.highlight && (
                  <span className="text-[10px] bg-blue-500/20 text-blue-300 px-1.5 py-0.5 rounded font-mono font-medium">
                    AI
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* User Profile & Logout Footer */}
      <div className="p-4 border-t border-navy-800/80 bg-navy-900/60">
        <div className="flex items-center gap-3 mb-3 px-1">
          <div className="w-8 h-8 rounded-full bg-slate-700 border border-slate-600 flex items-center justify-center text-white text-xs font-bold uppercase">
            {user?.full_name ? user.full_name.charAt(0) : 'U'}
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-xs font-semibold text-white truncate">
              {user?.full_name || user?.username}
            </p>
            <div className="flex items-center gap-1.5 mt-0.5">
              <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              <p className="text-[10px] text-slate-400 font-medium truncate">
                {primaryRole}
              </p>
            </div>
          </div>
        </div>

        <button
          onClick={handleLogout}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold text-slate-300 bg-navy-800/80 hover:bg-red-500/20 hover:text-red-400 hover:border-red-500/30 border border-navy-700/60 transition-all"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>Sign out</span>
        </button>
      </div>
    </aside>
  );
}
