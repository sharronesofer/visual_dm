from typing import Any


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
{ BaseEntity } from '../services/base/BaseEntity'
{ User, UserModel } from './User'
{ MediaAsset, MediaAssetModel } from './MediaAsset'
{ Collection, CollectionModel } from './Collection'
* from './typeGuards'