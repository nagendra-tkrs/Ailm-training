import { test, expect } from '@playwright/test';

function uniqueEmail(prefix) {
  return `${prefix}${Date.now()}@example.com`;
}

const PASSWORD = 'P@ssw0rd!1';

test('Full frontend workflow: register → login → dashboard → apply → approve → verify', async ({ page, request }) => {
  // Generate unique users
  const empEmail = uniqueEmail('e');
  const adminEmail = uniqueEmail('a');

  // 1) Signup via UI
  await page.goto('/signup');
  await page.fill('#name', 'E2E Employee');
  await page.fill('#signup-email', empEmail);
  await page.fill('#signup-password', PASSWORD);
  await page.fill('#confirm-password', PASSWORD);
  await Promise.all([
    page.waitForNavigation(),
    page.click('.signup-button'),
  ]);
  await expect(page).toHaveURL(/login/);

  // 2) Create admin via API (no need to use UI)
  const regAdmin = await request.post('http://localhost:5000/api/auth/register', { data: { name: 'E2E Admin', email: adminEmail, password: PASSWORD, role: 'admin' } });
  expect([200,201]).toContain(regAdmin.status());

  // 3) Login via UI as employee
  await page.fill('#email', empEmail);
  await page.fill('#password', PASSWORD);
  await Promise.all([
    page.waitForNavigation(),
    page.click('.login-button'),
  ]);
  await expect(page).toHaveURL(/dashboard/);

  // 4) Apply leave via UI
  await page.selectOption('#leaveType', 'Casual Leave');
  const start = new Date();
  start.setDate(start.getDate() + 3);
  const end = new Date(start);
  end.setDate(start.getDate() + 1);
  const startIso = start.toISOString().split('T')[0];
  const endIso = end.toISOString().split('T')[0];
  await page.fill('#startDate', startIso);
  await page.fill('#endDate', endIso);
  await page.fill('#reason', 'E2E test leave');
  await Promise.all([
    page.waitForResponse(resp => resp.url().includes('/api/leave') && resp.status() < 500),
    page.click('.apply-leave-button'),
  ]);

  // 5) Obtain employee token via API for subsequent checks
  const loginEmp = await request.post('http://localhost:5000/api/auth/login', { data: { email: empEmail, password: PASSWORD } });
  expect(loginEmp.status()).toBe(200);
  const empToken = (await loginEmp.json()).access_token;

  // 6) Find the applied leave through API
  const myLeaves = await request.get('http://localhost:5000/api/leave/my', { headers: { Authorization: `Bearer ${empToken}` } });
  expect(myLeaves.status()).toBe(200);
  const leaves = (await myLeaves.json()).leaves;
  const applied = leaves.find(l => l.reason === 'E2E test leave');
  expect(applied).toBeTruthy();

  const leaveId = applied.id;

  // 7) Admin login via API and approve
  const loginAdmin = await request.post('http://localhost:5000/api/auth/login', { data: { email: adminEmail, password: PASSWORD } });
  expect(loginAdmin.status()).toBe(200);
  const adminToken = (await loginAdmin.json()).access_token;

  const approve = await request.put(`http://localhost:5000/api/leave/${leaveId}/approve`, { headers: { Authorization: `Bearer ${adminToken}` } });
  expect(approve.status()).toBe(200);

  // 8) Refresh leave history UI and verify status
  await page.goto('/leave-history');
  await page.waitForLoadState('networkidle');
  await expect(page.locator('table.leave-history-table')).toBeVisible();
  // Check row with reason 'E2E test leave' has status 'approved'
  const row = page.locator('table.leave-history-table tbody tr').filter({ hasText: 'E2E test leave' }).first();
  await expect(row).toContainText('approved');

  // 9) Profile get + update via UI
  await page.goto('/profile');
  await page.waitForLoadState('networkidle');
  // Enter edit mode
  await page.click('.profile-edit-button');
  await expect(page.locator('#profileName')).toBeVisible();
  // Append ' E2E' to name
  const nameInput = page.locator('#profileName');
  const currentName = await nameInput.inputValue();
  await nameInput.fill(currentName + ' E2E');
  await Promise.all([
    page.waitForResponse(resp => resp.url().includes('/api/profile') && resp.status() < 500),
    page.click('button.apply-leave-button'),
  ]);

  // Capture final screenshot
  await page.screenshot({ path: '../reports/playwright/e2e-final.png', fullPage: true });
});
