import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Users, AlertTriangle, Database, Activity, Zap, Shield } from 'lucide-react';
import { getStats } from '../utils/api';
import { formatNumber, formatLargeNumber } from '../utils/helpers';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await getStats();
        setStats(data);
      } catch (err) {
        console.error('Failed to fetch stats:', err);
        
        // Check if it's a connection error
        if (err.code === 'ERR_NETWORK' || err.code === 'ECONNREFUSED' || 
            err.message?.includes('ERR_CONNECTION_REFUSED') || 
            err.message?.includes('Network Error') ||
            !err.response) {
          setError('⚠️ Backend server is not running! Please start it: cd backend && npm run dev');
        } else {
          setError(err.userMessage || 'Failed to load dashboard statistics');
        }
        
        // Set mock data for development
        setStats({
          total_tokens: 10234,
          total_wallets: 1250000,
          total_transactions: 52345678,
          high_risk_tokens: 1234,
          mixer_detections: 567,
          wash_trading_cases: 890,
          avg_risk_score: 45.6,
          active_analyses: 23
        });
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const statCards = [
    {
      title: 'Total Tokens Analyzed',
      value: stats?.total_tokens || 0,
      icon: Database,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/30',
      format: formatNumber
    },
    {
      title: 'Total Wallets Tracked',
      value: stats?.total_wallets || 0,
      icon: Users,
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10',
      borderColor: 'border-purple-500/30',
      format: formatLargeNumber
    },
    {
      title: 'Transactions Processed',
      value: stats?.total_transactions || 0,
      icon: Activity,
      color: 'text-green-400',
      bgColor: 'bg-green-500/10',
      borderColor: 'border-green-500/30',
      format: formatLargeNumber
    },
    {
      title: 'High Risk Tokens',
      value: stats?.high_risk_tokens || 0,
      icon: AlertTriangle,
      color: 'text-red-400',
      bgColor: 'bg-red-500/10',
      borderColor: 'border-red-500/30',
      format: formatNumber
    },
    {
      title: 'Mixer Detections',
      value: stats?.mixer_detections || 0,
      icon: Shield,
      color: 'text-orange-400',
      bgColor: 'bg-orange-500/10',
      borderColor: 'border-orange-500/30',
      format: formatNumber
    },
    {
      title: 'Wash Trading Cases',
      value: stats?.wash_trading_cases || 0,
      icon: TrendingUp,
      color: 'text-yellow-400',
      bgColor: 'bg-yellow-500/10',
      borderColor: 'border-yellow-500/30',
      format: formatNumber
    }
  ];

  if (loading) {
    return (
      <div className="container mx-auto px-6 py-12">
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-purple-500/30 border-t-purple-500 rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-400">Loading dashboard statistics...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-6 py-8">
      {/* Header */}
      <div className="mb-10">
        <div className="flex items-center gap-4 mb-4">
          <BarChart3 className="w-10 h-10 text-purple-400" />
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              Global Dashboard
            </h1>
            <p className="text-gray-400 mt-1">Real-time statistics and insights</p>
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400">
          {error}
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
        {statCards.map((card, index) => {
          const Icon = card.icon;
          return (
            <div
              key={index}
              className={`${card.bgColor} ${card.borderColor} border rounded-2xl p-6 hover:scale-105 transition-transform`}
            >
              <div className="flex items-center justify-between mb-4">
                <Icon className={`w-8 h-8 ${card.color}`} />
                <div className="text-right">
                  <p className="text-3xl font-black text-white mb-1">
                    {card.format(card.value)}
                  </p>
                  <p className="text-sm text-gray-400">{card.title}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Additional Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Average Risk Score */}
        <div className="bg-slate-900/90 backdrop-blur-xl rounded-2xl p-6 border border-purple-500/20">
          <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-purple-400" />
            Average Risk Score
          </h3>
          <div className="relative">
            <div className="text-5xl font-black text-purple-400 mb-2">
              {stats?.avg_risk_score?.toFixed(1) || '0.0'}%
            </div>
            <div className="h-4 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"
                style={{ width: `${stats?.avg_risk_score || 0}%` }}
              />
            </div>
            <p className="text-sm text-gray-400 mt-2">
              Across all analyzed tokens
            </p>
          </div>
        </div>

        {/* Active Analyses */}
        <div className="bg-slate-900/90 backdrop-blur-xl rounded-2xl p-6 border border-purple-500/20">
          <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Zap className="w-6 h-6 text-yellow-400" />
            Active Analyses
          </h3>
          <div className="text-5xl font-black text-yellow-400 mb-2">
            {stats?.active_analyses || 0}
          </div>
          <p className="text-sm text-gray-400">
            Currently running in real-time
          </p>
        </div>
      </div>

      {/* Info Section */}
      <div className="mt-10 bg-slate-900/50 border border-purple-500/20 rounded-2xl p-8">
        <h3 className="text-2xl font-bold mb-4">Platform Overview</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-gray-400">
          <div>
            <p className="mb-2">
              <strong className="text-white">BlockStat Pro</strong> provides comprehensive blockchain forensic analysis
              capabilities, enabling users to detect suspicious patterns, identify wash trading,
              and assess risk levels across token ecosystems.
            </p>
          </div>
          <div>
            <p className="mb-2">
              Our advanced algorithms analyze transaction networks, detect privacy mixer usage,
              and calculate risk metrics including Gini coefficients and concentration ratios
              to provide actionable insights.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

