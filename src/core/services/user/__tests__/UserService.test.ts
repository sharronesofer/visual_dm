import { UserService, UserEntity } from '../UserService';
import { Logger } from '../../../utils/logger';
import { ValidationError, NotFoundError } from '../../../errors';
import { Transaction } from '../../../types/Transaction';

describe('UserService', () => {
  let service: UserService;
  let logger: Logger;

  beforeEach(() => {
    logger = new Logger('UserService');
    service = new UserService(logger);

    // Mock the abstract methods with type assertions
    jest.spyOn(service as any, 'executeCreate').mockImplementation(
      (async (data: Partial<UserEntity>) => ({
        id: '1',
        ...data,
        createdAt: new Date(),
        updatedAt: new Date()
      })) as unknown as (...args: unknown[]) => unknown
    );

    jest.spyOn(service as any, 'executeFindById').mockImplementation(
      (async (id: string | number) => {
        if (id === '1') {
          return {
            id: '1',
            email: 'test@example.com',
            username: 'testuser',
            passwordHash: 'hashedpassword',
            isActive: true,
            role: 'user',
            createdAt: new Date(),
            updatedAt: new Date()
          };
        }
        return null;
      }) as unknown as (...args: unknown[]) => unknown
    );

    jest.spyOn(service as any, 'executeUpdate').mockImplementation(
      (async (id: string | number, data: Partial<UserEntity>) => ({
        id,
        ...data,
        updatedAt: new Date()
      })) as unknown as (...args: unknown[]) => unknown
    );

    jest.spyOn(service as any, 'executeDelete').mockImplementation(
      (async () => {}) as unknown as (...args: unknown[]) => unknown
    );
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('validateEntity', () => {
    it('should validate a valid user entity', async () => {
      const validEntity: Partial<UserEntity> = {
        email: 'test@example.com',
        username: 'testuser',
        passwordHash: 'hashedpassword',
        isActive: true,
        role: 'user'
      };

      await expect(service['validateEntity'](validEntity)).resolves.not.toThrow();
    });

    it('should throw ValidationError for missing required fields', async () => {
      const invalidEntity: Partial<UserEntity> = {
        email: 'test@example.com',
        username: 'testuser'
      };

      await expect(service['validateEntity'](invalidEntity)).rejects.toThrow(ValidationError);
    });

    it('should throw ValidationError for invalid email format', async () => {
      const invalidEntity: Partial<UserEntity> = {
        email: 'invalid-email',
        username: 'testuser',
        passwordHash: 'hashedpassword'
      };

      await expect(service['validateEntity'](invalidEntity)).rejects.toThrow(ValidationError);
    });

    it('should throw ValidationError for short username', async () => {
      const invalidEntity: Partial<UserEntity> = {
        email: 'test@example.com',
        username: 'te',
        passwordHash: 'hashedpassword'
      };

      await expect(service['validateEntity'](invalidEntity)).rejects.toThrow(ValidationError);
    });

    it('should throw ValidationError for invalid role', async () => {
      const invalidEntity: Partial<UserEntity> = {
        email: 'test@example.com',
        username: 'testuser',
        passwordHash: 'hashedpassword',
        role: 'superuser' as any
      };

      await expect(service['validateEntity'](invalidEntity)).rejects.toThrow(ValidationError);
    });
  });

  describe('updateLastLogin', () => {
    it('should update last login timestamp successfully', async () => {
      const updateSpy = jest.spyOn(service, 'update');
      await service.updateLastLogin('1');

      expect(updateSpy).toHaveBeenCalledWith('1', expect.objectContaining({
        lastLoginAt: expect.any(Date)
      }), undefined);
    });

    it('should throw NotFoundError for non-existent user', async () => {
      await expect(service.updateLastLogin('999')).rejects.toThrow(NotFoundError);
    });
  });

  describe('deactivateUser', () => {
    it('should deactivate user successfully', async () => {
      const updateSpy = jest.spyOn(service, 'update');
      await service.deactivateUser('1');

      expect(updateSpy).toHaveBeenCalledWith('1', expect.objectContaining({
        isActive: false
      }), undefined);
    });

    it('should throw NotFoundError for non-existent user', async () => {
      await expect(service.deactivateUser('999')).rejects.toThrow(NotFoundError);
    });
  });

  describe('activateUser', () => {
    it('should activate user successfully', async () => {
      const updateSpy = jest.spyOn(service, 'update');
      await service.activateUser('1');

      expect(updateSpy).toHaveBeenCalledWith('1', expect.objectContaining({
        isActive: true
      }), undefined);
    });

    it('should throw NotFoundError for non-existent user', async () => {
      await expect(service.activateUser('999')).rejects.toThrow(NotFoundError);
    });
  });

  describe('changeRole', () => {
    it('should change user role successfully', async () => {
      const updateSpy = jest.spyOn(service, 'update');
      await service.changeRole('1', 'admin');

      expect(updateSpy).toHaveBeenCalledWith('1', expect.objectContaining({
        role: 'admin'
      }), undefined);
    });

    it('should throw NotFoundError for non-existent user', async () => {
      await expect(service.changeRole('999', 'admin')).rejects.toThrow(NotFoundError);
    });
  });
}); 