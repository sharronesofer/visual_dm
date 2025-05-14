import React from 'react';
import { Listbox } from '@headlessui/react';
import { CheckIcon, SelectorIcon } from '@heroicons/react/solid';
import { classNames } from '../../../../src/utils/styles';

interface SelectOption {
  value: string;
  label: string;
  count?: number;
}

interface SelectFilterProps {
  value: string | null;
  options: SelectOption[];
  onChange: (value: string | null) => void;
  placeholder?: string;
}

export const SelectFilter: React.FC<SelectFilterProps> = ({
  value,
  options,
  onChange,
  placeholder = 'Select an option',
}) => {
  const selectedOption = options.find((option) => option.value === value);

  return (
    <Listbox value={value} onChange={onChange}>
      <div className="relative mt-1">
        <Listbox.Button className="relative w-full cursor-default rounded-lg bg-white py-2 pl-3 pr-10 text-left border border-gray-300 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 sm:text-sm">
          <span className="block truncate">
            {selectedOption ? selectedOption.label : placeholder}
          </span>
          <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
            <SelectorIcon
              className="h-5 w-5 text-gray-400"
              aria-hidden="true"
            />
          </span>
        </Listbox.Button>

        <Listbox.Options className="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
          {/* Clear option */}
          {value !== null && (
            <Listbox.Option
              value={null}
              className={({ active }) =>
                classNames(
                  'relative cursor-default select-none py-2 pl-3 pr-9',
                  active ? 'bg-primary-100 text-primary-900' : 'text-gray-900'
                )
              }
            >
              {({ active, selected }) => (
                <>
                  <span className="block truncate font-medium text-gray-500">
                    Clear selection
                  </span>
                  {selected && (
                    <span
                      className={classNames(
                        'absolute inset-y-0 right-0 flex items-center pr-4',
                        active ? 'text-primary-600' : 'text-primary-600'
                      )}
                    >
                      <CheckIcon className="h-5 w-5" aria-hidden="true" />
                    </span>
                  )}
                </>
              )}
            </Listbox.Option>
          )}

          {options.map((option) => (
            <Listbox.Option
              key={option.value}
              value={option.value}
              className={({ active }) =>
                classNames(
                  'relative cursor-default select-none py-2 pl-3 pr-9',
                  active ? 'bg-primary-100 text-primary-900' : 'text-gray-900'
                )
              }
            >
              {({ active, selected }) => (
                <>
                  <div className="flex items-center">
                    <span className={classNames(
                      'block truncate',
                      selected && 'font-semibold'
                    )}>
                      {option.label}
                    </span>
                    {option.count !== undefined && (
                      <span className={classNames(
                        'ml-2 text-sm',
                        active ? 'text-primary-600' : 'text-gray-500'
                      )}>
                        ({option.count})
                      </span>
                    )}
                  </div>
                  {selected && (
                    <span
                      className={classNames(
                        'absolute inset-y-0 right-0 flex items-center pr-4',
                        active ? 'text-primary-600' : 'text-primary-600'
                      )}
                    >
                      <CheckIcon className="h-5 w-5" aria-hidden="true" />
                    </span>
                  )}
                </>
              )}
            </Listbox.Option>
          ))}
        </Listbox.Options>
      </div>
    </Listbox>
  );
}; 