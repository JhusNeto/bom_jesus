import { test, expect } from '@playwright/test';

/**
 * E2E: fluxo operador - login → pesagem/entrada → mover → perda → devolução → dashboard
 * Requer: backend em localhost:3000, frontend em 5173 (ou baseURL)
 * Dados: admin@bomjesus.local / admin1234 (seed)
 */
test.describe('Fluxo operador', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.setItem('bom-jesus-onboarding-seen', '1');
    });
  });

  test('login e redirecionamento para home', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('admin@bomjesus.local');
    await page.getByLabel(/senha/i).fill('admin1234');
    await page.getByRole('button', { name: /entrar/i }).click();
    await expect(page).toHaveURL(/\/(?!login)/, { timeout: 10000 });
  });

  test('home carrega após login', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('admin@bomjesus.local');
    await page.getByLabel(/senha/i).fill('admin1234');
    await page.getByRole('button', { name: /entrar/i }).click();
    await page.waitForURL(/\/(?!login)/, { timeout: 10000 });
    await expect(page.getByRole('link', { name: 'Ver dashboard' })).toBeVisible({ timeout: 10000 });
  });

  test('dashboard acessível', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('admin@bomjesus.local');
    await page.getByLabel(/senha/i).fill('admin1234');
    await page.getByRole('button', { name: /entrar/i }).click();
    await page.waitForURL(/\/(?!login)/, { timeout: 10000 });
    await page.getByRole('link', { name: 'Ver dashboard' }).click();
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page.getByText(/Dashboard MVP|perdas|estoque|caixas/i).first()).toBeVisible({
      timeout: 15000,
    });
  });

  test('admin acessível para gestor', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel(/email/i).fill('admin@bomjesus.local');
    await page.getByLabel(/senha/i).fill('admin1234');
    await page.getByRole('button', { name: /entrar/i }).click();
    await page.waitForURL(/\/(?!login)/, { timeout: 10000 });
    await page.getByRole('link', { name: 'Ver dashboard' }).click();
    await page.waitForURL(/\/dashboard/);
    await page.getByRole('link', { name: 'Admin', exact: true }).click();
    await expect(page).toHaveURL(/\/admin/);
    await expect(page.getByText(/Admin Cadastros|Novo produto/i).first()).toBeVisible({
      timeout: 15000,
    });
  });
});
