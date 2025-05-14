import React from 'react';
import { classNames } from '../../../../src/utils/styles';

interface RangeFilterProps {
  value: [number, number];
  min: number;
  max: number;
  step?: number;
  onChange: (value: [number, number]) => void;
}

export const RangeFilter: React.FC<RangeFilterProps> = ({
  value,
  min,
  max,
  step = 1,
  onChange,
}) => {
  const handleMinChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newMin = Number(e.target.value);
    if (!isNaN(newMin) && newMin >= min && newMin <= value[1]) {
      onChange([newMin, value[1]]);
    }
  };

  const handleMaxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newMax = Number(e.target.value);
    if (!isNaN(newMax) && newMax <= max && newMax >= value[0]) {
      onChange([value[0], newMax]);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-4">
        <input
          type="range"
          min={min}
          max={value[1]}
          step={step}
          value={value[0]}
          onChange={handleMinChange}
          className={classNames(
            'w-full',
            'range-sm h-2 rounded-lg appearance-none cursor-pointer',
            'bg-gray-200',
            'focus:outline-none focus:ring-2 focus:ring-primary-500'
          )}
        />
        <input
          type="range"
          min={value[0]}
          max={max}
          step={step}
          value={value[1]}
          onChange={handleMaxChange}
          className={classNames(
            'w-full',
            'range-sm h-2 rounded-lg appearance-none cursor-pointer',
            'bg-gray-200',
            'focus:outline-none focus:ring-2 focus:ring-primary-500'
          )}
        />
      </div>
      <div className="flex items-center justify-between">
        <input
          type="number"
          min={min}
          max={value[1]}
          value={value[0]}
          onChange={handleMinChange}
          className="w-20 rounded-md border-gray-300 py-1 text-sm focus:border-primary-500 focus:ring-primary-500"
        />
        <span className="text-sm text-gray-500">to</span>
        <input
          type="number"
          min={value[0]}
          max={max}
          value={value[1]}
          onChange={handleMaxChange}
          className="w-20 rounded-md border-gray-300 py-1 text-sm focus:border-primary-500 focus:ring-primary-500"
        />
      </div>
    </div>
  );
}; 