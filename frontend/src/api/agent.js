import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const getAgentResponse = async (tasks, message = "") => {
  const response = await axios.post(`${API_BASE_URL}/agent-response`, {
    tasks,
    message,
  });
  return response.data.response;
};

export const getSuggestedTasks = async (inputText) => {
  const response = await axios.post(`${API_BASE_URL}/suggest-tasks`, {
    text: inputText,
  });
  return response.data.suggestions;
};

export const getDecomposedTasks = async (taskTitle) => {
  const response = await axios.post(`${API_BASE_URL}/decompose-task`, {
    task: taskTitle,
  });
  return response.data.subtasks;
};

export const getCalendarEvents = async () => {
  const response = await axios.get(`${API_BASE_URL}/calendar/events`);
  return response.data.events;
};

export const createCalendarEvent = async (event) => {
  const response = await axios.post(`${API_BASE_URL}/calendar/events`, event);
  return response.data.event;
};

export const updateCalendarEvent = async (eventId, event) => {
  const response = await axios.put(`${API_BASE_URL}/calendar/events/${eventId}`, event);
  return response.data.event;
};

export const deleteCalendarEvent = async (eventId) => {
  const response = await axios.delete(`${API_BASE_URL}/calendar/events/${eventId}`);
  return response.data;
};

export const createTaskAndCalendarEvent = async (taskTitle, startDt, endDt) => {
  const response = await axios.post('http://localhost:8000/agentic/task-to-task-and-calendar', {
    task_title: taskTitle,
    start_dt: startDt,
    end_dt: endDt
  });
  return response.data.result;
};

export const createTaskAll = async (taskTitle, startDt, endDt) => {
  const response = await axios.post('http://localhost:8000/agentic/task-to-all', {
    task_title: taskTitle,
    start_dt: startDt,
    end_dt: endDt
  });
  return response.data;
};

export const emailToAll = async () => {
  const response = await axios.post('http://localhost:8000/agentic/email-to-all');
  return response.data;
};
