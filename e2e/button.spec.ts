import { test, expect } from '@playwright/test';
import { getButtonTestId, getFormFieldTestId } from '../src/__tests__/__test-utils__/test-ids';

test.describe('Button Component E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the test page
    await page.goto('/');
  });

  test('button interactions work correctly', async ({ page }) => {
    // Find the button
    const button = page.getByTestId(getButtonTestId('click-me'));
    
    // Check initial state
    await expect(button).toBeVisible();
    await expect(button).toBeEnabled();
    
    // Click the button
    await button.click();
    
    // Check loading state
    await expect(button).toBeDisabled();
    await expect(page.getByTestId('loading-icon')).toBeVisible();
    
    // Wait for loading to complete
    await expect(button).toBeEnabled({ timeout: 2000 });
    await expect(page.getByTestId('loading-icon')).not.toBeVisible();
    
    // Check counter update
    await expect(page.getByText('Clicked: 1')).toBeVisible();
  });

  test('form submission flow works', async ({ page }) => {
    // Find form elements
    const form = page.getByTestId('test-form');
    const emailInput = page.getByTestId(getFormFieldTestId('email'));
    const passwordInput = page.getByTestId(getFormFieldTestId('password'));
    const submitButton = page.getByTestId(getButtonTestId('submit'));

    // Fill the form
    await emailInput.fill('test@example.com');
    await passwordInput.fill('password123');

    // Submit the form
    await submitButton.click();

    // Check loading state
    await expect(submitButton).toBeDisabled();
    await expect(page.getByTestId('loading-icon')).toBeVisible();
    await expect(submitButton).toHaveText('Submitting...');

    // Wait for submission to complete
    await expect(submitButton).toBeEnabled({ timeout: 2000 });
    await expect(submitButton).toHaveText('Submit');
    await expect(page.getByTestId('loading-icon')).not.toBeVisible();

    // Check success message
    await expect(page.getByTestId('success-message')).toBeVisible();
    await expect(page.getByTestId('success-message')).toHaveText('Form submitted 1 times!');
  });

  test('button accessibility features work', async ({ page }) => {
    // Find the button
    const button = page.getByTestId(getButtonTestId('click-me'));

    // Check initial focus
    await expect(button).not.toBeFocused();

    // Tab to focus
    await page.keyboard.press('Tab');
    await expect(button).toBeFocused();

    // Activate with Enter key
    await page.keyboard.press('Enter');
    await expect(button).toBeDisabled();
    await expect(page.getByTestId('loading-icon')).toBeVisible();

    // Wait for loading to complete
    await expect(button).toBeEnabled({ timeout: 2000 });

    // Tab away
    await page.keyboard.press('Tab');
    await expect(button).not.toBeFocused();

    // Tab back and activate with Space key
    await page.keyboard.press('Shift+Tab');
    await expect(button).toBeFocused();
    await page.keyboard.press('Space');
    await expect(button).toBeDisabled();
  });

  test('button visual feedback works', async ({ page }) => {
    // Find the button
    const button = page.getByTestId(getButtonTestId('click-me'));

    // Take screenshot of initial state
    await expect(button).toHaveScreenshot('button-initial.png');

    // Hover state
    await button.hover();
    await expect(button).toHaveScreenshot('button-hover.png');

    // Active state (mousedown)
    await page.mouse.down();
    await expect(button).toHaveScreenshot('button-active.png');
    await page.mouse.up();

    // Focus state
    await button.focus();
    await expect(button).toHaveScreenshot('button-focus.png');

    // Loading state
    await button.click();
    await expect(button).toHaveScreenshot('button-loading.png');

    // Wait for loading to complete
    await expect(button).toBeEnabled({ timeout: 2000 });
    await expect(button).toHaveScreenshot('button-after-loading.png');
  });

  test('button responsiveness works', async ({ page }) => {
    // Test different viewport sizes
    for (const size of [
      { width: 320, height: 568 }, // Mobile
      { width: 768, height: 1024 }, // Tablet
      { width: 1024, height: 768 }, // Laptop
      { width: 1920, height: 1080 }, // Desktop
    ]) {
      await page.setViewportSize(size);
      const button = page.getByTestId(getButtonTestId('click-me'));
      await expect(button).toBeVisible();
      await expect(button).toHaveScreenshot(`button-viewport-${size.width}x${size.height}.png`);
    }
  });

  test('button error handling works', async ({ page }) => {
    // Find the error button
    const errorButton = page.getByTestId(getButtonTestId('error-button'));
    
    // Click to trigger error
    await errorButton.click();
    
    // Check error state
    await expect(page.getByTestId('error-message')).toBeVisible();
    await expect(errorButton).toBeEnabled();
    await expect(errorButton).toHaveClass(/error/);
    
    // Click to retry
    await errorButton.click();
    
    // Check loading state
    await expect(errorButton).toBeDisabled();
    await expect(page.getByTestId('loading-icon')).toBeVisible();
    
    // Wait for success
    await expect(errorButton).toBeEnabled({ timeout: 2000 });
    await expect(page.getByTestId('error-message')).not.toBeVisible();
  });

  test('button theme switching works', async ({ page }) => {
    // Find the theme toggle and button
    const themeToggle = page.getByTestId('theme-toggle');
    const button = page.getByTestId(getButtonTestId('click-me'));

    // Check light theme
    await expect(button).toHaveScreenshot('button-light-theme.png');

    // Switch to dark theme
    await themeToggle.click();
    await expect(button).toHaveScreenshot('button-dark-theme.png');

    // Switch back to light theme
    await themeToggle.click();
    await expect(button).toHaveScreenshot('button-light-theme-again.png');
  });
}); 