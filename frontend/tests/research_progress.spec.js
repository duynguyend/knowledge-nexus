// @ts-check
const { test, expect } = require('@playwright/test');

const HOME_URL = 'http://localhost:3000/';

async function startResearch(page, topic = 'Test Topic') {
  await page.goto(HOME_URL);
  const searchBar = page.locator('input.research-topic-input');
  await searchBar.fill(topic);
  const startResearchingButton = page.locator('button.start-research-button');
  await startResearchingButton.click();
  // Wait for navigation to the research progress part (input field disappears)
  await expect(searchBar).not.toBeVisible({ timeout: 10000 });
}

test.describe('Research Progress Page', () => {
  test('should display initial loading and then progress elements', async ({ page }) => {
    // Mock the initial /api/research/start response if needed, though not strictly necessary for this component's direct tests
    // For now, assume startResearchTopic will yield a task_id
    // Mock the status endpoint before starting research
    await page.route('**/api/tasks/*/status', async route => {
      const request = route.request();
      const taskId = request.url().split('/')[5]; // Extract task ID from URL
      console.log(`Mocking status for task ID: ${taskId}`);
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          task_id: taskId,
          status: 'in_progress',
          message: 'Agents are currently gathering information...',
          progress: 0.25, // Example progress: 25%
          // other fields like 'verification_request' can be added if needed for specific tests
        }),
      });
    });

    await startResearch(page, 'Quantum Computing Impact');

    // Verify elements on the Research Progress page
    const researchProgressTitle = page.locator('h2:has-text("Research Progress")');
    await expect(researchProgressTitle).toBeVisible();

    const taskIdDisplay = page.locator(`p:has-text("Task ID:")`);
    await expect(taskIdDisplay).toBeVisible();
    // We can't easily get the task ID itself from the frontend to check against the mock
    // but its presence is a good sign.

    const statusDisplay = page.locator('p:has-text("Status:")');
    await expect(statusDisplay).toBeVisible();
    await expect(statusDisplay).toContainText('in_progress');

    // Check for the message based on our mock
    const messageDisplay = page.locator('p:has-text("Message:")');
    await expect(messageDisplay).toBeVisible();
    await expect(messageDisplay).toContainText('Agents are currently gathering information...');

    // Check for the progress bar
    const progressBarContainer = page.locator('.progress-bar-container');
    await expect(progressBarContainer).toBeVisible();
    const progressBar = progressBarContainer.locator('.progress-bar');
    await expect(progressBar).toBeVisible();
    await expect(progressBar).toHaveText('25%'); // From mock: 0.25 * 100
    // Check style for width (approximate due to potential floating point issues)
    const progressBarWidth = await progressBar.evaluate(el => el.style.width);
    expect(parseFloat(progressBarWidth)).toBeCloseTo(25);


    // The requirements "Sources Explored" and "Data Collected" are not explicitly in the component
    // The "data summary section" is vague. For now, we confirm the message and progress.
  });

  test('should update progress based on subsequent API calls', async ({ page }) => {
    let callCount = 0;
    const mockTaskData = [
      { status: 'in_progress', message: 'Gathering initial sources...', progress: 0.1 },
      { status: 'in_progress', message: 'Analyzing data...', progress: 0.5, sources_explored: 10, data_collected: 50 },
      { status: 'completed', message: 'Research complete. Findings ready.', progress: 1.0, results_summary: 'AI is good.' }
    ];

    await page.route('**/api/tasks/*/status', async route => {
      const taskId = route.request().url().split('/')[5];
      const data = mockTaskData[callCount] || mockTaskData[mockTaskData.length -1]; // Use last data if callCount exceeds
      console.log(`Mocking status (call ${callCount + 1}) for task ID: ${taskId} with progress ${data.progress}`);
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ task_id: taskId, ...data }),
      });
      callCount++;
    });

    await startResearch(page, 'Renewable Energy Trends');

    // Initial state (callCount = 1 after first fetch in component)
    await expect(page.locator('p:has-text("Status:")')).toContainText('in_progress', { timeout: 10000 });
    await expect(page.locator('p:has-text("Message:")')).toContainText('Gathering initial sources...');
    await expect(page.locator('.progress-bar')).toHaveText('10%');

    // Wait for polling to trigger the next mock response (callCount = 2)
    // The default poll interval in ResearchProgress.js is 5000ms.
    // We need to ensure enough time for the component to make the next call.
    await page.waitForTimeout(6000); // Wait longer than poll interval

    await expect(page.locator('p:has-text("Status:")')).toContainText('in_progress'); // Should still be in_progress
    await expect(page.locator('p:has-text("Message:")')).toContainText('Analyzing data...');
    await expect(page.locator('.progress-bar')).toHaveText('50%');

    // Wait for polling to trigger the final mock response (callCount = 3)
    await page.waitForTimeout(6000);

    await expect(page.locator('p:has-text("Status:")')).toContainText('completed');
    // Message for 'completed' status is in a different block
    const completionMessage = page.locator('.completion-message-block');
    await expect(completionMessage).toBeVisible();
    await expect(completionMessage).toContainText('Research Complete');
    await expect(completionMessage).toContainText('Research complete. Findings ready.');
    await expect(page.locator('.progress-bar-container')).not.toBeVisible(); // Progress bar hidden on completion

    // Verify "View Results" button
    const viewResultsButton = page.locator('button.view-results-button');
    await expect(viewResultsButton).toBeVisible();
    await expect(viewResultsButton).toBeEnabled();
  });

  // Add more tests for 'failed' status, 'awaiting_human_verification', etc.
  // For example:
  test('should display human verification section when status is awaiting_human_verification', async ({ page }) => {
    await page.route('**/api/tasks/*/status', async route => {
      const taskId = route.request().url().split('/')[5];
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          task_id: taskId,
          status: 'awaiting_human_verification',
          message: 'Please verify the collected data.',
          progress: 0.8,
          verification_request: {
            data_id: 'verify123',
            data_to_verify: {
              content_preview: 'This is some content to verify.',
              url: 'http://example.com/source1'
            },
            conflicting_sources: []
          }
        }),
      });
    });

    await startResearch(page, 'Human Verification Test');

    await expect(page.locator('h2:has-text("Research Progress")')).toBeVisible({timeout: 10000});
    await expect(page.locator('p:has-text("Status:")')).toContainText('awaiting_human_verification');

    const verificationSection = page.locator('.human-verification-section');
    await expect(verificationSection).toBeVisible();
    await expect(verificationSection.locator('h3')).toHaveText('Human Verification Needed');
    await expect(verificationSection).toContainText('Item to Verify (ID: verify123)');
    await expect(verificationSection).toContainText('Content Preview: This is some content to verify.');
    await expect(verificationSection.locator('a[href="http://example.com/source1"]')).toBeVisible();
    await expect(verificationSection.locator('button:has-text("Submit Verification")')).toBeVisible();
  });

});
