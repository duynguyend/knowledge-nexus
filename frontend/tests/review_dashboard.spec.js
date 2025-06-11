// @ts-check
const { test, expect } = require('@playwright/test');

const REVIEW_DASHBOARD_URL = 'http://localhost:3000/review';

// Placeholder data from ReviewDashboard.js - for verification
const placeholderCurrentProjects = [
  { id: 'proj001', name: 'AI in Healthcare', status: 'Data Collection', progress: 30 },
  { id: 'proj002', name: 'Climate Change Impact', status: 'Verification', progress: 65 },
];

const placeholderReviewQueue = [
  { id: 'task003', project: 'AI in Healthcare', item: 'Source Verification: Nature Article', priority: 'High' },
  { id: 'task004', project: 'Climate Change Impact', item: 'Conflict Resolution: Sea Level Rise Data', priority: 'Medium' },
];

test.beforeEach(async ({ page }) => {
  await page.goto(REVIEW_DASHBOARD_URL);
});

test.describe('Review Dashboard Page Structure and Content', () => {
  test('should display the main title', async ({ page }) => {
    const mainTitle = page.locator('h1:has-text("Review & Verification Dashboard")');
    await expect(mainTitle).toBeVisible();
  });

  test.describe('Current Projects Section', () => {
    test('should display the "Current Projects Overview" title', async ({ page }) => {
      const sectionTitle = page.locator('h2:has-text("Current Projects Overview")');
      await expect(sectionTitle).toBeVisible();
    });

    test('should display the projects table with correct headers', async ({ page }) => {
      const projectsTable = page.locator('table.projects-table');
      await expect(projectsTable).toBeVisible();
      const headers = projectsTable.locator('thead tr th');
      await expect(headers).toHaveCount(4);
      await expect(headers.nth(0)).toHaveText('Project ID');
      await expect(headers.nth(1)).toHaveText('Name');
      await expect(headers.nth(2)).toHaveText('Status');
      await expect(headers.nth(3)).toHaveText('Progress');
    });

    test('should display placeholder project data correctly', async ({ page }) => {
      const projectsTable = page.locator('table.projects-table');
      const rows = projectsTable.locator('tbody tr');
      await expect(rows).toHaveCount(placeholderCurrentProjects.length);

      for (let i = 0; i < placeholderCurrentProjects.length; i++) {
        const project = placeholderCurrentProjects[i];
        const row = rows.nth(i);
        await expect(row.locator('td').nth(0)).toHaveText(project.id);
        await expect(row.locator('td').nth(1)).toHaveText(project.name);
        await expect(row.locator('td').nth(2)).toHaveText(project.status);
        await expect(row.locator('td').nth(3)).toHaveText(`${project.progress}%`);
      }
    });

    test('NOTE: "View" button test skipped as it is not in the current component code', () => {
      // Test for "View" button would go here if implemented
      // e.g., const viewButton = rows.nth(0).locator('button:has-text("View")');
      // await expect(viewButton).toBeVisible();
      // await viewButton.click();
      // await expect(page).toHaveURL(...); // or other expected behavior
      console.warn('Test for "View" button in "Current Projects" is skipped as the button is not implemented in ReviewDashboard.js.');
      expect(true).toBe(true); // Placeholder to make test runner happy
    });
  });

  test.describe('Review Queue Section', () => {
    test('should display the "Review Queue" title', async ({ page }) => {
      const sectionTitle = page.locator('h2:has-text("Review Queue")');
      await expect(sectionTitle).toBeVisible();
    });

    test('should display the queue table with correct headers', async ({ page }) => {
      const queueTable = page.locator('table.queue-table');
      await expect(queueTable).toBeVisible();
      const headers = queueTable.locator('thead tr th');
      await expect(headers).toHaveCount(5);
      await expect(headers.nth(0)).toHaveText('Task ID');
      await expect(headers.nth(1)).toHaveText('Project');
      await expect(headers.nth(2)).toHaveText('Item for Review');
      await expect(headers.nth(3)).toHaveText('Priority');
      await expect(headers.nth(4)).toHaveText('Action');
    });

    test('should display placeholder queue data correctly', async ({ page }) => {
      const queueTable = page.locator('table.queue-table');
      const rows = queueTable.locator('tbody tr');
      await expect(rows).toHaveCount(placeholderReviewQueue.length);

      for (let i = 0; i < placeholderReviewQueue.length; i++) {
        const item = placeholderReviewQueue[i];
        const row = rows.nth(i);
        await expect(row.locator('td').nth(0)).toHaveText(item.id);
        await expect(row.locator('td').nth(1)).toHaveText(item.project);
        await expect(row.locator('td').nth(2)).toHaveText(item.item);
        await expect(row.locator('td').nth(3)).toHaveText(item.priority);
        await expect(row.locator('td').nth(3)).toHaveClass(`priority-${item.priority.toLowerCase()}`);

        const reviewButton = row.locator('td').nth(4).locator('button.review-action-button');
        await expect(reviewButton).toBeVisible();
        await expect(reviewButton).toHaveText('Review Item');
      }
    });

    test('clicking "Review Item" button (basic check - presence and enabled)', async ({ page }) => {
      const queueTable = page.locator('table.queue-table');
      const firstReviewButton = queueTable.locator('tbody tr').first().locator('button.review-action-button');
      await expect(firstReviewButton).toBeVisible();
      await expect(firstReviewButton).toBeEnabled();
      // Actual click action and navigation/modal test would require:
      // 1. Knowing the intended behavior (e.g., navigate to /review/{itemId} or open a modal)
      // 2. Potentially mocking API calls if the action triggers data fetching for the item
      // For now, this test just confirms the button is there and clickable.
      // Example of further testing if it navigated:
      // await firstReviewButton.click();
      // await expect(page).toHaveURL(new RegExp(`/review/${placeholderReviewQueue[0].id}$`));
       console.warn('Further test for "Review Item" button click action (navigation/modal) is not implemented as target behavior is not defined yet.');
    });
  });
});
