import React from 'react';
import { Info, Copy } from 'lucide-react';
import { shortenAddress, formatNumber, formatDate, copyToClipboard } from '../utils/helpers';

const NodeDetails = ({ node }) => {
    if (!node) {
        return (
            <div className="text-center py-8 text-gray-400">
                <Info className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>Click on a node to view details</p>
            </div>
        );
    }

    const handleCopy = async () => {
        const success = await copyToClipboard(node.address || node.id);
        if (success) {
            alert('Address copied to clipboard!');
        }
    };

    return (
        <div className="space-y-4">
            {/* Address */}
            <div>
                <p className="text-xs text-gray-400 mb-2">Wallet Address</p>
                <div className="flex items-center gap-2">
                    <p className="font-mono text-sm bg-slate-800 px-3 py-2 rounded flex-1 truncate">
                        {node.address || node.id}
                    </p>
                    <button
                        onClick={handleCopy}
                        className="p-2 bg-slate-800 hover:bg-slate-700 rounded transition-colors"
                        title="Copy address"
                    >
                        <Copy className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {/* Type */}
            <div>
                <p className="text-xs text-gray-400 mb-2">Type</p>
                <span className={`inline-block px-3 py-1 rounded-lg text-xs font-semibold ${node.type === 'deployer' ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30' :
                        node.type === 'mixer' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                            node.type === 'wash_trading' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' :
                                node.type === 'whale' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' :
                                    'bg-green-500/20 text-green-400 border border-green-500/30'
                    }`}>
                    {node.type?.toUpperCase() || 'NORMAL'}
                </span>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 gap-4">
                <div>
                    <p className="text-xs text-gray-400 mb-1">Balance</p>
                    <p className="font-bold">{formatNumber(node.balance)}</p>
                </div>
                <div>
                    <p className="text-xs text-gray-400 mb-1">Transactions</p>
                    <p className="font-bold">{node.tx_count || 0}</p>
                </div>
                <div>
                    <p className="text-xs text-gray-400 mb-1">Sent</p>
                    <p className="font-bold text-red-400">{formatNumber(node.total_sent || 0)}</p>
                </div>
                <div>
                    <p className="text-xs text-gray-400 mb-1">Received</p>
                    <p className="font-bold text-green-400">{formatNumber(node.total_received || 0)}</p>
                </div>
            </div>

            {/* Tags */}
            {node.tags && node.tags.length > 0 && (
                <div>
                    <p className="text-xs text-gray-400 mb-2">Tags</p>
                    <div className="flex flex-wrap gap-2">
                        {node.tags.map((tag, i) => (
                            <span key={i} className="px-2 py-1 bg-purple-500/20 text-purple-400 rounded text-xs">
                                {tag}
                            </span>
                        ))}
                    </div>
                </div>
            )}

            {/* Timestamps */}
            {node.firstSeen && (
                <div className="text-xs text-gray-400 space-y-1">
                    <p>First Seen: {formatDate(node.firstSeen)}</p>
                    {node.lastActive && <p>Last Active: {formatDate(node.lastActive)}</p>}
                </div>
            )}
        </div>
    );
};

export default NodeDetails;