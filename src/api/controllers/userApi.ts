import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

interface User {
  id: number;
  name: string;
  email: string;
}

interface CreateUserData {
  name: string;
  email: string;
}

interface UpdateUserData {
  name: string;
  email: string;
}

const handleResponse = async (response: Response) => {
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'An error occurred');
  }
  if (response.status === 204) {
    return null;
  }
  return response.json();
};

export const useUserApi = () => {
  const queryClient = useQueryClient();

  const getUsers = async (): Promise<User[]> => {
    const response = await fetch('/api/users');
    return handleResponse(response);
  };

  const getUser = async (id: number): Promise<User> => {
    const response = await fetch(`/api/users/${id}`);
    if (response.status === 404) {
      throw new Error('User not found');
    }
    return handleResponse(response);
  };

  const createUser = async (data: CreateUserData): Promise<User> => {
    const response = await fetch('/api/users', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  };

  const updateUser = async (id: number, data: UpdateUserData): Promise<User> => {
    const response = await fetch(`/api/users/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (response.status === 404) {
      throw new Error('User not found');
    }
    return handleResponse(response);
  };

  const deleteUser = async (id: number): Promise<void> => {
    const response = await fetch(`/api/users/${id}`, {
      method: 'DELETE',
    });
    if (response.status === 404) {
      throw new Error('User not found');
    }
    return handleResponse(response);
  };

  // React Query hooks
  const useUsers = () => 
    useQuery({
      queryKey: ['users'],
      queryFn: getUsers
    });

  const useUser = (id: number) => 
    useQuery({
      queryKey: ['user', id],
      queryFn: () => getUser(id)
    });

  const useCreateUser = () => 
    useMutation({
      mutationFn: createUser,
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['users'] });
      },
    });

  const useUpdateUser = () => 
    useMutation({
      mutationFn: ({ id, data }: { id: number; data: UpdateUserData }) => 
        updateUser(id, data),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['users'] });
      },
    });

  const useDeleteUser = () => 
    useMutation({
      mutationFn: deleteUser,
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['users'] });
      },
    });

  return {
    // Direct API methods
    getUsers,
    getUser,
    createUser,
    updateUser,
    deleteUser,
    
    // React Query hooks
    useUsers,
    useUser,
    useCreateUser,
    useUpdateUser,
    useDeleteUser,
  };
}; 