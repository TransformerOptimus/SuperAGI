import axios from 'axios';

const GITHUB_CLIENT_ID = "06b962774236a4a8448f"

const API_BASE_URL = 'https://app.superagi.com/api';
// const API_BASE_URL = 'http://192.168.127.48:8001';

export const baseUrl = () => {
  return API_BASE_URL;
};

export const githubClientId = () => {
  return GITHUB_CLIENT_ID;
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
