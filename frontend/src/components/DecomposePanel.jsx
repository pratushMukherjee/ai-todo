import React, { useState } from 'react';
import { getDecomposedTasks } from '../api/agent';

function DecomposePanel({ onAddTask }) {
  const [taskTitle, setTaskTitle] = useState('');
  const [subtasks, setSubtasks] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleDecompose = async () => {
    if (!taskTitle.trim()) return;
    setLoading(true);
    try {
      const result = await getDecomposedTasks(taskTitle.trim());
      setSubtasks(result);
    } catch (err) {
      console.error('Error decomposing task:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card my-4">
      <div className="card-body">
        <h5 className="card-title">AI Task Decomposer</h5>
        <div className="input-group mb-3">
          <input
            type="text"
            className="form-control"
            placeholder="Enter a complex task to break down..."
            value={taskTitle}
            onChange={(e) => setTaskTitle(e.target.value)}
          />
          <button onClick={handleDecompose} className="btn btn-secondary">
            {loading ? 'Loading...' : 'Decompose'}
          </button>
        </div>

        {subtasks.length > 0 && (
          <ul className="list-group">
            {subtasks.map((sub, idx) => (
              <li key={idx} className="list-group-item d-flex justify-content-between align-items-center">
                {sub}
                <button className="btn btn-sm btn-primary" onClick={() => onAddTask(sub)}>
                  Add
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default DecomposePanel;
