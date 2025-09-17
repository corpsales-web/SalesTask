/**
 * After Fix: Unified ResizeObserver Error Handling Test
 * This test verifies that the unified error handler works across all browsers
 */

const { chromium, firefox, webkit } = require('playwright');

async function testUnifiedResizeObserverHandler() {
  const browsers = [
    { name: 'Chromium', browser: chromium },
    { name: 'Firefox', browser: firefox },
    { name: 'WebKit', browser: webkit }
  ];

  const results = {
    timestamp: new Date().toISOString(),
    afterFix: true,
    unifiedHandler: true,
    browsers: {}
  };

  for (const { name, browser } of browsers) {
    console.log(`\n=== Testing ${name} with Unified Handler ===`);
    
    const browserInstance = await browser.launch();
    const context = await browserInstance.newContext();
    const page = await context.newPage();
    
    // Collect all console messages
    const consoleMessages = [];
    page.on('console', msg => {
      const text = msg.text();
      consoleMessages.push({
        type: msg.type(),
        text,
        timestamp: new Date().toISOString(),
        isResizeObserver: text.includes('ResizeObserver')
      });
    });

    // Collect page errors
    const pageErrors = [];
    page.on('pageerror', error => {
      pageErrors.push({
        message: error.message,
        stack: error.stack,
        timestamp: new Date().toISOString(),
        isResizeObserver: error.message.includes('ResizeObserver')
      });
    });

    try {
      await page.goto('https://green-crm-suite.preview.emergentagent.com');
      await page.waitForTimeout(3000);

      console.log('Testing unified ResizeObserver handler...');

      // Intensive ResizeObserver triggering test
      const testFlows = [
        {
          name: 'Add Lead Modal with Rapid Resizing',
          action: async () => {
            const addLeadBtn = await page.locator('button:has-text("Add Lead")').first();
            if (await addLeadBtn.isVisible()) {
              await addLeadBtn.click();
              await page.waitForTimeout(500);
              
              // Multiple rapid viewport changes
              const viewports = [
                { width: 800, height: 600 },
                { width: 1200, height: 800 },
                { width: 1600, height: 900 },
                { width: 320, height: 568 },
                { width: 1920, height: 1080 }
              ];
              
              for (const viewport of viewports) {
                await page.setViewportSize(viewport);
                await page.waitForTimeout(100);
              }
              
              await page.press('body', 'Escape');
              await page.waitForTimeout(500);
            }
          }
        },
        {
          name: 'Tab Switching with Viewport Changes',
          action: async () => {
            const tabs = ['dashboard', 'leads', 'tasks', 'ai', 'admin'];
            for (const tab of tabs) {
              const tabBtn = await page.locator(`button[value="${tab}"]`);
              if (await tabBtn.isVisible()) {
                await tabBtn.click();
                await page.setViewportSize({ 
                  width: 800 + Math.random() * 400, 
                  height: 600 + Math.random() * 200 
                });
                await page.waitForTimeout(300);
              }
            }
          }
        },
        {
          name: 'Goals Modal with Resizing',
          action: async () => {
            const goalsBtn = await page.locator('.fixed.bottom-6').filter(text => /Goals/i);
            if (await goalsBtn.count() > 0) {
              await goalsBtn.first().click();
              await page.waitForTimeout(500);
              
              // Resize during modal interaction
              await page.setViewportSize({ width: 1024, height: 768 });
              await page.waitForTimeout(300);
              await page.setViewportSize({ width: 1920, height: 1080 });
              await page.waitForTimeout(300);
              
              await goalsBtn.first().click(); // Close
              await page.waitForTimeout(500);
            }
          }
        }
      ];

      // Execute all test flows
      for (const flow of testFlows) {
        console.log(`  Executing: ${flow.name}`);
        try {
          await flow.action();
        } catch (error) {
          console.log(`    Warning: ${flow.name} failed - ${error.message}`);
        }
      }

      // Test unified handler stats (if available)
      const handlerStats = await page.evaluate(() => {
        if (window.resizeObserverErrorHandler) {
          return window.resizeObserverErrorHandler.getStats();
        }
        return null;
      });

    } catch (error) {
      console.error(`Error during ${name} testing:`, error.message);
    }

    // Filter ResizeObserver related messages
    const resizeObserverErrors = consoleMessages.filter(msg => 
      msg.isResizeObserver || 
      (msg.type === 'error' && msg.text.includes('ResizeObserver'))
    );

    const resizeObserverPageErrors = pageErrors.filter(error => error.isResizeObserver);

    results.browsers[name] = {
      totalConsoleMessages: consoleMessages.length,
      resizeObserverConsoleErrors: resizeObserverErrors.length,
      resizeObserverPageErrors: resizeObserverPageErrors.length,
      allConsoleMessages: consoleMessages,
      resizeObserverErrors: [...resizeObserverErrors, ...resizeObserverPageErrors],
      testCompleted: true
    };

    console.log(`${name} Results:`);
    console.log(`  Total console messages: ${consoleMessages.length}`);
    console.log(`  ResizeObserver console errors: ${resizeObserverErrors.length}`);
    console.log(`  ResizeObserver page errors: ${resizeObserverPageErrors.length}`);
    
    if (resizeObserverErrors.length > 0) {
      console.log('  ResizeObserver console errors found:');
      resizeObserverErrors.forEach((error, index) => {
        console.log(`    ${index + 1}. [${error.type}] ${error.text}`);
      });
    }
    
    if (resizeObserverPageErrors.length > 0) {
      console.log('  ResizeObserver page errors found:');
      resizeObserverPageErrors.forEach((error, index) => {
        console.log(`    ${index + 1}. ${error.message}`);
      });
    }

    await browserInstance.close();
  }

  // Save results
  const fs = require('fs');
  fs.writeFileSync('/app/resizeobserver_after_results.json', JSON.stringify(results, null, 2));
  
  console.log('\n=== AFTER FIX SUMMARY ===');
  let totalErrors = 0;
  Object.entries(results.browsers).forEach(([browser, data]) => {
    const browserErrors = data.resizeObserverConsoleErrors + data.resizeObserverPageErrors;
    totalErrors += browserErrors;
    console.log(`${browser}: ${browserErrors} ResizeObserver errors (${data.totalConsoleMessages} total messages)`);
  });
  
  console.log(`\nTotal ResizeObserver errors across all browsers: ${totalErrors}`);
  console.log(totalErrors === 0 ? '✅ SUCCESS: Unified handler is working!' : '❌ FAILURE: ResizeObserver errors still present');

  return results;
}

// Run the test
if (require.main === module) {
  testUnifiedResizeObserverHandler().catch(console.error);
}

module.exports = { testUnifiedResizeObserverHandler };