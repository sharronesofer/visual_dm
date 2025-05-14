/**
 * Export all data models, types, and type guards
 *
 * Relationships:
 * - User may own Collections (one-to-many, via Collection IDs)
 * - Collection contains MediaAssets (one-to-many, via MediaAsset IDs)
 * - MediaAsset may reference User as creator/owner (via User ID)
 *
 * All relationships are decoupled using IDs for flexibility and to avoid circular dependencies.
 */

// Add export statements here as components are implemented
export { BaseEntity } from '../services/base/BaseEntity';
export { User, UserModel } from './User';
export { MediaAsset, MediaAssetModel } from './MediaAsset';
export { Collection, CollectionModel } from './Collection';
export * from './typeGuards';
