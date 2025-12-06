import React, { useRef, useCallback, useEffect } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { getNodeColor, calculateNodeSize } from '../utils/helpers';

const GraphView = ({
    graphData,
    selectedNode,
    onNodeClick,
    showLabels = true,
    isAnimating = true
}) => {
    const graphRef = useRef();

    useEffect(() => {
        if (graphRef.current && selectedNode) {
            graphRef.current.centerAt(selectedNode.x, selectedNode.y, 1000);
            graphRef.current.zoom(2.5, 1000);
        }
    }, [selectedNode]);

    const handleNodeClick = useCallback((node) => {
        onNodeClick(node);
    }, [onNodeClick]);

    const paintNode = useCallback((node, ctx, globalScale) => {
        const size = calculateNodeSize(node);
        const color = getNodeColor(node.type);

        // Glow effect
        ctx.shadowBlur = 20;
        ctx.shadowColor = color;

        // Node circle
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
        ctx.fill();

        // Border for selected node
        if (selectedNode?.id === node.id) {
            ctx.strokeStyle = '#fbbf24';
            ctx.lineWidth = 3;
            ctx.stroke();
        }

        ctx.shadowBlur = 0;

        // Labels
        if (showLabels && (globalScale > 1.5 || node.type === 'deployer' || selectedNode?.id === node.id)) {
            const label = node.name || node.id?.slice(0, 10);
            const fontSize = 11 / globalScale;
            ctx.font = `bold ${fontSize}px Inter, sans-serif`;
            const textWidth = ctx.measureText(label).width;
            const padding = fontSize * 0.4;

            // Background
            ctx.fillStyle = 'rgba(0, 0, 0, 0.85)';
            ctx.fillRect(
                node.x - textWidth / 2 - padding,
                node.y + size + 5,
                textWidth + padding * 2,
                fontSize + padding * 2
            );

            // Text
            ctx.fillStyle = '#ffffff';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(label, node.x, node.y + size + 5 + fontSize / 2 + padding);
        }
    }, [selectedNode, showLabels]);

    if (!graphData || !graphData.nodes.length) {
        return (
            <div className="w-full h-full flex items-center justify-center text-gray-400">
                <p>No graph data available</p>
            </div>
        );
    }

    return (
        <ForceGraph2D
            ref={graphRef}
            graphData={graphData}
            nodeLabel="name"
            nodeVal={calculateNodeSize}
            linkWidth={link => Math.sqrt(link.value) / 150}
            linkColor={() => 'rgba(107, 114, 128, 0.3)'}
            linkDirectionalParticles={isAnimating ? 2 : 0}
            linkDirectionalParticleWidth={3}
            linkDirectionalParticleSpeed={0.005}
            onNodeClick={handleNodeClick}
            backgroundColor="#020617"
            enableNodeDrag={true}
            cooldownTime={3000}
            nodeCanvasObject={paintNode}
        />
    );
};

export default GraphView;