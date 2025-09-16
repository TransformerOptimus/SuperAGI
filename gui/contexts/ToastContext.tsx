import React, { createContext, useContext, useCallback, ReactNode } from 'react';
import { toast, ToastContainer, ToastOptions, Slide } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { ToastContextType } from '../types';

// Toast context
const ToastContext = createContext<ToastContextType | undefined>(undefined);

// Toast provider component
interface ToastProviderProps {
  children: ReactNode;
}

export function ToastProvider({ children }: ToastProviderProps) {
  const showToast = useCallback((
    message: string, 
    type: 'success' | 'error' | 'warning' | 'info' = 'info'
  ) => {
    const options: ToastOptions = {
      position: 'top-right',
      autoClose: 5000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
      progress: undefined,
      theme: 'light',
    };

    switch (type) {
      case 'success':
        toast.success(message, options);
        break;
      case 'error':
        toast.error(message, options);
        break;
      case 'warning':
        toast.warning(message, options);
        break;
      case 'info':
      default:
        toast.info(message, options);
        break;
    }
  }, []);

  const value: ToastContextType = {
    showToast,
  };

  return (
    <ToastContext.Provider value={value}>
      {children}
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light"
        transition={Slide}
        className="z-50"
        toastClassName="bg-white shadow-lg rounded-lg border border-gray-200"
        bodyClassName="text-gray-800 font-medium"
        progressClassName="bg-primary-500"
      />
    </ToastContext.Provider>
  );
}

// Hook to use toast context
export function useToast(): ToastContextType {
  const context = useContext(ToastContext);
  if (context === undefined) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

// Utility functions for common toast patterns
export const toastUtils = {
  success: (message: string) => toast.success(message),
  error: (message: string) => toast.error(message),
  warning: (message: string) => toast.warning(message),
  info: (message: string) => toast.info(message),
  
  // API-specific toasts
  apiSuccess: (action: string) => toast.success(`${action} completed successfully`),
  apiError: (action: string, error?: string) => 
    toast.error(`Failed to ${action}${error ? `: ${error}` : ''}`),
  
  // Loading toast with promise
  promise: <T,>(
    promise: Promise<T>,
    messages: {
      pending: string;
      success: string;
      error: string;
    }
  ) => toast.promise(promise, messages),
  
  // Custom toast with actions
  custom: (message: string, onAction?: () => void, actionLabel = 'Undo') => {
    toast.success(
      <div className="flex items-center justify-between">
        <span>{message}</span>
        {onAction && (
          <button
            onClick={onAction}
            className="ml-4 text-primary-600 hover:text-primary-700 font-medium text-sm"
          >
            {actionLabel}
          </button>
        )}
      </div>,
      {
        closeButton: false,
        autoClose: 10000,
      }
    );
  },
};

// Hook for handling API errors with toast
export function useApiErrorHandler() {
  const { showToast } = useToast();

  return useCallback((error: any, customMessage?: string) => {
    const message = customMessage || 
                   error.response?.data?.detail || 
                   error.message || 
                   'An unexpected error occurred';
    showToast(message, 'error');
  }, [showToast]);
}

// Hook for handling API success with toast
export function useApiSuccessHandler() {
  const { showToast } = useToast();

  return useCallback((message: string) => {
    showToast(message, 'success');
  }, [showToast]);
}