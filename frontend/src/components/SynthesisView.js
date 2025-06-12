import React from 'react';
import './SynthesisView.css';

// Data for the "Conflict Resolution Example" table, based on the design
const conflictExampleData = [
  {
    source: 'Tech News Today',
    claim: 'Product X launches on July 15th',
    verificationStatus: 'Unverified',
    statusColor: 'yellow', // For styling the badge
    resolution: 'Pending cross-reference',
  },
  {
    source: 'Gadget Reviewer',
    claim: 'Product X launches on July 22nd',
    verificationStatus: 'Verified (Manufacturer)',
    statusColor: 'green',
    resolution: 'July 22nd is the correct launch date',
  },
  {
    source: 'Official Press Release',
    claim: 'Product X launches on July 22nd',
    verificationStatus: 'Authoritative Source',
    statusColor: 'green',
    resolution: '-',
  },
];

// Data for the "Data Integration Process" steps
const integrationSteps = [
  {
    icon: 'search', // Material Symbols Outlined name
    title: 'Source Identification',
    description: 'Agent identifies relevant sources from various repositories.',
  },
  {
    icon: 'file_present', // Using file_present (article could also work)
    title: 'Data Extraction',
    description: 'Agent extracts key information and metadata from identified sources.',
  },
  {
    icon: 'task_alt',
    title: 'Conflict Resolution & Verification',
    description: 'Agent resolves conflicting information using predefined rules and verification protocols.',
  },
  {
    icon: 'storage', // or 'database' or 'dataset'
    title: 'Knowledge Integration',
    description: 'Agent integrates verified and harmonized information into the central knowledge base.',
  },
];

function SynthesisView() {
  return (
    <div className="sv-body-bg">
      <div className="sv-layout-container">
        {/* Header section removed */}
        <main className="sv-main-content">
          <div className="sv-content-wrapper">
            <div className="sv-main-card">
              <div className="sv-section-header">
                <h1 className="sv-main-title">Knowledge Synthesis</h1>
                <p className="sv-main-description">
                  Observe how AI agents integrate information from diverse sources, resolve discrepancies, and construct a unified knowledge base.
                </p>
              </div>

              <section className="sv-section">
                <h2 className="sv-section-title">Data Integration Process</h2>
                <div className="sv-integration-steps-grid">
                  {integrationSteps.map((step, index) => (
                    <React.Fragment key={index}>
                      <div className="sv-step-icon-container">
                        <div className="sv-step-icon-wrapper">
                           {/* Using Material Icons as per synthesis.html design */}
                          <span className="material-icons">{step.icon}</span>
                        </div>
                        {index < integrationSteps.length - 1 && <div className="sv-step-connector"></div>}
                      </div>
                      <div className={`sv-step-content ${index === integrationSteps.length -1 ? 'sv-step-content-last':''}`}>
                        <h3 className="sv-step-title">{step.title}</h3>
                        <p className="sv-step-description">{step.description}</p>
                      </div>
                    </React.Fragment>
                  ))}
                </div>
              </section>

              <section className="sv-section">
                <h2 className="sv-section-title">Knowledge Graph Visualization</h2>
                <p className="sv-section-description">
                  The graph below illustrates the relationships between different pieces of information within the knowledge base. Nodes represent concepts, and edges represent relationships between them.
                </p>
                <div className="sv-graph-placeholder">
                  <p className="sv-graph-placeholder-text">Knowledge Graph Placeholder</p>
                </div>
              </section>

              <section className="sv-section">
                <h2 className="sv-section-title">Conflict Resolution Example</h2>
                <p className="sv-section-description">
                  In this example, two sources provide conflicting information about the launch date of a product. The AI agent verifies the information using additional sources and resolves the conflict.
                </p>
                <div className="sv-table-container">
                  <table className="sv-table">
                    <thead className="sv-table-header">
                      <tr>
                        <th scope="col" className="sv-th">Source</th>
                        <th scope="col" className="sv-th">Claim</th>
                        <th scope="col" className="sv-th">Verification Status</th>
                        <th scope="col" className="sv-th">Resolution</th>
                      </tr>
                    </thead>
                    <tbody className="sv-table-body">
                      {conflictExampleData.map((conflict, index) => (
                        <tr key={index}>
                          <td className="sv-td sv-td-source">{conflict.source}</td>
                          <td className="sv-td">{conflict.claim}</td>
                          <td className="sv-td">
                            <span className={`sv-status-badge sv-status-${conflict.statusColor}`}>
                              {/* Using Material Symbols Outlined for status icons if desired, or simple dot */}
                              <svg className={`sv-status-dot sv-dot-${conflict.statusColor}`} fill="currentColor" viewBox="0 0 8 8">
                                <circle cx="4" cy="4" r="3"></circle>
                              </svg>
                              {conflict.verificationStatus}
                            </span>
                          </td>
                          <td className={`sv-td ${conflict.resolution.includes('correct launch date') ? 'sv-td-resolved' : ''}`}>{conflict.resolution}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default SynthesisView;
