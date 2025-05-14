import { renderHook, act } from '@testing-library/react';
import { useForm } from '@/hooks/useForm';

describe('useForm', () => {
  const initialValues = {
    name: '',
    email: '',
    password: ''
  };

  const validationRules = {
    name: (value: string) => !value ? 'Name is required' : '',
    email: (value: string) => {
      if (!value) return 'Email is required';
      if (!/\S+@\S+\.\S+/.test(value)) return 'Invalid email format';
      return '';
    },
    password: (value: string) => {
      if (!value) return 'Password is required';
      if (value.length < 8) return 'Password must be at least 8 characters';
      return '';
    }
  };

  it('initializes with provided values', () => {
    const { result } = renderHook(() => useForm(initialValues, validationRules));
    
    expect(result.current.values).toEqual(initialValues);
    expect(result.current.errors).toEqual({});
    expect(result.current.touched).toEqual({});
  });

  it('updates field value and validates on change', () => {
    const { result } = renderHook(() => useForm(initialValues, validationRules));

    act(() => {
      result.current.handleChange({
        target: { name: 'email', value: 'invalid-email' }
      } as React.ChangeEvent<HTMLInputElement>);
    });

    expect(result.current.values.email).toBe('invalid-email');
    expect(result.current.errors.email).toBe('Invalid email format');
  });

  it('marks field as touched on blur', () => {
    const { result } = renderHook(() => useForm(initialValues, validationRules));

    act(() => {
      result.current.handleBlur({
        target: { name: 'name' }
      } as React.FocusEvent<HTMLInputElement>);
    });

    expect(result.current.touched.name).toBe(true);
  });

  it('validates all fields on submit', () => {
    const onSubmit = jest.fn();
    const { result } = renderHook(() => useForm(initialValues, validationRules));

    act(() => {
      result.current.handleSubmit(onSubmit)({
        preventDefault: () => {}
      } as React.FormEvent);
    });

    expect(result.current.errors).toEqual({
      name: 'Name is required',
      email: 'Email is required',
      password: 'Password must be at least 8 characters'
    });
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('calls onSubmit when form is valid', () => {
    const onSubmit = jest.fn();
    const { result } = renderHook(() => useForm(initialValues, validationRules));

    act(() => {
      result.current.handleChange({
        target: { name: 'name', value: 'John Doe' }
      } as React.ChangeEvent<HTMLInputElement>);
      result.current.handleChange({
        target: { name: 'email', value: 'john@example.com' }
      } as React.ChangeEvent<HTMLInputElement>);
      result.current.handleChange({
        target: { name: 'password', value: 'password123' }
      } as React.ChangeEvent<HTMLInputElement>);
    });

    act(() => {
      result.current.handleSubmit(onSubmit)({
        preventDefault: () => {}
      } as React.FormEvent);
    });

    expect(result.current.errors).toEqual({});
    expect(onSubmit).toHaveBeenCalledWith({
      name: 'John Doe',
      email: 'john@example.com',
      password: 'password123'
    });
  });

  it('resets form to initial values', () => {
    const { result } = renderHook(() => useForm(initialValues, validationRules));

    act(() => {
      result.current.handleChange({
        target: { name: 'name', value: 'John Doe' }
      } as React.ChangeEvent<HTMLInputElement>);
      result.current.handleBlur({
        target: { name: 'name' }
      } as React.FocusEvent<HTMLInputElement>);
    });

    act(() => {
      result.current.resetForm();
    });

    expect(result.current.values).toEqual(initialValues);
    expect(result.current.errors).toEqual({});
    expect(result.current.touched).toEqual({});
  });
}); 