import { BaseEntity } from '../services/base/BaseEntity';

/**
 * User interface: represents a user in the system.
 */
export interface User extends BaseEntity {
  username: string;
  email: string;
  passwordHash: string;
  profileImageUrl?: string;
  role: 'user' | 'admin' | 'moderator';
  preferences?: Record<string, any>;
}

/**
 * Concrete implementation of User with authentication and profile management.
 */
export class UserModel implements User {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  isActive: boolean;
  username: string;
  email: string;
  passwordHash: string;
  profileImageUrl?: string;
  role: 'user' | 'admin' | 'moderator';
  preferences?: Record<string, any>;

  constructor(data: User) {
    this.id = data.id;
    this.createdAt = data.createdAt;
    this.updatedAt = data.updatedAt;
    this.isActive = data.isActive;
    this.username = data.username;
    this.email = data.email;
    this.passwordHash = data.passwordHash;
    this.profileImageUrl = data.profileImageUrl;
    this.role = data.role;
    this.preferences = data.preferences ? { ...data.preferences } : {};
    this.validate();
  }

  /**
   * Simulate password authentication (for demo; not secure for production).
   * In real code, use bcrypt or similar.
   */
  authenticate(password: string): boolean {
    // Simulate hash check: passwordHash is just 'hashed:' + password
    return this.passwordHash === `hashed:${password}`;
  }

  /**
   * Check if the user has a specific role.
   */
  hasRole(role: string): boolean {
    return this.role === role;
  }

  /**
   * Update profile fields (except id, createdAt, updatedAt, passwordHash).
   */
  updateProfile(data: Partial<User>): void {
    if (data.username) this.username = data.username;
    if (data.email) this.email = data.email;
    if (data.profileImageUrl) this.profileImageUrl = data.profileImageUrl;
    if (data.role) this.role = data.role;
    if (data.preferences) this.preferences = { ...this.preferences, ...data.preferences };
    this.updatedAt = new Date();
    this.validate();
  }

  /**
   * Validate the user fields.
   * Throws an error if validation fails.
   */
  validate() {
    if (!this.username || typeof this.username !== 'string') {
      throw new Error('Username is required.');
    }
    if (!this.email || typeof this.email !== 'string') {
      throw new Error('Email is required.');
    }
    if (!this.passwordHash || typeof this.passwordHash !== 'string') {
      throw new Error('Password hash is required.');
    }
    const allowedRoles = ['user', 'admin', 'moderator'];
    if (!allowedRoles.includes(this.role)) {
      throw new Error(`Invalid role: ${this.role}`);
    }
  }
}
