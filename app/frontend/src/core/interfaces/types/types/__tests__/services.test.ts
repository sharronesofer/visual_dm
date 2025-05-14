import {
  IBaseService,
  ServiceEntity,
  ServiceCreateDTO,
  ServiceUpdateDTO,
  FullService,
  ServiceFactory,
  ServiceDecorator,
  ServiceEventHandler,
  ServiceMiddleware,
  ServiceQueryBuilder,
  ServiceHooks,
} from '../services';
import {
  ApiResponse,
  ValidationResult,
  ValidationError,
  ServiceConfig,
} from '../common';

// Test entity type
interface User {
  id: string;
  name: string;
  email: string;
}

// Test DTO types
interface CreateUserDTO {
  name: string;
  email: string;
}

interface UpdateUserDTO {
  name?: string;
  email?: string;
}

// Test service implementation
class UserService implements IBaseService<User, CreateUserDTO, UpdateUserDTO> {
  async create(data: CreateUserDTO): Promise<ApiResponse<User>> {
    return {
      success: true,
      data: { id: '1', ...data },
    };
  }

  async update(id: string, data: UpdateUserDTO): Promise<ApiResponse<User>> {
    return {
      success: true,
      data: { id, name: 'Test', email: 'test@example.com', ...data },
    };
  }

  async delete(id: string): Promise<ApiResponse<void>> {
    return {
      success: true,
      data: undefined,
    };
  }

  async getById(id: string): Promise<ApiResponse<User>> {
    return {
      success: true,
      data: { id, name: 'Test', email: 'test@example.com' },
    };
  }

  async getAll(): Promise<ApiResponse<User[]>> {
    return {
      success: true,
      data: [],
    };
  }

  async list(): Promise<ApiResponse<User[]>> {
    return {
      success: true,
      data: [],
    };
  }

  async validate(
    data: CreateUserDTO | UpdateUserDTO
  ): Promise<ValidationResult> {
    return {
      isValid: true,
      errors: [],
    };
  }

  async validateField(
    field: keyof (CreateUserDTO | UpdateUserDTO),
    value: any
  ): Promise<ValidationResult> {
    return {
      isValid: true,
      errors: [],
    };
  }

  getConfig(): ServiceConfig {
    return {
      baseURL: 'http://localhost:3000',
      timeout: 5000,
      headers: {},
    };
  }

  async setConfig(config: Record<string, any>): Promise<ApiResponse<void>> {
    return {
      success: true,
      data: undefined,
    };
  }
}

describe('Service Types', () => {
  describe('Type Extraction', () => {
    it('should correctly extract entity type', () => {
      type ExtractedEntity = ServiceEntity<UserService>;
      const user: ExtractedEntity = {
        id: '1',
        name: 'Test',
        email: 'test@example.com',
      };
      expect(user).toBeDefined();
    });

    it('should correctly extract create DTO type', () => {
      type ExtractedCreateDTO = ServiceCreateDTO<UserService>;
      const createDTO: ExtractedCreateDTO = {
        name: 'Test',
        email: 'test@example.com',
      };
      expect(createDTO).toBeDefined();
    });

    it('should correctly extract update DTO type', () => {
      type ExtractedUpdateDTO = ServiceUpdateDTO<UserService>;
      const updateDTO: ExtractedUpdateDTO = {
        name: 'Updated',
      };
      expect(updateDTO).toBeDefined();
    });
  });

  describe('Service Factory', () => {
    it('should create service instance', () => {
      const factory: ServiceFactory<User, CreateUserDTO, UpdateUserDTO> = {
        create: () => new UserService(),
      };
      const service = factory.create();
      expect(service).toBeInstanceOf(UserService);
    });
  });

  describe('Service Decorator', () => {
    it('should decorate service', () => {
      const decorator: ServiceDecorator<
        User,
        CreateUserDTO,
        UpdateUserDTO
      > = service => {
        return {
          ...service,
          async create(data) {
            console.log('Creating user:', data);
            return service.create(data);
          },
        };
      };
      const service = new UserService();
      const decorated = decorator(service);
      expect(decorated.create).toBeDefined();
    });
  });

  describe('Service Event Handler', () => {
    it('should handle events', async () => {
      const handler: ServiceEventHandler<User> = {
        onCreated: jest.fn(),
        onUpdated: jest.fn(),
        onDeleted: jest.fn(),
        onError: jest.fn(),
      };

      const user = { id: '1', name: 'Test', email: 'test@example.com' };
      await handler.onCreated!(user);
      await handler.onUpdated!(user);
      await handler.onDeleted!('1');
      await handler.onError!(new Error('Test error'));

      expect(handler.onCreated).toHaveBeenCalledWith(user);
      expect(handler.onUpdated).toHaveBeenCalledWith(user);
      expect(handler.onDeleted).toHaveBeenCalledWith('1');
      expect(handler.onError).toHaveBeenCalledWith(expect.any(Error));
    });
  });

  describe('Service Query Builder', () => {
    it('should build query', () => {
      const builder: ServiceQueryBuilder<User> = {
        where: jest.fn().mockReturnThis(),
        orderBy: jest.fn().mockReturnThis(),
        limit: jest.fn().mockReturnThis(),
        offset: jest.fn().mockReturnThis(),
        include: jest.fn().mockReturnThis(),
        build: jest.fn().mockReturnValue({ where: { name: 'Test' } }),
      };

      builder
        .where({ name: 'Test' })
        .orderBy('name', 'asc')
        .limit(10)
        .offset(0)
        .include(['posts']);

      const query = builder.build();
      expect(query).toEqual({ where: { name: 'Test' } });
    });
  });

  describe('Service Hooks', () => {
    it('should handle hooks', async () => {
      const hooks: ServiceHooks<User, CreateUserDTO, UpdateUserDTO> = {
        beforeCreate: jest.fn().mockImplementation(data => data),
        afterCreate: jest.fn().mockImplementation(entity => entity),
        beforeUpdate: jest.fn().mockImplementation((id, data) => data),
        afterUpdate: jest.fn().mockImplementation(entity => entity),
        beforeDelete: jest.fn(),
        afterDelete: jest.fn(),
      };

      const createData = { name: 'Test', email: 'test@example.com' };
      const updateData = { name: 'Updated' };
      const user = { id: '1', name: 'Test', email: 'test@example.com' };

      await hooks.beforeCreate!(createData);
      await hooks.afterCreate!(user);
      await hooks.beforeUpdate!('1', updateData);
      await hooks.afterUpdate!(user);
      await hooks.beforeDelete!('1');
      await hooks.afterDelete!('1');

      expect(hooks.beforeCreate).toHaveBeenCalledWith(createData);
      expect(hooks.afterCreate).toHaveBeenCalledWith(user);
      expect(hooks.beforeUpdate).toHaveBeenCalledWith('1', updateData);
      expect(hooks.afterUpdate).toHaveBeenCalledWith(user);
      expect(hooks.beforeDelete).toHaveBeenCalledWith('1');
      expect(hooks.afterDelete).toHaveBeenCalledWith('1');
    });
  });
});
