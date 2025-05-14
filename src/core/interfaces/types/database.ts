/**
 * Database query result type
 */
export type QueryResult = Record<string, any>[];

/**
 * Database interface for persistence operations
 */
export interface Database {
  /**
   * Execute a SQL statement
   */
  execute(sql: string, params?: any[]): Promise<void>;

  /**
   * Execute a SQL query and return results
   */
  query(sql: string, params?: any[]): Promise<QueryResult>;

  /**
   * Begin a transaction if supported
   */
  beginTransaction?(): Promise<void>;

  /**
   * Commit a transaction if supported
   */
  commitTransaction?(): Promise<void>;

  /**
   * Rollback a transaction if supported
   */
  rollbackTransaction?(): Promise<void>;
} 