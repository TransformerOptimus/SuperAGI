import axios from 'axios';

const GITHUB_CLIENT_ID = "06b962774236a4a8448f"

const API_BASE_URL = 'https://app.superagi.com/api';
const GOOGLE_ANALYTICS_MEASUREMENT_ID =  process.env.GOOGLE_ANALYTICS_MEASUREMENT_ID;
const GOOGLE_ANALYTICS_API_SECRET =  process.env.GOOGLE_ANALYTICS_API_SECRET;
const MIXPANEL_AUTH_ID = process.env.MIXPANEL_AUTH_ID

export const baseUrl = () => {
  return API_BASE_URL;
};

export const githubClientId = () => {
  return GITHUB_CLIENT_ID;
};

export const analyticsMeasurementId = () => {
  return GOOGLE_ANALYTICS_MEASUREMENT_ID;
};

export const analyticsApiSecret = () => {
  return GOOGLE_ANALYTICS_API_SECRET;
};

export const mixpanelId = () => {
  return MIXPANEL_AUTH_ID;
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
