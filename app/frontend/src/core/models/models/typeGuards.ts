import { User } from './User';
import { MediaAsset } from './MediaAsset';
import { Collection } from './Collection';

export function isUser(obj: any): obj is User {
  return (
    obj &&
    typeof obj === 'object' &&
    typeof obj.id === 'string' &&
    typeof obj.username === 'string' &&
    typeof obj.email === 'string' &&
    typeof obj.passwordHash === 'string' &&
    typeof obj.role === 'string' &&
    typeof obj.isActive === 'boolean'
  );
}

export function isMediaAsset(obj: any): obj is MediaAsset {
  return (
    obj &&
    typeof obj === 'object' &&
    typeof obj.id === 'string' &&
    typeof obj.title === 'string' &&
    typeof obj.fileUrl === 'string' &&
    typeof obj.fileType === 'string' &&
    typeof obj.fileSize === 'number' &&
    typeof obj.isActive === 'boolean'
  );
}

export function isCollection(obj: any): obj is Collection {
  return (
    obj &&
    typeof obj === 'object' &&
    typeof obj.id === 'string' &&
    typeof obj.name === 'string' &&
    Array.isArray(obj.mediaAssets) &&
    typeof obj.visibility === 'string' &&
    typeof obj.isActive === 'boolean'
  );
} 