import React, { useMemo } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Handle,
  Position,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';

// --- Custom Flow Nodes ---

// 1. Learner Input Node
function LearnerInputNode({ data }) {
  return (
    <div className={`rf-custom-node rf-input-node ${data.isActive ? 'active' : ''}`}>
      <Handle type="source" position={Position.Right} id="out" />
      <div className="rf-node-header">
        <span className="rf-node-icon">📝</span>
        <div className="rf-node-title-group">
          <span className="rf-node-tag">Input Stage</span>
          <h4>Learner Response</h4>
        </div>
      </div>
      <div className="rf-node-body">
        <div className="rf-meta-row">
          <span className="rf-meta-label">Predicted Answer:</span>
          <span className="rf-meta-val mono">{data.studentAnswer || '(awaiting answer)'}</span>
        </div>
        {data.studentReasoning && (
          <div className="rf-meta-row rf-reasoning-preview">
            <span className="rf-meta-label">Reasoning:</span>
            <span className="rf-meta-snippet">"{data.studentReasoning.slice(0, 55)}{data.studentReasoning.length > 55 ? '...' : ''}"</span>
          </div>
        )}
      </div>
    </div>
  );
}

// 2. Evidence Extractor Node (AST, Sandbox, Text Cues)
function EvidenceExtractorNode({ data }) {
  const isTriggered = Boolean(data.evidenceText);
  return (
    <div className={`rf-custom-node rf-evidence-node ${isTriggered ? 'triggered' : ''} ${data.type}`}>
      <Handle type="target" position={Position.Left} id="in" />
      <Handle type="source" position={Position.Right} id="out" />
      <div className="rf-node-header">
        <span className="rf-node-icon">{data.icon}</span>
        <div className="rf-node-title-group">
          <span className="rf-node-tag">{data.category}</span>
          <h4>{data.title}</h4>
        </div>
      </div>
      <div className="rf-node-body">
        <div className="rf-status-pill">
          <span className={`dot ${isTriggered ? 'dot-active' : ''}`} />
          <span>{isTriggered ? 'Pattern Signal Detected' : 'Standby / Analyzing'}</span>
        </div>
        {isTriggered && (
          <div className="rf-evidence-snippet">
            {data.evidenceText}
          </div>
        )}
      </div>
    </div>
  );
}

// 3. Fusion & Nemotron NIM Node
function DiagnosticFusionNode({ data }) {
  const isProcessing = data.isProcessing;
  const isDiagnosed = Boolean(data.diagnosisResult);

  return (
    <div className={`rf-custom-node rf-fusion-node ${isDiagnosed ? 'diagnosed' : ''} ${isProcessing ? 'processing' : ''}`}>
      <Handle type="target" position={Position.Left} id="in" />
      <Handle type="source" position={Position.Right} id="out" />
      <div className="rf-node-header">
        <span className="rf-node-icon">⚡</span>
        <div className="rf-node-title-group">
          <span className="rf-node-tag">Fusion & NIM Core</span>
          <h4>NVIDIA Nemotron 30B</h4>
        </div>
      </div>
      <div className="rf-node-body">
        <div className="rf-model-badge">nvidia/nemotron-3.5-lightning</div>
        <p className="rf-fusion-desc">
          Fuses deterministic AST, runtime sandbox trace, and lexical reasoning markers to classify misconception.
        </p>
        {isProcessing && (
          <div className="rf-processing-banner">
            <span className="loading-spinner" style={{ width: 14, height: 14 }} />
            <span>Analyzing cognitive cues...</span>
          </div>
        )}
      </div>
    </div>
  );
}

// 4. Misconception Diagnosis Outcome Node
function DiagnosisOutcomeNode({ data }) {
  const res = data.diagnosisResult;
  const isDiagnosed = Boolean(res);
  const isCorrect = res?.status === 'CORRECT';
  const isModelUnavail = res?.status === 'MODEL_UNAVAILABLE';

  return (
    <div className={`rf-custom-node rf-outcome-node ${isCorrect ? 'outcome-correct' : isModelUnavail ? 'outcome-error' : isDiagnosed ? 'outcome-diagnosed' : ''}`}>
      <Handle type="target" position={Position.Left} id="in" />
      <Handle type="source" position={Position.Right} id="out" />
      <div className="rf-node-header">
        <span className="rf-node-icon">{isCorrect ? '🎉' : isDiagnosed ? '🎯' : '⏳'}</span>
        <div className="rf-node-title-group">
          <span className="rf-node-tag">Diagnostic Decision</span>
          <h4>{isCorrect ? 'Sound Understanding' : isDiagnosed ? `Diagnosed: ${res.primary?.id || res.status}` : 'Awaiting Diagnosis'}</h4>
        </div>
      </div>
      <div className="rf-node-body">
        {isDiagnosed ? (
          <>
            <div className="rf-confidence-gauge">
              <div className="rf-gauge-header">
                <span>Model Confidence</span>
                <span className="mono">{(Number(res.primary?.confidence || 0) * 100).toFixed(0)}%</span>
              </div>
              <div className="rf-gauge-bar">
                <div
                  className="rf-gauge-fill"
                  style={{ width: `${Number(res.primary?.confidence || 0) * 100}%` }}
                />
              </div>
            </div>
            {res.primary?.name && (
              <div className="rf-misc-title">{res.primary.name}</div>
            )}
            {res.expert_reasoning && (
              <p className="rf-expert-note">"{res.expert_reasoning.slice(0, 75)}..."</p>
            )}
          </>
        ) : (
          <p className="rf-standby-text">Submit your code and reasoning to trigger multi-modal cognitive diagnosis.</p>
        )}
      </div>
    </div>
  );
}

// 5. Scaffolding & Remediation Node
function ScaffoldingNode({ data }) {
  const intervention = data.interventionResult;
  const isTriggered = Boolean(intervention);

  return (
    <div className={`rf-custom-node rf-scaffold-node ${isTriggered ? 'triggered' : ''}`}>
      <Handle type="target" position={Position.Left} id="in" />
      <Handle type="source" position={Position.Right} id="out" />
      <div className="rf-node-header">
        <span className="rf-node-icon">💡</span>
        <div className="rf-node-title-group">
          <span className="rf-node-tag">Pedagogical Scaffolding</span>
          <h4>Adaptive Intervention</h4>
        </div>
      </div>
      <div className="rf-node-body">
        {isTriggered ? (
          <>
            <span className="rf-tier-pill">Tier: {intervention.type || 'Hint'}</span>
            <p className="rf-scaffold-preview">
              "{intervention.content ? intervention.content.slice(0, 65) + '...' : 'Targeted remediation applied.'}"
            </p>
          </>
        ) : (
          <span className="rf-standby-text">6-Tier Hierarchical Scaffolding (Zero answer leakage)</span>
        )}
      </div>
    </div>
  );
}

// 6. Independent Resolution Node
function ResolutionNode({ data }) {
  const res = data.resolutionResult;
  const isResolved = res?.status === 'LIKELY_RESOLVED';
  const hasResult = Boolean(res);

  return (
    <div className={`rf-custom-node rf-resolution-node ${isResolved ? 'resolved' : hasResult ? 'unresolved' : ''}`}>
      <Handle type="target" position={Position.Left} id="in" />
      <div className="rf-node-header">
        <span className="rf-node-icon">{isResolved ? '✅' : hasResult ? '⚠️' : '🔄'}</span>
        <div className="rf-node-title-group">
          <span className="rf-node-tag">Cognitive Model</span>
          <h4>Transfer &amp; Resolution</h4>
        </div>
      </div>
      <div className="rf-node-body">
        {hasResult ? (
          <>
            <span className={`rf-res-badge ${isResolved ? 'badge-pass' : 'badge-fail'}`}>
              {res.status}
            </span>
            <div className="rf-transfer-stats">
              <span>Transfer: {res.evidence?.transfer_problem ? 'Passed' : 'Pending'}</span>
              <span>Confidence: {(Number(res.confidence || 0) * 100).toFixed(0)}%</span>
            </div>
          </>
        ) : (
          <span className="rf-standby-text">Isomorphic &amp; Transfer Re-testing with Bayesian Mastery Updates</span>
        )}
      </div>
    </div>
  );
}

const nodeTypes = {
  learnerInput: LearnerInputNode,
  evidenceExtractor: EvidenceExtractorNode,
  diagnosticFusion: DiagnosticFusionNode,
  diagnosisOutcome: DiagnosisOutcomeNode,
  scaffolding: ScaffoldingNode,
  resolution: ResolutionNode,
};

export default function DiagnosisFlowChart({
  studentAnswer,
  studentReasoning,
  diagnosisResult,
  interventionResult,
  resolutionResult,
  loading,
  journeyStep,
}) {
  // Extract specific evidence traces from diagnosisResult if available
  const evidenceList = diagnosisResult?.evidence || [];
  const astEvidence = evidenceList.find((e) => e.toLowerCase().includes('ast')) || '';
  const execEvidence = evidenceList.find((e) => e.toLowerCase().includes('runtime') || e.toLowerCase().includes('output') || e.toLowerCase().includes('symptom')) || '';
  const textEvidence = evidenceList.find((e) => e.toLowerCase().includes('reasoning') || e.toLowerCase().includes('cue') || e.toLowerCase().includes('stated')) || '';

  const isDiagnosed = Boolean(diagnosisResult);
  const isIntervention = Boolean(interventionResult);
  const isResolved = Boolean(resolutionResult);

  // Define Nodes layout (generous vertical and horizontal spacing to prevent overlap)
  const nodes = useMemo(() => [
    // Column 1: Input (x: 20, centered at y: 300)
    {
      id: 'input-1',
      type: 'learnerInput',
      position: { x: 20, y: 300 },
      data: {
        studentAnswer,
        studentReasoning,
        isActive: Boolean(studentAnswer || studentReasoning),
      },
    },

    // Column 2: Evidence Extractors (x: 410, y: 10, 300, 590 - 290px gap)
    {
      id: 'ev-ast',
      type: 'evidenceExtractor',
      position: { x: 410, y: 10 },
      data: {
        title: 'AST Structural Analyzer',
        category: 'Static Analysis',
        type: 'ast',
        icon: '🌲',
        evidenceText: astEvidence || (studentAnswer ? 'Scanning AST syntax & control flow...' : ''),
      },
    },
    {
      id: 'ev-sandbox',
      type: 'evidenceExtractor',
      position: { x: 410, y: 300 },
      data: {
        title: 'Sandboxed Execution',
        category: 'Runtime Trace',
        type: 'exec',
        icon: '⚡',
        evidenceText: execEvidence || (studentAnswer ? 'Subprocess runner active (timeout 2.0s)' : ''),
      },
    },
    {
      id: 'ev-text',
      type: 'evidenceExtractor',
      position: { x: 410, y: 590 },
      data: {
        title: 'Reasoning Cue Detector',
        category: 'Verbalization',
        type: 'text',
        icon: '💬',
        evidenceText: textEvidence || (studentReasoning ? `Verbal cues extracted (${studentReasoning.length} chars)` : ''),
      },
    },

    // Column 3: Fusion & Nemotron Core (x: 810, centered at y: 290)
    {
      id: 'fusion-core',
      type: 'diagnosticFusion',
      position: { x: 810, y: 290 },
      data: {
        isProcessing: loading,
        diagnosisResult,
      },
    },

    // Column 4: Diagnosis Outcome (x: 1210, centered at y: 280)
    {
      id: 'diagnosis-outcome',
      type: 'diagnosisOutcome',
      position: { x: 1210, y: 280 },
      data: {
        diagnosisResult,
      },
    },

    // Column 5: Scaffolding (x: 1610, y: 100)
    {
      id: 'scaffolding-step',
      type: 'scaffolding',
      position: { x: 1610, y: 100 },
      data: {
        interventionResult,
      },
    },

    // Column 6: Resolution & Bayesian Model (x: 1610, y: 460)
    {
      id: 'resolution-step',
      type: 'resolution',
      position: { x: 1610, y: 460 },
      data: {
        resolutionResult,
      },
    },
  ], [
    studentAnswer,
    studentReasoning,
    diagnosisResult,
    interventionResult,
    resolutionResult,
    loading,
    astEvidence,
    execEvidence,
    textEvidence,
  ]);

  // Define Edges with crisp high-contrast colors for White Theme
  const edges = useMemo(() => [
    // Input -> Evidence Extractors
    {
      id: 'e-in-ast',
      source: 'input-1',
      target: 'ev-ast',
      animated: Boolean(studentAnswer),
      style: { stroke: studentAnswer ? '#0284c7' : '#cbd5e1', strokeWidth: studentAnswer ? 2.5 : 1.5 },
      markerEnd: { type: MarkerType.ArrowClosed, color: studentAnswer ? '#0284c7' : '#94a3b8' },
    },
    {
      id: 'e-in-sandbox',
      source: 'input-1',
      target: 'ev-sandbox',
      animated: Boolean(studentAnswer),
      style: { stroke: studentAnswer ? '#4f46e5' : '#cbd5e1', strokeWidth: studentAnswer ? 2.5 : 1.5 },
      markerEnd: { type: MarkerType.ArrowClosed, color: studentAnswer ? '#4f46e5' : '#94a3b8' },
    },
    {
      id: 'e-in-text',
      source: 'input-1',
      target: 'ev-text',
      animated: Boolean(studentReasoning),
      style: { stroke: studentReasoning ? '#9333ea' : '#cbd5e1', strokeWidth: studentReasoning ? 2.5 : 1.5 },
      markerEnd: { type: MarkerType.ArrowClosed, color: studentReasoning ? '#9333ea' : '#94a3b8' },
    },

    // Evidence Extractors -> Fusion Core
    {
      id: 'e-ast-fusion',
      source: 'ev-ast',
      target: 'fusion-core',
      animated: isDiagnosed || loading,
      style: { stroke: isDiagnosed ? '#0284c7' : '#cbd5e1', strokeWidth: isDiagnosed ? 2.5 : 1.5 },
      markerEnd: { type: MarkerType.ArrowClosed, color: isDiagnosed ? '#0284c7' : '#94a3b8' },
    },
    {
      id: 'e-sandbox-fusion',
      source: 'ev-sandbox',
      target: 'fusion-core',
      animated: isDiagnosed || loading,
      style: { stroke: isDiagnosed ? '#4f46e5' : '#cbd5e1', strokeWidth: isDiagnosed ? 2.5 : 1.5 },
      markerEnd: { type: MarkerType.ArrowClosed, color: isDiagnosed ? '#4f46e5' : '#94a3b8' },
    },
    {
      id: 'e-text-fusion',
      source: 'ev-text',
      target: 'fusion-core',
      animated: isDiagnosed || loading,
      style: { stroke: isDiagnosed ? '#9333ea' : '#cbd5e1', strokeWidth: isDiagnosed ? 2.5 : 1.5 },
      markerEnd: { type: MarkerType.ArrowClosed, color: isDiagnosed ? '#9333ea' : '#94a3b8' },
    },

    // Fusion Core -> Diagnosis Outcome
    {
      id: 'e-fusion-outcome',
      source: 'fusion-core',
      target: 'diagnosis-outcome',
      animated: isDiagnosed,
      style: {
        stroke: isDiagnosed ? '#16a34a' : '#cbd5e1',
        strokeWidth: isDiagnosed ? 3 : 1.5,
      },
      markerEnd: { type: MarkerType.ArrowClosed, color: isDiagnosed ? '#16a34a' : '#94a3b8' },
    },

    // Diagnosis Outcome -> Scaffolding / Intervention
    {
      id: 'e-outcome-scaffold',
      source: 'diagnosis-outcome',
      target: 'scaffolding-step',
      animated: isIntervention,
      style: {
        stroke: isIntervention ? '#0284c7' : '#cbd5e1',
        strokeWidth: isIntervention ? 2.5 : 1.5,
      },
      markerEnd: { type: MarkerType.ArrowClosed, color: isIntervention ? '#0284c7' : '#94a3b8' },
    },

    // Diagnosis Outcome / Scaffolding -> Resolution
    {
      id: 'e-scaffold-res',
      source: 'scaffolding-step',
      target: 'resolution-step',
      animated: isResolved,
      style: {
        stroke: isResolved ? '#16a34a' : '#cbd5e1',
        strokeWidth: isResolved ? 2.5 : 1.5,
      },
      markerEnd: { type: MarkerType.ArrowClosed, color: isResolved ? '#16a34a' : '#94a3b8' },
    },
    {
      id: 'e-outcome-res',
      source: 'diagnosis-outcome',
      target: 'resolution-step',
      animated: isResolved,
      style: {
        stroke: isResolved ? '#16a34a' : '#cbd5e1',
        strokeWidth: isResolved ? 2 : 1,
        strokeDasharray: '4 4',
      },
      markerEnd: { type: MarkerType.ArrowClosed, color: isResolved ? '#16a34a' : '#94a3b8' },
    },
  ], [studentAnswer, studentReasoning, isDiagnosed, isIntervention, isResolved, loading]);

  return (
    <div className="reactflow-diagnosis-container white-theme">
      <div className="rf-flow-header">
        <div className="rf-header-left">
          <div className="rf-live-badge">
            <span className="live-pulse" />
            <span>Interactive Diagnostic Pipeline</span>
          </div>
          <span className="rf-subtext">Multi-source evidence fusion &amp; cognitive trace graph</span>
        </div>
        <div className="rf-header-actions">
          <span className="rf-tag-pill">Pan &amp; Zoom Enabled</span>
          {isDiagnosed && <span className="rf-tag-pill tag-success">✓ Diagnosis Mapped</span>}
        </div>
      </div>

      <div className="rf-canvas-wrapper">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.12 }}
          minZoom={0.2}
          maxZoom={1.6}
          attributionPosition="bottom-right"
        >
          <Background color="#cbd5e1" gap={20} size={1.2} />
          <Controls className="rf-custom-controls" showInteractive={false} />
          <MiniMap
            className="rf-custom-minimap"
            nodeColor={(n) => {
              if (n.type === 'learnerInput') return '#4f46e5';
              if (n.type === 'evidenceExtractor') return '#0284c7';
              if (n.type === 'diagnosticFusion') return '#9333ea';
              if (n.type === 'diagnosisOutcome') return '#16a34a';
              if (n.type === 'scaffolding') return '#d97706';
              return '#94a3b8';
            }}
            maskColor="rgba(241, 245, 249, 0.75)"
          />
        </ReactFlow>
      </div>
    </div>
  );
}
