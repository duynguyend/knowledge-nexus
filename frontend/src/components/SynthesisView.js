import React from 'react';
import './SynthesisView.css'; // Assuming you'll create this CSS file

function SynthesisView() {
  // Placeholder data - replace with actual data fetching and state management
  const synthesisProgress = {
    currentStep: 'Knowledge Graph Construction',
    details: 'Identifying entities and relationships from verified data sources.',
    percentage: 45,
  };

  const conflicts = [
    {
      id: 'conf001',
      description: 'Discrepancy in reported figures for market size between Source A and Source B.',
      sourcesInvolved: ['Source A (doc_id_001)', 'Source B (doc_id_002)'],
      status: 'Pending Review'
    },
    {
      id: 'conf002',
      description: 'Contradictory statements on the effectiveness of a particular policy.',
      sourcesInvolved: ['Source C (doc_id_003)', 'Source D (doc_id_004)'],
      status: 'Resolved - Chose Source C'
    },
  ];

  return (
    <div className="synthesis-view-container">
      <header className="synthesis-header">
        <h1>Knowledge Synthesis & Conflict Resolution</h1>
        <p>Visualize the data integration process and manage detected conflicts.</p>
      </header>

      <section className="synthesis-section process-overview">
        <h2>Data Integration Process</h2>
        <div className="progress-card">
          <h3>Current Stage: {synthesisProgress.currentStep}</h3>
          <p>{synthesisProgress.details}</p>
          <div className="progress-bar-container-synthesis">
            <div
              className="progress-bar-synthesis"
              style={{ width: `${synthesisProgress.percentage}%` }}
            >
              {synthesisProgress.percentage}%
            </div>
          </div>
        </div>
        <div className="knowledge-graph-placeholder">
          <h4>Knowledge Graph Visualization (Placeholder)</h4>
          <p><em>[Interactive graph showing entities and relationships will be displayed here]</em></p>
          <div className="graph-mockup">
            (Entity A) --[Relates to]--> (Entity B) <br/>
            (Entity C) --[Contradicts]--> (Entity D)
          </div>
        </div>
      </section>

      <section className="synthesis-section conflict-resolution">
        <h2>Conflict Resolution Center</h2>
        <p>Review and resolve discrepancies identified during data synthesis.</p>
        {conflicts.length > 0 ? (
          <table className="conflicts-table">
            <thead>
              <tr>
                <th>Conflict ID</th>
                <th>Description</th>
                <th>Sources Involved</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {conflicts.map(conflict => (
                <tr key={conflict.id}>
                  <td>{conflict.id}</td>
                  <td>{conflict.description}</td>
                  <td>{conflict.sourcesInvolved.join(', ')}</td>
                  <td className={`status-${conflict.status.toLowerCase().replace(/\s+/g, '-')}`}>
                    {conflict.status}
                  </td>
                  <td>
                    {conflict.status === 'Pending Review' && (
                      <button className="resolve-button">Resolve Conflict</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No conflicts detected at this time.</p>
        )}
      </section>
    </div>
  );
}

export default SynthesisView;
