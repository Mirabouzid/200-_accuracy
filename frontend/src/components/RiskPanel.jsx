import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { getRiskLevel } from '../utils/helpers';

const RiskPanel = ({ riskScore }) => {
    if (!riskScore) return null;

    const riskInfo = getRiskLevel(riskScore.overall);

    return (
        <div className="bg-slate-900/90 backdrop-blur-xl rounded-2xl p-6 border border-purple-500/20">
            <div className="flex items-center gap-3 mb-6">
                <AlertTriangle className="w-6 h-6 text-red-400 animate-pulse" />
                <h3 className="text-xl font-bold">Risk Assessment</h3>
            </div>

            {/* Overall Score */}
            <div className="relative mb-8">
                <div className="absolute inset-0 bg-gradient-to-r from-red-600 to-pink-600 rounded-full blur-2xl opacity-30"></div>
                <div className="relative bg-slate-800/50 rounded-2xl p-6 border border-red-500/30">
                    <div className="text-center">
                        <div className={`text-6xl font-black mb-2 ${riskInfo.textColor}`}>
                            {riskScore.overall}%
                        </div>
                        <div className="text-sm font-semibold text-red-400 uppercase tracking-wider">
                            {riskInfo.level === 'CRITICAL' ? '⛔ Critical Risk' :
                                riskInfo.level === 'HIGH' ? '⚠️ High Risk' :
                                    riskInfo.level === 'MEDIUM' ? '⚡ Medium Risk' :
                                        '✓ Low Risk'}
                        </div>
                    </div>
                </div>
            </div>

            {/* Metrics */}
            <div className="space-y-4">
                {/* Gini Coefficient */}
                <div className="bg-slate-800/30 rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-400">Gini Coefficient</span>
                        <span className="font-bold text-red-400">{riskScore.gini}</span>
                    </div>
                    <div className="h-2 bg-slate-900 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-gradient-to-r from-red-500 to-red-600 rounded-full"
                            style={{ width: `${riskScore.gini * 100}%` }}
                        />
                    </div>
                </div>

                {/* Concentration */}
                <div className="bg-slate-800/30 rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-400">Top 10% Holdings</span>
                        <span className="font-bold text-orange-400">{riskScore.concentration}%</span>
                    </div>
                    <div className="h-2 bg-slate-900 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-gradient-to-r from-orange-500 to-orange-600 rounded-full"
                            style={{ width: `${riskScore.concentration}%` }}
                        />
                    </div>
                </div>

                {/* Clustering */}
                {riskScore.clustering !== undefined && (
                    <div className="bg-slate-800/30 rounded-xl p-4">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-gray-400">Network Clustering</span>
                            <span className="font-bold text-yellow-400">{(riskScore.clustering * 100).toFixed(1)}%</span>
                        </div>
                        <div className="h-2 bg-slate-900 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-gradient-to-r from-yellow-500 to-yellow-600 rounded-full"
                                style={{ width: `${riskScore.clustering * 100}%` }}
                            />
                        </div>
                    </div>
                )}
            </div>

            {/* Alert */}
            <div className="mt-6 p-4 bg-red-500/10 border-2 border-red-500/30 rounded-xl">
                <div className="flex items-start gap-3">
                    <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                    <div>
                        <p className="text-sm font-semibold text-red-400 mb-1">
                            {riskInfo.level === 'CRITICAL' ? '⚠️ High Risk Detected' :
                                riskInfo.level === 'HIGH' ? '⚠️ Elevated Risk' :
                                    '⚡ Caution Advised'}
                        </p>
                        <p className="text-xs text-gray-400">
                            {riskScore.total_wallets} total wallets analyzed.
                            {riskInfo.level === 'CRITICAL' && ' Multiple red flags identified.'}
                            {riskInfo.level === 'HIGH' && ' Suspicious patterns detected.'}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RiskPanel;