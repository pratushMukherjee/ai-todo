import React, { useState } from 'react';
import { createTaskAll } from '../api/agent';

function TaskInput({ onAddTask, onAddCalendarEvent, onSuggestions }) {
  const [taskTitle, setTaskTitle] = useState('');
  const [startDt, setStartDt] = useState('');
  const [endDt, setEndDt] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!taskTitle.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const result = await createTaskAll(
        taskTitle.trim(),
        startDt ? new Date(startDt).toISOString() : undefined,
        endDt ? new Date(endDt).toISOString() : undefined
      );
      if (result.created_task && onAddTask) {
        onAddTask(result.created_task);
      }
      if (result.created_event && onAddCalendarEvent) {
        onAddCalendarEvent(result.created_event);
      }
      if (result.suggestions && onSuggestions) {
        onSuggestions(result.suggestions);
      }
      setTaskTitle('');
      setStartDt('');
      setEndDt('');
    } catch (err) {
      setError('Failed to create task and calendar event');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mb-3">
      <div className="input-group mb-2">
        <input
          type="text"
          className="form-control"
          placeholder="Enter a new task..."
          value={taskTitle}
          onChange={(e) => setTaskTitle(e.target.value)}
        />
      </div>
      <div className="input-group mb-2">
        <input
          type="datetime-local"
          className="form-control"
          placeholder="Start time (optional)"
          value={startDt}
          onChange={(e) => setStartDt(e.target.value)}
        />
        <input
          type="datetime-local"
          className="form-control"
          placeholder="End time (optional)"
          value={endDt}
          onChange={(e) => setEndDt(e.target.value)}
        />
      </div>
      <button type="submit" className="btn btn-primary" disabled={loading}>
        {loading ? 'Adding...' : 'Add Task & Calendar Event'}
      </button>
      {error && <div className="alert alert-danger mt-2">{error}</div>}
    </form>
  );
}

export default TaskInput;
