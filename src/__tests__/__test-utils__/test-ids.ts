// Common component test IDs
export const commonTestIds = {
  button: {
    primary: 'primary-button',
    secondary: 'secondary-button',
    submit: 'submit-button',
    cancel: 'cancel-button',
    close: 'close-button',
  },
  input: {
    email: 'email-input',
    password: 'password-input',
    search: 'search-input',
  },
  form: {
    login: 'login-form',
    register: 'register-form',
    search: 'search-form',
  },
  modal: {
    container: 'modal-container',
    title: 'modal-title',
    content: 'modal-content',
    actions: 'modal-actions',
  },
  navigation: {
    header: 'main-header',
    footer: 'main-footer',
    menu: 'main-menu',
    menuItem: 'menu-item',
  },
  loading: {
    spinner: 'loading-spinner',
    skeleton: 'loading-skeleton',
    progressBar: 'progress-bar',
  },
  error: {
    message: 'error-message',
    alert: 'error-alert',
    boundary: 'error-boundary',
  },
};

// Feature-specific test IDs
export const featureTestIds = {
  auth: {
    loginForm: 'auth-login-form',
    registerForm: 'auth-register-form',
    forgotPasswordForm: 'auth-forgot-password-form',
    emailInput: 'auth-email-input',
    passwordInput: 'auth-password-input',
    submitButton: 'auth-submit-button',
    errorMessage: 'auth-error-message',
  },
  profile: {
    container: 'profile-container',
    avatar: 'profile-avatar',
    nameInput: 'profile-name-input',
    emailInput: 'profile-email-input',
    saveButton: 'profile-save-button',
  },
  dashboard: {
    container: 'dashboard-container',
    sidebar: 'dashboard-sidebar',
    content: 'dashboard-content',
    header: 'dashboard-header',
  },
  settings: {
    container: 'settings-container',
    themeToggle: 'settings-theme-toggle',
    notificationToggle: 'settings-notification-toggle',
    saveButton: 'settings-save-button',
  },
};

// Helper function to generate unique test IDs
export const generateTestId = (base: string, identifier: string | number) =>
  `${base}-${identifier}`;

// Helper function to get list item test ID
export const getListItemTestId = (index: number) =>
  generateTestId('list-item', index);

// Helper function to get table cell test ID
export const getTableCellTestId = (row: number, col: number) =>
  `table-cell-${row}-${col}`;

// Helper function to get form field test ID
export const getFormFieldTestId = (fieldName: string) =>
  `form-field-${fieldName}`;

// Helper function to get error message test ID
export const getErrorMessageTestId = (fieldName: string) =>
  `error-message-${fieldName}`;

// Helper function to get modal test ID
export const getModalTestId = (modalName: string) => `modal-${modalName}`;

// Helper function to get button test ID
export const getButtonTestId = (buttonName: string) => `button-${buttonName}`;

// Helper function to get input test ID
export const getInputTestId = (inputName: string) => `input-${inputName}`;

// Helper function to get section test ID
export const getSectionTestId = (sectionName: string) =>
  `section-${sectionName}`;

// Helper function to get tab test ID
export const getTabTestId = (tabName: string) => `tab-${tabName}`;

// Helper function to get panel test ID
export const getPanelTestId = (panelName: string) => `panel-${panelName}`;
