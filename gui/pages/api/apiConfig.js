import axios from 'axios';

const github_client_id = process.env.github_client_id;
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8001';
// const API_BASE_URL = 'http://192.168.1.200:8001';

export const baseUrl = () => {
  return API_BASE_URL;
};

export const githubClientId = () => {
  return github_client_id;
};

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    common: {
      'Content-Type': 'application/json',
    },
  },
});

api.interceptors.request.use(config => {
  if (typeof window !== 'undefined') {
    const accessToken = localStorage.getItem("accessToken");
    if (accessToken) {
      config.headers['Authorization'] = `Bearer ${accessToken}`;
    }
  }
  return config;
});

export default api;
