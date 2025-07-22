import React, { useState } from 'react';
import { addFeedback, getFeedbackForTask, semanticSearchTasks } from '../api/tasks';

function TaskList({ tasks, onToggleDone, onDeleteTask }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [sortBy, setSortBy] = useState('priority');
  const [sortDir, setSortDir] = useState('asc');
  const [feedbacks, setFeedbacks] = useState({});
  const [commentInput, setCommentInput] = useState({});

  const handleSemanticSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      const results = await semanticSearchTasks(searchQuery.trim());
      setSearchResults(results);
    } catch (err) {
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  };

  const handleFeedback = async (taskId, rating) => {
    await addFeedback(taskId, rating, null);
    fetchFeedback(taskId);
  };

  const handleComment = async (taskId) => {
    if (!commentInput[taskId]) return;
    await addFeedback(taskId, null, commentInput[taskId]);
    setCommentInput((prev) => ({ ...prev, [taskId]: '' }));
    fetchFeedback(taskId);
  };

  const fetchFeedback = async (taskId) => {
    const data = await getFeedbackForTask(taskId);
    setFeedbacks((prev) => ({ ...prev, [taskId]: data }));
  };

  // Fetch feedback for all tasks on mount or when tasks change
  React.useEffect(() => {
    tasks.forEach((task) => fetchFeedback(task.id));
    // eslint-disable-next-line
  }, [tasks]);

  // Sort tasks by selected field and direction
  const sortedTasks = [...tasks].sort((a, b) => {
    const field = sortBy;
    const aVal = a[field] ?? 99;
    const bVal = b[field] ?? 99;
    if (sortDir === 'asc') return aVal - bVal;
    return bVal - aVal;
  });

  return (
    <>
      <form className="mb-3" onSubmit={handleSemanticSearch}>
        <div className="input-group">
          <input
            type="text"
            className="form-control"
            placeholder="Semantic search tasks..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button className="btn btn-primary" type="submit" disabled={searching}>
            {searching ? 'Searching...' : 'Semantic Search'}
          </button>
        </div>
      </form>
      <div className="mb-2 d-flex align-items-center">
        <span className="me-2">Sort by:</span>
        <select className="form-select form-select-sm w-auto me-2" value={sortBy} onChange={e => setSortBy(e.target.value)}>
          <option value="priority">Priority</option>
          <option value="urgency">Urgency</option>
        </select>
        <button className="btn btn-sm btn-outline-secondary" onClick={() => setSortDir(d => d === 'asc' ? 'desc' : 'asc')}>
          {sortDir === 'asc' ? '↑' : '↓'}
        </button>
      </div>
      {searchResults && searchResults.documents && searchResults.documents.length > 0 && (
        <div className="card mb-3">
          <div className="card-body">
            <h5 className="card-title">Semantic Search Results</h5>
            <ul className="list-group">
              {searchResults.documents[0].map((doc, idx) => (
                <li key={idx} className="list-group-item">
                  {doc}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
      {(!tasks.length && (!searchResults || !searchResults.documents || searchResults.documents.length === 0)) ? (
        <div className="alert alert-info text-center" role="alert">
          No tasks yet — add something!
        </div>
      ) : (
        <table className="table table-striped mt-4">
          <thead>
            <tr>
              <th>Task</th>
              <th>Status</th>
              <th>Priority</th>
              <th>Urgency</th>
              <th>Actions</th>
              <th>Feedback</th>
            </tr>
          </thead>
          <tbody>
            {sortedTasks.map((task) => (
              <tr key={task.id}>
                <td className={task.is_done ? 'text-decoration-line-through text-muted' : ''}>
                  {task.title}
                </td>
                <td>
                  {task.is_done ? (
                    <span className="badge bg-success">Done</span>
                  ) : (
                    <span className="badge bg-secondary">Pending</span>
                  )}
                </td>
                <td>{task.priority ?? '-'}</td>
                <td>{task.urgency ?? '-'}</td>
                <td>
                  <button
                    className={`btn btn-sm me-2 ${task.is_done ? 'btn-success' : 'btn-outline-secondary'}`}
                    onClick={() => onToggleDone(task.id)}
                  >
                    {task.is_done ? 'Completed' : 'Mark Done'}
                  </button>
                  <button className="btn btn-sm btn-danger" onClick={() => onDeleteTask(task.id)}>
                    Delete
                  </button>
                </td>
                <td>
                  <button className="btn btn-sm btn-outline-success me-1" title="Thumbs up" onClick={() => handleFeedback(task.id, 5)}>
                    👍
                  </button>
                  <button className="btn btn-sm btn-outline-danger me-1" title="Thumbs down" onClick={() => handleFeedback(task.id, 1)}>
                    👎
                  </button>
                  <input
                    type="text"
                    className="form-control form-control-sm d-inline w-auto me-1"
                    style={{ width: 100 }}
                    placeholder="Comment"
                    value={commentInput[task.id] || ''}
                    onChange={e => setCommentInput(prev => ({ ...prev, [task.id]: e.target.value }))}
                    onKeyDown={e => { if (e.key === 'Enter') handleComment(task.id); }}
                  />
                  <button className="btn btn-sm btn-outline-primary" onClick={() => handleComment(task.id)}>
                    💬
                  </button>
                  {feedbacks[task.id] && feedbacks[task.id].length > 0 && (
                    <span className="ms-2 text-muted" style={{ fontSize: '0.9em' }}>
                      {feedbacks[task.id][feedbacks[task.id].length - 1].comment || ''}
                      {feedbacks[task.id].filter(fb => fb.rating === 5).length > 0 && ' 👍'}
                      {feedbacks[task.id].filter(fb => fb.rating === 1).length > 0 && ' 👎'}
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}

export default TaskList;
