import { BaseService } from '../base/BaseService';
import { User } from '../../core/interfaces/User';
import { Repository } from '../../core/interfaces/Repository';
import { Logger } from '../../utils/logger';
import { ServiceResult } from '../base/ServiceResult';

/**
 * Concrete service for User entity, extending the generic BaseService.
 * Demonstrates domain-specific validation and business logic.
 */
export class UserService extends BaseService<User> {
  protected readonly entityName = 'User';
  protected tableName = 'users';

  constructor(repository: Repository<User>, logger?: Logger) {
    super(repository, logger);
  }

  /**
   * Validate user entity data before creation or update.
   * Throws an error if validation fails.
   */
  protected async validateEntity(data: Partial<User>): Promise<void> {
    if (!data.username || typeof data.username !== 'string' || data.username.length < 3) {
      throw new Error('Username must be at least 3 characters long.');
    }
    if (!data.email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(data.email)) {
      throw new Error('A valid email address is required.');
    }
    // Additional domain-specific validation can be added here
  }

  /**
   * Example: Update user preferences with business logic and return a standardized result.
   */
  async updatePreferences(userId: string | number, preferences: Record<string, any>) {
    try {
      const user = await this.getById(userId);
      if (!user) {
        return ServiceResult.failure<User>('User not found');
      }
      const updated = await this.update(userId, {
        preferences: { ...user.preferences, ...preferences }
      });
      return ServiceResult.success<User>(updated);
    } catch (error: any) {
      this.logger.error('Failed to update user preferences', error);
      return ServiceResult.failure<User>(error.message);
    }
  }

  /**
   * Example: Add a collection to a user, with business rules.
   */
  async addCollection(userId: string | number, collectionId: string | number) {
    try {
      const user = await this.getById(userId);
      if (!user) {
        return ServiceResult.failure<User>('User not found');
      }
      if (user.collections.some(c => c.id === collectionId)) {
        return ServiceResult.failure<User>('Collection already added to user');
      }
      user.collections.push({ id: collectionId } as any); // Replace with proper collection fetch if needed
      const updated = await this.update(userId, { collections: user.collections });
      return ServiceResult.success<User>(updated);
    } catch (error: any) {
      this.logger.error('Failed to add collection to user', error);
      return ServiceResult.failure<User>(error.message);
    }
  }
} 