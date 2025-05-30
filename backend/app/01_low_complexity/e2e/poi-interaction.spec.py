from typing import Any, Dict



test.describe('POI Interaction', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/map')
  })
  test('should show POI dialog when clicking on a POI', async ({ page }) => {
    await page.waitForSelector('[data-testid="poi-marker"]')
    await page.click('[data-testid="poi-marker"]')
    const dialog = await page.waitForSelector('[role="dialog"]')
    expect(dialog).toBeTruthy()
    const title = await dialog.textContent()
    expect(title).toContain('Test City')
    await page.click('button[aria-label="close"]')
    await expect(page.locator('[role="dialog"]')).not.toBeVisible()
  })
  test('should handle keyboard navigation in POI dialog', async ({ page }) => {
    await page.click('[data-testid="poi-marker"]')
    await page.waitForSelector('[role="dialog"]')
    await page.keyboard.press('Tab')
    const focusedElement = await page.evaluate(() => document.activeElement?.getAttribute('aria-label'))
    expect(focusedElement).toBe('close')
    await page.keyboard.press('Escape')
    await expect(page.locator('[role="dialog"]')).not.toBeVisible()
  })
  test('should show POI details and handle interactions', async ({ page }) => {
    await page.click('[data-testid="poi-marker"]')
    const dialog = await page.waitForSelector('[role="dialog"]')
    await expect(page.locator('text=Type: city')).toBeVisible()
    await expect(page.locator('text=Size: medium')).toBeVisible()
    await expect(page.locator('text=Theme: medieval')).toBeVisible()
    await page.click('text=Test Option')
    await expect(page.locator('.visual-feedback')).toBeVisible()
    await page.waitForTimeout(1000)
    await expect(page.locator('.visual-feedback')).not.toBeVisible()
  })
  test('should handle multiple POI interactions', async ({ page }) => {
    await page.click('[data-testid="poi-marker"]:first-child')
    await page.waitForSelector('[role="dialog"]')
    await expect(page.locator('text=Test City')).toBeVisible()
    await page.click('button[aria-label="close"]')
    await page.click('[data-testid="poi-marker"]:nth-child(2)')
    await page.waitForSelector('[role="dialog"]')
    await expect(page.locator('text=Test Dungeon')).toBeVisible()
  })
  test('should maintain POI state across navigation', async ({ page }) => {
    await page.click('[data-testid="poi-marker"]')
    await page.waitForSelector('[role="dialog"]')
    await page.click('[data-testid="menu-button"]')
    await page.click('text=Inventory')
    await page.goBack()
    await expect(page.locator('[role="dialog"]')).not.toBeVisible()
    await expect(page.locator('[data-testid="poi-marker"].active')).toBeVisible()
  })
  test('should handle POI range restrictions', async ({ page }) => {
    await page.evaluate(() => {
      window.dispatchEvent(new CustomEvent('movePlayer', {
        detail: Dict[str, Any]
      }))
    })
    await page.click('[data-testid="poi-marker"]')
    await expect(page.locator('[role="dialog"]')).not.toBeVisible()
    await expect(page.locator('text=Too far to interact')).toBeVisible()
    await page.evaluate(() => {
      window.dispatchEvent(new CustomEvent('movePlayer', {
        detail: Dict[str, Any]
      }))
    })
    await page.click('[data-testid="poi-marker"]')
    await expect(page.locator('[role="dialog"]')).toBeVisible()
  })
}) 