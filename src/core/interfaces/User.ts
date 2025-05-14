import { BaseEntity } from './BaseEntity';
import { Collection } from './Collection';

export interface User extends BaseEntity {
  username: string;
  email: string;
  collections: Collection[];
  preferences: Record<string, any>;
} 