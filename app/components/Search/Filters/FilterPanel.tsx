import React from 'react';
import { Disclosure } from '@headlessui/react';
import { ChevronDownIcon } from '@heroicons/react/solid';
import { EntityType } from '../../../../src/types/search';
import { classNames } from '../../../../src/utils/styles';
import { FilterGroup } from './FilterGroup';
import { RangeFilter } from './RangeFilter';
import { SelectFilter } from './SelectFilter';
import { CheckboxFilter } from './CheckboxFilter';

interface FilterPanelProps {
  filters: Record<string, any>;
  facets: Record<string, any>;
  onFilterChange: (field: string, value: any) => void;
  onClearFilters: () => void;
  className?: string;
}

export const FilterPanel: React.FC<FilterPanelProps> = ({
  filters,
  facets,
  onFilterChange,
  onClearFilters,
  className = '',
}) => {
  return (
    <div className={classNames('space-y-4', className)}>
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-medium text-gray-900">Filters</h2>
        {Object.keys(filters).length > 0 && (
          <button
            type="button"
            onClick={onClearFilters}
            className="text-sm font-medium text-primary-600 hover:text-primary-500"
          >
            Clear all
          </button>
        )}
      </div>

      <div className="space-y-4">
        {/* Entity Type Filter */}
        <Disclosure as="div" defaultOpen>
          {({ open }) => (
            <>
              <Disclosure.Button className="flex w-full items-center justify-between text-left">
                <span className="text-sm font-medium text-gray-900">Type</span>
                <ChevronDownIcon
                  className={classNames(
                    open ? '-rotate-180' : 'rotate-0',
                    'h-5 w-5 transform text-gray-500'
                  )}
                  aria-hidden="true"
                />
              </Disclosure.Button>
              <Disclosure.Panel className="pt-4">
                <SelectFilter
                  value={filters.type}
                  options={Object.values(EntityType).map((type) => ({
                    value: type,
                    label: type,
                    count: facets.type?.[type] || 0,
                  }))}
                  onChange={(value) => onFilterChange('type', value)}
                />
              </Disclosure.Panel>
            </>
          )}
        </Disclosure>

        {/* Rarity Filter (for items) */}
        {filters.type === EntityType.ITEM && (
          <FilterGroup title="Rarity">
            <CheckboxFilter
              value={filters.rarity || []}
              options={[
                { value: 'common', label: 'Common' },
                { value: 'uncommon', label: 'Uncommon' },
                { value: 'rare', label: 'Rare' },
                { value: 'epic', label: 'Epic' },
                { value: 'legendary', label: 'Legendary' },
              ]}
              onChange={(value) => onFilterChange('rarity', value)}
            />
          </FilterGroup>
        )}

        {/* Level Range Filter */}
        <FilterGroup title="Level">
          <RangeFilter
            value={filters.level || [0, 100]}
            min={0}
            max={100}
            step={1}
            onChange={(value) => onFilterChange('level', value)}
          />
        </FilterGroup>

        {/* Faction Filter */}
        {filters.type === EntityType.NPC && (
          <FilterGroup title="Faction">
            <SelectFilter
              value={filters.faction}
              options={Object.entries(facets.faction || {}).map(([value, count]) => ({
                value,
                label: value,
                count: count as number,
              }))}
              onChange={(value) => onFilterChange('faction', value)}
            />
          </FilterGroup>
        )}

        {/* Location Type Filter */}
        {filters.type === EntityType.LOCATION && (
          <FilterGroup title="Location Type">
            <CheckboxFilter
              value={filters.locationType || []}
              options={Object.entries(facets.locationType || {}).map(([value, count]) => ({
                value,
                label: value,
                count: count as number,
              }))}
              onChange={(value) => onFilterChange('locationType', value)}
            />
          </FilterGroup>
        )}

        {/* Quest Status Filter */}
        {filters.type === EntityType.QUEST && (
          <FilterGroup title="Status">
            <CheckboxFilter
              value={filters.status || []}
              options={[
                { value: 'available', label: 'Available' },
                { value: 'in_progress', label: 'In Progress' },
                { value: 'completed', label: 'Completed' },
                { value: 'failed', label: 'Failed' },
              ]}
              onChange={(value) => onFilterChange('status', value)}
            />
          </FilterGroup>
        )}
      </div>
    </div>
  );
}; 