import React from 'react';
import './ReviewDashboard.css';

function ReviewDashboard() {
  // Placeholder data - replace with actual data fetching later
  const currentProjects = [
    { id: 'proj001', name: 'AI in Healthcare', status: 'Data Collection', progress: 30 },
    { id: 'proj002', name: 'Climate Change Impact', status: 'Verification', progress: 65 },
  ];

  const reviewQueue = [
    { id: 'task003', project: 'AI in Healthcare', item: 'Source Verification: Nature Article', priority: 'High' },
    { id: 'task004', project: 'Climate Change Impact', item: 'Conflict Resolution: Sea Level Rise Data', priority: 'Medium' },
  ];

  return (
    <div className="review-dashboard-container">
      <header className="review-header">
        <h1>Review & Verification Dashboard</h1>
        <p>Monitor ongoing projects and manage items requiring human review.</p>
      </header>

      <section className="dashboard-section">
        <h2>Current Projects Overview</h2>
        <table className="projects-table">
          <thead>
            <tr>
              <th>Project ID</th>
              <th>Name</th>
              <th>Status</th>
              <th>Progress</th>
            </tr>
          </thead>
          <tbody>
            {currentProjects.map(project => (
              <tr key={project.id}>
                <td>{project.id}</td>
                <td>{project.name}</td>
                <td>{project.status}</td>
                <td>{project.progress}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="dashboard-section">
        <h2>Review Queue</h2>
        <p>Items needing immediate attention for verification or conflict resolution.</p>
        <table className="queue-table">
          <thead>
            <tr>
              <th>Task ID</th>
              <th>Project</th>
              <th>Item for Review</th>
              <th>Priority</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {reviewQueue.map(item => (
              <tr key={item.id}>
                <td>{item.id}</td>
                <td>{item.project}</td>
                <td>{item.item}</td>
                <td className={`priority-${item.priority.toLowerCase()}`}>{item.priority}</td>
                <td><button className="review-action-button">Review Item</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

export default ReviewDashboard;
