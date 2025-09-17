/**
 * Before Fix: ResizeObserver Error Reproduction Test
 * This test documents current ResizeObserver errors for baseline comparison
 */

const { chromium, firefox, webkit } = require('playwright');

async function testResizeObserverErrors() {
  const browsers = [
    { name: 'Chromium', browser: chromium },
    { name: 'Firefox', browser: firefox },
    { name: 'WebKit', browser: webkit }
  ];

  const results = {
    timestamp: new Date().toISOString(),
    beforeFix: true,
    browsers: {}
  };

  for (const { name, browser } of browsers) {
    console.log(`\n=== Testing ${name} ===`);
    
    const browserInstance = await browser.launch();
    const context = await browserInstance.newContext();
    const page = await context.newPage();
    
    // Collect console errors
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        const text = msg.text();
        if (text.includes('ResizeObserver')) {
          consoleErrors.push({
            text,
            timestamp: new Date().toISOString()
          });
        }
      }
    });

    try {
      await page.goto('https://green-crm-suite.preview.emergentagent.com');
      await page.waitForTimeout(2000);

      // Test Flow 1: Add Lead Modal
      console.log('Testing Add Lead Modal...');
      await page.click('button:has-text("Add Lead")');
      await page.waitForTimeout(1000);
      
      // Rapid window resize (triggers ResizeObserver)
      await page.setViewportSize({ width: 800, height: 600 });
      await page.waitForTimeout(500);
      await page.setViewportSize({ width: 1200, height: 800 });
      await page.waitForTimeout(500);
      await page.setViewportSize({ width: 1920, height: 1080 });
      await page.waitForTimeout(1000);

      // Close modal
      await page.press('body', 'Escape');
      await page.waitForTimeout(500);

      // Test Flow 2: Goals/Targets
      console.log('Testing Goals button...');
      const goalsButton = await page.locator('.fixed.bottom-6.left-24').first();
      if (await goalsButton.isVisible()) {
        await goalsButton.click();
        await page.waitForTimeout(1000);
        await goalsButton.click(); // Close
        await page.waitForTimeout(500);
      }

      // Test Flow 3: Tab Switching
      console.log('Testing tab switching...');
      await page.click('button[value="tasks"]');
      await page.waitForTimeout(500);
      await page.click('button[value="ai"]');
      await page.waitForTimeout(500);
      await page.click('button[value="admin"]');
      await page.waitForTimeout(500);
      await page.click('button[value="dashboard"]');
      await page.waitForTimeout(500);

      // Test Flow 4: Multiple Modal Operations
      console.log('Testing multiple modals...');
      await page.click('button[value="tasks"]');
      await page.waitForTimeout(500);
      
      const addTaskButton = await page.locator('button:has-text("Add Task")').first();
      if (await addTaskButton.isVisible()) {
        await addTaskButton.click();
        await page.waitForTimeout(1000);
        await page.press('body', 'Escape');
        await page.waitForTimeout(500);
      }

    } catch (error) {
      console.error(`Error during ${name} testing:`, error.message);
    }

    results.browsers[name] = {
      totalErrors: consoleErrors.length,
      errors: consoleErrors,
      testCompleted: true
    };

    console.log(`${name} - ResizeObserver Errors Found: ${consoleErrors.length}`);
    consoleErrors.forEach((error, index) => {
      console.log(`  ${index + 1}. ${error.text}`);
    });

    await browserInstance.close();
  }

  // Save results
  const fs = require('fs');
  fs.writeFileSync('/app/resizeobserver_before_results.json', JSON.stringify(results, null, 2));
  
  console.log('\n=== BEFORE FIX SUMMARY ===');
  Object.entries(results.browsers).forEach(([browser, data]) => {
    console.log(`${browser}: ${data.totalErrors} ResizeObserver errors`);
  });

  return results;
}

// Run the test
if (require.main === module) {
  testResizeObserverErrors().catch(console.error);
}

module.exports = { testResizeObserverErrors };