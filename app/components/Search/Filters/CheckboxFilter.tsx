import React from 'react';
import { classNames } from '../../../../src/utils/styles';

interface CheckboxOption {
  value: string;
  label: string;
  count?: number;
}

interface CheckboxFilterProps {
  value: string[];
  options: CheckboxOption[];
  onChange: (value: string[]) => void;
}

export const CheckboxFilter: React.FC<CheckboxFilterProps> = ({
  value,
  options,
  onChange,
}) => {
  const handleChange = (optionValue: string) => {
    const newValue = value.includes(optionValue)
      ? value.filter((v) => v !== optionValue)
      : [...value, optionValue];
    onChange(newValue);
  };

  return (
    <div className="space-y-2">
      {options.map((option) => (
        <label
          key={option.value}
          className="relative flex items-start py-1 cursor-pointer"
        >
          <div className="flex h-5 items-center">
            <input
              type="checkbox"
              checked={value.includes(option.value)}
              onChange={() => handleChange(option.value)}
              className={classNames(
                'h-4 w-4 rounded border-gray-300 text-primary-600',
                'focus:ring-primary-500 focus:ring-offset-0',
                'cursor-pointer'
              )}
            />
          </div>
          <div className="ml-3 flex items-center">
            <span className="text-sm text-gray-900">{option.label}</span>
            {option.count !== undefined && (
              <span className="ml-2 text-sm text-gray-500">
                ({option.count})
              </span>
            )}
          </div>
        </label>
      ))}
    </div>
  );
}; 