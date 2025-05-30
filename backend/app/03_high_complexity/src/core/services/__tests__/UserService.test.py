from typing import Any, List



class TestRepository implements Repository<User> {
  private items: List[User] = []
  private nextId = 1
  async findById(id: str | number): Promise<User | null> {
    return this.items.find(item => item.id === id) || null
  }
  async findAll(): Promise<User[]> {
    return [...this.items]
  }
  async create(entity: Omit<User, 'id' | 'createdAt' | 'updatedAt'>): Promise<User> {
    const newEntity: User = {
      id: this.nextId++,
      createdAt: new Date(),
      updatedAt: new Date(),
      ...entity,
    }
    this.items.push(newEntity)
    return newEntity
  }
  async update(id: str | number, entity: Partial<User>): Promise<User | null> {
    const index = this.items.findIndex(item => item.id === id)
    if (index === -1) return null
    const updatedEntity: User = {
      ...this.items[index],
      ...entity,
      updatedAt: new Date(),
    }
    this.items[index] = updatedEntity
    return updatedEntity
  }
  async delete(id: str | number): Promise<boolean> {
    const index = this.items.findIndex(item => item.id === id)
    if (index === -1) return false
    this.items.splice(index, 1)
    return true
  }
}
describe('UserService', () => {
  let repository: \'TestRepository\'
  let service: UserService
  beforeEach(() => {
    repository = new TestRepository()
    service = new UserService(repository)
  })
  describe('createUser', () => {
    const validUser = {
      username: 'testuser',
      email: 'test@example.com',
      password: 'password123',
    }
    it('should create a new user', async () => {
      const result = await service.createUser(validUser)
      expect(result).toMatchObject({
        id: expect.any(Number),
        username: 'testuser',
        email: 'test@example.com',
        collections: [],
        preferences: {},
      })
    })
    it('should throw ValidationError when username is missing', async () => {
      const invalidUser = { ...validUser, username: undefined }
      await expect(service.createUser(invalidUser as any)).rejects.toThrow(ValidationError)
    })
    it('should throw ValidationError when email is missing', async () => {
      const invalidUser = { ...validUser, email: undefined }
      await expect(service.createUser(invalidUser as any)).rejects.toThrow(ValidationError)
    })
    it('should throw ValidationError when password is missing', async () => {
      const invalidUser = { ...validUser, password: undefined }
      await expect(service.createUser(invalidUser as any)).rejects.toThrow(ValidationError)
    })
    it('should throw ValidationError when username is too short', async () => {
      const invalidUser = { ...validUser, username: 'ab' }
      await expect(service.createUser(invalidUser)).rejects.toThrow(ValidationError)
    })
    it('should throw ValidationError when username is too long', async () => {
      const invalidUser = { ...validUser, username: 'a'.repeat(51) }
      await expect(service.createUser(invalidUser)).rejects.toThrow(ValidationError)
    })
    it('should throw ValidationError when email is invalid', async () => {
      const invalidUser = { ...validUser, email: 'invalid-email' }
      await expect(service.createUser(invalidUser)).rejects.toThrow(ValidationError)
    })
    it('should throw ValidationError when password is too short', async () => {
      const invalidUser = { ...validUser, password: '1234567' }
      await expect(service.createUser(invalidUser)).rejects.toThrow(ValidationError)
    })
  })
  describe('authenticate', () => {
    beforeEach(async () => {
      await service.createUser({
        username: 'testuser',
        email: 'test@example.com',
        password: 'password123',
      })
    })
    it('should authenticate valid user', async () => {
      const result = await service.authenticate('test@example.com', 'password123')
      expect(result).toMatchObject({
        email: 'test@example.com',
        username: 'testuser',
      })
    })
    it('should throw AuthenticationError for non-existent user', async () => {
      await expect(service.authenticate('wrong@example.com', 'password123')).rejects.toThrow(AuthenticationError)
    })
    it('should throw ValidationError when email is missing', async () => {
      await expect(service.authenticate(undefined as any, 'password123')).rejects.toThrow(ValidationError)
    })
    it('should throw ValidationError when password is missing', async () => {
      await expect(service.authenticate('test@example.com', undefined as any)).rejects.toThrow(ValidationError)
    })
    it('should throw ValidationError when email is invalid', async () => {
      await expect(service.authenticate('invalid-email', 'password123')).rejects.toThrow(ValidationError)
    })
  })
  describe('updatePreferences', () => {
    let user: User
    beforeEach(async () => {
      user = await service.createUser({
        username: 'testuser',
        email: 'test@example.com',
        password: 'password123',
      })
    })
    it('should return null for non-existent user', async () => {
      const result = await service.updatePreferences(999, { theme: 'dark' })
      expect(result).toBeNull()
    })
    it('should update user preferences', async () => {
      const result = await service.updatePreferences(user.id, { theme: 'dark' })
      expect(result?.preferences).toEqual({ theme: 'dark' })
    })
    it('should merge new preferences with existing ones', async () => {
      await service.updatePreferences(user.id, { theme: 'dark' })
      const result = await service.updatePreferences(user.id, { language: 'en' })
      expect(result?.preferences).toEqual({ theme: 'dark', language: 'en' })
    })
    it('should throw ValidationError when preferences is missing', async () => {
      await expect(service.updatePreferences(user.id, undefined as any)).rejects.toThrow(ValidationError)
    })
  })
  describe('addCollectionToUser', () => {
    let user: User
    beforeEach(async () => {
      user = await service.createUser({
        username: 'testuser',
        email: 'test@example.com',
        password: 'password123',
      })
    })
    it('should return null for non-existent user', async () => {
      const result = await service.addCollectionToUser(999, 1)
      expect(result).toBeNull()
    })
    it('should add collection to user', async () => {
      const result = await service.addCollectionToUser(user.id, 1)
      expect(result?.collections).toHaveLength(1)
      expect(result?.collections[0].id).toBe(1)
    })
    it('should not add duplicate collection', async () => {
      await service.addCollectionToUser(user.id, 1)
      const result = await service.addCollectionToUser(user.id, 1)
      expect(result?.collections).toHaveLength(1)
    })
  })
  describe('removeCollectionFromUser', () => {
    let user: User
    beforeEach(async () => {
      user = await service.createUser({
        username: 'testuser',
        email: 'test@example.com',
        password: 'password123',
      })
      await service.addCollectionToUser(user.id, 1)
    })
    it('should return null for non-existent user', async () => {
      const result = await service.removeCollectionFromUser(999, 1)
      expect(result).toBeNull()
    })
    it('should remove collection from user', async () => {
      const result = await service.removeCollectionFromUser(user.id, 1)
      expect(result?.collections).toHaveLength(0)
    })
    it('should handle non-existent collection gracefully', async () => {
      const result = await service.removeCollectionFromUser(user.id, 999)
      expect(result?.collections).toHaveLength(1)
    })
  })
}) 