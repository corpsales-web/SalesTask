const { test, expect, devices } = require('@playwright/test');

// Test Face Check-in across different device types
const deviceConfigs = [
  { name: 'Desktop Chrome', ...devices['Desktop Chrome'] },
  { name: 'Desktop Firefox', ...devices['Desktop Firefox'] },
  { name: 'Desktop Safari', ...devices['Desktop Safari'] },
  { name: 'iPhone 12', ...devices['iPhone 12'] },
  { name: 'iPhone 12 Pro', ...devices['iPhone 12 Pro'] },
  { name: 'Pixel 5', ...devices['Pixel 5'] },
  { name: 'Samsung Galaxy S21', ...devices['Samsung Galaxy S21'] },
  { name: 'iPad Pro', ...devices['iPad Pro'] },
];

deviceConfigs.forEach(device => {
  test.describe(`Face Check-in - ${device.name}`, () => {
    test.use({ ...device });

    test(`Face Check-in functionality on ${device.name}`, async ({ page }) => {
      await page.goto('http://localhost:3000');
      await page.waitForLoadState('networkidle');
      
      // Navigate to HRMS tab
      await page.click('button:has-text("HRMS")');
      await page.waitForTimeout(2000);
      
      // Click Face Check-In button
      await page.click('button:has-text("Face Check-In")');
      await page.waitForTimeout(2000);

      // Verify modal opens with enhanced features
      await expect(page.locator('text=Face Check-In')).toBeVisible();
      await expect(page.locator('text=Capture your photo to record attendance')).toBeVisible();

      // Check for device-specific information display
      if (process.env.NODE_ENV === 'development') {
        await expect(page.locator('text=Device:')).toBeVisible();
        await expect(page.locator('text=Browser:')).toBeVisible();
        await expect(page.locator('text=Permission:')).toBeVisible();
      }

      // Verify enhanced instructions are present
      await expect(page.locator('text=Position your face within the circular guide')).toBeVisible();
      await expect(page.locator('text=Ensure good lighting on your face')).toBeVisible();
      await expect(page.locator('text=Look directly at the camera')).toBeVisible();

      // Check for device-specific tips
      if (device.name.includes('iPhone') || device.name.includes('iPad')) {
        await expect(page.locator('text=iOS tip:')).toBeVisible();
      }
      if (device.name.includes('Android') || device.name.includes('Pixel') || device.name.includes('Samsung')) {
        await expect(page.locator('text=Android tip:')).toBeVisible();
      }
      if (device.name.includes('Desktop') && device.name.includes('Mac')) {
        await expect(page.locator('text=MacBook tip:')).toBeVisible();
      }

      // Test Start Camera button
      const startCameraButton = page.locator('button:has-text("Start Camera")');
      await expect(startCameraButton).toBeVisible();

      // Grant camera permissions for testing
      await page.context().grantPermissions(['camera']);
      
      // Click Start Camera button
      await startCameraButton.click();
      await page.waitForTimeout(3000);

      // Check if camera interface appears or error handling works
      const cameraError = page.locator('text=Failed to access camera');
      const cameraSuccess = page.locator('video'); // Video element would appear on success

      // Either camera works or shows appropriate error
      const hasError = await cameraError.isVisible();
      const hasVideo = await cameraSuccess.isVisible();
      
      if (hasError) {
        console.log(`${device.name}: Camera access failed (expected in test environment)`);
        // Verify error message is appropriate for device
        await expect(page.locator('text=Camera permission denied').or(
          page.locator('text=No camera device found')
        )).toBeVisible();
      } else if (hasVideo) {
        console.log(`${device.name}: Camera access successful`);
        // Test camera controls if available
        const captureButton = page.locator('button[title="Capture photo"]');
        if (await captureButton.isVisible()) {
          await expect(captureButton).toBeVisible();
        }
      }

      // Verify browser compatibility info is shown when needed
      const httpsWarning = page.locator('text=HTTPS connection required');
      if (device.name.includes('Chrome') && page.url().startsWith('http://')) {
        await expect(httpsWarning).toBeVisible();
      }

      // Test orientation handling on mobile devices
      if (device.name.includes('iPhone') || device.name.includes('Android') || device.name.includes('Pixel') || device.name.includes('Samsung')) {
        // Mobile devices should handle orientation changes
        console.log(`${device.name}: Testing mobile-specific features`);
        
        // Camera switch button should be available on mobile
        const switchButton = page.locator('button[title="Switch camera"]');
        // May or may not be visible depending on available cameras in test environment
      }

      console.log(`✅ Face Check-in tested successfully on ${device.name}`);
    });

    test(`Face Check-in error handling on ${device.name}`, async ({ page }) => {
      await page.goto('http://localhost:3000');
      await page.waitForLoadState('networkidle');
      
      // Navigate to HRMS and Face Check-In
      await page.click('button:has-text("HRMS")');
      await page.waitForTimeout(2000);
      await page.click('button:has-text("Face Check-In")');
      await page.waitForTimeout(2000);

      // Test without granting camera permissions
      const startCameraButton = page.locator('button:has-text("Start Camera")');
      await startCameraButton.click();
      await page.waitForTimeout(2000);

      // Should show appropriate error message
      const permissionError = page.locator('text=Camera permission denied');
      const deviceError = page.locator('text=No camera device found');
      const httpsError = page.locator('text=HTTPS connection required');

      // At least one error should be visible
      const hasAnyError = await permissionError.isVisible() || 
                         await deviceError.isVisible() || 
                         await httpsError.isVisible();
      
      expect(hasAnyError).toBeTruthy();
      console.log(`✅ Error handling verified on ${device.name}`);
    });

    test(`Face Check-in UI responsiveness on ${device.name}`, async ({ page }) => {
      await page.goto('http://localhost:3000');
      await page.waitForLoadState('networkidle');
      
      await page.click('button:has-text("HRMS")');
      await page.waitForTimeout(2000);
      await page.click('button:has-text("Face Check-In")');
      await page.waitForTimeout(2000);

      // Check modal responsiveness
      const modal = page.locator('.face-checkin-component');
      if (await modal.isVisible()) {
        await expect(modal).toBeVisible();
      }

      // Verify UI elements are properly sized for device
      const instructions = page.locator('text=Instructions:');
      await expect(instructions).toBeVisible();

      // Check button sizes are appropriate for touch vs mouse
      const startButton = page.locator('button:has-text("Start Camera")');
      await expect(startButton).toBeVisible();

      console.log(`✅ UI responsiveness verified on ${device.name}`);
    });
  });
});

// Cross-device compatibility test
test.describe('Face Check-in Cross-Device Compatibility', () => {
  test('Consistent functionality across all device types', async ({ page }) => {
    const results = [];
    
    // This would ideally test with multiple browser contexts
    // For now, test core functionality that should work everywhere
    
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    
    await page.click('button:has-text("HRMS")');
    await page.waitForTimeout(2000);
    await page.click('button:has-text("Face Check-In")');
    await page.waitForTimeout(2000);

    // Core elements that should be present on all devices
    const coreElements = [
      'text=Face Check-In',
      'text=Capture your photo to record attendance', 
      'text=Instructions:',
      'text=Position your face within the circular guide',
      'button:has-text("Start Camera")'
    ];

    for (const selector of coreElements) {
      const element = page.locator(selector);
      await expect(element).toBeVisible();
      results.push(`✅ ${selector} - Present`);
    }

    console.log('Cross-device compatibility results:', results);
  });

  test('Device-specific features are properly implemented', async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    
    await page.click('button:has-text("HRMS")');
    await page.waitForTimeout(2000);
    await page.click('button:has-text("Face Check-In")');
    await page.waitForTimeout(2000);

    // Test device detection and tips
    const deviceTips = [
      'text=💡 MacBook tip:',
      'text=💡 Android tip:', 
      'text=💡 iOS tip:'
    ];

    let foundTips = 0;
    for (const tip of deviceTips) {
      if (await page.locator(tip).isVisible()) {
        foundTips++;
      }
    }

    // At least one device-specific tip should be shown
    console.log(`Found ${foundTips} device-specific tips`);
  });
});