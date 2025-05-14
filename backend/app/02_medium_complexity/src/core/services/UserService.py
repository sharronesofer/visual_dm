from typing import Any, Dict



class UserService extends BaseService<User> {
  constructor(repository: Repository<User>) {
    super(repository)
  }
  async createUser(data: Dict[str, Any]): Promise<User> {
    validateRequired(data.username, 'username')
    validateRequired(data.email, 'email')
    validateRequired(data.password, 'password')
    validateLength(data.username, 'username', 3, 50)
    validateEmail(data.email)
    validateLength(data.password, 'password', 8, 100)
    logger.info('Creating new user', { username: data.username })
    const user = await this.create({
      username: data.username,
      email: data.email,
      collections: [],
      preferences: {},
    })
    logger.info('User created successfully', { id: user.id })
    return user
  }
  async authenticate(email: str, password: str): Promise<User> {
    validateRequired(email, 'email')
    validateRequired(password, 'password')
    validateEmail(email)
    const users = await this.findAll()
    const user = users.find(u => u.email === email)
    if (!user) {
      logger.warn('Authentication failed: user not found', { email })
      throw new AuthenticationError('Invalid email or password')
    }
    logger.info('User authenticated successfully', { id: user.id })
    return user
  }
  async updatePreferences(userId: str | number, preferences: Record<string, any>): Promise<User | null> {
    validateRequired(preferences, 'preferences')
    const user = await this.findById(userId)
    if (!user) {
      logger.warn('User not found', { userId })
      return null
    }
    const updatedUser = await this.update(userId, {
      preferences: Dict[str, Any]
    })
    if (updatedUser) {
      logger.info('User preferences updated', { userId })
    }
    return updatedUser
  }
  async addCollectionToUser(userId: str | number, collectionId: str | number): Promise<User | null> {
    const user = await this.findById(userId)
    if (!user) {
      logger.warn('User not found', { userId })
      return null
    }
    const collectionExists = user.collections.some(collection => collection.id === collectionId)
    if (collectionExists) {
      logger.warn('Collection already exists for user', { userId, collectionId })
      return user
    }
    user.collections.push({ id: collectionId } as any)
    const updatedUser = await this.update(userId, user)
    if (updatedUser) {
      logger.info('Collection added to user', { userId, collectionId })
    }
    return updatedUser
  }
  async removeCollectionFromUser(userId: str | number, collectionId: str | number): Promise<User | null> {
    const user = await this.findById(userId)
    if (!user) {
      logger.warn('User not found', { userId })
      return null
    }
    const collectionIndex = user.collections.findIndex(collection => collection.id === collectionId)
    if (collectionIndex === -1) {
      logger.warn('Collection not found for user', { userId, collectionId })
      return user
    }
    user.collections.splice(collectionIndex, 1)
    const updatedUser = await this.update(userId, user)
    if (updatedUser) {
      logger.info('Collection removed from user', { userId, collectionId })
    }
    return updatedUser
  }
} 