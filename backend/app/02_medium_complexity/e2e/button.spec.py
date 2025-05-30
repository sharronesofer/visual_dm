from typing import Any



test.describe('Button Component E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })
  test('button interactions work correctly', async ({ page }) => {
    const button = page.getByTestId(getButtonTestId('click-me'))
    await expect(button).toBeVisible()
    await expect(button).toBeEnabled()
    await button.click()
    await expect(button).toBeDisabled()
    await expect(page.getByTestId('loading-icon')).toBeVisible()
    await expect(button).toBeEnabled({ timeout: 2000 })
    await expect(page.getByTestId('loading-icon')).not.toBeVisible()
    await expect(page.getByText('Clicked: 1')).toBeVisible()
  })
  test('form submission flow works', async ({ page }) => {
    const form = page.getByTestId('test-form')
    const emailInput = page.getByTestId(getFormFieldTestId('email'))
    const passwordInput = page.getByTestId(getFormFieldTestId('password'))
    const submitButton = page.getByTestId(getButtonTestId('submit'))
    await emailInput.fill('test@example.com')
    await passwordInput.fill('password123')
    await submitButton.click()
    await expect(submitButton).toBeDisabled()
    await expect(page.getByTestId('loading-icon')).toBeVisible()
    await expect(submitButton).toHaveText('Submitting...')
    await expect(submitButton).toBeEnabled({ timeout: 2000 })
    await expect(submitButton).toHaveText('Submit')
    await expect(page.getByTestId('loading-icon')).not.toBeVisible()
    await expect(page.getByTestId('success-message')).toBeVisible()
    await expect(page.getByTestId('success-message')).toHaveText('Form submitted 1 times!')
  })
  test('button accessibility features work', async ({ page }) => {
    const button = page.getByTestId(getButtonTestId('click-me'))
    await expect(button).not.toBeFocused()
    await page.keyboard.press('Tab')
    await expect(button).toBeFocused()
    await page.keyboard.press('Enter')
    await expect(button).toBeDisabled()
    await expect(page.getByTestId('loading-icon')).toBeVisible()
    await expect(button).toBeEnabled({ timeout: 2000 })
    await page.keyboard.press('Tab')
    await expect(button).not.toBeFocused()
    await page.keyboard.press('Shift+Tab')
    await expect(button).toBeFocused()
    await page.keyboard.press('Space')
    await expect(button).toBeDisabled()
  })
  test('button visual feedback works', async ({ page }) => {
    const button = page.getByTestId(getButtonTestId('click-me'))
    await expect(button).toHaveScreenshot('button-initial.png')
    await button.hover()
    await expect(button).toHaveScreenshot('button-hover.png')
    await page.mouse.down()
    await expect(button).toHaveScreenshot('button-active.png')
    await page.mouse.up()
    await button.focus()
    await expect(button).toHaveScreenshot('button-focus.png')
    await button.click()
    await expect(button).toHaveScreenshot('button-loading.png')
    await expect(button).toBeEnabled({ timeout: 2000 })
    await expect(button).toHaveScreenshot('button-after-loading.png')
  })
  test('button responsiveness works', async ({ page }) => {
    for (const size of [
      { width: 320, height: 568 }, 
      { width: 768, height: 1024 }, 
      { width: 1024, height: 768 }, 
      { width: 1920, height: 1080 }, 
    ]) {
      await page.setViewportSize(size)
      const button = page.getByTestId(getButtonTestId('click-me'))
      await expect(button).toBeVisible()
      await expect(button).toHaveScreenshot(`button-viewport-${size.width}x${size.height}.png`)
    }
  })
  test('button error handling works', async ({ page }) => {
    const errorButton = page.getByTestId(getButtonTestId('error-button'))
    await errorButton.click()
    await expect(page.getByTestId('error-message')).toBeVisible()
    await expect(errorButton).toBeEnabled()
    await expect(errorButton).toHaveClass(/error/)
    await errorButton.click()
    await expect(errorButton).toBeDisabled()
    await expect(page.getByTestId('loading-icon')).toBeVisible()
    await expect(errorButton).toBeEnabled({ timeout: 2000 })
    await expect(page.getByTestId('error-message')).not.toBeVisible()
  })
  test('button theme switching works', async ({ page }) => {
    const themeToggle = page.getByTestId('theme-toggle')
    const button = page.getByTestId(getButtonTestId('click-me'))
    await expect(button).toHaveScreenshot('button-light-theme.png')
    await themeToggle.click()
    await expect(button).toHaveScreenshot('button-dark-theme.png')
    await themeToggle.click()
    await expect(button).toHaveScreenshot('button-light-theme-again.png')
  })
}) 