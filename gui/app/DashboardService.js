import axios from 'axios';
const API_BASE_URL = 'http://192.168.235.48:8001'; //for testing
// const API_BASE_URL = 'http://localhost:8001';

export const getOrganization = () => {
  return axios.get(`${API_BASE_URL}/organisations/get/1`);
};

export const addUser = (userData) => {
  return axios.post(`${API_BASE_URL}/users/add`, userData);
};

export const getProject = (organizationId) => {
  return axios.get(`${API_BASE_URL}/projects/get/${organizationId}`);
};
