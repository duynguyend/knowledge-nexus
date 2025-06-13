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


    // The requirements "Sources Explored" and "Data Collected" are now explicitly in the component.
    // Let's check for them if the mock provides them.
    // Assuming the initial mock (progress 0.25) might not have these, or they are 0.
    // We can add them to the mock if we want to test their initial state too.
    // For now, this test focuses on basic progress elements.
    // The dynamic stats will be more thoroughly tested in 'should update progress based on subsequent API calls'.
  });

  test('should update progress based on subsequent API calls', async ({ page }) => {
    let callCount = 0;
    const mockTaskData = [
      { status: 'in_progress', message: 'Gathering initial sources...', progress: 0.1, sources_explored: 0, data_collected: 0 }, // Initial state with 0s
      { status: 'in_progress', message: 'Analyzing data...', progress: 0.5, sources_explored: 10, data_collected: 50 },
      { status: 'completed', message: 'Research complete. Findings ready.', progress: 1.0, sources_explored: 10, data_collected: 50 } // Completed state might carry over last known values
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

    // Assertions for the second state (progress 0.5, with sources and data)
    await expect(page.locator('p:has-text("Status:")')).toContainText('in_progress');
    await expect(page.locator('p:has-text("Message:")')).toContainText('Analyzing data...');
    await expect(page.locator('.progress-bar')).toHaveText('50%');

    // Verify dynamic stats
    const sourcesExploredStatCard = page.locator('.stat-card:has-text("Sources Explored")');
    await expect(sourcesExploredStatCard.locator('.stat-value')).toHaveText('10');

    const dataCollectedStatCard = page.locator('.stat-card:has-text("Data Collected")');
    await expect(dataCollectedStatCard.locator('.stat-value')).toHaveText('50');

    const currentProgressStatCard = page.locator('.stat-card:has-text("Current Progress")');
    await expect(currentProgressStatCard.locator('.stat-value-highlight')).toHaveText('50%');

    // Verify dynamic summary text
    const summaryText = page.locator('p.summary-text');
    await expect(summaryText).toContainText('explored 10 sources');
    await expect(summaryText).toContainText('collecting 50 data points');
    await expect(summaryText).toContainText('progress is at 50%');

    // Wait for polling to trigger the final mock response (callCount = 3)
    await page.waitForTimeout(6000);

    // Assertions for the completed state
    await expect(page.locator('p:has-text("Status:")')).toContainText('completed');
    const completionMessage = page.locator('.completion-message-block');
    await expect(completionMessage).toBeVisible();
    await expect(completionMessage).toContainText('Research Complete');
    await expect(completionMessage).toContainText('Research complete. Findings ready.');

    // Progress bar in the main section should be 100% (or hidden, depending on implementation for 'completed')
    // The component logic hides the main progress bar and shows "100% Complete" if status is 'completed'.
    // The .progress-bar itself might not exist or be styled to 100% but within a hidden container.
    // Let's check the specific "100% Complete" text in the progress section header.
    const progressSectionHeader = page.locator('.progress-section .progress-percentage');
    await expect(progressSectionHeader).toHaveText('100% Complete');
    // The main progress bar fill should reflect 100%
    await expect(page.locator('.progress-bar-fill')).toHaveAttribute('style', /width: 100%;?/);


    // Stats should still reflect the last known values before completion, or updated values if provided by 'completed' mock
    await expect(sourcesExploredStatCard.locator('.stat-value')).toHaveText('10'); // Assuming these carry from previous state or are in 'completed' mock
    await expect(dataCollectedStatCard.locator('.stat-value')).toHaveText('50');
    await expect(currentProgressStatCard.locator('.stat-value-highlight')).toHaveText('100%'); // Progress stat card should update to 100%

    // Summary text might also update if 'completed' state changes it, or reflect last known numbers
    await expect(summaryText).toContainText('explored 10 sources');
    await expect(summaryText).toContainText('collecting 50 data points');
    await expect(summaryText).toContainText('progress is at 100%');


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
