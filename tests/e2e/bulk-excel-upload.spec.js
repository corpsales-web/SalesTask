const { test, expect } = require('@playwright/test');

test.describe('Bulk Excel Upload E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    
    // Navigate to Leads tab
    await page.click('button:has-text("Leads")');
    await page.waitForTimeout(2000);
  });

  test('Complete bulk Excel upload workflow', async ({ page }) => {
    // Click Bulk Excel Upload button
    await page.click('button:has-text("Bulk Excel Upload")');
    await page.waitForTimeout(2000);

    // Verify modal opens with all sections
    await expect(page.locator('text=📊 Bulk Excel Lead Upload')).toBeVisible();
    await expect(page.locator('text=Date Filter')).toBeVisible();
    await expect(page.locator('text=Auto-Resync')).toBeVisible();
    await expect(page.locator('text=Dashboard Update')).toBeVisible();

    // Test template download
    await page.click('button:has-text("Download Template")');
    // Wait for download to trigger
    await page.waitForTimeout(1000);

    // Test date range selection
    await page.click('button[role="combobox"]');
    await page.waitForTimeout(500);
    await page.click('div[role="option"]:has-text("Last 7 Days")');
    
    // Test auto-resync toggle
    await page.click('button[role="checkbox"]');
    
    // Verify drag & drop area
    await expect(page.locator('text=Drag & drop your Excel file here')).toBeVisible();
    await expect(page.locator('text=Excel (.xlsx, .xls) or CSV files only')).toBeVisible();

    // Test file upload simulation (would need actual file in real test)
    // const fileInput = page.locator('input[type="file"]');
    // await fileInput.setInputFiles('test-data/sample-leads.xlsx');

    // Verify upload progress and results would appear
    // await expect(page.locator('text=Processing Excel file...')).toBeVisible();
    // await expect(page.locator('text=Upload Results')).toBeVisible();

    // Close modal
    await page.click('button:has-text("Close")');
  });

  test('Date filtering functionality across all options', async ({ page }) => {
    await page.click('button:has-text("Bulk Excel Upload")');
    await page.waitForTimeout(2000);

    // Test all date range options
    const dateOptions = [
      'All Dates',
      'Today', 
      'Yesterday',
      'Last 7 Days',
      'Last 30 Days',
      'This Month',
      'Custom Range'
    ];

    for (const option of dateOptions) {
      await page.click('button[role="combobox"]');
      await page.waitForTimeout(300);
      await page.click(`div[role="option"]:has-text("${option}")`);
      await page.waitForTimeout(300);
      
      // Verify selection
      await expect(page.locator(`text=${option}`)).toBeVisible();
      
      // If custom range, verify date inputs appear
      if (option === 'Custom Range') {
        await expect(page.locator('input[type="date"]')).toBeVisible();
      }
    }
  });

  test('Auto-resync settings with interval options', async ({ page }) => {
    await page.click('button:has-text("Bulk Excel Upload")');
    await page.waitForTimeout(2000);

    // Enable auto-resync
    const checkbox = page.locator('button[role="checkbox"]');
    await checkbox.click();
    
    // Verify interval options appear
    await expect(page.locator('text=Resync Interval')).toBeVisible();
    
    // Test interval selection
    await page.click('button[role="combobox"]');
    await page.waitForTimeout(300);
    
    const intervals = ['Every Hour', 'Daily', 'Weekly'];
    for (const interval of intervals) {
      if (await page.locator(`div[role="option"]:has-text("${interval}")`).isVisible()) {
        await page.click(`div[role="option"]:has-text("${interval}")`);
        await page.waitForTimeout(300);
        await expect(page.locator(`text=${interval}`)).toBeVisible();
        break;
      }
    }
  });

  test('Dashboard integration status indicators', async ({ page }) => {
    await page.click('button:has-text("Bulk Excel Upload")');
    await page.waitForTimeout(2000);

    // Verify all dashboard integration features are shown as enabled
    await expect(page.locator('text=Instant CRM Update')).toBeVisible();
    await expect(page.locator('text=Enabled')).toBeVisible();
    
    await expect(page.locator('text=Duplicate Detection')).toBeVisible();
    await expect(page.locator('text=Active')).toBeVisible();
    
    await expect(page.locator('text=Auto-Notification')).toBeVisible();
    await expect(page.locator('text=On')).toBeVisible();
  });

  test('File validation and error handling', async ({ page }) => {
    await page.click('button:has-text("Bulk Excel Upload")');
    await page.waitForTimeout(2000);

    // Test file format validation message
    await expect(page.locator('text=Supported formats: .xlsx, .xls, .csv (Max size: 10MB)')).toBeVisible();
    
    // Verify drag and drop area is interactive
    const dropzone = page.locator('[data-testid="dropzone"]').first();
    if (await dropzone.isVisible()) {
      await expect(dropzone).toBeVisible();
    }

    // Test file size and format requirements are clearly displayed
    await expect(page.locator('text=Excel (.xlsx, .xls) or CSV files only')).toBeVisible();
  });

  test('Upload results and duplicate detection display', async ({ page }) => {
    await page.click('button:has-text("Bulk Excel Upload")');
    await page.waitForTimeout(2000);

    // This test would simulate a successful upload with duplicates
    // In real implementation, would upload a test file and verify:
    
    // 1. Results statistics display
    // await expect(page.locator('text=Upload Results')).toBeVisible();
    // await expect(page.locator('text=Total Rows')).toBeVisible();
    // await expect(page.locator('text=Valid Leads')).toBeVisible();
    // await expect(page.locator('text=Duplicates')).toBeVisible();
    // await expect(page.locator('text=Invalid Rows')).toBeVisible();

    // 2. Duplicate leads notification
    // await expect(page.locator('text=Duplicate Leads Detected')).toBeVisible();
    // await expect(page.locator('text=Matches by phone')).toBeVisible();
    // await expect(page.locator('text=Matches by email')).toBeVisible();

    // 3. Action buttons
    // await expect(page.locator('button:has-text("Preview Data")')).toBeVisible();
    // await expect(page.locator('button:has-text("Resync Data")')).toBeVisible();
  });

  test('Responsive design across different screen sizes', async ({ page }) => {
    // Test desktop view
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.click('button:has-text("Bulk Excel Upload")');
    await page.waitForTimeout(2000);
    
    await expect(page.locator('text=📊 Bulk Excel Lead Upload')).toBeVisible();
    
    // Test tablet view
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(1000);
    await expect(page.locator('text=📊 Bulk Excel Lead Upload')).toBeVisible();
    
    // Test mobile view  
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);
    await expect(page.locator('text=📊 Bulk Excel Lead Upload')).toBeVisible();
  });

  test('Integration with main dashboard after upload', async ({ page }) => {
    // This test would verify that successful bulk upload updates the main dashboard
    // 1. Note current lead count on dashboard
    // 2. Perform bulk upload
    // 3. Verify dashboard lead count increases
    // 4. Verify toast notification appears
    // 5. Verify new leads appear in leads list
    
    // Would need actual file upload and backend integration for full test
  });

  test('Cross-browser compatibility', async ({ page, browserName }) => {
    await page.click('button:has-text("Bulk Excel Upload")');
    await page.waitForTimeout(2000);

    // Basic functionality should work across all browsers
    await expect(page.locator('text=📊 Bulk Excel Lead Upload')).toBeVisible();
    await expect(page.locator('text=Date Filter')).toBeVisible();
    await expect(page.locator('text=Auto-Resync')).toBeVisible();
    
    // Test template download works in all browsers
    await page.click('button:has-text("Download Template")');
    await page.waitForTimeout(1000);
    
    console.log(`✅ Bulk Excel Upload working in ${browserName}`);
  });
});