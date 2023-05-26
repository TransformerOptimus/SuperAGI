import axios from 'axios';
const API_BASE_URL = 'http://192.168.235.48:8001'; //for testing
// const API_BASE_URL = 'http://localhost:8001';

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

export const createAgent = (agentData) => {
  return axios.post(`${API_BASE_URL}/agents/create`, agentData);
};

export const deleteAgent = (agentId) => {
  return axios.delete(`${API_BASE_URL}/agents/delete/${agentId}`);
};
