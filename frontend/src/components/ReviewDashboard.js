import React from 'react';
import './ReviewDashboard.css';

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

function ReviewDashboard() {
  return (
    <div className="rd-page-container">
      <main className="rd-main-content">
        <h1 className="rd-page-title">Review Dashboard</h1>
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
  );
}

export default ReviewDashboard;
