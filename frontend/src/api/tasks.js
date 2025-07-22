import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const getAllTasks = async () => {
  const response = await axios.get(`${API_BASE_URL}/tasks`);
  return response.data;
};

export const createTask = async (title) => {
  const response = await axios.post(`${API_BASE_URL}/tasks`, { title });
  return response.data;
};

export const deleteTask = async (taskId) => {
  const response = await axios.delete(`${API_BASE_URL}/tasks/${taskId}`);
  return response.data;
};

export const markTaskDone = async (taskId) => {
  const response = await axios.put(`${API_BASE_URL}/tasks/${taskId}/done`);
  return response.data;
};

export const patchTask = async (taskId, update) => {
  const response = await axios.patch(`${API_BASE_URL}/tasks/${taskId}`, update);
  return response.data;
};

export const clearAllTasks = async () => {
  const response = await axios({
    method: 'delete',
    url: `${API_BASE_URL}/tasks/clear`
    // No data property, so no body is sent
  });
  return response.data;
};

export const semanticSearchTasks = async (query) => {
  const response = await axios.post(`${API_BASE_URL}/tasks/semantic-search`, { query });
  return response.data.results;
};

export const addFeedback = async (taskId, rating, comment) => {
  const response = await axios.post(`${API_BASE_URL}/feedback`, { task_id: taskId, rating, comment });
  return response.data;
};

export const getFeedbackForTask = async (taskId) => {
  const response = await axios.get(`${API_BASE_URL}/feedback/${taskId}`);
  return response.data;
};
