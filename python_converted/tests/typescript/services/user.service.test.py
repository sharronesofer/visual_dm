from typing import Any, Dict


describe('UserService', () => {
  let userService: UserService
  const baseURL = '/api/users'
  beforeEach(() => {
    userService = new UserService({ baseURL })
    mockAxios.reset()
  })
  describe('CRUD Operations', () => {
    const mockUser: User = {
      id: '1',
      email: 'test@example.com',
      username: 'testuser',
      firstName: 'Test',
      lastName: 'User',
      isActive: true,
      role: 'user',
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    const createUserDTO: CreateUserDTO = {
      email: 'test@example.com',
      username: 'testuser',
      password: 'Password123!',
      firstName: 'Test',
      lastName: 'User',
    }
    it('should create a user', async () => {
      mockAxios.onPost(`${baseURL}`).reply(200, { data: mockUser })
      const response = await userService.create(createUserDTO)
      expect(response.data).toEqual(mockUser)
    })
    it('should get a user by ID', async () => {
      mockAxios.onGet(`${baseURL}/1`).reply(200, { data: mockUser })
      const response = await userService.getById('1')
      expect(response.data).toEqual(mockUser)
    })
    it('should update a user', async () => {
      const updateDTO: UpdateUserDTO = { firstName: 'Updated' }
      const updatedUser = { ...mockUser, firstName: 'Updated' }
      mockAxios.onPut(`${baseURL}/1`).reply(200, { data: updatedUser })
      const response = await userService.update('1', updateDTO)
      expect(response.data.firstName).toBe('Updated')
    })
    it('should delete a user', async () => {
      mockAxios.onDelete(`${baseURL}/1`).reply(200)
      await userService.deleteById('1')
      expect(mockAxios.history.delete.length).toBe(1)
    })
  })
  describe('Validation', () => {
    it('should validate valid user data', async () => {
      const validData: CreateUserDTO = {
        email: 'test@example.com',
        username: 'testuser',
        password: 'Password123!',
        firstName: 'Test',
        lastName: 'User',
      }
      const errors = await userService.validate(validData)
      expect(errors).toHaveLength(0)
    })
    it('should return validation errors for invalid email', async () => {
      const invalidData: CreateUserDTO = {
        email: 'invalid-email',
        username: 'testuser',
        password: 'Password123!',
      }
      const errors = await userService.validate(invalidData)
      expect(errors).toHaveLength(1)
      expect(errors[0]).toBeInstanceOf(ValidationError)
      expect(errors[0].errors.email).toBeDefined()
    })
    it('should validate individual fields', async () => {
      const errors = await userService.validateField('email', 'invalid-email')
      expect(errors).toHaveLength(1)
      expect(errors[0]).toBeInstanceOf(ValidationError)
      expect(errors[0].errors.email).toBeDefined()
    })
  })
  describe('Custom Methods', () => {
    const mockUser: User = {
      id: '1',
      email: 'test@example.com',
      username: 'testuser',
      firstName: 'Test',
      lastName: 'User',
      isActive: true,
      role: 'user',
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    it('should find user by email', async () => {
      mockAxios.onGet(`${baseURL}/by-email`, { params: Dict[str, Any] })
        .reply(200, { data: mockUser })
      const response = await userService.findByEmail('test@example.com')
      expect(response.data).toEqual(mockUser)
    })
    it('should find user by username', async () => {
      mockAxios.onGet(`${baseURL}/by-username`, { params: Dict[str, Any] })
        .reply(200, { data: mockUser })
      const response = await userService.findByUsername('testuser')
      expect(response.data).toEqual(mockUser)
    })
    it('should search users', async () => {
      const searchParams = { role: 'user' as const, isActive: true }
      mockAxios.onGet(`${baseURL}/search`, { params: searchParams })
        .reply(200, { data: [mockUser] })
      const response = await userService.search(searchParams)
      expect(response.data).toHaveLength(1)
      expect(response.data[0]).toEqual(mockUser)
    })
    it('should change password', async () => {
      mockAxios.onPut(`${baseURL}/1/password`)
        .reply(200)
      await userService.changePassword('1', 'oldPass', 'newPass')
      expect(mockAxios.history.put.length).toBe(1)
    })
    it('should deactivate user', async () => {
      const deactivatedUser = { ...mockUser, isActive: false }
      mockAxios.onPut(`${baseURL}/1/deactivate`)
        .reply(200, { data: deactivatedUser })
      const response = await userService.deactivate('1')
      expect(response.data.isActive).toBe(false)
    })
    it('should activate user', async () => {
      const activatedUser = { ...mockUser, isActive: true }
      mockAxios.onPut(`${baseURL}/1/activate`)
        .reply(200, { data: activatedUser })
      const response = await userService.activate('1')
      expect(response.data.isActive).toBe(true)
    })
  })
  describe('Caching', () => {
    const mockUser: User = {
      id: '1',
      email: 'test@example.com',
      username: 'testuser',
      isActive: true,
      role: 'user',
      createdAt: new Date(),
      updatedAt: new Date(),
    }
    it('should cache get requests', async () => {
      mockAxios.onGet(`${baseURL}/1`).reply(200, { data: mockUser })
      const response1 = await userService.getById('1')
      expect(response1.data).toEqual(mockUser)
      expect(mockAxios.history.get.length).toBe(1)
      const response2 = await userService.getById('1')
      expect(response2.data).toEqual(mockUser)
      expect(mockAxios.history.get.length).toBe(1) 
    })
    it('should clear cache', async () => {
      mockAxios.onGet(`${baseURL}/1`).reply(200, { data: mockUser })
      await userService.getById('1')
      expect(mockAxios.history.get.length).toBe(1)
      userService.clearCache()
      await userService.getById('1')
      expect(mockAxios.history.get.length).toBe(2)
    })
    it('should respect cache timeout', async () => {
      mockAxios.onGet(`${baseURL}/1`).reply(200, { data: mockUser })
      userService.setCacheTimeout(100)
      await userService.getById('1')
      expect(mockAxios.history.get.length).toBe(1)
      await new Promise(resolve => setTimeout(resolve, 150))
      await userService.getById('1')
      expect(mockAxios.history.get.length).toBe(2)
    })
  })
}) 