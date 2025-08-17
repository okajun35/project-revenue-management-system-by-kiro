// global-teardown.js
async function globalTeardown(config) {
  console.log('Starting global teardown for frontend tests...');
  
  // Clean up test database and temporary files
  const fs = require('fs');
  const path = require('path');
  
  try {
    // Remove test database if it exists
    const testDbPath = 'test_frontend.db';
    if (fs.existsSync(testDbPath)) {
      fs.unlinkSync(testDbPath);
      console.log('Test database cleaned up');
    }
    
    // Clean up old screenshots (keep only last 10 runs)
    const screenshotsDir = path.join(__dirname, '../reports/screenshots');
    if (fs.existsSync(screenshotsDir)) {
      const files = fs.readdirSync(screenshotsDir)
        .map(file => ({
          name: file,
          path: path.join(screenshotsDir, file),
          time: fs.statSync(path.join(screenshotsDir, file)).mtime.getTime()
        }))
        .sort((a, b) => b.time - a.time);
      
      // Keep only the 50 most recent files
      const filesToDelete = files.slice(50);
      filesToDelete.forEach(file => {
        try {
          fs.unlinkSync(file.path);
        } catch (error) {
          console.warn(`Could not delete ${file.name}:`, error.message);
        }
      });
      
      if (filesToDelete.length > 0) {
        console.log(`Cleaned up ${filesToDelete.length} old screenshot files`);
      }
    }
    
    console.log('Global teardown completed successfully');
  } catch (error) {
    console.error('Error during global teardown:', error);
  }
}

module.exports = globalTeardown;