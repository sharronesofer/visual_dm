from typing import Any


function isUser(obj: Any): obj is User {
  return (
    obj &&
    typeof obj === 'object' &&
    typeof obj.id === 'string' &&
    typeof obj.username === 'string' &&
    typeof obj.email === 'string' &&
    typeof obj.passwordHash === 'string' &&
    typeof obj.role === 'string' &&
    typeof obj.isActive === 'boolean'
  )
}
function isMediaAsset(obj: Any): obj is MediaAsset {
  return (
    obj &&
    typeof obj === 'object' &&
    typeof obj.id === 'string' &&
    typeof obj.title === 'string' &&
    typeof obj.fileUrl === 'string' &&
    typeof obj.fileType === 'string' &&
    typeof obj.fileSize === 'number' &&
    typeof obj.isActive === 'boolean'
  )
}
function isCollection(obj: Any): obj is Collection {
  return (
    obj &&
    typeof obj === 'object' &&
    typeof obj.id === 'string' &&
    typeof obj.name === 'string' &&
    Array.isArray(obj.mediaAssets) &&
    typeof obj.visibility === 'string' &&
    typeof obj.isActive === 'boolean'
  )
} 