import React from "react";
import "./Dashboard.css";

const Dashboard = () => {
  return (
    <div className="dashboard-root">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <span className="logo-iff">iff</span>
          <span className="logo-ai">AutoList AI</span>
        </div>
        <nav className="sidebar-nav">
          <a className="active" href="#">Dashboard</a>
          <a href="#">My Task</a>
          <a href="#">Calendar</a>
          <a href="#">Integration</a>
        </nav>
      </aside>
      <main className="dashboard-main">
        <header className="dashboard-header">
          <h2>Dashboard</h2>
          <div className="greeting">Good Afternoon!<br /><span>Here's what's on your agenda today.</span></div>
        </header>
        <section className="summary-cards">
          <div className="summary-card">
            <div className="summary-title">Today's Task</div>
            <div className="summary-value">1</div>
            <div className="summary-desc">1 Completed</div>
          </div>
          <div className="summary-card">
            <div className="summary-title">Overdue</div>
            <div className="summary-value overdue">3</div>
            <div className="summary-desc">Need Attention</div>
          </div>
          <div className="summary-card">
            <div className="summary-title">Urgent Tasks</div>
            <div className="summary-value urgent">3</div>
            <div className="summary-desc">High Priority</div>
          </div>
          <div className="summary-card">
            <div className="summary-title">Completion Rate</div>
            <div className="summary-value completion">17%</div>
            <div className="summary-bar"><div className="bar-fill" style={{width: "17%"}}></div></div>
            <div className="summary-desc">1 of 6 tasks completed</div>
          </div>
        </section>
        <section className="ai-insights">
          <div className="ai-insights-header">
            <span className="ai-insights-title">AI Insights</span>
            <span className="ai-insights-link">View All Insights &rarr;</span>
          </div>
          <div className="ai-insights-list">
            <div className="ai-insight priority">High Priority Task Due Soon<br /><span>Your quarterly reports are due tomorrow. Consider prioritizing this over other tasks.</span></div>
            <div className="ai-insight priority">Break Down Complex Task<br /><span>The presentation task could be broken into smaller, manageable sub tasks.</span></div>
            <div className="ai-insight priority">Productivity Pattern Detected.<br /><span>You complete most tasks in the morning. Consider scheduling important tasks earlier.</span></div>
          </div>
        </section>
        <section className="dashboard-bottom">
          <div className="upcoming-tasks">
            <div className="upcoming-header">
              <span>Upcoming Task</span>
              <span className="upcoming-link">View All Insights</span>
            </div>
            <div className="upcoming-sub">Your Next 5 Scheduled Tasks</div>
            <div className="upcoming-list">
              <div className="upcoming-task">
                <span>Review Quarterly Reports</span>
                <span className="tag urgent">urgent</span>
                <span className="upcoming-date">7/16/2025</span>
              </div>
              <div className="upcoming-task">
                <span>Prepare Presentation Slides</span>
                <span className="tag urgent">urgent</span>
                <span className="upcoming-date">7/17/2025</span>
              </div>
              <div className="upcoming-task">
                <span>Schedule Doctor Appointment</span>
                <span className="tag urgent">urgent</span>
                <span className="upcoming-date">7/18/2025</span>
              </div>
              <div className="upcoming-task">
                <span>Team Lunch Meeting</span>
                <span className="tag medium">medium</span>
                <span className="upcoming-date">7/21/2025</span>
              </div>
              <div className="upcoming-task">
                <span>Dentist Appointment</span>
                <span className="tag high">high</span>
                <span className="upcoming-date">7/24/2025</span>
              </div>
            </div>
          </div>
          <div className="quick-actions">
            <div className="quick-header">Quick Actions</div>
            <div className="quick-sub">Common tasks to get you started</div>
            <div className="quick-list">
              <div className="quick-action"><span role="img" aria-label="plus">📝</span> Create New Task</div>
              <div className="quick-action"><span role="img" aria-label="calendar">📅</span> View Today's schedule</div>
              <div className="quick-action"><span role="img" aria-label="overdue">⏰</span> Review overdue task</div>
              <div className="quick-action"><span role="img" aria-label="ai">⚡</span> Get AI suggestion</div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default Dashboard;
