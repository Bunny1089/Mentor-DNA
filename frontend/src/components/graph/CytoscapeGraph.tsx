import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import type { Core, EventObject } from 'cytoscape';
import {
  Maximize2,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Layers,
  Info,
  ExternalLink,
} from 'lucide-react';
import type { SubgraphResponse, GraphNode } from '../../types';

interface CytoscapeGraphProps {
  graphData: SubgraphResponse | null;
  selectedMerchantId?: string;
  onSelectMerchant?: (merchantId: string) => void;
  height?: string;
  title?: string;
}

export const CytoscapeGraph: React.FC<CytoscapeGraphProps> = ({
  graphData,
  selectedMerchantId,
  onSelectMerchant,
  height = '500px',
  title,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [layoutName] = useState<'cose' | 'concentric' | 'circle'>('cose');

  useEffect(() => {
    if (!containerRef.current || !graphData || !graphData.nodes.length) return;

    // Convert GraphNode/GraphEdge to Cytoscape elements
    const elements: cytoscape.ElementDefinition[] = [];

    // Nodes
    graphData.nodes.forEach((n) => {
      const isTarget = n.id === selectedMerchantId || n.id === graphData.merchant_id;
      elements.push({
        group: 'nodes',
        data: {
          id: n.id,
          label: n.label || n.id,
          entity_type: n.entity_type,
          risk_level: n.risk_level || 'LOW',
          risk_score: n.risk_score || 0,
          is_ring_member: n.is_ring_member,
          is_target: isTarget,
          raw_node: n,
        },
      });
    });

    // Edges
    graphData.edges.forEach((e) => {
      elements.push({
        group: 'edges',
        data: {
          id: e.id,
          source: e.source,
          target: e.target,
          label: e.relation_type?.replace(/_/g, ' ') || '',
          weight: e.weight || 1,
          is_suspicious: e.is_suspicious,
        },
      });
    });

    const stylesheet: any = [
      // Base Node Style
      {
        selector: 'node',
        style: {
          'background-color': '#20232B',
          'label': 'data(label)',
          'color': '#E8E6DE',
          'font-size': '10px',
          'font-family': 'IBM Plex Sans, sans-serif',
          'text-valign': 'bottom',
          'text-margin-y': 6,
          'border-width': 2,
          'border-color': '#3A3E48',
          'width': 32,
          'height': 32,
        },
      },
      // Merchant Nodes
      {
        selector: 'node[entity_type = "MERCHANT"]',
        style: {
          'shape': 'hexagon',
          'width': 40,
          'height': 40,
          'font-size': '11px',
          'font-weight': '600',
          'border-width': 2.5,
          'border-color': '#5A5E68',
          'background-color': '#20232B',
        },
      },
      // High/Critical Risk Merchant Nodes
      {
        selector: 'node[entity_type = "MERCHANT"][risk_level = "CRITICAL"]',
        style: {
          'border-color': '#A83D3D',
          'background-color': '#421C1C',
        },
      },
      {
        selector: 'node[entity_type = "MERCHANT"][risk_level = "HIGH"]',
        style: {
          'border-color': '#B8862E',
          'background-color': '#3D2F15',
        },
      },
      // Target / Anchor Merchant Node
      {
        selector: 'node[?is_target]',
        style: {
          'width': 48,
          'height': 48,
          'border-width': 3,
          'border-color': '#B8862E',
        },
      },
      // Device Nodes
      {
        selector: 'node[entity_type = "DEVICE"]',
        style: {
          'shape': 'diamond',
          'width': 30,
          'height': 30,
          'background-color': '#2A2035',
          'border-color': '#7C4D99',
        },
      },
      // Bank Account Nodes
      {
        selector: 'node[entity_type = "BANK_ACCOUNT"]',
        style: {
          'shape': 'round-rectangle',
          'width': 34,
          'height': 26,
          'background-color': '#332917',
          'border-color': '#B8862E',
        },
      },
      // UPI Nodes
      {
        selector: 'node[entity_type = "UPI_HANDLE"]',
        style: {
          'shape': 'tag',
          'width': 30,
          'height': 30,
          'background-color': '#162D28',
          'border-color': '#4B7A6F',
        },
      },
      // Address Nodes
      {
        selector: 'node[entity_type = "ADDRESS"]',
        style: {
          'shape': 'triangle',
          'width': 30,
          'height': 30,
          'background-color': '#331B26',
          'border-color': '#9E4A6E',
        },
      },
      // Phone Nodes
      {
        selector: 'node[entity_type = "PHONE"]',
        style: {
          'shape': 'rectangle',
          'width': 28,
          'height': 28,
          'background-color': '#1C2233',
          'border-color': '#516594',
        },
      },
      // Buyer Nodes
      {
        selector: 'node[entity_type = "BUYER"]',
        style: {
          'shape': 'ellipse',
          'width': 24,
          'height': 24,
          'background-color': '#20232B',
          'border-color': '#5A5E68',
        },
      },
      // Base Edge Style
      {
        selector: 'edge',
        style: {
          'width': 1.5,
          'line-color': '#2A2D35',
          'target-arrow-color': '#3A3E48',
          'target-arrow-shape': 'triangle',
          'curve-style': 'bezier',
          'arrow-scale': 0.8,
          'opacity': 0.8,
        },
      },
      // Suspicious / Shared Infrastructure Edges
      {
        selector: 'edge[?is_suspicious]',
        style: {
          'width': 2,
          'line-color': '#A83D3D',
          'target-arrow-color': '#A83D3D',
          'line-style': 'dashed',
          'opacity': 0.9,
        },
      },
      // Selected / Highlighted State
      {
        selector: 'node:selected',
        style: {
          'border-color': '#E8E6DE',
          'border-width': 3,
        },
      },
    ];

    // Initialize Cytoscape Instance
    const cy = cytoscape({
      container: containerRef.current,
      elements: elements,
      boxSelectionEnabled: false,
      autounselectify: false,
      style: stylesheet,
      layout: {
        name: layoutName,
        animate: false,
        padding: 50,
      },
    });

    // Event handlers
    cy.on('tap', 'node', (evt: EventObject) => {
      const node = evt.target;
      const rawNode: GraphNode = node.data('raw_node');
      setSelectedNode(rawNode);
    });

    cy.on('tap', (evt: EventObject) => {
      if (evt.target === cy) {
        setSelectedNode(null);
      }
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
    };
  }, [graphData, layoutName, selectedMerchantId]);

  const handleFit = () => {
    cyRef.current?.fit(undefined, 40);
  };

  const handleZoomIn = () => {
    if (cyRef.current) {
      cyRef.current.zoom(cyRef.current.zoom() * 1.25);
    }
  };

  const handleZoomOut = () => {
    if (cyRef.current) {
      cyRef.current.zoom(cyRef.current.zoom() * 0.8);
    }
  };

  const handleResetLayout = () => {
    if (cyRef.current) {
      cyRef.current.layout({ name: layoutName, animate: true, animationDuration: 400 }).run();
    }
  };

  return (
    <div className="relative w-full rounded-md border border-[#2A2D35] overflow-hidden bg-[#14161B] font-sans">
      {/* Top Toolbar */}
      <div className="absolute top-3 left-3 right-3 z-10 flex items-center justify-between pointer-events-none">
        <div className="bg-[#1C1F26] px-3 py-1.5 rounded border border-[#2A2D35] flex items-center gap-2 pointer-events-auto">
          <Layers className="h-3.5 w-3.5 text-[#B8862E]" />
          <span className="text-xs font-semibold text-[#E8E6DE]">{title || 'Multi-entity graph'}</span>
          {graphData && (
            <span className="text-[11px] text-[#8B8F98]">
              (<span className="font-mono">{graphData.nodes.length}</span> nodes · <span className="font-mono">{graphData.edges.length}</span> edges)
            </span>
          )}
          {graphData?.ring_id && (
            <span className="ml-1 text-[10.5px] font-mono font-medium px-2 py-0.5 rounded bg-[rgba(168,61,61,0.15)] text-[#A83D3D] border border-[#A83D3D]/40">
              {graphData.ring_id}
            </span>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-1 bg-[#1C1F26] p-1 rounded border border-[#2A2D35] pointer-events-auto">
          <button
            onClick={handleZoomIn}
            title="Zoom in"
            className="p-1 rounded hover:bg-[#20232B] text-[#8B8F98] hover:text-[#E8E6DE] transition-colors cursor-pointer"
          >
            <ZoomIn className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={handleZoomOut}
            title="Zoom out"
            className="p-1 rounded hover:bg-[#20232B] text-[#8B8F98] hover:text-[#E8E6DE] transition-colors cursor-pointer"
          >
            <ZoomOut className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={handleFit}
            title="Fit view"
            className="p-1 rounded hover:bg-[#20232B] text-[#8B8F98] hover:text-[#E8E6DE] transition-colors cursor-pointer"
          >
            <Maximize2 className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={handleResetLayout}
            title="Reset layout"
            className="p-1 rounded hover:bg-[#20232B] text-[#8B8F98] hover:text-[#E8E6DE] transition-colors cursor-pointer"
          >
            <RotateCcw className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      {/* Legend */}
      <div className="absolute bottom-3 left-3 z-10 bg-[#1C1F26] px-3 py-1.5 rounded border border-[#2A2D35] text-[10.5px] text-[#8B8F98] flex items-center gap-3 pointer-events-auto">
        <span className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-xs bg-[#20232B] border border-[#5A5E68]"></span> Merchant
        </span>
        <span className="flex items-center gap-1">
          <span className="h-2 w-2 rotate-45 bg-[#2A2035] border border-[#7C4D99]"></span> Device
        </span>
        <span className="flex items-center gap-1">
          <span className="h-1.5 w-2.5 rounded-xs bg-[#332917] border border-[#B8862E]"></span> Bank
        </span>
        <span className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-xs bg-[#162D28] border border-[#4B7A6F]"></span> UPI
        </span>
        <span className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-[#20232B] border border-[#5A5E68]"></span> Buyer
        </span>
      </div>

      {/* Main Cytoscape Div */}
      <div ref={containerRef} style={{ height }} className="cytoscape-container cursor-grab active:cursor-grabbing" />

      {/* Node Inspector Side Panel */}
      {selectedNode && (
        <div className="absolute top-14 right-3 z-20 w-64 bg-[#1C1F26] border border-[#2A2D35] rounded-md p-3.5 shadow-xl space-y-2.5">
          <div className="flex items-center justify-between border-b border-[#2A2D35] pb-1.5">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-[#E8E6DE]">
              <Info className="h-3.5 w-3.5 text-[#B8862E]" />
              <span>Entity details</span>
            </div>
            <button
              onClick={() => setSelectedNode(null)}
              className="text-[#8B8F98] hover:text-[#E8E6DE] text-xs px-1 cursor-pointer font-mono"
            >
              ✕
            </button>
          </div>

          <div className="space-y-1.5 text-xs">
            <div className="flex justify-between">
              <span className="text-[#8B8F98]">Type:</span>
              <span className="font-medium text-[#E8E6DE]">{selectedNode.entity_type.replace('_', ' ')}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#8B8F98]">Identifier:</span>
              <span className="font-mono text-[#E8E6DE] truncate max-w-[130px]" title={selectedNode.id}>
                {selectedNode.id}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#8B8F98]">Label:</span>
              <span className="font-medium text-[#E8E6DE] truncate max-w-[130px]">{selectedNode.label}</span>
            </div>
            {selectedNode.risk_score !== undefined && selectedNode.risk_score > 0 && (
              <div className="flex justify-between">
                <span className="text-[#8B8F98]">Risk score:</span>
                <span className="font-mono font-bold text-[#A83D3D]">{selectedNode.risk_score.toFixed(1)}</span>
              </div>
            )}
          </div>

          {/* Quick Merchant Investigation Action */}
          {selectedNode.entity_type === 'MERCHANT' && onSelectMerchant && (
            <button
              onClick={() => onSelectMerchant(selectedNode.id)}
              className="w-full mt-2 flex items-center justify-center gap-1.5 py-1.5 px-3 rounded bg-[#20232B] hover:bg-[#2A2D35] border border-[#2A2D35] text-[#E8E6DE] font-medium text-xs transition-colors cursor-pointer"
            >
              <ExternalLink className="h-3 w-3" />
              <span>Investigate merchant</span>
            </button>
          )}
        </div>
      )}
    </div>
  );
};
