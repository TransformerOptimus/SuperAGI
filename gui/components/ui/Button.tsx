import React, { forwardRef, ButtonHTMLAttributes } from 'react';
import { cn } from '../../lib/utils';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'warning' | 'ghost' | 'outline';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'primary',
      size = 'md',
      loading = false,
      leftIcon,
      rightIcon,
      fullWidth = false,
      disabled,
      children,
      ...props
    },
    ref
  ) => {
    const baseStyles = [
      'inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200',
      'focus:outline-none focus:ring-2 focus:ring-offset-2',
      'disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none',
    ];

    const variants = {
      primary: [
        'bg-primary-600 text-white shadow-md',
        'hover:bg-primary-700 hover:shadow-lg',
        'focus:ring-primary-500',
        'active:bg-primary-800',
      ],
      secondary: [
        'bg-secondary-100 text-secondary-900 shadow-sm',
        'hover:bg-secondary-200 hover:shadow-md',
        'focus:ring-secondary-500',
        'active:bg-secondary-300',
      ],
      danger: [
        'bg-error-600 text-white shadow-md',
        'hover:bg-error-700 hover:shadow-lg',
        'focus:ring-error-500',
        'active:bg-error-800',
      ],
      success: [
        'bg-success-600 text-white shadow-md',
        'hover:bg-success-700 hover:shadow-lg',
        'focus:ring-success-500',
        'active:bg-success-800',
      ],
      warning: [
        'bg-warning-600 text-white shadow-md',
        'hover:bg-warning-700 hover:shadow-lg',
        'focus:ring-warning-500',
        'active:bg-warning-800',
      ],
      ghost: [
        'text-secondary-700 bg-transparent',
        'hover:bg-secondary-100',
        'focus:ring-secondary-500',
        'active:bg-secondary-200',
      ],
      outline: [
        'border-2 border-primary-600 text-primary-600 bg-transparent',
        'hover:bg-primary-50 hover:border-primary-700',
        'focus:ring-primary-500',
        'active:bg-primary-100',
      ],
    };

    const sizes = {
      sm: 'px-3 py-1.5 text-sm min-h-[32px]',
      md: 'px-4 py-2 text-sm min-h-[40px]',
      lg: 'px-6 py-3 text-base min-h-[48px]',
      xl: 'px-8 py-4 text-lg min-h-[56px]',
    };

    const iconSizes = {
      sm: 'h-4 w-4',
      md: 'h-4 w-4',
      lg: 'h-5 w-5',
      xl: 'h-6 w-6',
    };

    const isDisabled = disabled || loading;

    return (
      <button
        ref={ref}
        className={cn(
          baseStyles,
          variants[variant],
          sizes[size],
          fullWidth && 'w-full',
          className
        )}
        disabled={isDisabled}
        {...props}
      >
        {loading && (
          <svg
            className={cn('animate-spin mr-2', iconSizes[size])}
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        )}
        
        {!loading && leftIcon && (
          <span className={cn('mr-2', iconSizes[size])}>{leftIcon}</span>
        )}
        
        <span className={loading ? 'opacity-0' : 'opacity-100'}>
          {children}
        </span>
        
        {!loading && rightIcon && (
          <span className={cn('ml-2', iconSizes[size])}>{rightIcon}</span>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button };