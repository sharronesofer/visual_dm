import {
  createInitialFormState,
  createFormValidator,
  createFormValidationHandler,
  createFormController,
  FormState,
  FormValues,
  FormErrors,
  FormFieldError,
  FormValidationOptions,
} from '../form';
import { Schema } from '../schema';

describe('Form Validation', () => {
  describe('createInitialFormState', () => {
    it('should create initial form state', () => {
      const initialValues: FormValues = {
        name: '',
        age: 0,
        active: false,
      };

      const state = createInitialFormState(initialValues);

      expect(state.values).toEqual(initialValues);
      expect(state.errors).toEqual({});
      expect(state.touched).toEqual({
        name: false,
        age: false,
        active: false,
      });
      expect(state.dirty).toEqual({
        name: false,
        age: false,
        active: false,
      });
      expect(state.isValid).toBe(true);
      expect(state.isSubmitting).toBe(false);
    });
  });

  describe('createFormValidator', () => {
    it('should create a form validator function', async () => {
      const schema: Schema = {
        name: {
          type: 'string',
          required: true,
        },
        age: {
          type: 'number',
          required: true,
          min: 0,
        },
      };

      const validator = createFormValidator(schema);

      const validResult: FormErrors = await validator({
        name: 'John',
        age: 25,
      });
      expect(validResult).toEqual({});

      const invalidResult: FormErrors = await validator({
        name: '',
        age: -1,
      });
      expect(invalidResult).toHaveProperty('name.message');
      expect(invalidResult).toHaveProperty('age.message');
    });
  });

  describe('createFormValidationHandler', () => {
    const schema: Schema = {
      name: {
        type: 'string',
        required: true,
        min: 2,
      },
      age: {
        type: 'number',
        required: true,
        min: 0,
      },
    };

    const initialState: FormState = {
      values: {
        name: '',
        age: 0,
      },
      errors: {},
      touched: {
        name: false,
        age: false,
      },
      dirty: {
        name: false,
        age: false,
      },
      isValid: true,
      isSubmitting: false,
    };

    it('should handle change without validation', async () => {
      const { handleChange } = createFormValidationHandler(schema);

      const newState: FormState = await handleChange('name', 'John', initialState);

      expect(newState.values.name).toBe('John');
      expect(newState.dirty.name).toBe(true);
      expect(newState.errors).toEqual({});
    });

    it('should handle change with validation', async () => {
      const { handleChange } = createFormValidationHandler(schema, { validateOnChange: true });

      const validState: FormState = await handleChange('name', 'John', initialState);
      expect(validState.values.name).toBe('John');
      expect(validState.dirty.name).toBe(true);
      expect(validState.errors).toEqual({});
      expect(validState.isValid).toBe(true);

      const invalidState: FormState = await handleChange('name', 'J', initialState);
      expect(invalidState.values.name).toBe('J');
      expect(invalidState.dirty.name).toBe(true);
      expect(invalidState.errors.name).toBeDefined();
      expect(invalidState.isValid).toBe(false);
    });

    it('should handle blur without validation', async () => {
      const { handleBlur } = createFormValidationHandler(schema);

      const newState: FormState = await handleBlur('name', initialState);

      expect(newState.touched.name).toBe(true);
      expect(newState.errors).toEqual({});
    });

    it('should handle blur with validation', async () => {
      const { handleBlur } = createFormValidationHandler(schema, { validateOnBlur: true });

      const invalidState: FormState = await handleBlur('name', initialState);
      expect(invalidState.touched.name).toBe(true);
      expect(invalidState.errors.name).toBeDefined();
      expect(invalidState.isValid).toBe(false);

      const validState: FormState = await handleBlur('name', {
        ...initialState,
        values: { ...initialState.values, name: 'John' },
      });
      expect(validState.touched.name).toBe(true);
      expect(validState.errors).toEqual({});
      expect(validState.isValid).toBe(true);
    });

    it('should handle submit', async () => {
      const { handleSubmit } = createFormValidationHandler(schema);

      const invalidState: FormState = await handleSubmit(initialState);
      expect(invalidState.touched).toEqual({
        name: true,
        age: true,
      });
      expect(invalidState.errors.name).toBeDefined();
      expect(invalidState.errors.age).toBeDefined();
      expect(invalidState.isValid).toBe(false);
      expect(invalidState.isSubmitting).toBe(false);

      const validState: FormState = await handleSubmit({
        ...initialState,
        values: {
          name: 'John',
          age: 25,
        },
      });
      expect(validState.touched).toEqual({
        name: true,
        age: true,
      });
      expect(validState.errors).toEqual({});
      expect(validState.isValid).toBe(true);
      expect(validState.isSubmitting).toBe(false);
    });
  });

  describe('createFormController', () => {
    it('should create a form controller', () => {
      const schema: Schema = {
        name: {
          type: 'string',
          required: true,
        },
        age: {
          type: 'number',
          required: true,
        },
      };

      const initialValues: FormValues = {
        name: '',
        age: 0,
      };

      const controller = createFormController(initialValues, schema, {
        validateOnChange: true,
        validateOnBlur: true,
      });

      expect(controller.initialState).toBeDefined();
      expect(controller.handleChange).toBeDefined();
      expect(controller.handleBlur).toBeDefined();
      expect(controller.handleSubmit).toBeDefined();
    });

    it('should handle form lifecycle', async () => {
      const schema: Schema = {
        name: {
          type: 'string',
          required: true,
          min: 2,
        },
      };

      const initialValues: FormValues = {
        name: '',
      };

      const controller = createFormController(initialValues, schema, {
        validateOnChange: true,
        validateOnBlur: true,
      });

      // Initial state
      let state: FormState = controller.initialState;
      expect(state.values.name).toBe('');
      expect(state.isValid).toBe(true);

      // Change event
      state = await controller.handleChange('name', 'J', state);
      expect(state.values.name).toBe('J');
      expect(state.dirty.name).toBe(true);
      expect(state.errors.name).toBeDefined();
      expect(state.isValid).toBe(false);

      // Blur event
      state = await controller.handleBlur('name', state);
      expect(state.touched.name).toBe(true);
      expect(state.errors.name).toBeDefined();
      expect(state.isValid).toBe(false);

      // Valid change
      state = await controller.handleChange('name', 'John', state);
      expect(state.values.name).toBe('John');
      expect(state.errors).toEqual({});
      expect(state.isValid).toBe(true);

      // Submit
      state = await controller.handleSubmit(state);
      expect(state.touched.name).toBe(true);
      expect(state.errors).toEqual({});
      expect(state.isValid).toBe(true);
      expect(state.isSubmitting).toBe(false);
    });
  });
}); 