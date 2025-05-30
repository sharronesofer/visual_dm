from typing import Any



describe('Type Guards', () => {
  const user: User = {
    id: 'u1',
    createdAt: new Date(),
    updatedAt: new Date(),
    isActive: true,
    username: 'bob',
    email: 'bob@example.com',
    passwordHash: 'hashed:pw',
    role: 'user',
  }
  const mediaAsset: MediaAsset = {
    id: 'm1',
    createdAt: new Date(),
    updatedAt: new Date(),
    isActive: true,
    title: 'Asset',
    fileUrl: 'url',
    fileType: 'image/png',
    fileSize: 100,
  }
  const collection: Collection = {
    id: 'c1',
    createdAt: new Date(),
    updatedAt: new Date(),
    isActive: true,
    name: 'Collection',
    mediaAssets: ['m1'],
    visibility: 'public',
  }
  it('should identify User objects', () => {
    expect(isUser(user)).toBe(true)
    expect(isUser({ ...user, username: undefined })).toBe(false)
    expect(isUser({})).toBe(false)
  })
  it('should identify MediaAsset objects', () => {
    expect(isMediaAsset(mediaAsset)).toBe(true)
    expect(isMediaAsset({ ...mediaAsset, fileType: undefined })).toBe(false)
    expect(isMediaAsset({})).toBe(false)
  })
  it('should identify Collection objects', () => {
    expect(isCollection(collection)).toBe(true)
    expect(isCollection({ ...collection, name: undefined })).toBe(false)
    expect(isCollection({})).toBe(false)
  })
}) 