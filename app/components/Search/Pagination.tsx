import React from 'react';
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/solid';
import { classNames } from '../../../src/utils/styles';

interface PaginationProps {
  total: number;
  page: number;
  limit: number;
  onChange: (page: number) => void;
  maxPages?: number;
}

export const Pagination: React.FC<PaginationProps> = ({
  total,
  page,
  limit,
  onChange,
  maxPages = 5,
}) => {
  const totalPages = Math.ceil(total / limit);
  if (totalPages <= 1) return null;

  const getPageNumbers = () => {
    const pages: (number | string)[] = [];
    const halfMax = Math.floor(maxPages / 2);

    let start = Math.max(1, page - halfMax);
    let end = Math.min(totalPages, start + maxPages - 1);

    if (end - start + 1 < maxPages) {
      start = Math.max(1, end - maxPages + 1);
    }

    if (start > 1) {
      pages.push(1);
      if (start > 2) pages.push('...');
    }

    for (let i = start; i <= end; i++) {
      pages.push(i);
    }

    if (end < totalPages) {
      if (end < totalPages - 1) pages.push('...');
      pages.push(totalPages);
    }

    return pages;
  };

  return (
    <nav className="flex items-center justify-between border-t border-gray-200 px-4 sm:px-0">
      <div className="-mt-px flex w-0 flex-1">
        <button
          onClick={() => onChange(page - 1)}
          disabled={page <= 1}
          className={classNames(
            'inline-flex items-center border-t-2 pt-4 pr-1 text-sm font-medium',
            page <= 1
              ? 'border-transparent text-gray-400 cursor-not-allowed'
              : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
          )}
        >
          <ChevronLeftIcon className="mr-3 h-5 w-5" aria-hidden="true" />
          Previous
        </button>
      </div>
      <div className="-mt-px flex">
        {getPageNumbers().map((pageNum, i) => (
          <React.Fragment key={i}>
            {typeof pageNum === 'string' ? (
              <span className="inline-flex items-center border-t-2 border-transparent px-4 pt-4 text-sm font-medium text-gray-500">
                {pageNum}
              </span>
            ) : (
              <button
                onClick={() => onChange(pageNum)}
                className={classNames(
                  'inline-flex items-center border-t-2 px-4 pt-4 text-sm font-medium',
                  page === pageNum
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                )}
              >
                {pageNum}
              </button>
            )}
          </React.Fragment>
        ))}
      </div>
      <div className="-mt-px flex w-0 flex-1 justify-end">
        <button
          onClick={() => onChange(page + 1)}
          disabled={page >= totalPages}
          className={classNames(
            'inline-flex items-center border-t-2 pt-4 pl-1 text-sm font-medium',
            page >= totalPages
              ? 'border-transparent text-gray-400 cursor-not-allowed'
              : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
          )}
        >
          Next
          <ChevronRightIcon className="ml-3 h-5 w-5" aria-hidden="true" />
        </button>
      </div>
    </nav>
  );
}; 