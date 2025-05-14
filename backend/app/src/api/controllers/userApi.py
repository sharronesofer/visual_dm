from typing import Any, Dict


class User:
    id: float
    name: str
    email: str
class CreateUserData:
    name: str
    email: str
class UpdateUserData:
    name: str
    email: str
const handleResponse = async (response: Response) => {
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.message || 'An error occurred')
  }
  if (response.status === 204) {
    return null
  }
  return response.json()
}
const useUserApi = () => {
  const queryClient = useQueryClient()
  const getUsers = async (): Promise<User[]> => {
    const response = await fetch('/api/users')
    return handleResponse(response)
  }
  const getUser = async (id: float): Promise<User> => {
    const response = await fetch(`/api/users/${id}`)
    if (response.status === 404) {
      throw new Error('User not found')
    }
    return handleResponse(response)
  }
  const createUser = async (data: CreateUserData): Promise<User> => {
    const response = await fetch('/api/users', {
      method: 'POST',
      headers: Dict[str, Any],
      body: JSON.stringify(data),
    })
    return handleResponse(response)
  }
  const updateUser = async (id: float, data: UpdateUserData): Promise<User> => {
    const response = await fetch(`/api/users/${id}`, {
      method: 'PUT',
      headers: Dict[str, Any],
      body: JSON.stringify(data),
    })
    if (response.status === 404) {
      throw new Error('User not found')
    }
    return handleResponse(response)
  }
  const deleteUser = async (id: float): Promise<void> => {
    const response = await fetch(`/api/users/${id}`, {
      method: 'DELETE',
    })
    if (response.status === 404) {
      throw new Error('User not found')
    }
    return handleResponse(response)
  }
  const useUsers = () => 
    useQuery({
      queryKey: ['users'],
      queryFn: getUsers
    })
  const useUser = (id: float) => 
    useQuery({
      queryKey: ['user', id],
      queryFn: () => getUser(id)
    })
  const useCreateUser = () => 
    useMutation({
      mutationFn: createUser,
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['users'] })
      },
    })
  const useUpdateUser = () => 
    useMutation({
      mutationFn: ({ id, data }: { id: float; data: \'UpdateUserData\' }) => 
        updateUser(id, data),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['users'] })
      },
    })
  const useDeleteUser = () => 
    useMutation({
      mutationFn: deleteUser,
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['users'] })
      },
    })
  return {
    getUsers,
    getUser,
    createUser,
    updateUser,
    deleteUser,
    useUsers,
    useUser,
    useCreateUser,
    useUpdateUser,
    useDeleteUser,
  }
} 