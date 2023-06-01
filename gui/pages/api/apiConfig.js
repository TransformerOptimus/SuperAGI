import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8001';
// const API_BASE_URL = 'http://192.168.1.200:8001';

export const baseUrl = () => {
  return API_BASE_URL;
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
