import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8001';
// const API_BASE_URL = 'http://192.168.131.48:8001';

export const baseUrl = () => {
  return API_BASE_URL;
};

export const getOrganization = () => {
  return axios.get(`${API_BASE_URL}/organisations/get/1`);
};

export const addUser = (userData) => {
  return axios.post(`${API_BASE_URL}/users/add`, userData);
};

export const getProject = (organisationId) => {
  return axios.get(`${API_BASE_URL}/projects/get/organisation/${organisationId}`);
};

export const getAgents = (projectId) => {
  return axios.get(`${API_BASE_URL}/agents/get/project/${projectId}`);
};

export const getTools = () => {
  return axios.get(`${API_BASE_URL}/tools/get`);
};

export const getAgentDetails = (agentId) => {
  return axios.get(`${API_BASE_URL}/agents/get/details/${agentId}`);
};

export const getAgentExecutions = (agentId) => {
  return axios.get(`${API_BASE_URL}/agentexecutions/get/agent/${agentId}`);
};

export const getExecutionFeeds = (executionId) => {
  return axios.get(`${API_BASE_URL}/agentexecutionfeeds/get/execution/${executionId}`);
};

export const createAgent = (agentData) => {
  return axios.post(`${API_BASE_URL}/agents/create`, agentData);
};

export const updateAgents = (agentData) => {
  return axios.put(`${API_BASE_URL}/agentconfigs/update/`, agentData);
};

export const updateExecution = (executionId, executionData) => {
  return axios.put(`${API_BASE_URL}/agentexecutions/update/${executionId}`, executionData);
};

export const addExecution = (executionData) => {
  return axios.post(`${API_BASE_URL}/agentexecutions/add`, executionData);
};

export const getResources = (agentId) => {
  return axios.get(`${API_BASE_URL}/resources/get/all/${agentId}`);
};

export const getLastActiveAgent = (projectId) => {
  return axios.get(`${API_BASE_URL}/agentexecutions/get/latest/agent/project/${projectId}`);
};