const puppeteer = require('puppeteer');

const BASE_URL = 'http://localhost:3000';
const CREDENTIALS = {
  kailash_code: '<REDACTED_kailash_code>',
  password: '<REDACTED_PASSWORD>',
  two_factor: '123456'
};

const ROUTES_TO_TEST = [
  { path: '/dashboard', name: 'Dashboard' },
  { path: '/kailash', name: 'KAILASH Command' },
  { path: '/dashboard/executive', name: 'Executive Dashboard' },
  { path: '/ganesha-analytics', name: 'Analytics Dashboard' },
  { path: '/departments', name: 'Departments' },
  { path: '/department/ganesha', name: 'GANESHA Detail' },
  { path: '/department/prajapati', name: 'PRAJAPATI Detail' },
  { path: '/department/chitragupta', name: 'CHITRAGUPTA Detail' },
  { path: '/ganesha-v2', name: 'GANESHA Chat' }
];

async function login(page) {
  console.log('🔐 Logging in...');
  await page.goto(BASE_URL);
  await page.waitForSelector('input[name="kailash_code"], input[placeholder*="Kailash"]', { timeout: 5000 });
  
  await page.type('input[name="kailash_code"], input[placeholder*="Kailash"]', CREDENTIALS.kailash_code);
  await page.type('input[name="password"], input[type="password"]', CREDENTIALS.password);
  
  await page.click('button[type="submit"]');
  await page.waitForTimeout(2000);
  
  const has2FA = await page.$('input[placeholder*="2FA"], input[placeholder*="code"]');
  if (has2FA) {
    await page.type('input[placeholder*="2FA"], input[placeholder*="code"]', CREDENTIALS.two_factor);
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);
  }
  
  console.log('✅ Login successful');
}

async function testRoute(page, route) {
  try {
    console.log(`\n📍 Testing: ${route.name} (${route.path})`);
    await page.goto(BASE_URL + route.path, { waitUntil: 'networkidle0', timeout: 10000 });
    
    const title = await page.title();
    const hasError = await page.$('text/error, text/Error, text/404');
    
    if (hasError) {
      console.log(`❌ ${route.name}: Error found on page`);
      return { route: route.name, status: 'FAIL', error: 'Error message on page' };
    }
    
    console.log(`✅ ${route.name}: Loaded successfully`);
    return { route: route.name, status: 'PASS', title };
  } catch (error) {
    console.log(`❌ ${route.name}: ${error.message}`);
    return { route: route.name, status: 'FAIL', error: error.message };
  }
}

async function runTests() {
  console.log('🚀 Starting Comprehensive Frontend Tests\n');
  
  const browser = await puppeteer.launch({ 
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });
  
  const results = [];
  
  try {
    await login(page);
    
    for (const route of ROUTES_TO_TEST) {
      const result = await testRoute(page, route);
      results.push(result);
      await page.waitForTimeout(1000);
    }
  } catch (error) {
    console.error('❌ Test suite error:', error.message);
  } finally {
    await browser.close();
  }
  
  console.log('\n' + '='.repeat(60));
  console.log('📊 TEST RESULTS SUMMARY');
  console.log('='.repeat(60));
  
  const passed = results.filter(r => r.status === 'PASS').length;
  const failed = results.filter(r => r.status === 'FAIL').length;
  
  results.forEach(r => {
    const icon = r.status === 'PASS' ? '✅' : '❌';
    console.log(`${icon} ${r.route}: ${r.status}`);
    if (r.error) console.log(`   Error: ${r.error}`);
  });
  
  console.log('\n' + '='.repeat(60));
  console.log(`Total: ${results.length} | Passed: ${passed} | Failed: ${failed}`);
  console.log(`Success Rate: ${((passed/results.length)*100).toFixed(1)}%`);
  console.log('='.repeat(60));
  
  process.exit(failed > 0 ? 1 : 0);
}

runTests();
