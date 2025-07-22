import React, { useState } from 'react';
import { getSuggestedTasks } from '../api/agent';

function SuggestionsPanel({ onAddTask }) {
  const [inputText, setInputText] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSuggest = async () => {
    if (!inputText.trim()) return;
    setLoading(true);
    try {
      const response = await getSuggestedTasks(inputText.trim());
      setSuggestions(response);
    } catch (err) {
      console.error('Error fetching suggestions:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card my-4">
      <div className="card-body">
        <h5 className="card-title">AI Task Suggestions</h5>
        <div className="input-group mb-3">
          <input
            type="text"
            className="form-control"
            placeholder="Give me task suggestions based on..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
          />
          <button onClick={handleSuggest} className="btn btn-secondary">
            {loading ? 'Loading...' : 'Suggest'}
          </button>
        </div>

        {suggestions.length > 0 && (
          <ul className="list-group">
            {suggestions.map((sugg, idx) => (
              <li key={idx} className="list-group-item d-flex justify-content-between align-items-center">
                {sugg}
                <button className="btn btn-sm btn-primary" onClick={() => onAddTask(sugg)}>
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

export default SuggestionsPanel;
