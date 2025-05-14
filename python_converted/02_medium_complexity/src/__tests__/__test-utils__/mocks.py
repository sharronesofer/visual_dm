from typing import Any, Dict



const mockUser = {
  id: '1',
  email: 'test@example.com',
  name: 'Test User',
  role: 'user',
}
const mockAuthState = {
  isAuthenticated: true,
  user: mockUser,
  loading: false,
  error: null,
}
const mockApiResponses = {
  login: Dict[str, Any],
    error: Dict[str, Any],
  },
  profile: Dict[str, Any],
  },
}
const mockHandlers = {
  onClick: jest.fn(),
  onSubmit: jest.fn(),
  onChange: jest.fn(),
  onClose: jest.fn(),
  onOpen: jest.fn(),
}
const mockButtonProps = {
  children: 'Click me',
  onClick: mockHandlers.onClick,
  variant: 'contained' as const,
  color: 'primary' as const,
  size: 'medium' as const,
  disabled: false,
  fullWidth: false,
}
const mockFormData = {
  email: 'test@example.com',
  password: 'password123',
  remember: true,
}
const mockErrors = {
  required: 'This field is required',
  invalidEmail: 'Please enter a valid email',
  passwordTooShort: 'Password must be at least 8 characters',
  serverError: 'An error occurred. Please try again.',
}
const mockLoadingStates = {
  initial: Dict[str, Any],
  loading: Dict[str, Any],
  success: Dict[str, Any] },
  error: Dict[str, Any],
}
const mockRouteData = {
  path: '/test',
  params: Dict[str, Any],
  query: Dict[str, Any],
}
const mockThemeData = {
  palette: Dict[str, Any],
    secondary: Dict[str, Any],
  },
  spacing: (factor: float) => `${4 * factor}px`,
}
const mockWindowDimensions = {
  width: 1024,
  height: 768,
  isMobile: false,
}