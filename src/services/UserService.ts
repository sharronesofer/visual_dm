import { BaseService } from './base/BaseService';
import { User } from '../models/User';
import { ServiceResponse, ValidationError } from './base/types';
import { hashPassword, comparePassword } from '../utils/password';
import { generateToken } from '../utils/auth';
import { NotFoundError } from '../errors/NotFoundError';
import { ValidationError as ValidationErrorClass } from '../errors/ValidationError';
import { AxiosError } from 'axios';
import { generateMfaSecret, verifyToken, verifyBackupCode } from '../utils/mfa';

export interface CreateUserDTO {
  email: string;
  password: string;
  firstName?: string;
  lastName?: string;
  role?: 'user' | 'admin';
  paymentEnabled?: boolean;
}

export interface UpdateUserDTO {
  email?: string;
  password?: string;
  firstName?: string;
  lastName?: string;
  role?: 'user' | 'admin';
  paymentEnabled?: boolean;
}

export interface LoginResponse {
  user: Omit<User, 'password'>;
  token: string;
  requiresMfa: boolean;
}

export interface MfaSetupResponse {
  secret: string;
  otpauth_url: string;
  backup_codes: string[];
  qrcode?: string;
}

export interface VerifyMfaDTO {
  userId: string;
  token: string;
  isBackupCode?: boolean;
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

      // Check if the user needs MFA
      const requiresMfa = user.paymentEnabled || user.mfaEnabled;

      return {
        success: true,
        data: {
          user: userWithoutPassword,
          token,
          requiresMfa,
        },
      };
    } catch (error) {
      return this.handleError(error);
    }
  }

  /**
   * Setup MFA for a user
   */
  async setupMfa(userId: string): Promise<ServiceResponse<MfaSetupResponse>> {
    try {
      const userResult = await this.findById(userId);
      if (!userResult.success || !userResult.data) {
        throw new NotFoundError('User not found');
      }

      const user = userResult.data;
      const mfaData = generateMfaSecret(user.email);

      // Update user with MFA data
      await this.update(userId, {
        mfaSecret: mfaData.secret,
        mfaBackupCodes: mfaData.backup_codes,
        // Don't enable MFA until verification is complete
      });

      return {
        success: true,
        data: mfaData,
      };
    } catch (error) {
      return this.handleError(error);
    }
  }

  /**
   * Enable MFA for a user after verifying the initial token
   */
  async enableMfa(userId: string, token: string): Promise<ServiceResponse<boolean>> {
    try {
      const userResult = await this.findById(userId);
      if (!userResult.success || !userResult.data) {
        throw new NotFoundError('User not found');
      }

      const user = userResult.data;

      if (!user.mfaSecret) {
        throw new ValidationErrorClass('MFA setup not completed');
      }

      // Verify the provided token
      const isValid = verifyToken(token, user.mfaSecret);
      if (!isValid) {
        throw new ValidationErrorClass('Invalid MFA token');
      }

      // Enable MFA for the user
      await this.update(userId, { mfaEnabled: true });

      return {
        success: true,
        data: true,
      };
    } catch (error) {
      return this.handleError(error);
    }
  }

  /**
   * Verify MFA token or backup code
   */
  async verifyMfa(data: VerifyMfaDTO): Promise<ServiceResponse<{ token: string }>> {
    try {
      const userResult = await this.findById(data.userId);
      if (!userResult.success || !userResult.data) {
        throw new NotFoundError('User not found');
      }

      const user = userResult.data;

      if (!user.mfaEnabled || !user.mfaSecret) {
        throw new ValidationErrorClass('MFA not enabled for this user');
      }

      let isValid = false;

      // Check if this is a backup code
      if (data.isBackupCode && user.mfaBackupCodes && user.mfaBackupCodes.length > 0) {
        const matchingCode = verifyBackupCode(data.token, user.mfaBackupCodes);
        if (matchingCode) {
          // Remove used backup code
          const updatedCodes = user.mfaBackupCodes.filter(code => code !== matchingCode);
          await this.update(data.userId, { mfaBackupCodes: updatedCodes });
          isValid = true;
        }
      } else {
        // Verify TOTP token
        isValid = verifyToken(data.token, user.mfaSecret);
      }

      if (!isValid) {
        throw new ValidationErrorClass('Invalid MFA token or backup code');
      }

      // Generate a new authentication token with MFA verified
      const authToken = generateToken({
        ...user,
        mfaVerified: true, // Add MFA verification to the token
      });

      return {
        success: true,
        data: {
          token: authToken,
        },
      };
    } catch (error) {
      return this.handleError(error);
    }
  }

  /**
   * Disable MFA for a user
   */
  async disableMfa(userId: string): Promise<ServiceResponse<boolean>> {
    try {
      const userResult = await this.findById(userId);
      if (!userResult.success || !userResult.data) {
        throw new NotFoundError('User not found');
      }

      const user = userResult.data;

      // Check if user has payment enabled
      if (user.paymentEnabled) {
        throw new ValidationErrorClass('Cannot disable MFA for users with payment enabled');
      }

      // Disable MFA
      await this.update(userId, {
        mfaEnabled: false,
        mfaSecret: undefined,
        mfaBackupCodes: []
      });

      return {
        success: true,
        data: true,
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
        mfaEnabled: false, // Initialize MFA as disabled
        paymentEnabled: data.paymentEnabled || false,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      // If payment is enabled, we need to ensure MFA setup is part of onboarding
      if (userData.paymentEnabled) {
        userData.mfaRequired = true;
      }

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
      // If enabling payment, ensure MFA is required
      if (data.paymentEnabled) {
        const userResult = await this.findById(id);
        if (userResult.success && userResult.data) {
          const user = userResult.data;
          if (!user.mfaEnabled) {
            throw new ValidationErrorClass('MFA must be enabled before enabling payments');
          }
        }
      }

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
      } else if (data.password.length < 12) {
        errors.push({ field: 'password', message: 'Password must be at least 12 characters long' });
      }
    }

    // Role validation
    if (data.role && !['user', 'admin'].includes(data.role)) {
      errors.push({ field: 'role', message: 'Invalid role' });
    }

    // MFA validation
    if (data.paymentEnabled && (!data.mfaEnabled && !isUpdate)) {
      errors.push({ field: 'mfaEnabled', message: 'MFA must be enabled for payment-enabled users' });
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
