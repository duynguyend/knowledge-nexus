// @ts-check
const { test, expect } = require('@playwright/test');

const HOME_URL = 'http://localhost:3000/';

test.beforeEach(async ({ page }) => {
  await page.goto(HOME_URL);
});

test.describe('Home Page Elements Verification', () => {
  test('should display the search bar', async ({ page }) => {
    const searchBar = page.locator('input.research-topic-input');
    await expect(searchBar).toBeVisible();
    await expect(searchBar).toHaveAttribute('placeholder', 'E.g., The impact of AI on climate change');
  });

  // Skipping popular topics test as it's not in Home.js currently
  // test('should display popular topics section', async ({ page }) => {
  //   const popularTopicsSection = page.locator('text=Popular Topics'); // Adjust selector
  //   await expect(popularTopicsSection).toBeVisible();
  //   const topicButton = page.locator('.popular-topics-list button').first(); // Adjust selector
  //   await expect(topicButton).toBeVisible();
  // });

  test('should display the "Start Researching" button', async ({ page }) => {
    const startResearchingButton = page.locator('button.start-research-button');
    await expect(startResearchingButton).toBeVisible();
    await expect(startResearchingButton).toHaveText('Start Researching');
  });
});

test.describe('Home Page Functionality', () => {
  test('searching for a topic should navigate to research progress', async ({ page }) => {
    const searchBar = page.locator('input.research-topic-input');
    await searchBar.fill('AI in healthcare');

    const startResearchingButton = page.locator('button.start-research-button');
    await startResearchingButton.click();

    // Check if the research progress component is visible
    const researchProgressTitle = page.locator('h2:has-text("Research Progress")');
    await expect(researchProgressTitle).toBeVisible({ timeout: 10000 }); // Increased timeout for backend processing

    // Also check that the input field is gone
    await expect(searchBar).not.toBeVisible();
  });

  // Skipping popular topics test as it's not in Home.js currently
  // test('clicking a popular topic populates the search bar', async ({ page }) => {
  //   const topicButton = page.locator('.popular-topics-list button').first(); // Adjust selector
  //   const topicText = await topicButton.textContent();
  //   await topicButton.click();
  //   const searchBar = page.locator('input.research-topic-input');
  //   await expect(searchBar).toHaveValue(topicText);
  // });

  test('clicking "Start Researching" without a topic shows an error', async ({ page }) => {
    const startResearchingButton = page.locator('button.start-research-button');
    await startResearchingButton.click();

    const errorMessage = page.locator('.error-message');
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toContainText('Please enter a research topic.');

    // Ensure no navigation occurred / input is still visible
    const searchBar = page.locator('input.research-topic-input');
    await expect(searchBar).toBeVisible();
  });
});
