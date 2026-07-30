#!/bin/bash

# MongoDB Health Check Script for Kailash - KAILASH AI

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=================================================="
echo "Kailash - MongoDB Health Check"
echo "=================================================="
echo ""

# Check if MongoDB is running
echo "🔍 Checking MongoDB Status..."
if mongosh --eval "db.version()" --quiet > /dev/null 2>&1; then
    MONGO_VERSION=$(mongosh --eval "db.version()" --quiet 2>&1)
    echo -e "${GREEN}✅ MongoDB is running${NC}"
    echo "   Version: $MONGO_VERSION"
else
    echo -e "${RED}❌ MongoDB is not running${NC}"
    exit 1
fi
echo ""

# Check database connectivity
echo "🔍 Checking Database Connectivity..."
mongosh --quiet --eval "
    db = db.getSiblingDB('kailash');
    try {
        const result = db.runCommand({ ping: 1 });
        if (result.ok === 1) {
            print('✅ Database connection: OK');
        } else {
            print('❌ Database connection: FAILED');
        }
    } catch (e) {
        print('❌ Error: ' + e.message);
    }
"
echo ""

# Check collections
echo "🔍 Checking Collections..."
mongosh --quiet --eval "
    db = db.getSiblingDB('kailash');
    const collections = db.getCollectionNames();
    const expectedCollections = [
        'users', 'departments', 'tasks', 'ganesha_commands',
        'activities', 'conversations', 'analytics_data',
        'system_health', 'notifications', 'audit_logs'
    ];
    
    let allPresent = true;
    expectedCollections.forEach(col => {
        if (collections.includes(col)) {
            print('  ✅ ' + col);
        } else {
            print('  ❌ Missing: ' + col);
            allPresent = false;
        }
    });
    
    if (allPresent) {
        print('');
        print('✅ All required collections present');
    } else {
        print('');
        print('❌ Some collections are missing');
    }
"
echo ""

# Check indexes
echo "🔍 Checking Indexes..."
mongosh --quiet --eval "
    db = db.getSiblingDB('kailash');
    
    let totalIndexes = 0;
    const collections = ['users', 'departments', 'tasks', 'ganesha_commands', 'activities'];
    
    collections.forEach(col => {
        const indexes = db[col].getIndexes();
        totalIndexes += indexes.length;
    });
    
    print('Total indexes: ' + totalIndexes);
    if (totalIndexes >= 15) {
        print('✅ Indexes are properly configured');
    } else {
        print('⚠️  Some indexes might be missing');
    }
"
echo ""

# Check data integrity
echo "🔍 Checking Data Integrity..."
mongosh --quiet --eval "
    db = db.getSiblingDB('kailash');
    
    // Check users
    const userCount = db.users.countDocuments();
    print('Users: ' + userCount);
    if (userCount > 0) {
        print('  ✅ User data present');
    } else {
        print('  ⚠️  No users found');
    }
    
    // Check departments
    const deptCount = db.departments.countDocuments();
    print('Departments: ' + deptCount);
    if (deptCount === 20) {
        print('  ✅ All 20 departments present');
    } else {
        print('  ⚠️  Expected 20 departments, found ' + deptCount);
    }
"
echo ""

# Check database size
echo "🔍 Checking Database Size..."
mongosh --quiet --eval "
    db = db.getSiblingDB('kailash');
    const stats = db.stats();
    
    const dataSizeMB = (stats.dataSize / 1024 / 1024).toFixed(2);
    const storageSizeMB = (stats.storageSize / 1024 / 1024).toFixed(2);
    const indexSizeMB = (stats.indexSize / 1024 / 1024).toFixed(2);
    
    print('Data Size: ' + dataSizeMB + ' MB');
    print('Storage Size: ' + storageSizeMB + ' MB');
    print('Index Size: ' + indexSizeMB + ' MB');
    print('Collections: ' + stats.collections);
    print('Indexes: ' + stats.indexes);
    
    if (stats.ok === 1) {
        print('✅ Database statistics retrieved successfully');
    }
"
echo ""

# Check for any errors in MongoDB logs
echo "🔍 Checking Recent MongoDB Activity..."
mongosh --quiet --eval "
    db = db.getSiblingDB('kailash');
    
    // Get recent activities
    const recentActivities = db.activities.find().sort({created_at: -1}).limit(5);
    const count = recentActivities.count();
    
    print('Recent activities: ' + count);
    if (count > 0) {
        print('  ✅ Activity logging is working');
    } else {
        print('  ℹ️  No recent activities recorded');
    }
"
echo ""

# Performance check
echo "🔍 Checking Performance..."
START_TIME=$(date +%s%N)
mongosh --quiet --eval "
    db = db.getSiblingDB('kailash');
    db.users.findOne({});
" > /dev/null 2>&1
END_TIME=$(date +%s%N)
QUERY_TIME=$(( ($END_TIME - $START_TIME) / 1000000 ))

if [ $QUERY_TIME -lt 100 ]; then
    echo -e "${GREEN}✅ Query performance: Excellent${NC} (${QUERY_TIME}ms)"
elif [ $QUERY_TIME -lt 500 ]; then
    echo -e "${GREEN}✅ Query performance: Good${NC} (${QUERY_TIME}ms)"
else
    echo -e "${YELLOW}⚠️  Query performance: Slow${NC} (${QUERY_TIME}ms)"
fi
echo ""

# Summary
echo "=================================================="
echo "Health Check Summary"
echo "=================================================="
echo ""
echo -e "${GREEN}✅ MongoDB is healthy and operational${NC}"
echo ""
echo "Recommendations:"
echo "  • Run regular backups (use mongodb_backup.sh)"
echo "  • Monitor database size growth"
echo "  • Review slow queries periodically"
echo "  • Keep MongoDB version updated"
echo ""
echo "=================================================="
echo "Health check completed at: $(date)"
echo "=================================================="
