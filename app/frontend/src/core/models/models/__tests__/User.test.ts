import { BaseEntity } from '../services/base/BaseEntity';
import { User } from '../User';

describe('User interface', () => {
  it('should extend BaseEntity and require all base fields', () => {
    const user: User = {
      id: 'uuid-123',
      createdAt: new Date(),
      updatedAt: new Date(),
      isActive: true,
      email: 'test@example.com',
      password: 'hashed',
      role: 'user',
    };
    expect(user.id).toBeDefined();
    expect(user.isActive).toBe(true);
  });

  it('should not allow missing base fields', () => {
    // @ts-expect-error
    const invalidUser: User = {
      email: 'test@example.com',
      password: 'hashed',
      role: 'user',
      // missing id, createdAt, updatedAt, isActive
    };
    expect(invalidUser).toBeDefined();
  });
}); 