// @ts-check
const { test, expect } = require('@playwright/test');

const BASE_URL = 'http://localhost:3000/';

test.describe('Main Application Flow', () => {
  test('Basic Navigation to Home Page', async ({ page }) => {
    await page.goto(BASE_URL);
    // Assert that the main topic input field is visible
    const topicInput = page.locator('input.kn-search-input');
    await expect(topicInput).toBeVisible({ timeout: 10000 }); // Increased timeout for initial load
  });

  test('User Topic Input, Submission, and Progress Indication', async ({ page }) => {
    await page.goto(BASE_URL);

    const topicInput = page.locator('input.kn-search-input');
    await topicInput.fill('AI impact on healthcare');

    const startResearchButton = page.locator('button.kn-start-research-button');
    await startResearchButton.click();

    // Assert that the URL has changed or a new component is visible indicating navigation
    // For ResearchProgress, the component itself replaces Home, so no specific URL change other than potentially search params if they were used.
    // We'll check for a loading indicator specific to ResearchProgress.
    // It might initially show "Loading task details..." or quickly transition to showing progress.
    const loadingIndicator = page.locator('.task-details-section p:has-text("Loading task details for")');
    const updatingIndicator = page.locator('.task-details-section span:has-text("(Updating...)")');
    const overallProgressTitle = page.locator('h1:has-text("Research Progress Overview")');


    // Wait for either the specific loading message, the "Updating..." text, or the general progress page title
    await expect(
      loadingIndicator.or(updatingIndicator).or(overallProgressTitle)
    ).toBeVisible({ timeout: 15000 }); // Increased timeout for backend processing and UI update

    // Assert that the initial topic input field is no longer visible
    await expect(topicInput).not.toBeVisible();
  });

  test('Knowledge Display (Results View)', async ({ page }) => {
    await page.goto(BASE_URL);

    const topicInput = page.locator('input.kn-search-input');
    await topicInput.fill('Benefits of renewable energy');

    const startResearchButton = page.locator('button.kn-start-research-button');
    await startResearchButton.click();

    // Wait for the "View Results" button to be visible and enabled
    // This button appears in ResearchProgress.js when status is 'completed'
    const viewResultsButton = page.locator('button.view-results-button');
    await expect(viewResultsButton).toBeVisible({ timeout: 60000 }); // Long timeout to allow for backend processing
    await expect(viewResultsButton).toBeEnabled({ timeout: 10000 });

    await viewResultsButton.click();

    // Assert navigation to results page
    await expect(page).toHaveURL(/\/results\/.+/, { timeout: 10000 }); // Check for /results/:taskId pattern

    // Assert visibility of loading message on results page
    const resultsLoadingMessage = page.locator('div.results-view-container p:has-text("Loading results for task")');
    await expect(resultsLoadingMessage).toBeVisible({ timeout: 10000 });

    // Assert that the results content area becomes visible
    const resultsContent = page.locator('div.results-view-container .results-content');
    await expect(resultsContent).toBeVisible({ timeout: 30000 }); // Timeout for content to load
    await expect(resultsContent).not.toBeEmpty(); // Ensure it's not just an empty div
  });

  test('Document Generation (Interaction on CustomizeOutput Page)', async ({ page }) => {
    const mockTaskId = 'sample-task-123';
    await page.goto(`${BASE_URL}customize/${mockTaskId}`);

    // Assert the "Generate Document" button is visible
    const generateButton = page.locator('button.co-generate-button');
    await expect(generateButton).toBeVisible({ timeout: 10000 });

    // Set up a handler to listen for dialogs (alerts)
    let alertMessage = '';
    page.on('dialog', async dialog => {
      alertMessage = dialog.message();
      await dialog.accept(); // Accept the dialog
    });

    // Click the "Generate Document" button
    await generateButton.click();

    // Assert that an alert dialog was shown and its message matches
    // Need a short wait for the dialog event to be processed
    await page.waitForTimeout(500); // Small delay to ensure dialog event is captured

    expect(alertMessage).toContain(`Simulating document generation for task ${mockTaskId}`);
  });
});
