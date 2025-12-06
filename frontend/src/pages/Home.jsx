import React from 'react';
import { Link } from 'react-router-dom';
import {
    Shield,
    AlertTriangle,
    Users,
    TrendingUp,
    Zap,
    Database,
    BarChart3,
    Network,
    Search,
    ArrowRight,
    CheckCircle2
} from 'lucide-react';

const Home = () => {
    const features = [
        {
            icon: AlertTriangle,
            title: 'Mixer Detection',
            description: 'Automatically flag wallets funded from privacy mixers like Tornado Cash',
            color: 'text-red-400',
            bgColor: 'bg-red-500/10',
            borderColor: 'border-red-500/30'
        },
        {
            icon: Users,
            title: 'Cluster Analysis',
            description: 'Identify wash trading rings and circular transaction patterns',
            color: 'text-orange-400',
            bgColor: 'bg-orange-500/10',
            borderColor: 'border-orange-500/30'
        },
        {
            icon: TrendingUp,
            title: 'Risk Scoring',
            description: 'Comprehensive risk assessment using Gini coefficient and concentration metrics',
            color: 'text-yellow-400',
            bgColor: 'bg-yellow-500/10',
            borderColor: 'border-yellow-500/30'
        },
        {
            icon: Network,
            title: 'Graph Visualization',
            description: 'Interactive network graphs showing wallet relationships and transaction flows',
            color: 'text-blue-400',
            bgColor: 'bg-blue-500/10',
            borderColor: 'border-blue-500/30'
        },
        {
            icon: Database,
            title: 'Real-time Analysis',
            description: 'Live blockchain data analysis with up-to-date transaction information',
            color: 'text-green-400',
            bgColor: 'bg-green-500/10',
            borderColor: 'border-green-500/30'
        },
        {
            icon: BarChart3,
            title: 'Advanced Metrics',
            description: 'Deep insights into token distribution, whale concentration, and network topology',
            color: 'text-purple-400',
            bgColor: 'bg-purple-500/10',
            borderColor: 'border-purple-500/30'
        }
    ];

    const stats = [
        { label: 'Tokens Analyzed', value: '10,000+', icon: Database },
        { label: 'Wallets Tracked', value: '1M+', icon: Users },
        { label: 'Transactions Processed', value: '50M+', icon: TrendingUp },
        { label: 'Risk Patterns Detected', value: '5,000+', icon: AlertTriangle }
    ];

    const capabilities = [
        'Privacy mixer wallet detection',
        'Wash trading pattern identification',
        'Whale concentration analysis',
        'Network clustering algorithms',
        'Gini coefficient calculation',
        'Real-time risk scoring',
        'Interactive graph visualization',
        'Exportable forensic reports'
    ];

    return (
        <div className="container mx-auto px-6 py-12">
            {/* Hero Section */}
            <div className="text-center mb-20">
                <div className="relative inline-block mb-8">
                    <Shield className="w-32 h-32 text-purple-400 animate-glow" />
                    <div className="absolute inset-0 bg-purple-500 blur-3xl opacity-30 animate-pulse"></div>
                </div>

                <h1 className="text-6xl md:text-7xl font-black mb-6 bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
                    Advanced Forensic
                    <br />
                    Graph Intelligence
                </h1>

                <p className="text-xl md:text-2xl text-gray-400 mb-8 max-w-3xl mx-auto">
                    Uncover hidden patterns and detect manipulation in token ecosystems
                    with cutting-edge blockchain analysis technology
                </p>

                <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                    <Link
                        to="/analysis"
                        className="px-8 py-4 bg-gradient-to-r from-purple-600 via-pink-600 to-purple-600 rounded-2xl font-bold hover:from-purple-700 hover:via-pink-700 hover:to-purple-700 transition-all flex items-center gap-3 shadow-lg shadow-purple-500/50 hover:shadow-purple-500/70 hover:scale-105 text-lg"
                    >
                        <Search className="w-6 h-6" />
                        Start Analysis
                        <ArrowRight className="w-5 h-5" />
                    </Link>
                    <Link
                        to="/dashboard"
                        className="px-8 py-4 bg-slate-800/50 border-2 border-purple-500/30 rounded-2xl font-bold hover:bg-slate-800 transition-all flex items-center gap-3 text-lg"
                    >
                        <BarChart3 className="w-6 h-6" />
                        View Dashboard
                    </Link>
                </div>
            </div>

            {/* Stats Section */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-20">
                {stats.map((stat, index) => {
                    const Icon = stat.icon;
                    return (
                        <div
                            key={index}
                            className="bg-slate-900/90 backdrop-blur-xl rounded-2xl p-6 border border-purple-500/20 hover:border-purple-500/50 transition-all"
                        >
                            <Icon className="w-8 h-8 text-purple-400 mb-3" />
                            <div className="text-3xl font-black text-white mb-1">{stat.value}</div>
                            <div className="text-sm text-gray-400">{stat.label}</div>
                        </div>
                    );
                })}
            </div>

            {/* Features Grid */}
            <div className="mb-20">
                <h2 className="text-4xl font-bold text-center mb-4 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                    Powerful Features
                </h2>
                <p className="text-center text-gray-400 mb-12 max-w-2xl mx-auto">
                    Comprehensive tools for blockchain forensic analysis and risk assessment
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {features.map((feature, index) => {
                        const Icon = feature.icon;
                        return (
                            <div
                                key={index}
                                className={`${feature.bgColor} ${feature.borderColor} border rounded-2xl p-6 hover:scale-105 transition-transform cursor-default`}
                            >
                                <div className={`${feature.color} mb-4`}>
                                    <Icon className="w-10 h-10" />
                                </div>
                                <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                                <p className="text-gray-400 text-sm">{feature.description}</p>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Capabilities Section */}
            <div className="bg-slate-900/90 backdrop-blur-xl rounded-3xl p-8 md:p-12 border border-purple-500/20 mb-20">
                <div className="max-w-4xl mx-auto">
                    <div className="flex items-center gap-3 mb-8">
                        <Zap className="w-8 h-8 text-purple-400" />
                        <h2 className="text-3xl font-bold">Platform Capabilities</h2>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {capabilities.map((capability, index) => (
                            <div key={index} className="flex items-center gap-3">
                                <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0" />
                                <span className="text-gray-300">{capability}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* CTA Section */}
            <div className="text-center bg-gradient-to-r from-purple-600/20 via-pink-600/20 to-purple-600/20 rounded-3xl p-12 border border-purple-500/30">
                <h2 className="text-4xl font-bold mb-4">Ready to Get Started?</h2>
                <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
                    Analyze any ERC-20 token and uncover hidden patterns in its transaction network
                </p>
                <Link
                    to="/analysis"
                    className="inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-purple-600 via-pink-600 to-purple-600 rounded-2xl font-bold hover:from-purple-700 hover:via-pink-700 hover:to-purple-700 transition-all shadow-lg shadow-purple-500/50 hover:shadow-purple-500/70 hover:scale-105 text-lg"
                >
                    <Search className="w-6 h-6" />
                    Analyze Token Now
                    <ArrowRight className="w-5 h-5" />
                </Link>
            </div>
        </div>
    );
};

export default Home;

