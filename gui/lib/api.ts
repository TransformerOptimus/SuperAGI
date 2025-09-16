import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { 
  User, 
  Agent, 
  Project, 
  Tool, 
  Toolkit,
  LoginRequest,
  LoginResponse,
  CreateAgentRequest,
  ApiResponse,
  Config,
  Organisation,
  Resource,
  PaginationParams,
  SortParams,
  FilterParams,
} from '../types';

// Create axios instance with default configuration
const createApiInstance = (): AxiosInstance => {
  const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
  
  const instance = axios.create({
    baseURL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor for auth token
  instance.interceptors.request.use(
    (config) => {
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor for error handling
  instance.interceptors.response.use(
    (response: AxiosResponse) => response,
    (error) => {
      if (error.response?.status === 401) {
        // Unauthorized - redirect to login
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
      }
      return Promise.reject(error);
    }
  );

  return instance;
};

const api = createApiInstance();

// Utility function to handle API responses
const handleResponse = <T>(response: AxiosResponse<T>): T => response.data;

// Utility function to build query string from params
const buildQueryString = (params: Record<string, any>): string => {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, String(value));
    }
  });
  return searchParams.toString();
};

// Auth API
export const authApi = {
  login: (credentials: LoginRequest): Promise<LoginResponse> =>
    api.post<LoginResponse>('/login', credentials).then(handleResponse),

  validateToken: (): Promise<User> =>
    api.get<User>('/validate-access-token').then(handleResponse),

  getCurrentUser: (): Promise<{ user: string }> =>
    api.get<{ user: string }>('/user').then(handleResponse),

  getGithubClientId: (): Promise<{ github_client_id: string }> =>
    api.get<{ github_client_id: string }>('/get/github_client_id').then(handleResponse),
};

// Users API
export const usersApi = {
  getUsers: (params?: PaginationParams & SortParams & FilterParams): Promise<User[]> => {
    const queryString = params ? buildQueryString(params) : '';
    return api.get<User[]>(`/users?${queryString}`).then(handleResponse);
  },

  getUserById: (id: number): Promise<User> =>
    api.get<User>(`/users/${id}`).then(handleResponse),

  createUser: (user: Omit<User, 'id' | 'created_at' | 'updated_at'>): Promise<User> =>
    api.post<User>('/users', user).then(handleResponse),

  updateUser: (id: number, user: Partial<User>): Promise<User> =>
    api.put<User>(`/users/${id}`, user).then(handleResponse),

  deleteUser: (id: number): Promise<void> =>
    api.delete(`/users/${id}`).then(handleResponse),
};

// Agents API
export const agentsApi = {
  getAgents: (params?: PaginationParams & SortParams & FilterParams): Promise<Agent[]> => {
    const queryString = params ? buildQueryString(params) : '';
    return api.get<Agent[]>(`/agents?${queryString}`).then(handleResponse);
  },

  getAgentById: (id: number): Promise<Agent> =>
    api.get<Agent>(`/agents/${id}`).then(handleResponse),

  createAgent: (agent: CreateAgentRequest): Promise<Agent> =>
    api.post<Agent>('/agents', agent).then(handleResponse),

  updateAgent: (id: number, agent: Partial<Agent>): Promise<Agent> =>
    api.put<Agent>(`/agents/${id}`, agent).then(handleResponse),

  deleteAgent: (id: number): Promise<void> =>
    api.delete(`/agents/${id}`).then(handleResponse),

  runAgent: (id: number): Promise<{ message: string }> =>
    api.post<{ message: string }>(`/agents/${id}/run`).then(handleResponse),

  pauseAgent: (id: number): Promise<{ message: string }> =>
    api.post<{ message: string }>(`/agents/${id}/pause`).then(handleResponse),
};

// Projects API
export const projectsApi = {
  getProjects: (params?: PaginationParams & SortParams & FilterParams): Promise<Project[]> => {
    const queryString = params ? buildQueryString(params) : '';
    return api.get<Project[]>(`/projects?${queryString}`).then(handleResponse);
  },

  getProjectById: (id: number): Promise<Project> =>
    api.get<Project>(`/projects/${id}`).then(handleResponse),

  createProject: (project: Omit<Project, 'id' | 'created_at' | 'updated_at'>): Promise<Project> =>
    api.post<Project>('/projects', project).then(handleResponse),

  updateProject: (id: number, project: Partial<Project>): Promise<Project> =>
    api.put<Project>(`/projects/${id}`, project).then(handleResponse),

  deleteProject: (id: number): Promise<void> =>
    api.delete(`/projects/${id}`).then(handleResponse),
};

// Tools API
export const toolsApi = {
  getTools: (params?: PaginationParams & SortParams & FilterParams): Promise<Tool[]> => {
    const queryString = params ? buildQueryString(params) : '';
    return api.get<Tool[]>(`/tools?${queryString}`).then(handleResponse);
  },

  getToolById: (id: number): Promise<Tool> =>
    api.get<Tool>(`/tools/${id}`).then(handleResponse),

  getToolkits: (params?: PaginationParams & SortParams & FilterParams): Promise<Toolkit[]> => {
    const queryString = params ? buildQueryString(params) : '';
    return api.get<Toolkit[]>(`/toolkits?${queryString}`).then(handleResponse);
  },
};

// Resources API
export const resourcesApi = {
  getResources: (agentId: number, params?: PaginationParams): Promise<Resource[]> => {
    const queryString = params ? buildQueryString(params) : '';
    return api.get<Resource[]>(`/resources/agent/${agentId}?${queryString}`).then(handleResponse);
  },

  uploadResource: (agentId: number, file: File): Promise<Resource> => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post<Resource>(`/resources/agent/${agentId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }).then(handleResponse);
  },

  deleteResource: (id: number): Promise<void> =>
    api.delete(`/resources/${id}`).then(handleResponse),
};

// Configurations API
export const configsApi = {
  getConfigs: (): Promise<Config[]> =>
    api.get<Config[]>('/configs').then(handleResponse),

  updateConfig: (key: string, value: string): Promise<Config> =>
    api.put<Config>('/configs', { key, value }).then(handleResponse),

  validateLlmApiKey: (modelSource: string, apiKey: string): Promise<{ status: string; message: string }> =>
    api.post<{ status: string; message: string }>('/validate-llm-api-key', {
      model_source: modelSource,
      model_api_key: apiKey,
    }).then(handleResponse),
};

// Organizations API
export const organisationsApi = {
  getOrganisations: (): Promise<Organisation[]> =>
    api.get<Organisation[]>('/organisations').then(handleResponse),

  getOrganisationById: (id: number): Promise<Organisation> =>
    api.get<Organisation>(`/organisations/${id}`).then(handleResponse),

  createOrganisation: (org: Omit<Organisation, 'id' | 'created_at' | 'updated_at'>): Promise<Organisation> =>
    api.post<Organisation>('/organisations', org).then(handleResponse),

  updateOrganisation: (id: number, org: Partial<Organisation>): Promise<Organisation> =>
    api.put<Organisation>(`/organisations/${id}`, org).then(handleResponse),
};

// Health check
export const healthApi = {
  check: (): Promise<{ status: string; timestamp: string; version: string }> =>
    api.get<{ status: string; timestamp: string; version: string }>('/health').then(handleResponse),
};

// Export the axios instance for custom calls
export { api };

// Export a function to update the auth token
export const setAuthToken = (token: string): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('access_token', token);
  }
};

export const clearAuthToken = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('access_token');
  }
};