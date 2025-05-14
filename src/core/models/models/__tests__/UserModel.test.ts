import { User, UserModel } from '../User';

describe('UserModel', () => {
  const baseData: User = {
    id: 'user-1',
    createdAt: new Date(),
    updatedAt: new Date(),
    isActive: true,
    username: 'alice',
    email: 'alice@example.com',
    passwordHash: 'hashed:password123',
    role: 'user',
  };

  it('should instantiate with valid data', () => {
    const user = new UserModel(baseData);
    expect(user.username).toBe('alice');
    expect(user.email).toBe('alice@example.com');
    expect(user.role).toBe('user');
    expect(user.isActive).toBe(true);
  });

  it('should authenticate with correct password', () => {
    const user = new UserModel(baseData);
    expect(user.authenticate('password123')).toBe(true);
    expect(user.authenticate('wrong')).toBe(false);
  });

  it('should check roles correctly', () => {
    const user = new UserModel({ ...baseData, role: 'admin' });
    expect(user.hasRole('admin')).toBe(true);
    expect(user.hasRole('user')).toBe(false);
  });

  it('should update profile fields', () => {
    const user = new UserModel(baseData);
    user.updateProfile({ username: 'bob', email: 'bob@example.com', profileImageUrl: 'img.png', preferences: { theme: 'dark' } });
    expect(user.username).toBe('bob');
    expect(user.email).toBe('bob@example.com');
    expect(user.profileImageUrl).toBe('img.png');
    expect(user.preferences?.theme).toBe('dark');
  });

  it('should validate required fields and throw on invalid data', () => {
    expect(() => new UserModel({ ...baseData, username: '' })).toThrow();
    expect(() => new UserModel({ ...baseData, email: '' })).toThrow();
    expect(() => new UserModel({ ...baseData, passwordHash: '' })).toThrow();
    expect(() => new UserModel({ ...baseData, role: 'invalid' as any })).toThrow();
  });
}); 