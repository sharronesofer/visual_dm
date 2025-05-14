import { test, expect } from '@playwright/test';

test.describe('POI Interaction', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the map page where POIs are displayed
    await page.goto('/map');
  });

  test('should show POI dialog when clicking on a POI', async ({ page }) => {
    // Wait for POIs to load
    await page.waitForSelector('[data-testid="poi-marker"]');

    // Click the first POI
    await page.click('[data-testid="poi-marker"]');

    // Verify dialog appears
    const dialog = await page.waitForSelector('[role="dialog"]');
    expect(dialog).toBeTruthy();

    // Verify dialog content
    const title = await dialog.textContent();
    expect(title).toContain('Test City');

    // Close dialog
    await page.click('button[aria-label="close"]');
    await expect(page.locator('[role="dialog"]')).not.toBeVisible();
  });

  test('should handle keyboard navigation in POI dialog', async ({ page }) => {
    // Open POI dialog
    await page.click('[data-testid="poi-marker"]');
    await page.waitForSelector('[role="dialog"]');

    // Press Tab to navigate
    await page.keyboard.press('Tab');
    
    // Verify focus is trapped in dialog
    const focusedElement = await page.evaluate(() => document.activeElement?.getAttribute('aria-label'));
    expect(focusedElement).toBe('close');

    // Press Escape to close
    await page.keyboard.press('Escape');
    await expect(page.locator('[role="dialog"]')).not.toBeVisible();
  });

  test('should show POI details and handle interactions', async ({ page }) => {
    // Open POI dialog
    await page.click('[data-testid="poi-marker"]');
    const dialog = await page.waitForSelector('[role="dialog"]');

    // Verify POI details
    await expect(page.locator('text=Type: city')).toBeVisible();
    await expect(page.locator('text=Size: medium')).toBeVisible();
    await expect(page.locator('text=Theme: medieval')).toBeVisible();

    // Click interaction option
    await page.click('text=Test Option');

    // Verify feedback is shown
    await expect(page.locator('.visual-feedback')).toBeVisible();
    
    // Wait for feedback animation
    await page.waitForTimeout(1000);
    
    // Verify feedback is removed
    await expect(page.locator('.visual-feedback')).not.toBeVisible();
  });

  test('should handle multiple POI interactions', async ({ page }) => {
    // Open first POI
    await page.click('[data-testid="poi-marker"]:first-child');
    await page.waitForSelector('[role="dialog"]');
    
    // Verify first POI content
    await expect(page.locator('text=Test City')).toBeVisible();
    
    // Close dialog
    await page.click('button[aria-label="close"]');
    
    // Open second POI
    await page.click('[data-testid="poi-marker"]:nth-child(2)');
    await page.waitForSelector('[role="dialog"]');
    
    // Verify second POI content
    await expect(page.locator('text=Test Dungeon')).toBeVisible();
  });

  test('should maintain POI state across navigation', async ({ page }) => {
    // Open POI dialog
    await page.click('[data-testid="poi-marker"]');
    await page.waitForSelector('[role="dialog"]');
    
    // Navigate to another route
    await page.click('[data-testid="menu-button"]');
    await page.click('text=Inventory');
    
    // Navigate back
    await page.goBack();
    
    // Verify POI dialog is closed but POI state is preserved
    await expect(page.locator('[role="dialog"]')).not.toBeVisible();
    await expect(page.locator('[data-testid="poi-marker"].active')).toBeVisible();
  });

  test('should handle POI range restrictions', async ({ page }) => {
    // Move player far from POI
    await page.evaluate(() => {
      window.dispatchEvent(new CustomEvent('movePlayer', {
        detail: { x: 1000, y: 1000 }
      }));
    });
    
    // Try to interact with POI
    await page.click('[data-testid="poi-marker"]');
    
    // Verify interaction is prevented
    await expect(page.locator('[role="dialog"]')).not.toBeVisible();
    await expect(page.locator('text=Too far to interact')).toBeVisible();
    
    // Move player closer to POI
    await page.evaluate(() => {
      window.dispatchEvent(new CustomEvent('movePlayer', {
        detail: { x: 150, y: 250 }
      }));
    });
    
    // Try interaction again
    await page.click('[data-testid="poi-marker"]');
    
    // Verify interaction is allowed
    await expect(page.locator('[role="dialog"]')).toBeVisible();
  });
}); 