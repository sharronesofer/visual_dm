import React from 'react';
import { Disclosure } from '@headlessui/react';
import { ChevronDownIcon } from '@heroicons/react/solid';
import { classNames } from '../../../../src/utils/styles';

interface FilterGroupProps {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}

export const FilterGroup: React.FC<FilterGroupProps> = ({
  title,
  children,
  defaultOpen = true,
}) => {
  return (
    <Disclosure as="div" defaultOpen={defaultOpen}>
      {({ open }) => (
        <>
          <Disclosure.Button className="flex w-full items-center justify-between text-left">
            <span className="text-sm font-medium text-gray-900">{title}</span>
            <ChevronDownIcon
              className={classNames(
                open ? '-rotate-180' : 'rotate-0',
                'h-5 w-5 transform text-gray-500'
              )}
              aria-hidden="true"
            />
          </Disclosure.Button>
          <Disclosure.Panel className="pt-4">
            {children}
          </Disclosure.Panel>
        </>
      )}
    </Disclosure>
  );
}; 