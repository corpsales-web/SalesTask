// Global teardown for Playwright tests
const fs = require('fs');
const path = require('path');

async function globalTeardown(config) {
  console.log('🧹 Cleaning up test environment...');
  
  try {
    // Generate test summary report
    const reportsDir = path.join(__dirname, '../reports');
    const testResultsFile = path.join(reportsDir, 'test-results.json');
    
    if (fs.existsSync(testResultsFile)) {
      const results = JSON.parse(fs.readFileSync(testResultsFile, 'utf8'));
      
      console.log('📊 Test Summary:');
      console.log(`   Total Tests: ${results.stats?.total || 'N/A'}`);
      console.log(`   Passed: ${results.stats?.passed || 'N/A'}`);
      console.log(`   Failed: ${results.stats?.failed || 'N/A'}`);
      console.log(`   Skipped: ${results.stats?.skipped || 'N/A'}`);
      console.log(`   Duration: ${results.stats?.duration || 'N/A'}ms`);
    }
    
    // Archive old logs and reports
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const archiveDir = path.join(__dirname, '../archives', timestamp);
    
    if (fs.existsSync(reportsDir)) {
      fs.mkdirSync(archiveDir, { recursive: true });
      
      // Move reports to archive
      const reportFiles = fs.readdirSync(reportsDir);
      reportFiles.forEach(file => {
        const srcPath = path.join(reportsDir, file);
        const destPath = path.join(archiveDir, file);
        if (fs.statSync(srcPath).isFile()) {
          fs.copyFileSync(srcPath, destPath);
        }
      });
      
      console.log(`📦 Reports archived to: ${archiveDir}`);
    }
    
    // Clean up temporary files
    const tempFiles = [
      path.join(__dirname, '../temp'),
      path.join(__dirname, '../.cache')
    ];
    
    tempFiles.forEach(tempPath => {
      if (fs.existsSync(tempPath)) {
        fs.rmSync(tempPath, { recursive: true, force: true });
        console.log(`🗑️ Cleaned up: ${tempPath}`);
      }
    });
    
    // Generate CI/CD friendly output
    if (process.env.CI) {
      const summary = {
        timestamp: new Date().toISOString(),
        environment: 'test',
        status: 'completed',
        artifacts: {
          reports: fs.existsSync(reportsDir) ? fs.readdirSync(reportsDir) : [],
          logs: fs.existsSync(path.join(__dirname, '../logs')) ? fs.readdirSync(path.join(__dirname, '../logs')) : []
        }
      };
      
      fs.writeFileSync(
        path.join(__dirname, '../reports/test-summary.json'),
        JSON.stringify(summary, null, 2)
      );
      
      console.log('🏗️ CI/CD artifacts prepared');
    }
    
    console.log('✅ Test environment cleanup complete!');
    
  } catch (error) {
    console.error('❌ Global teardown failed:', error);
    // Don't throw error in teardown to avoid masking test failures
  }
}

module.exports = globalTeardown;