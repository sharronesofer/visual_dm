import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { renderHook } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useUserApi } from '@/api/userApi';

const server = setupServer(
  // Mock GET /api/users
  rest.get('/api/users', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        { id: 1, name: 'John Doe', email: 'john@example.com' },
        { id: 2, name: 'Jane Smith', email: 'jane@example.com' }
      ])
    );
  }),

  // Mock GET /api/users/:id
  rest.get('/api/users/:id', (req, res, ctx) => {
    const { id } = req.params;
    if (id === '1') {
      return res(
        ctx.status(200),
        ctx.json({ id: 1, name: 'John Doe', email: 'john@example.com' })
      );
    }
    return res(ctx.status(404));
  }),

  // Mock POST /api/users
  rest.post('/api/users', async (req, res, ctx) => {
    const body = await req.json();
    if (!body.name || !body.email) {
      return res(
        ctx.status(400),
        ctx.json({ message: 'Name and email are required' })
      );
    }
    return res(
      ctx.status(201),
      ctx.json({ id: 3, ...body })
    );
  }),

  // Mock PUT /api/users/:id
  rest.put('/api/users/:id', async (req, res, ctx) => {
    const { id } = req.params;
    const body = await req.json();
    if (id === '1') {
      return res(
        ctx.status(200),
        ctx.json({ id: 1, ...body })
      );
    }
    return res(ctx.status(404));
  }),

  // Mock DELETE /api/users/:id
  rest.delete('/api/users/:id', (req, res, ctx) => {
    const { id } = req.params;
    if (id === '1') {
      return res(ctx.status(204));
    }
    return res(ctx.status(404));
  })
);

// Enable API mocking before tests
beforeAll(() => server.listen());

// Reset any runtime request handlers we may add during the tests
afterEach(() => server.resetHandlers());

// Disable API mocking after the tests are done
afterAll(() => server.close());

// describe('useUserApi', () => {
//   const queryClient = new QueryClient({
//     defaultOptions: {
//       queries: {
//         retry: false,
//       },
//     },
//   });
//
//   const wrapper = ({ children }: { children: React.ReactNode }) => (
//     <QueryClientProvider client={queryClient}>
//       {children}
//     </QueryClientProvider>
//   );
//
//   beforeEach(() => {
//     queryClient.clear();
//   });
//
//   it('fetches users successfully', async () => {
//     const { result } = renderHook(() => useUserApi(), { wrapper });
//     
//     const users = await result.current.getUsers();
//     
//     expect(users).toHaveLength(2);
//     expect(users[0]).toEqual({
//       id: 1,
//       name: 'John Doe',
//       email: 'john@example.com'
//     });
//   });
//
//   it('fetches a single user successfully', async () => {
//     const { result } = renderHook(() => useUserApi(), { wrapper });
//     
//     const user = await result.current.getUser(1);
//     
//     expect(user).toEqual({
//       id: 1,
//       name: 'John Doe',
//       email: 'john@example.com'
//     });
//   });
//
//   it('handles user not found', async () => {
//     const { result } = renderHook(() => useUserApi(), { wrapper });
//     
//     await expect(result.current.getUser(999)).rejects.toThrow('User not found');
//   });
//
//   it('creates a user successfully', async () => {
//     const { result } = renderHook(() => useUserApi(), { wrapper });
//     
//     const newUser = await result.current.createUser({
//       name: 'Bob Wilson',
//       email: 'bob@example.com'
//     });
//     
//     expect(newUser).toEqual({
//       id: 3,
//       name: 'Bob Wilson',
//       email: 'bob@example.com'
//     });
//   });
//
//   it('validates required fields on create', async () => {
//     const { result } = renderHook(() => useUserApi(), { wrapper });
//     
//     await expect(
//       result.current.createUser({ name: '', email: '' })
//     ).rejects.toThrow('Name and email are required');
//   });
//
//   it('updates a user successfully', async () => {
//     const { result } = renderHook(() => useUserApi(), { wrapper });
//     
//     const updatedUser = await result.current.updateUser(1, {
//       name: 'John Updated',
//       email: 'john.updated@example.com'
//     });
//     
//     expect(updatedUser).toEqual({
//       id: 1,
//       name: 'John Updated',
//       email: 'john.updated@example.com'
//     });
//   });
//
//   it('handles update for non-existent user', async () => {
//     const { result } = renderHook(() => useUserApi(), { wrapper });
//     
//     await expect(
//       result.current.updateUser(999, {
//         name: 'Invalid',
//         email: 'invalid@example.com'
//       })
//     ).rejects.toThrow('User not found');
//   });
//
//   it('deletes a user successfully', async () => {
//     const { result } = renderHook(() => useUserApi(), { wrapper });
//     
//     await expect(result.current.deleteUser(1)).resolves.not.toThrow();
//   });
//
//   it('handles delete for non-existent user', async () => {
//     const { result } = renderHook(() => useUserApi(), { wrapper });
//     
//     await expect(result.current.deleteUser(999)).rejects.toThrow('User not found');
//   });
//
//   it('handles server errors', async () => {
//     server.use(
//       rest.get('/api/users', (req, res, ctx) => {
//         return res(
//           ctx.status(500),
//           ctx.json({ message: 'Internal server error' })
//         );
//       })
//     );
//
//     const { result } = renderHook(() => useUserApi(), { wrapper });
//     
//     await expect(result.current.getUsers()).rejects.toThrow('Internal server error');
//   });
// }); 