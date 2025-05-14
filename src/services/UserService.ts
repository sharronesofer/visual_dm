import { BaseService } from './base/BaseService';
import { User } from '../models/User';
import { ServiceResponse, ValidationError } from './base/types';
import { hashPassword, comparePassword } from '../utils/password';
import { generateToken } from '../utils/auth';
import { NotFoundError } from '../errors/NotFoundError';
import { ValidationError as ValidationErrorClass } from '../errors/ValidationError';
import { AxiosError } from 'axios';

export interface CreateUserDTO {
  email: string;
  password: string;
  firstName?: string;
  lastName?: string;
  role?: 'user' | 'admin';
}

export interface UpdateUserDTO {
  email?: string;
  password?: string;
  firstName?: string;
  lastName?: string;
  role?: 'user' | 'admin';
}

export interface LoginResponse {
  user: Omit<User, 'password'>;
  token: string;
}

export class UserService extends BaseService<User> {
  protected tableName = 'users';

  /**
   * Login a user with email and password
   */
  async login(email: string, password: string): Promise<ServiceResponse<LoginResponse>> {
    try {
      const user = await this.findByEmail(email);
      if (!user) {
        throw new NotFoundError('User not found');
      }

      const isPasswordValid = await comparePassword(password, user.password);
      if (!isPasswordValid) {
        throw new ValidationErrorClass('Invalid password');
      }

      const token = generateToken(user);
      const { password: _, ...userWithoutPassword } = user;

      return {
        success: true,
        data: {
          user: userWithoutPassword,
          token,
        },
      };
    } catch (error) {
      return this.handleError(error);
    }
  }

  /**
   * Find a user by email
   */
  async findByEmail(email: string): Promise<User | null> {
    const users = await this.performFindAll({ email });
    return users[0] || null;
  }

  /**
   * Override create to hash password
   */
  async create(data: CreateUserDTO): Promise<ServiceResponse<User>> {
    try {
      // Hash password before creating user
      const hashedPassword = await hashPassword(data.password);
      const userData = {
        ...data,
        password: hashedPassword,
        role: data.role || 'user',
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      return super.create(userData);
    } catch (error) {
      return this.handleError(error);
    }
  }

  /**
   * Override update to hash password if provided
   */
  async update(id: string, data: UpdateUserDTO): Promise<ServiceResponse<User>> {
    try {
      const updateData: Partial<User> = {
        ...data,
        updatedAt: new Date(),
      };

      if (data.password) {
        updateData.password = await hashPassword(data.password);
      }

      return super.update(id, updateData);
    } catch (error) {
      return this.handleError(error);
    }
  }

  /**
   * Validate user data
   */
  protected async validateEntity(data: Partial<User>, isUpdate: boolean = false): Promise<void> {
    await super.validateEntity(data, isUpdate);

    const errors: ValidationError[] = [];

    // Email validation
    if (!isUpdate || data.email) {
      if (!data.email) {
        errors.push({ field: 'email', message: 'Email is required' });
      } else if (!this.isValidEmail(data.email)) {
        errors.push({ field: 'email', message: 'Invalid email format' });
      }

      // Check for existing email
      if (data.email) {
        const existingUser = await this.findByEmail(data.email);
        if (existingUser) {
          errors.push({ field: 'email', message: 'Email already exists' });
        }
      }
    }

    // Password validation
    if (!isUpdate || data.password) {
      if (!data.password) {
        errors.push({ field: 'password', message: 'Password is required' });
      } else if (data.password.length < 8) {
        errors.push({ field: 'password', message: 'Password must be at least 8 characters long' });
      }
    }

    // Role validation
    if (data.role && !['user', 'admin'].includes(data.role)) {
      errors.push({ field: 'role', message: 'Invalid role' });
    }

    if (errors.length > 0) {
      throw new ValidationErrorClass(
        'Validation failed: ' + errors.map(e => `${e.field}: ${e.message}`).join(', ')
      );
    }
  }

  /**
   * Validate email format
   */
  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  // Implement abstract methods
  protected async performCreate(data: Partial<User>): Promise<User> {
    const response = await this.client.post<User>('/users', data);
    return response.data;
  }

  protected async performFindById(id: string): Promise<User | null> {
    try {
      const response = await this.client.get<User>(`/users/${id}`);
      return response.data;
    } catch (error) {
      if ((error as AxiosError).response?.status === 404) {
        return null;
      }
      throw error;
    }
  }

  protected async performFindAll(filter?: Partial<User>): Promise<User[]> {
    const response = await this.client.get<User[]>('/users', { params: filter });
    return response.data;
  }

  protected async performUpdate(id: string, data: Partial<User>): Promise<User> {
    const response = await this.client.put<User>(`/users/${id}`, data);
    return response.data;
  }

  protected async performDelete(id: string): Promise<void> {
    await this.client.delete(`/users/${id}`);
  }
}
