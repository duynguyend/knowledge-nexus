// @ts-check
const { test, expect } = require('@playwright/test');

const BASE_URL = 'http://localhost:3000';
const MOCK_TASK_ID = 'task123';
const CUSTOMIZE_OUTPUT_URL = `${BASE_URL}/customize/${MOCK_TASK_ID}`;

// From CustomizeOutput.js - for verification
const MOCK_AVAILABLE_SECTIONS = [
  { id: 'introduction', name: 'Introduction', default: true },
  { id: 'methodology', name: 'Methodology', default: true },
  { id: 'findings', name: 'Key Findings', default: true },
  { id: 'discussion', name: 'Discussion', default: false },
  { id: 'conclusion', name: 'Conclusion', default: true },
  { id: 'references', name: 'References', default: true },
  { id: 'appendix', name: 'Appendix', default: false },
];

test.beforeEach(async ({ page }) => {
  await page.goto(CUSTOMIZE_OUTPUT_URL);
});

test.describe('Customize Output Page Structure and Content', () => {
  test('should display the main title with task ID', async ({ page }) => {
    const mainTitle = page.locator(`h1:has-text("Customize Output for Task: ${MOCK_TASK_ID}")`);
    await expect(mainTitle).toBeVisible();
  });

  test.describe('Document Template Section', () => {
    const sectionTitle = 'Document Template';
    const radioName = 'documentTemplate';
    const options = [
      { value: 'research_report', labelText: 'Research Report' },
      { value: 'executive_summary', labelText: 'Executive Summary' },
      { value: 'presentation_slides', labelText: 'Presentation Slides' },
    ];

    test(`should display the "${sectionTitle}" section title`, async ({ page }) => {
      await expect(page.locator(`h2:has-text("${sectionTitle}")`)).toBeVisible();
    });

    test('should allow only one template to be selected', async ({ page }) => {
      for (const option of options) {
        const radio = page.locator(`input[name="${radioName}"][value="${option.value}"]`);
        await expect(radio).toBeVisible();
        await expect(page.locator(`label:has-text("${option.labelText}")`)).toBeVisible();
      }

      // Check default (first one)
      await expect(page.locator(`input[name="${radioName}"][value="${options[0].value}"]`)).toBeChecked();

      // Select second option
      await page.locator(`input[name="${radioName}"][value="${options[1].value}"]`).check();
      await expect(page.locator(`input[name="${radioName}"][value="${options[0].value}"]`)).not.toBeChecked();
      await expect(page.locator(`input[name="${radioName}"][value="${options[1].value}"]`)).toBeChecked();
      await expect(page.locator(`input[name="${radioName}"][value="${options[2].value}"]`)).not.toBeChecked();

      // Select third option
      await page.locator(`label:has-text("${options[2].labelText}")`).click(); // Click label
      await expect(page.locator(`input[name="${radioName}"][value="${options[0].value}"]`)).not.toBeChecked();
      await expect(page.locator(`input[name="${radioName}"][value="${options[1].value}"]`)).not.toBeChecked();
      await expect(page.locator(`input[name="${radioName}"][value="${options[2].value}"]`)).toBeChecked();
    });
  });

  test.describe('Citation Style Section', () => {
    const sectionTitle = 'Citation Style';
    const radioName = 'citationStyle';
    const options = [
      { value: 'apa', labelText: 'APA' },
      { value: 'mla', labelText: 'MLA' },
      { value: 'chicago', labelText: 'Chicago' },
    ];

    test(`should display the "${sectionTitle}" section title`, async ({ page }) => {
      await expect(page.locator(`h2:has-text("${sectionTitle}")`)).toBeVisible();
    });

    test('should allow only one citation style to be selected', async ({ page }) => {
      for (const option of options) {
        await expect(page.locator(`input[name="${radioName}"][value="${option.value}"]`)).toBeVisible();
        await expect(page.locator(`label:has-text("${option.labelText}")`)).toBeVisible();
      }
      // Default (APA)
      await expect(page.locator(`input[name="${radioName}"][value="apa"]`)).toBeChecked();

      await page.locator(`input[name="${radioName}"][value="mla"]`).check();
      await expect(page.locator(`input[name="${radioName}"][value="apa"]`)).not.toBeChecked();
      await expect(page.locator(`input[name="${radioName}"][value="mla"]`)).toBeChecked();

      await page.locator(`label:has-text("Chicago")`).click();
      await expect(page.locator(`input[name="${radioName}"][value="mla"]`)).not.toBeChecked();
      await expect(page.locator(`input[name="${radioName}"][value="chicago"]`)).toBeChecked();
    });
  });

  test.describe('Sections to Include Section', () => {
    const sectionTitle = 'Sections to Include';

    test(`should display the "${sectionTitle}" section title`, async ({ page }) => {
      await expect(page.locator(`h2:has-text("${sectionTitle}")`)).toBeVisible();
    });

    test('should display all available sections with correct default selections', async ({ page }) => {
      for (const section of MOCK_AVAILABLE_SECTIONS) {
        const checkbox = page.locator(`input[type="checkbox"][value="${section.id}"]`);
        await expect(checkbox).toBeVisible();
        await expect(page.locator(`label:has-text("${section.name}")`)).toBeVisible();
        if (section.default) {
          await expect(checkbox).toBeChecked();
        } else {
          await expect(checkbox).not.toBeChecked();
        }
      }
    });

    test('should allow selecting and deselecting multiple sections', async ({ page }) => {
      const introCheckbox = page.locator('input[type="checkbox"][value="introduction"]'); // Default: true
      const methodologyCheckbox = page.locator('input[type="checkbox"][value="methodology"]'); // Default: true
      const discussionCheckbox = page.locator('input[type="checkbox"][value="discussion"]'); // Default: false

      // Initial state
      await expect(introCheckbox).toBeChecked();
      await expect(methodologyCheckbox).toBeChecked();
      await expect(discussionCheckbox).not.toBeChecked();

      // Deselect Introduction
      await introCheckbox.uncheck();
      await expect(introCheckbox).not.toBeChecked();

      // Select Discussion
      await discussionCheckbox.check();
      await expect(discussionCheckbox).toBeChecked();

      // Methodology should remain checked
      await expect(methodologyCheckbox).toBeChecked();
    });
  });

  test.describe('Generate Document Button', () => {
    test('should display the "Generate Document" button', async ({ page }) => {
      const generateButton = page.locator('button.generate-document-button');
      await expect(generateButton).toBeVisible();
      await expect(generateButton).toHaveText('Generate Document');
      await expect(generateButton).toBeEnabled();
    });

    test('clicking "Generate Document" button (mocked action)', async ({ page }) => {
      const generateButton = page.locator('button.generate-document-button');

      // Mock the API call if the component was making one
      // For now, we'll check for the alert which is a side-effect of the current mock implementation in the component
      let alertMessage = '';
      page.on('dialog', async dialog => {
        alertMessage = dialog.message();
        await dialog.accept();
      });

      await generateButton.click();

      // Verify loading state (if component implements it visibly beyond just disabled)
      await expect(generateButton).toHaveText('Generating...'); // Assuming text changes
      await expect(generateButton).toBeDisabled();

      // Wait for the action to complete (button text to revert, enabled)
      await expect(generateButton).toHaveText('Generate Document', { timeout: 5000 }); // Or whatever it reverts to
      await expect(generateButton).toBeEnabled();

      // Check the alert message (current mock behavior)
      const expectedTemplate = 'research_report'; // Default
      const expectedStyle = 'apa'; // Default
      const defaultSelectedSections = MOCK_AVAILABLE_SECTIONS.filter(s => s.default).length;
      expect(alertMessage).toBe(`Document generation started for task ${MOCK_TASK_ID} with template ${expectedTemplate}, style ${expectedStyle}, and ${defaultSelectedSections} sections.`);

      // If API call was made, we'd verify it using page.route or by checking for navigation/success message.
      // e.g. await page.waitForRequest(req => req.url().includes('/api/generate-document') && req.method() === 'POST');
    });

    test('should pass selected options when "Generate Document" is clicked', async ({ page }) => {
      // Change some options
      await page.locator('input[name="documentTemplate"][value="executive_summary"]').check();
      await page.locator('input[name="citationStyle"][value="mla"]').check();

      // Uncheck introduction, check discussion
      await page.locator('input[type="checkbox"][value="introduction"]').uncheck();
      await page.locator('input[type="checkbox"][value="discussion"]').check();

      const generateButton = page.locator('button.generate-document-button');

      let alertMessage = '';
      page.on('dialog', async dialog => {
        alertMessage = dialog.message();
        await dialog.accept();
      });

      await generateButton.click();

      await expect(generateButton).toHaveText('Generate Document', { timeout: 5000 }); // Wait for it to finish

      const expectedTemplate = 'executive_summary';
      const expectedStyle = 'mla';
      // Calculate expected sections: default ones - introduction + discussion
      const expectedSectionsCount = MOCK_AVAILABLE_SECTIONS.filter(s => s.default && s.id !== 'introduction').length + 1;

      expect(alertMessage).toBe(`Document generation started for task ${MOCK_TASK_ID} with template ${expectedTemplate}, style ${expectedStyle}, and ${expectedSectionsCount} sections.`);
    });
  });
});
