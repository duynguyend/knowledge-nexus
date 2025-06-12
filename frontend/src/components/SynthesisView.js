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
        <header className="sv-header">
          <div className="sv-header-left">
            <div className="sv-header-logo-title">
              <svg className="sv-logo-svg" fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                {/* SVG Path from design */}
                <path d="M39.5563 34.1455V13.8546C39.5563 15.708 36.8773 17.3437 32.7927 18.3189C30.2914 18.916 27.263 19.2655 24 19.2655C20.737 19.2655 17.7086 18.916 15.2073 18.3189C11.1227 17.3437 8.44365 15.708 8.44365 13.8546V34.1455C8.44365 35.9988 11.1227 37.6346 15.2073 38.6098C17.7086 39.2069 20.737 39.5564 24 39.5564C27.263 39.5564 30.2914 39.2069 32.7927 38.6098C36.8773 37.6346 39.5563 35.9988 39.5563 34.1455Z" fill="currentColor"></path>
                <path clipRule="evenodd" d="M10.4485 13.8519C10.4749 13.9271 10.6203 14.246 11.379 14.7361C12.298 15.3298 13.7492 15.9145 15.6717 16.3735C18.0007 16.9296 20.8712 17.2655 24 17.2655C27.1288 17.2655 29.9993 16.9296 32.3283 16.3735C34.2508 15.9145 35.702 15.3298 36.621 14.7361C37.3796 14.246 37.5251 13.9271 37.5515 13.8519C37.5287 13.7876 37.4333 13.5973 37.0635 13.2931C36.5266 12.8516 35.6288 12.3647 34.343 11.9175C31.79 11.0295 28.1333 10.4437 24 10.4437C19.8667 10.4437 16.2099 11.0295 13.657 11.9175C12.3712 12.3647 11.4734 12.8516 10.9365 13.2931C10.5667 13.5973 10.4713 13.7876 10.4485 13.8519ZM37.5563 18.7877C36.3176 19.3925 34.8502 19.8839 33.2571 20.2642C30.5836 20.9025 27.3973 21.2655 24 21.2655C20.6027 21.2655 17.4164 20.9025 14.7429 20.2642C13.1498 19.8839 11.6824 19.3925 10.4436 18.7877V34.1275C10.4515 34.1545 10.5427 34.4867 11.379 35.027C12.298 35.6207 13.7492 36.2054 15.6717 36.6644C18.0007 37.2205 20.8712 37.5564 24 37.5564C27.1288 37.5564 29.9993 37.2205 32.3283 36.6644C34.2508 36.2054 35.702 35.6207 36.621 35.027C37.4573 34.4867 37.5485 34.1546 37.5563 34.1275V18.7877ZM41.5563 13.8546V34.1455C41.5563 36.1078 40.158 37.5042 38.7915 38.3869C37.3498 39.3182 35.4192 40.0389 33.2571 40.5551C30.5836 41.1934 27.3973 41.5564 24 41.5564C20.6027 41.5564 17.4164 41.1934 14.7429 40.5551C12.5808 40.0389 10.6502 39.3182 9.20848 38.3869C7.84205 37.5042 6.44365 36.1078 6.44365 34.1455L6.44365 13.8546C6.44365 12.2684 7.37223 11.0454 8.39581 10.2036C9.43325 9.3505 10.8137 8.67141 12.343 8.13948C15.4203 7.06909 19.5418 6.44366 24 6.44366C28.4582 6.44366 32.5797 7.06909 35.657 8.13948C37.1863 8.67141 38.5667 9.3505 39.6042 10.2036C40.6278 11.0454 41.5563 12.2684 41.5563 13.8546Z" fill="currentColor" clipRule="evenodd"></path>
              </svg>
              <h2 className="sv-header-title-text">Knowledge Weaver</h2>
            </div>
            <nav className="sv-nav">
              <a className="sv-nav-link" href="#">Home</a>
              <a className="sv-nav-link" href="#">Agents</a>
              <a className="sv-nav-link sv-nav-link-active" href="#">Knowledge Base</a>
              <a className="sv-nav-link" href="#">Settings</a>
            </nav>
          </div>
          <div className="sv-header-right">
            <label className="sv-search-label">
              <div className="sv-search-icon-wrapper">
                {/* Using Material Icons as per synthesis.html design */}
                <span className="material-icons sv-search-icon">search</span>
              </div>
              <input className="sv-search-input" placeholder="Search..." defaultValue="" />
            </label>
            <div className="sv-profile-pic" style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuAphXWydUwY8-hWj8Tqt-jzVR93PL5osN-NymEFy_RB10KV33sHYTz8fG4-mdzh2hr5eeBQMBz8Y0-xpUGp9JnmGjhVF4qDWOQ6Q64Gc_x5Hc_2ZhfboXEQiNXScyGsDI4fvAdC93V0DdsBXSfpkhRljFkz7bdOMNndBK76u28HrA3ETIiCwHG9WZGCZLOYSF3t7p9lMko1dOWoOoiVs3yt-DzuFFoUNPskYeViPIonEP4LYC5qbUTNbvkUfzOIrZgTjUjhPZkqF0k")' }}></div>
          </div>
        </header>

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
