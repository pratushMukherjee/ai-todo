import React from "react";
import "./MyTask.css";

const MyTask = () => {
  return (
    <div className="dashboard-root">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <span className="logo-iff">iff</span>
          <span className="logo-ai">AutoList AI</span>
        </div>
        <nav className="sidebar-nav">
          <a href="#">Dashboard</a>
          <a className="active" href="#">My Task</a>
          <a href="#">Calendar</a>
          <a href="#">Integration</a>
        </nav>
      </aside>
      <main className="dashboard-main">
        <header className="dashboard-header">
          <h2>My Task</h2>
          <div className="greeting">Good Afternoon!<br /><span>Here's what's on your agenda today.</span></div>
        </header>
        <section className="summary-cards">
          <div className="summary-card task">
            <div className="summary-title">Today's Task</div>
            <div className="summary-value">6</div>
          </div>
          <div className="summary-card completed">
            <div className="summary-title">Completed</div>
            <div className="summary-value">1</div>
          </div>
          <div className="summary-card scheduled">
            <div className="summary-title">Scheduled</div>
            <div className="summary-value">2</div>
          </div>
          <div className="summary-card urgent">
            <div className="summary-title">Urgent</div>
            <div className="summary-value">3</div>
          </div>
        </section>
        <section className="add-task-section">
          <div className="add-task-header">+ Add New Task</div>
          <div className="add-task-input-row">
            <input className="add-task-input" placeholder="What needs to be done?" />
            <div className="add-task-priority">
              <span>Medium</span>
              <span className="tag high">High</span>
              <span className="tag urgent">Urgent</span>
            </div>
            <button className="add-task-btn" disabled>Add Task &rarr;</button>
            <button className="ai-suggest-btn">AI Suggest</button>
          </div>
        </section>
        <section className="task-list-section">
          <div className="task-list-tabs">
            <button className="tab active">ALL</button>
            <button className="tab">ACTIVE</button>
            <button className="tab">COMPLETED</button>
          </div>
          <div className="task-list">
            <div className="task-list-header">Task</div>
            <div className="task-list-item">
              <input type="checkbox" />
              <span className="task-title">Remember me</span>
              <span className="tag urgent">urgent</span>
              <span className="task-meta">120m 7/16/2025 <span className="task-label">Work</span></span>
              <span className="task-actions">✎ 🗑️</span>
            </div>
            <div className="task-list-item">
              <input type="checkbox" />
              <span className="task-title">Schedule doctor appointment</span>
              <span className="tag urgent">urgent</span>
              <span className="task-meta">90m 7/18/2025 <span className="task-label">Health</span></span>
              <span className="task-actions">✎ 🗑️</span>
            </div>
            <div className="task-list-item">
              <input type="checkbox" />
              <span className="task-title">Prepare presentation slides</span>
              <span className="tag urgent">urgent</span>
              <span className="task-meta">120m 7/17/2025 <span className="task-label">Work</span></span>
              <span className="task-actions">✎ 🗑️</span>
            </div>
            <div className="task-list-item">
              <input type="checkbox" />
              <span className="task-title">Dentist appointment</span>
              <span className="tag high">High</span>
              <span className="task-meta">90m 7/18/2025 <span className="task-label">Health</span></span>
              <span className="task-actions">✎ 🗑️</span>
            </div>
            <div className="task-list-item completed">
              <input type="checkbox" checked readOnly />
              <span className="task-title">Team Lunch meeting</span>
              <span className="tag medium">Medium</span>
              <span className="task-meta">60m 7/14/2025 <span className="task-label">Work</span></span>
              <span className="task-actions">✎ 🗑️</span>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default MyTask; 