import React from 'react';
import './ReviewDashboard.css';

// Adapted placeholder data to fit the new design
const currentProjectsData = [
  { id: 'proj001', name: 'Project Alpha', status: 'In Progress', lastUpdated: '2024-01-20' },
  { id: 'proj002', name: 'Project Beta', status: 'Completed', lastUpdated: '2024-01-15' },
  { id: 'proj003', name: 'Project Gamma', status: 'In Progress', lastUpdated: '2024-01-22' },
];

const reviewQueueData = [
  { id: 'item001', source: 'Source A', summary: 'Summary of findings from Source A' },
  { id: 'item002', source: 'Source B', summary: 'Summary of findings from Source B' },
  { id: 'item003', source: 'Source C', summary: 'Summary of findings from Source C' },
  { id: 'item004', source: 'Source D', summary: 'Summary of findings from Source D' },
  { id: 'item005', source: 'Source E', summary: 'Summary of findings from Source E' },
];

const navigationLinks = [
  { href: '#', icon: 'home', text: 'Dashboard' },
  { href: '#', icon: 'folder_open', text: 'Projects' },
  { href: '#', icon: 'search', text: 'Review', active: true }, // Mark Review as active
  { href: '#', icon: 'settings', text: 'Settings' },
];

const helpLink = { href: '#', icon: 'help_outline', text: 'Help' };

function ReviewDashboard() {
  return (
    <div className="rd-page-container"> {/* Corresponds to body bg-slate-50 and flex layout */}
      <div className="rd-layout-wrapper"> {/* Corresponds to layout-container flex h-full grow flex-col */}
        <div className="rd-flex-main-area"> {/* Corresponds to flex flex-1 */}
          <aside className="rd-sidebar">
            <div>
              <div className="rd-sidebar-header">
                <h1 className="rd-sidebar-title">Knowledge AI</h1>
                <p className="rd-sidebar-version">v1.0</p>
              </div>
              <nav className="rd-nav-list">
                {navigationLinks.map(link => (
                  <a
                    key={link.text}
                    href={link.href}
                    className={`rd-nav-link ${link.active ? 'rd-nav-link-active' : ''}`}
                  >
                    <span className="material-icons rd-nav-icon">{link.icon}</span>
                    <span className="rd-nav-text">{link.text}</span>
                  </a>
                ))}
              </nav>
            </div>
            <div className="rd-sidebar-footer">
              <a href={helpLink.href} className="rd-nav-link">
                <span className="material-icons rd-nav-icon">{helpLink.icon}</span>
                <span className="rd-nav-text">{helpLink.text}</span>
              </a>
            </div>
          </aside>

          <main className="rd-main-content">
            <header className="rd-main-header">
              <h1 className="rd-main-title-text">Review Dashboard</h1>
            </header>

            <section className="rd-content-section">
              <h2 className="rd-section-title">Current Projects</h2>
              <div className="rd-table-container">
                <table className="rd-table">
                  <thead className="rd-table-thead">
                    <tr>
                      <th className="rd-th">Project Name</th>
                      <th className="rd-th">Status</th>
                      <th className="rd-th">Last Updated</th>
                      <th className="rd-th rd-th-actions">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="rd-table-tbody">
                    {currentProjectsData.map(project => (
                      <tr key={project.id} className="rd-tr">
                        <td className="rd-td rd-td-project-name">{project.name}</td>
                        <td className="rd-td">
                          <span className={`rd-status-badge ${project.status === 'In Progress' ? 'rd-status-yellow' : 'rd-status-green'}`}>
                            {project.status}
                          </span>
                        </td>
                        <td className="rd-td rd-td-date">{project.lastUpdated}</td>
                        <td className="rd-td rd-td-actions">
                          <button className="rd-action-button">View</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            <section className="rd-content-section">
              <h2 className="rd-section-title">Review Queue</h2>
              <div className="rd-table-container">
                <table className="rd-table">
                  <thead className="rd-table-thead">
                    <tr>
                      <th className="rd-th">Source</th>
                      <th className="rd-th">Summary</th>
                      <th className="rd-th rd-th-actions">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="rd-table-tbody">
                    {reviewQueueData.map(item => (
                      <tr key={item.id} className="rd-tr">
                        <td className="rd-td rd-td-source-name">{item.source}</td>
                        <td className="rd-td rd-td-summary">{item.summary}</td>
                        <td className="rd-td rd-td-actions">
                          <button className="rd-action-button">Review</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          </main>
        </div>
      </div>
    </div>
  );
}

export default ReviewDashboard;
