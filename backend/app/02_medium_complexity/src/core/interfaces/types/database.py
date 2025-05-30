from typing import Any, Dict, List



/**
 * Database query result type
 */
QueryResult = List[Dict[str, Any>]
/**
 * Database interface for persistence operations
 */
class Database:
    /**
   * Execute a SQL statement
   */
  execute(sql: str, params?: Any[]): Awaitable[None>
    /**
   * Execute a SQL query and return results
   */
  query(sql: str, params?: Any[]): Awaitable[QueryResult>
    /**
   * Begin a transaction if supported
   */
  beginTransaction?(): Awaitable[None>
    /**
   * Commit a transaction if supported
   */
  commitTransaction?(): Awaitable[None>
    /**
   * Rollback a transaction if supported
   */
  rollbackTransaction?(): Awaitable[None> 