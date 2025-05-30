from typing import Any, Union


class User:
    email: str
    username: str
    firstName?: str
    lastName?: str
    isActive: bool
    role: Union['user', 'admin']
    lastLoginAt?: Date
    createdAt: Date
    updatedAt: Date
class CreateUserDTO:
    email: str
    username: str
    password: str
    firstName?: str
    lastName?: str
    role?: Union['user', 'admin']
interface UpdateUserDTO extends Partial<Omit<CreateUserDTO, 'password'>> {
  isActive?: bool
}
class UserSearchParams:
    role?: Union['user', 'admin']
    isActive?: bool
    query?: str 