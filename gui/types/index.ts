// Global type definitions for SuperAGI

export interface User {
  id: number;
  name: string;
  email: string;
  organisation_id?: number;
  created_at: string;
  updated_at: string;
}

export interface Agent {
  id: number;
  name: string;
  description: string;
  project_id: number;
  agent_workflow_id: number;
  created_at: string;
  updated_at: string;
  is_deleted: boolean;
}

export interface AgentExecution {
  id: number;
  agent_id: number;
  name: string;
  status: 'CREATED' | 'RUNNING' | 'PAUSED' | 'COMPLETED' | 'TERMINATED';
  current_step_id?: number;
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: number;
  name: string;
  description: string;
  organisation_id: number;
  created_at: string;
  updated_at: string;
}

export interface Tool {
  id: number;
  name: string;
  description: string;
  class_name: string;
  file_name: string;
  toolkit_id: number;
}

export interface Toolkit {
  id: number;
  name: string;
  description: string;
  show_toolkit: boolean;
  organisation_id: number;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface Config {
  key: string;
  value: string;
}

export interface Organisation {
  id: number;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface Resource {
  id: number;
  name: string;
  path: string;
  type: string;
  size: number;
  agent_id: number;
  created_at: string;
}

// API Request/Response types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
}

export interface CreateAgentRequest {
  name: string;
  description: string;
  project_id: number;
  agent_workflow_id: number;
  tools: number[];
  configs: Record<string, any>;
}

// UI Component types
export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
}

export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'warning';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
  className?: string;
}

export interface InputProps {
  label?: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  type?: 'text' | 'email' | 'password' | 'number';
}

// Context types
export interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  isAuthenticated: boolean;
}

export interface ToastContextType {
  showToast: (message: string, type: 'success' | 'error' | 'warning' | 'info') => void;
}

// Utility types
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface PaginationParams {
  page: number;
  limit: number;
}

export interface SortParams {
  field: string;
  order: 'asc' | 'desc';
}

export interface FilterParams {
  [key: string]: any;
}

export interface TableColumn<T = any> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  render?: (value: any, row: T) => React.ReactNode;
}

// API Error types
export interface ApiError {
  message: string;
  status_code: number;
  timestamp: string;
}

// Environment variables
export interface EnvironmentConfig {
  API_BASE_URL: string;
  NODE_ENV: 'development' | 'production' | 'test';
  GITHUB_CLIENT_ID?: string;
}

declare global {
  interface Window {
    ENV: EnvironmentConfig;
  }
}

export {};