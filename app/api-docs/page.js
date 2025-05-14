'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import 'swagger-ui-react/swagger-ui.css';

// Dynamically import SwaggerUI to avoid SSR issues
const SwaggerUI = dynamic(() => import('swagger-ui-react'), { ssr: false });

export default function ApiDocs() {
  const [spec, setSpec] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/docs')
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => setSpec(data))
      .catch((error) => {
        console.error('Error loading API docs:', error);
        setError(error.message);
      });
  }, []);

  if (error) {
    return (
      <div className="p-4">
        <h2 className="text-red-600 text-xl">Error loading API documentation</h2>
        <p className="text-gray-700">{error}</p>
      </div>
    );
  }

  if (!spec) {
    return (
      <div className="p-4">
        <h2 className="text-xl">Loading API documentation...</h2>
        <div className="mt-2 animate-pulse bg-gray-200 h-4 w-48 rounded"></div>
      </div>
    );
  }

  return (
    <div className="swagger-wrapper">
      <SwaggerUI spec={spec} />
      <style jsx global>{`
        .swagger-wrapper {
          padding: 1rem;
        }
        .swagger-ui .info .title {
          color: #2d3748;
        }
        .swagger-ui {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
        }
      `}</style>
    </div>
  );
} 