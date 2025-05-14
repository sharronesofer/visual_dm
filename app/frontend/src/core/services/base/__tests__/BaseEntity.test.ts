import { BaseEntity } from '../BaseEntity';

describe('BaseEntity interface', () => {
  it('should allow extension by other interfaces', () => {
    interface TestEntity extends BaseEntity {
      name: string;
    }
    const entity: TestEntity = {
      id: 'uuid-456',
      createdAt: new Date(),
      updatedAt: new Date(),
      isActive: true,
      name: 'Test',
    };
    expect(entity.id).toBeDefined();
    expect(entity.isActive).toBe(true);
    expect(entity.name).toBe('Test');
  });

  it('should not allow missing required fields', () => {
    // @ts-expect-error
    const invalidEntity: BaseEntity = {
      // missing id, createdAt, updatedAt, isActive
    };
    expect(invalidEntity).toBeDefined();
  });
}); 