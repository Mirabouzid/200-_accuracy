import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Shield, Database, Home, BarChart3, Info, Search } from 'lucide-react';
import Chatbot from './Chatbot';

const Layout = ({ children }) => {
    const location = useLocation();

    const isActive = (path) => location.pathname === path;

    const navItems = [
        { path: '/', icon: Home, label: 'Home' },
        { path: '/analysis', icon: Search, label: 'Analysis' },
        { path: '/dashboard', icon: BarChart3, label: 'Dashboard' },
        { path: '/about', icon: Info, label: 'About' },
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white">
            <header className="border-b border-purple-500/20 bg-slate-900/80 backdrop-blur-xl sticky top-0 z-50">
                <div className="container mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <Link to="/" className="flex items-center gap-4 hover:opacity-80 transition-opacity">
                            <div className="relative">
                                <Shield className="w-10 h-10 text-purple-400 animate-glow" />
                                <div className="absolute inset-0 bg-purple-500 blur-xl opacity-30"></div>
                            </div>
                            <div>
                                <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
                                    BlockStat Pro
                                </h1>
                                <p className="text-xs text-gray-400 tracking-wide">Advanced Forensic Graph Intelligence</p>
                            </div>
                        </Link>

                        <nav className="hidden md:flex items-center gap-2">
                            {navItems.map((item) => {
                                const Icon = item.icon;
                                return (
                                    <Link
                                        key={item.path}
                                        to={item.path}
                                        className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-all ${isActive(item.path)
                                            ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                                            : 'text-gray-400 hover:text-white hover:bg-slate-800/50'
                                            }`}
                                    >
                                        <Icon className="w-4 h-4" />
                                        <span className="font-medium">{item.label}</span>
                                    </Link>
                                );
                            })}
                        </nav>

                        <div className="flex items-center gap-6">
                            <div className="hidden lg:flex items-center gap-2 text-sm">
                                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                                <span className="text-gray-400">System Online</span>
                            </div>
                            <div className="hidden md:flex items-center gap-2 px-4 py-2 bg-purple-500/10 rounded-lg border border-purple-500/20">
                                <Database className="w-4 h-4 text-purple-400" />
                                <span className="text-sm font-semibold">Live Analysis</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Mobile Navigation */}
                <div className="md:hidden border-t border-purple-500/20">
                    <div className="container mx-auto px-6 py-3">
                        <nav className="flex items-center justify-around">
                            {navItems.map((item) => {
                                const Icon = item.icon;
                                return (
                                    <Link
                                        key={item.path}
                                        to={item.path}
                                        className={`flex flex-col items-center gap-1 px-3 py-2 rounded-lg transition-all ${isActive(item.path)
                                            ? 'text-purple-400'
                                            : 'text-gray-400'
                                            }`}
                                    >
                                        <Icon className="w-5 h-5" />
                                        <span className="text-xs font-medium">{item.label}</span>
                                    </Link>
                                );
                            })}
                        </nav>
                    </div>
                </div>
            </header>

    
            <main className="min-h-[calc(100vh-200px)]">
                {children}
            </main>

            {/* Footer */}
            <footer className="border-t border-purple-500/20 bg-slate-900/80 backdrop-blur-xl mt-20">
                <div className="container mx-auto px-6 py-8">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
                        <div>
                            <h3 className="text-lg font-bold text-purple-400 mb-4">BlockStat Pro</h3>
                            <p className="text-sm text-gray-400">
                                Advanced blockchain forensic analysis platform for detecting manipulation and suspicious activities.
                            </p>
                        </div>
                        <div>
                            <h3 className="text-lg font-bold mb-4">Quick Links</h3>
                            <ul className="space-y-2 text-sm text-gray-400">
                                <li>
                                    <Link to="/analysis" className="hover:text-purple-400 transition-colors">
                                        Token Analysis
                                    </Link>
                                </li>
                                <li>
                                    <Link to="/dashboard" className="hover:text-purple-400 transition-colors">
                                        Global Dashboard
                                    </Link>
                                </li>
                                <li>
                                    <Link to="/about" className="hover:text-purple-400 transition-colors">
                                        About & Features
                                    </Link>
                                </li>
                            </ul>
                        </div>
                        <div>
                            <h3 className="text-lg font-bold mb-4">Features</h3>
                            <ul className="space-y-2 text-sm text-gray-400">
                                <li>Mixer Detection</li>
                                <li>Wash Trading Analysis</li>
                                <li>Risk Scoring</li>
                                <li>Graph Visualization</li>
                            </ul>
                        </div>
                    </div>
                    <div className="border-t border-purple-500/20 pt-6 text-center">
                        <p className="text-lg font-bold text-purple-400 mb-2">
                            "Security is not a feature. It's the product."
                        </p>
                        <p className="text-sm text-gray-400">
                            Giving you vision in the dark forest of blockchain
                        </p>
                        <p className="text-xs text-gray-500 mt-4">
                            © 2025 BlockStat Pro. All rights reserved.
                        </p>
                    </div>
                </div>
            </footer>

            {/* Chatbot */}
            <Chatbot />
        </div>
    );
};

export default Layout;

