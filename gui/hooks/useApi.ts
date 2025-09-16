import { useState, useEffect, useCallback } from 'react';
import { LoadingState, ApiError } from '../types';

interface UseApiOptions<T> {
  initialData?: T;
  onSuccess?: (data: T) => void;
  onError?: (error: ApiError) => void;
}

export interface UseApiReturn<T> {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
  execute: (...args: any[]) => Promise<T>;
  reset: () => void;
  state: LoadingState;
}

/**
 * Modern hook for API calls with automatic loading states and error handling
 */
export function useApi<T = any>(
  apiFunction: (...args: any[]) => Promise<T>,
  options: UseApiOptions<T> = {}
): UseApiReturn<T> {
  const { initialData = null, onSuccess, onError } = options;

  const [data, setData] = useState<T | null>(initialData);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [state, setState] = useState<LoadingState>('idle');

  const execute = useCallback(
    async (...args: any[]): Promise<T> => {
      try {
        setLoading(true);
        setState('loading');
        setError(null);

        const result = await apiFunction(...args);
        
        setData(result);
        setState('success');
        
        if (onSuccess) {
          onSuccess(result);
        }
        
        return result;
      } catch (err: any) {
        const apiError: ApiError = {
          message: err.message || 'An error occurred',
          status_code: err.status || 500,
          timestamp: new Date().toISOString(),
        };
        
        setError(apiError);
        setState('error');
        
        if (onError) {
          onError(apiError);
        }
        
        throw apiError;
      } finally {
        setLoading(false);
      }
    },
    [apiFunction, onSuccess, onError]
  );

  const reset = useCallback(() => {
    setData(initialData);
    setLoading(false);
    setError(null);
    setState('idle');
  }, [initialData]);

  return {
    data,
    loading,
    error,
    execute,
    reset,
    state,
  };
}

/**
 * Hook for automatic API calls on component mount
 */
export function useApiCall<T = any>(
  apiFunction: (...args: any[]) => Promise<T>,
  dependencies: any[] = [],
  options: UseApiOptions<T> = {}
): UseApiReturn<T> {
  const apiHook = useApi(apiFunction, options);

  useEffect(() => {
    apiHook.execute();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, dependencies);

  return apiHook;
}

/**
 * Hook for pagination support
 */
export interface UsePaginationOptions {
  initialPage?: number;
  initialLimit?: number;
}

export interface UsePaginationReturn {
  page: number;
  limit: number;
  setPage: (page: number) => void;
  setLimit: (limit: number) => void;
  nextPage: () => void;
  prevPage: () => void;
  reset: () => void;
}

export function usePagination(
  options: UsePaginationOptions = {}
): UsePaginationReturn {
  const { initialPage = 1, initialLimit = 10 } = options;
  
  const [page, setPage] = useState(initialPage);
  const [limit, setLimit] = useState(initialLimit);

  const nextPage = useCallback(() => {
    setPage(prev => prev + 1);
  }, []);

  const prevPage = useCallback(() => {
    setPage(prev => Math.max(1, prev - 1));
  }, []);

  const reset = useCallback(() => {
    setPage(initialPage);
    setLimit(initialLimit);
  }, [initialPage, initialLimit]);

  return {
    page,
    limit,
    setPage,
    setLimit,
    nextPage,
    prevPage,
    reset,
  };
}

/**
 * Hook for search functionality with debouncing
 */
export interface UseSearchOptions {
  debounceMs?: number;
  minLength?: number;
}

export interface UseSearchReturn {
  searchTerm: string;
  debouncedSearchTerm: string;
  setSearchTerm: (term: string) => void;
  clearSearch: () => void;
}

export function useSearch(options: UseSearchOptions = {}): UseSearchReturn {
  const { debounceMs = 300, minLength = 0 } = options;
  
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');

  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchTerm.length >= minLength) {
        setDebouncedSearchTerm(searchTerm);
      } else {
        setDebouncedSearchTerm('');
      }
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [searchTerm, debounceMs, minLength]);

  const clearSearch = useCallback(() => {
    setSearchTerm('');
    setDebouncedSearchTerm('');
  }, []);

  return {
    searchTerm,
    debouncedSearchTerm,
    setSearchTerm,
    clearSearch,
  };
}

/**
 * Hook for local storage with TypeScript support
 */
export function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((prev: T) => T)) => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      if (typeof window !== 'undefined') {
        const item = window.localStorage.getItem(key);
        return item ? JSON.parse(item) : initialValue;
      }
      return initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = useCallback(
    (value: T | ((prev: T) => T)) => {
      try {
        const valueToStore = value instanceof Function ? value(storedValue) : value;
        setStoredValue(valueToStore);
        
        if (typeof window !== 'undefined') {
          window.localStorage.setItem(key, JSON.stringify(valueToStore));
        }
      } catch (error) {
        console.error(`Error setting localStorage key "${key}":`, error);
      }
    },
    [key, storedValue]
  );

  return [storedValue, setValue];
}