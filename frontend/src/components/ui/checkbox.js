import React from 'react';
import { Check } from 'lucide-react';

export const Checkbox = ({ 
  id, 
  checked, 
  onCheckedChange, 
  disabled = false,
  className = "",
  ...props 
}) => {
  return (
    <button
      id={id}
      type="button"
      role="checkbox"
      aria-checked={checked}
      disabled={disabled}
      onClick={() => onCheckedChange && onCheckedChange(!checked)}
      className={`
        inline-flex items-center justify-center
        w-4 h-4
        border border-gray-300 rounded
        focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
        ${checked 
          ? 'bg-blue-600 border-blue-600 text-white' 
          : 'bg-white hover:bg-gray-50'
        }
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        ${className}
      `}
      {...props}
    >
      {checked && <Check className="w-3 h-3" />}
    </button>
  );
};