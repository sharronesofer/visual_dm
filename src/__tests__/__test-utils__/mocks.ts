// Removed Vitest import

// Mock user data
export const mockUser = {
  id: '1',
  email: 'test@example.com',
  name: 'Test User',
  role: 'user',
};

// Mock authentication data
export const mockAuthState = {
  isAuthenticated: true,
  user: mockUser,
  loading: false,
  error: null,
};

// Mock API responses
export const mockApiResponses = {
  login: {
    success: {
      token: 'mock-jwt-token',
      user: mockUser,
    },
    error: {
      message: 'Invalid credentials',
    },
  },
  profile: {
    success: mockUser,
    error: {
      message: 'Failed to fetch profile',
    },
  },
};

// Mock functions
export const mockHandlers = {
  onClick: jest.fn(),
  onSubmit: jest.fn(),
  onChange: jest.fn(),
  onClose: jest.fn(),
  onOpen: jest.fn(),
};

// Mock component props
export const mockButtonProps = {
  children: 'Click me',
  onClick: mockHandlers.onClick,
  variant: 'contained' as const,
  color: 'primary' as const,
  size: 'medium' as const,
  disabled: false,
  fullWidth: false,
};

// Mock form data
export const mockFormData = {
  email: 'test@example.com',
  password: 'password123',
  remember: true,
};

// Mock error messages
export const mockErrors = {
  required: 'This field is required',
  invalidEmail: 'Please enter a valid email',
  passwordTooShort: 'Password must be at least 8 characters',
  serverError: 'An error occurred. Please try again.',
};

// Mock loading states
export const mockLoadingStates = {
  initial: { loading: false, error: null, data: null },
  loading: { loading: true, error: null, data: null },
  success: { loading: false, error: null, data: {} },
  error: { loading: false, error: new Error('Mock error'), data: null },
};

// Mock route data
export const mockRouteData = {
  path: '/test',
  params: { id: '123' },
  query: { sort: 'asc' },
};

// Mock theme data
export const mockThemeData = {
  palette: {
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#9c27b0',
      light: '#ba68c8',
      dark: '#7b1fa2',
    },
  },
  spacing: (factor: number) => `${4 * factor}px`,
};

// Mock window dimensions
export const mockWindowDimensions = {
  width: 1024,
  height: 768,
  isMobile: false,
};
