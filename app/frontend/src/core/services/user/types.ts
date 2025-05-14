import { BaseEntity } from '../base.service';

export interface User extends BaseEntity {
  email: string;
  username: string;
  firstName?: string;
  lastName?: string;
  isActive: boolean;
  role: 'user' | 'admin';
  lastLoginAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateUserDTO {
  email: string;
  username: string;
  password: string;
  firstName?: string;
  lastName?: string;
  role?: 'user' | 'admin';
}

export interface UpdateUserDTO extends Partial<Omit<CreateUserDTO, 'password'>> {
  isActive?: boolean;
}

export interface UserSearchParams {
  role?: 'user' | 'admin';
  isActive?: boolean;
  query?: string;
} 