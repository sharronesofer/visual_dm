/**
 * Base entity interface that all domain entities should implement
 */
export interface BaseEntity {
    id: string | number;
    createdAt?: Date;
    updatedAt?: Date;
} 