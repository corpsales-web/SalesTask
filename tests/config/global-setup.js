// Global setup for Playwright tests
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

async function globalSetup(config) {
  console.log('🚀 Setting up test environment...');
  
  try {
    // Ensure backend is running
    console.log('✅ Checking backend service...');
    const { stdout: backendStatus } = await execAsync('sudo supervisorctl status backend');
    console.log('Backend status:', backendStatus);
    
    // Ensure frontend is running  
    console.log('✅ Checking frontend service...');
    const { stdout: frontendStatus } = await execAsync('sudo supervisorctl status frontend');
    console.log('Frontend status:', frontendStatus);
    
    // Wait for services to be ready
    console.log('⏳ Waiting for services to be ready...');
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Verify API connectivity
    const axios = require('axios');
    const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
    
    try {
      const response = await axios.get(`${backendUrl}/api/dashboard/stats`, { timeout: 10000 });
      console.log('✅ Backend API responding');
    } catch (error) {
      console.log('⚠️ Backend API not responding, tests may use mock data');
    }
    
    // Create test directories
    const fs = require('fs');
    const path = require('path');
    
    const directories = [
      'tests/reports',
      'tests/logs', 
      'tests/screenshots',
      'tests/videos'
    ];
    
    directories.forEach(dir => {
      const fullPath = path.join(__dirname, '../../', dir);
      if (!fs.existsSync(fullPath)) {
        fs.mkdirSync(fullPath, { recursive: true });
        console.log(`✅ Created directory: ${dir}`);
      }
    });
    
    console.log('🎉 Test environment setup complete!');
    
  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  }
}

module.exports = globalSetup;