import React, { useState } from 'react';
import axios from 'axios';
import { emailToAll } from '../api/agent';
import SuggestionsPanel from './SuggestionsPanel';

function EmailsPanel({ onRefreshTasks, onRefreshCalendar }) {
  const [results, setResults] = useState([]); // [{email, suggested_tasks, created_tasks, ai_analyses}]
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [openIndexes, setOpenIndexes] = useState([]); // Track which cards are open
  const [aiSuggestions, setAISuggestions] = useState([]); // AI suggestions selected by user
  const [aiAnalyses, setAIAnalyses] = useState([]); // All AI analyses from backend

  const fetchAgenticEmails = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await emailToAll();
      setResults(response.results || []);
      // Collect all ai_analyses from all results
      const allAnalyses = [];
      (response.results || []).forEach(res => {
        if (res.ai_analyses) {
          res.ai_analyses.forEach(analysis => {
            allAnalyses.push({
              ...analysis,
              email: res.email
            });
          });
        }
      });
      setAIAnalyses(allAnalyses);
      if (onRefreshTasks) onRefreshTasks();
      if (onRefreshCalendar) onRefreshCalendar();
    } catch (error) {
      setError('Error fetching agentic emails: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const toggleDropdown = (idx) => {
    setOpenIndexes((prev) =>
      prev.includes(idx) ? prev.filter(i => i !== idx) : [...prev, idx]
    );
  };

  const addToAISuggestions = (task) => {
    if (!aiSuggestions.includes(task)) {
      setAISuggestions((prev) => [...prev, task]);
    }
  };

  const removeAISuggestion = (task) => {
    setAISuggestions((prev) => prev.filter((t) => t !== task));
  };

  // Helper to add an analysis as a suggestion
  const addAnalysisAsSuggestion = (analysis) => {
    if (analysis && analysis.chunks && analysis.chunks.length > 0) {
      addToAISuggestions(analysis.chunks[0]);
    } else if (analysis && analysis.subtasks && analysis.subtasks.length > 0) {
      addToAISuggestions(analysis.subtasks[0]);
    } else if (analysis && analysis.people && analysis.people.length > 0) {
      addToAISuggestions(analysis.people[0]);
    }
  };

  return (
    <div className="container">
      <h4 className="mt-4">Email Analysis</h4>
      <button className="btn btn-primary mb-3" onClick={fetchAgenticEmails}>
        {loading ? 'Loading...' : 'Scan Email & Update Everything'}
      </button>
      {error && <div className="alert alert-danger">{error}</div>}
      <ul className="list-group">
        {results.map((res, idx) => (
          <li key={idx} className="list-group-item mb-3 p-0" style={{ border: 'none', background: 'none' }}>
            <div className="card">
              <div className="card-body">
                <div className="d-flex justify-content-between align-items-center">
                  <div>
                    <h6 className="card-subtitle mb-1 text-muted">From: {res.email.from}</h6>
                    <h5 className="card-title mb-0">{res.email.subject}</h5>
                  </div>
                  <button
                    className="btn btn-sm btn-outline-secondary"
                    onClick={() => toggleDropdown(idx)}
                    aria-expanded={openIndexes.includes(idx)}
                  >
                    {openIndexes.includes(idx) ? 'Hide Details' : 'Show Details'}
                  </button>
                </div>
                {openIndexes.includes(idx) && (
                  <div className="mt-3">
                    <p className="card-text"><strong>Body:</strong> {res.email.body}</p>
                    <div>
                      <strong>Suggested Tasks:</strong>
                      <ul>
                        {res.suggested_tasks.map((task, i) => (
                          <li key={i} className="d-flex align-items-center justify-content-between">
                            <span>{task}</span>
                            <button
                              className="btn btn-sm btn-outline-primary ms-2"
                              onClick={() => addToAISuggestions(task)}
                              disabled={aiSuggestions.includes(task)}
                            >
                              {aiSuggestions.includes(task) ? 'Added' : 'Add to AI Suggestions'}
                            </button>
                          </li>
                        ))}
                      </ul>
                    </div>
                    {/* AI Analyses Section */}
                    {res.ai_analyses && res.ai_analyses.length > 0 && (
                      <div className="mt-2">
                        <strong>AI Analyses:</strong>
                        <ul>
                          {res.ai_analyses.map((analysis, i) => (
                            <li key={i} className="d-flex align-items-center justify-content-between">
                              <span>
                                {analysis.chunks && analysis.chunks.length > 0 ? analysis.chunks[0] : JSON.stringify(analysis)}
                              </span>
                              <button
                                className="btn btn-sm btn-outline-success ms-2"
                                onClick={() => addAnalysisAsSuggestion(analysis)}
                              >
                                Add as Task
                              </button>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </li>
        ))}
      </ul>
      {/* AI Suggestions Card */}
      <div className="card mt-4">
        <div className="card-body">
          <h5 className="card-title">AI Suggestions</h5>
          {aiSuggestions.length === 0 ? (
            <div className="text-muted">No suggestions added yet.</div>
          ) : (
            <ul>
              {aiSuggestions.map((sugg, idx) => (
                <li key={idx} className="d-flex align-items-center justify-content-between">
                  <span>{sugg}</span>
                  <button
                    className="btn btn-sm btn-outline-danger ms-2"
                    onClick={() => removeAISuggestion(sugg)}
                  >
                    Remove
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
      {/* Pass AI analyses to SuggestionsPanel if needed elsewhere */}
      {/* <SuggestionsPanel aiAnalyses={aiAnalyses} ... /> */}
      <hr />
      <h4 className="mt-4">Task List</h4>
      {/* The TaskList component should be rendered below this heading in your main page */}
    </div>
  );
}

export default EmailsPanel;
