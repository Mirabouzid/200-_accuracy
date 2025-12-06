import React, { useState, useRef, useCallback } from 'react';
import { Search, AlertTriangle, Shield, TrendingUp, Users, Zap, Info, Download, Activity, Eye, EyeOff, Play, Pause, Database } from 'lucide-react';
import GraphView from '../components/GraphView';
import RiskPanel from '../components/RiskPanel';
import NodeDetails from '../components/NodeDetails';
import { analyzeToken } from '../utils/api';
import { isValidAddress, downloadJSON } from '../utils/helpers';

const Analysis = () => {
    const [tokenAddress, setTokenAddress] = useState('');
    const [loading, setLoading] = useState(false);
    const [graphData, setGraphData] = useState(null);
    const [selectedNode, setSelectedNode] = useState(null);
    const [riskScore, setRiskScore] = useState(null);
    const [activeTab, setActiveTab] = useState('overview');
    const [showLabels, setShowLabels] = useState(true);
    const [isAnimating, setIsAnimating] = useState(true);
    const [analysisProgress, setAnalysisProgress] = useState(0);
    const [error, setError] = useState(null);
    const [insights, setInsights] = useState([]);

    const handleAnalyze = async () => {
        if (!tokenAddress) {
            setError('Please enter a token address');
            return;
        }

        if (!isValidAddress(tokenAddress)) {
            setError('Invalid Ethereum address format');
            return;
        }

        setLoading(true);
        setError(null);
        setSelectedNode(null);
        setAnalysisProgress(0);

        // Progress simulation
        const progressInterval = setInterval(() => {
            setAnalysisProgress(prev => {
                if (prev >= 90) {
                    clearInterval(progressInterval);
                    return prev;
                }
                return prev + 10;
            });
        }, 300);

        try {
            const data = await analyzeToken(tokenAddress);

            clearInterval(progressInterval);
            setAnalysisProgress(100);

            // Process data
            setGraphData({
                nodes: data.graph.nodes,
                links: data.graph.links
            });

            setRiskScore(data.risk_score);

            // Generate insights
            const newInsights = [];

            if (data.mixers && data.mixers.length > 0) {
                newInsights.push({
                    type: 'critical',
                    icon: '🚨',
                    title: 'Privacy Mixer Detected',
                    message: `${data.mixers.length} wallet(s) funded from Tornado Cash or similar mixers`
                });
            }

            if (data.clusters && data.clusters.length > 0) {
                const suspiciousClusters = data.clusters.filter(c => c.suspicious);
                if (suspiciousClusters.length > 0) {
                    newInsights.push({
                        type: 'warning',
                        icon: '⚠️',
                        title: 'Wash Trading Pattern',
                        message: `${suspiciousClusters.length} suspicious cluster(s) with circular trading patterns`
                    });
                }
            }

            if (data.whales && data.whales.length > 0) {
                const topWhale = data.whales[0];
                newInsights.push({
                    type: 'info',
                    icon: '🐋',
                    title: 'Whale Concentration',
                    message: `Top holder controls ${topWhale.percentage}% of supply`
                });
            }

            if (data.risk_score.gini > 0.8) {
                newInsights.push({
                    type: 'critical',
                    icon: '📊',
                    title: 'Extreme Centralization',
                    message: `Gini coefficient: ${data.risk_score.gini} (Highly unequal distribution)`
                });
            }

            setInsights(newInsights);

        } catch (err) {
            console.error('Analysis error:', err);
            setError(err.response?.data?.error || 'Analysis failed. Please try again.');
        } finally {
            clearInterval(progressInterval);
            setLoading(false);
            setAnalysisProgress(0);
        }
    };

    const handleNodeClick = useCallback((node) => {
        setSelectedNode(node);
        setActiveTab('details');
    }, []);

    const handleExport = () => {
        const report = {
            tokenAddress,
            analysisDate: new Date().toISOString(),
            riskScore,
            insights,
            graphData: {
                totalNodes: graphData.nodes.length,
                totalLinks: graphData.links.length
            }
        };
        downloadJSON(report, `forensic-report-${Date.now()}.json`);
    };

    return (
        <div className="container mx-auto px-6 py-8">
            {/* Search Section */}
            <div className="max-w-4xl mx-auto mb-10">
                <div className="relative">
                    <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 rounded-3xl blur-2xl opacity-20"></div>
                    <div className="relative bg-slate-900/90 backdrop-blur-xl rounded-3xl p-8 border border-purple-500/30 shadow-2xl">
                        <div className="flex items-center gap-3 mb-6">
                            <Search className="w-6 h-6 text-purple-400" />
                            <h2 className="text-2xl font-bold">Token Analysis Dashboard</h2>
                        </div>

                        <div className="flex gap-4 mb-4">
                            <div className="flex-1 relative group">
                                <Search className="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-purple-400" />
                                <input
                                    type="text"
                                    placeholder="0x... Token Contract Address"
                                    value={tokenAddress}
                                    onChange={(e) => {
                                        setTokenAddress(e.target.value);
                                        setError(null);
                                    }}
                                    className="w-full pl-14 pr-6 py-4 bg-slate-800/50 border-2 border-purple-500/30 rounded-2xl focus:outline-none focus:border-purple-500 text-white placeholder-gray-500 text-lg transition-all"
                                />
                            </div>
                            <button
                                onClick={handleAnalyze}
                                disabled={loading || !tokenAddress}
                                className="px-8 py-4 bg-gradient-to-r from-purple-600 via-pink-600 to-purple-600 rounded-2xl font-bold hover:from-purple-700 hover:via-pink-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-3 shadow-lg shadow-purple-500/50 hover:shadow-purple-500/70 hover:scale-105 text-lg"
                            >
                                {loading ? (
                                    <>
                                        <div className="w-6 h-6 border-3 border-white/30 border-t-white rounded-full animate-spin" />
                                        Analyzing
                                    </>
                                ) : (
                                    <>
                                        <Zap className="w-6 h-6" />
                                        Analyze
                                    </>
                                )}
                            </button>
                        </div>

                        {error && (
                            <div className="mb-4 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm">
                                {error}
                            </div>
                        )}

                        {loading && (
                            <div className="space-y-3">
                                <div className="flex items-center justify-between text-sm text-gray-400">
                                    <span>Analysis Progress</span>
                                    <span className="font-semibold">{analysisProgress}%</span>
                                </div>
                                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all duration-300"
                                        style={{ width: `${analysisProgress}%` }}
                                    />
                                </div>
                                <div className="flex items-center gap-2 text-xs text-purple-400">
                                    <Activity className="w-4 h-4 animate-pulse" />
                                    <span>
                                        {analysisProgress < 30 ? 'Fetching transactions...' :
                                            analysisProgress < 60 ? 'Building graph structure...' :
                                                analysisProgress < 90 ? 'Running algorithms...' :
                                                    'Generating report...'}
                                    </span>
                                </div>
                            </div>
                        )}

                        <div className="grid grid-cols-3 gap-4 mt-6 text-sm">
                            <div className="flex items-center gap-2 text-gray-400">
                                <Activity className="w-4 h-4 text-purple-400" />
                                <span>Real-time Detection</span>
                            </div>
                            <div className="flex items-center gap-2 text-gray-400">
                                <Shield className="w-4 h-4 text-green-400" />
                                <span>10,000 Tx Analyzed</span>
                            </div>
                            <div className="flex items-center gap-2 text-gray-400">
                                <Database className="w-4 h-4 text-blue-400" />
                                <span>NetworkX Powered</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Dashboard */}
            {graphData && (
                <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
                    {/* Graph Visualization */}
                    <div className="xl:col-span-3 space-y-6">
                        {/* Controls */}
                        <div className="bg-slate-900/90 backdrop-blur-xl rounded-2xl p-4 border border-purple-500/20">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-4">
                                    <button
                                        onClick={() => setIsAnimating(!isAnimating)}
                                        className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg flex items-center gap-2 transition-colors"
                                    >
                                        {isAnimating ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                                        <span className="text-sm">{isAnimating ? 'Pause' : 'Play'}</span>
                                    </button>
                                    <button
                                        onClick={() => setShowLabels(!showLabels)}
                                        className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg flex items-center gap-2 transition-colors"
                                    >
                                        {showLabels ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                        <span className="text-sm">Labels</span>
                                    </button>
                                </div>
                                <button
                                    onClick={handleExport}
                                    className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-lg flex items-center gap-2 transition-colors"
                                >
                                    <Download className="w-4 h-4" />
                                    <span className="text-sm font-semibold">Export</span>
                                </button>
                            </div>
                        </div>

                        {/* Graph */}
                        <div className="bg-slate-900/90 backdrop-blur-xl rounded-2xl p-6 border border-purple-500/20 h-[700px] relative overflow-hidden">
                            <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-pink-500/5"></div>
                            <div className="relative h-full bg-slate-950/50 rounded-xl overflow-hidden border border-slate-800">
                                <GraphView
                                    graphData={graphData}
                                    selectedNode={selectedNode}
                                    onNodeClick={handleNodeClick}
                                    showLabels={showLabels}
                                    isAnimating={isAnimating}
                                />
                            </div>
                        </div>

                        {/* Legend */}
                        <div className="bg-slate-900/90 backdrop-blur-xl rounded-2xl p-5 border border-purple-500/20">
                            <h4 className="font-semibold mb-4 flex items-center gap-2">
                                <Info className="w-5 h-5 text-purple-400" />
                                Network Legend
                            </h4>
                            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                                {[
                                    { color: 'bg-purple-500', name: 'Deployer', desc: 'Origin' },
                                    { color: 'bg-red-500', name: 'Mixer', desc: 'Critical' },
                                    { color: 'bg-orange-500', name: 'Wash Trade', desc: 'High Risk' },
                                    { color: 'bg-blue-500', name: 'Whale', desc: 'Large' },
                                    { color: 'bg-green-500', name: 'Normal', desc: 'Low Risk' }
                                ].map((item, i) => (
                                    <div key={i} className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-lg">
                                        <div className={`w-5 h-5 rounded-full ${item.color} shadow-lg`}></div>
                                        <div>
                                            <p className="text-sm font-semibold">{item.name}</p>
                                            <p className="text-xs text-gray-400">{item.desc}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Sidebar */}
                    <div className="xl:col-span-1 space-y-6">
                        <RiskPanel riskScore={riskScore} />

                        {/* Tabs */}
                        <div className="bg-slate-900/90 backdrop-blur-xl rounded-2xl border border-purple-500/20 overflow-hidden">
                            <div className="flex border-b border-slate-800">
                                {['overview', 'details', 'insights'].map(tab => (
                                    <button
                                        key={tab}
                                        onClick={() => setActiveTab(tab)}
                                        className={`flex-1 px-4 py-3 text-sm font-semibold transition-colors ${activeTab === tab
                                                ? 'bg-purple-500/20 text-purple-400 border-b-2 border-purple-500'
                                                : 'text-gray-400 hover:text-white hover:bg-slate-800/50'
                                            }`}
                                    >
                                        {tab.charAt(0).toUpperCase() + tab.slice(1)}
                                    </button>
                                ))}
                            </div>

                            <div className="p-6">
                                {activeTab === 'overview' && riskScore && (
                                    <div className="space-y-4">
                                        <div className="flex items-center justify-between text-sm">
                                            <span className="text-gray-400">Total Wallets</span>
                                            <span className="font-bold">{riskScore.total_wallets || 0}</span>
                                        </div>
                                        <div className="flex items-center justify-between text-sm">
                                            <span className="text-gray-400">Active Wallets</span>
                                            <span className="font-bold">{riskScore.active_wallets || 0}</span>
                                        </div>
                                        <div className="flex items-center justify-between text-sm">
                                            <span className="text-gray-400">Transactions</span>
                                            <span className="font-bold">{graphData.links.length}</span>
                                        </div>
                                    </div>
                                )}

                                {activeTab === 'details' && (
                                    <NodeDetails node={selectedNode} />
                                )}

                                {activeTab === 'insights' && (
                                    <div className="space-y-3">
                                        {insights.length > 0 ? (
                                            insights.map((insight, i) => (
                                                <div key={i} className={`p-4 rounded-xl border ${insight.type === 'critical' ? 'bg-red-500/10 border-red-500/30' :
                                                        insight.type === 'warning' ? 'bg-orange-500/10 border-orange-500/30' :
                                                            'bg-blue-500/10 border-blue-500/30'
                                                    }`}>
                                                    <div className="flex items-start gap-3">
                                                        <span className="text-2xl">{insight.icon}</span>
                                                        <div className="flex-1">
                                                            <p className="font-semibold text-sm mb-1">{insight.title}</p>
                                                            <p className="text-xs text-gray-400">{insight.message}</p>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))
                                        ) : (
                                            <div className="text-center py-8 text-gray-400">
                                                <Info className="w-12 h-12 mx-auto mb-3 opacity-50" />
                                                <p className="text-sm">No insights available yet</p>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Empty State */}
            {!graphData && !loading && (
                <div className="max-w-3xl mx-auto text-center py-20">
                    <div className="relative inline-block mb-8">
                        <Shield className="w-24 h-24 text-purple-400 animate-glow" />
                        <div className="absolute inset-0 bg-purple-500 blur-3xl opacity-30 animate-pulse"></div>
                    </div>
                    <h3 className="text-4xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                        Advanced Forensic Analysis
                    </h3>
                    <p className="text-xl text-gray-400 mb-12">
                        Uncover hidden patterns and detect manipulation in token ecosystems
                    </p>
                    <div className="grid grid-cols-3 gap-6">
                        {[
                            { icon: AlertTriangle, title: 'Mixer Detection', desc: 'Flag privacy-mixer funded wallets' },
                            { icon: Users, title: 'Cluster Analysis', desc: 'Identify wash trading rings' },
                            { icon: TrendingUp, title: 'Risk Scoring', desc: 'Comprehensive assessment' }
                        ].map((feature, i) => (
                            <div key={i} className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 hover:border-purple-500/50 transition-colors">
                                <feature.icon className="w-12 h-12 text-purple-400 mx-auto mb-4" />
                                <p className="font-bold mb-2">{feature.title}</p>
                                <p className="text-sm text-gray-400">{feature.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default Analysis;

