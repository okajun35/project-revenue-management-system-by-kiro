// global-setup.js
const { chromium } = require('@playwright/test');

async function globalSetup(config) {
  console.log('Starting global setup for frontend tests...');
  
  // Initialize test database
  const { spawn } = require('child_process');
  
  return new Promise((resolve, reject) => {
    const initDb = spawn('python', ['init_db.py'], {
      env: { ...process.env, FLASK_ENV: 'testing' }
    });
    
    initDb.on('close', (code) => {
      if (code === 0) {
        console.log('Test database initialized successfully');
        resolve();
      } else {
        console.error('Failed to initialize test database');
        reject(new Error(`Database initialization failed with code ${code}`));
      }
    });
    
    initDb.on('error', (error) => {
      console.error('Error initializing test database:', error);
      reject(error);
    });
  });
}

module.exports = globalSetup;