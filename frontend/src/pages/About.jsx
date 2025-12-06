import React from 'react';
import { Shield, AlertTriangle, Network, TrendingUp, Database, Zap, Users, BarChart3, CheckCircle2, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

const About = () => {
  const features = [
    {
      icon: AlertTriangle,
      title: 'Privacy Mixer Detection',
      description: 'Automatically identifies wallets that have received funds from privacy mixers like Tornado Cash, providing critical risk indicators for token analysis.',
      details: [
        'Real-time mixer address database',
        'Transaction flow tracing',
        'Risk flagging system'
      ]
    },
    {
      icon: Network,
      title: 'Network Graph Analysis',
      description: 'Visualize complex transaction networks with interactive force-directed graphs, revealing hidden relationships between wallets.',
      details: [
        'Interactive graph visualization',
        'Node clustering algorithms',
        'Transaction flow mapping'
      ]
    },
    {
      icon: TrendingUp,
      title: 'Wash Trading Detection',
      description: 'Identify circular trading patterns and suspicious clusters that indicate artificial volume manipulation.',
      details: [
        'Pattern recognition algorithms',
        'Cluster analysis',
        'Circular transaction detection'
      ]
    },
    {
      icon: BarChart3,
      title: 'Risk Scoring System',
      description: 'Comprehensive risk assessment using multiple metrics including Gini coefficient, concentration ratios, and network topology.',
      details: [
        'Multi-factor risk calculation',
        'Gini coefficient analysis',
        'Concentration metrics'
      ]
    },
    {
      icon: Database,
      title: 'Real-time Blockchain Data',
      description: 'Access up-to-date blockchain information with live transaction monitoring and analysis capabilities.',
      details: [
        'Live data feeds',
        'Historical analysis',
        'Transaction tracking'
      ]
    },
    {
      icon: Users,
      title: 'Whale Analysis',
      description: 'Track large holders and analyze token distribution patterns to identify centralization risks.',
      details: [
        'Whale wallet identification',
        'Distribution analysis',
        'Concentration tracking'
      ]
    }
  ];

  const technologies = [
    'React 19 - Modern UI framework',
    'NetworkX - Graph analysis algorithms',
    'Force-directed graph visualization',
    'Ethereum blockchain integration',
    'Real-time data processing',
    'Advanced pattern recognition'
  ];

  const useCases = [
    {
      title: 'Token Due Diligence',
      description: 'Perform comprehensive analysis before investing in new tokens',
      icon: Shield
    },
    {
      title: 'Regulatory Compliance',
      description: 'Identify and flag suspicious activities for compliance purposes',
      icon: AlertTriangle
    },
    {
      title: 'Market Research',
      description: 'Understand token distribution and holder behavior patterns',
      icon: TrendingUp
    },
    {
      title: 'Security Audits',
      description: 'Detect manipulation and fraud in token ecosystems',
      icon: Database
    }
  ];

  return (
    <div className="container mx-auto px-6 py-12">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <div className="relative inline-block mb-6">
          <Shield className="w-20 h-20 text-purple-400 animate-glow" />
          <div className="absolute inset-0 bg-purple-500 blur-3xl opacity-30"></div>
        </div>
        <h1 className="text-5xl md:text-6xl font-black mb-6 bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
          About BlockStat Pro
        </h1>
        <p className="text-xl text-gray-400 max-w-3xl mx-auto">
          Advanced blockchain forensic analysis platform designed to uncover hidden patterns
          and detect manipulation in token ecosystems
        </p>
      </div>

      {/* Mission Section */}
      <div className="bg-slate-900/90 backdrop-blur-xl rounded-3xl p-8 md:p-12 border border-purple-500/20 mb-16">
        <h2 className="text-3xl font-bold mb-6 flex items-center gap-3">
          <Zap className="w-8 h-8 text-purple-400" />
          Our Mission
        </h2>
        <p className="text-lg text-gray-300 leading-relaxed mb-4">
          BlockStat Pro was created to bring transparency and security to the blockchain ecosystem.
          We believe that every investor and user deserves access to powerful forensic analysis tools
          that can reveal the true nature of token projects.
        </p>
        <p className="text-lg text-gray-300 leading-relaxed">
          Our platform combines cutting-edge graph analysis algorithms with intuitive visualization
          to help users make informed decisions and identify potential risks before they become problems.
        </p>
      </div>

      {/* Features Detail */}
      <div className="mb-16">
        <h2 className="text-4xl font-bold text-center mb-12 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
          Core Features
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={index}
                className="bg-slate-900/90 backdrop-blur-xl rounded-2xl p-6 border border-purple-500/20 hover:border-purple-500/50 transition-all"
              >
                <div className="flex items-start gap-4 mb-4">
                  <div className="p-3 bg-purple-500/10 rounded-xl">
                    <Icon className="w-6 h-6 text-purple-400" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                    <p className="text-gray-400 mb-4">{feature.description}</p>
                    <ul className="space-y-2">
                      {feature.details.map((detail, i) => (
                        <li key={i} className="flex items-center gap-2 text-sm text-gray-300">
                          <CheckCircle2 className="w-4 h-4 text-green-400 flex-shrink-0" />
                          {detail}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Use Cases */}
      <div className="mb-16">
        <h2 className="text-4xl font-bold text-center mb-12 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
          Use Cases
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {useCases.map((useCase, index) => {
            const Icon = useCase.icon;
            return (
              <div
                key={index}
                className="bg-slate-900/90 backdrop-blur-xl rounded-2xl p-6 border border-purple-500/20 hover:scale-105 transition-transform"
              >
                <Icon className="w-10 h-10 text-purple-400 mb-4" />
                <h3 className="text-lg font-bold mb-2">{useCase.title}</h3>
                <p className="text-sm text-gray-400">{useCase.description}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Technologies */}
      <div className="bg-slate-900/90 backdrop-blur-xl rounded-3xl p-8 md:p-12 border border-purple-500/20 mb-16">
        <h2 className="text-3xl font-bold mb-8 flex items-center gap-3">
          <Database className="w-8 h-8 text-purple-400" />
          Technology Stack
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {technologies.map((tech, index) => (
            <div key={index} className="flex items-center gap-3">
              <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0" />
              <span className="text-gray-300">{tech}</span>
            </div>
          ))}
        </div>
      </div>

      {/* CTA */}
      <div className="text-center bg-gradient-to-r from-purple-600/20 via-pink-600/20 to-purple-600/20 rounded-3xl p-12 border border-purple-500/30">
        <h2 className="text-4xl font-bold mb-4">Ready to Get Started?</h2>
        <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
          Start analyzing tokens and uncovering hidden patterns in blockchain networks
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            to="/analysis"
            className="px-8 py-4 bg-gradient-to-r from-purple-600 via-pink-600 to-purple-600 rounded-2xl font-bold hover:from-purple-700 hover:via-pink-700 hover:to-purple-700 transition-all flex items-center gap-3 shadow-lg shadow-purple-500/50 hover:shadow-purple-500/70 hover:scale-105"
          >
            <Zap className="w-5 h-5" />
            Start Analysis
            <ArrowRight className="w-5 h-5" />
          </Link>
          <Link
            to="/dashboard"
            className="px-8 py-4 bg-slate-800/50 border-2 border-purple-500/30 rounded-2xl font-bold hover:bg-slate-800 transition-all flex items-center gap-3"
          >
            <BarChart3 className="w-5 h-5" />
            View Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
};

export default About;

