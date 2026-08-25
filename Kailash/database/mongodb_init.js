// MongoDB Initialization Script for Kailash - KAILASH AI
// This script sets up the database with all required collections, indexes, and initial data

print("=================================================");
print("Kailash - MongoDB Initialization Script");
print("Database: kailash");
print("=================================================");
print("");

// Switch to the application database
db = db.getSiblingDB('kailash');

// Function to create collection if it doesn't exist
function ensureCollection(collectionName) {
    const collections = db.getCollectionNames();
    if (!collections.includes(collectionName)) {
        db.createCollection(collectionName);
        print("✅ Created collection: " + collectionName);
    } else {
        print("ℹ️  Collection exists: " + collectionName);
    }
}

// Function to create index if it doesn't exist
function ensureIndex(collection, indexSpec, options) {
    const indexName = options.name || Object.keys(indexSpec).join("_");
    try {
        db[collection].createIndex(indexSpec, options);
        print("  ✅ Index: " + indexName);
    } catch (e) {
        if (e.code === 85 || e.code === 86) { // Index already exists
            print("  ℹ️  Index exists: " + indexName);
        } else {
            print("  ❌ Error creating index " + indexName + ": " + e.message);
        }
    }
}

print("Step 1: Creating Collections");
print("------------------------------");
const collections = [
    'users',
    'departments', 
    'tasks',
    'ganesha_commands',
    'activities',
    'conversations',
    'analytics_data',
    'system_health',
    'notifications',
    'audit_logs'
];

collections.forEach(col => ensureCollection(col));
print("");

print("Step 2: Creating Indexes");
print("-------------------------");

// Users collection indexes
print("Collection: users");
ensureIndex('users', { email: 1 }, { unique: true, name: "email_1" });
ensureIndex('users', { kailash_code: 1 }, { unique: true, name: "kailash_code_1" });
ensureIndex('users', { is_active: 1 }, { name: "is_active_1" });
ensureIndex('users', { role: 1 }, { name: "role_1" });

// Departments collection indexes
print("Collection: departments");
ensureIndex('departments', { id: 1 }, { unique: true, name: "id_1" });
ensureIndex('departments', { status: 1 }, { name: "status_1" });
ensureIndex('departments', { name: 1 }, { name: "name_1" });

// Tasks collection indexes
print("Collection: tasks");
ensureIndex('tasks', { status: 1 }, { name: "status_1" });
ensureIndex('tasks', { assigned_department: 1 }, { name: "assigned_department_1" });
ensureIndex('tasks', { priority: 1 }, { name: "priority_1" });
ensureIndex('tasks', { created_at: -1 }, { name: "created_at_-1" });
ensureIndex('tasks', { created_by: 1 }, { name: "created_by_1" });

// GANESHA commands collection indexes
print("Collection: ganesha_commands");
ensureIndex('ganesha_commands', { user_id: 1 }, { name: "user_id_1" });
ensureIndex('ganesha_commands', { processing_status: 1 }, { name: "processing_status_1" });
ensureIndex('ganesha_commands', { created_at: -1 }, { name: "created_at_-1" });

// Activities collection indexes
print("Collection: activities");
ensureIndex('activities', { type: 1 }, { name: "type_1" });
ensureIndex('activities', { created_at: -1 }, { name: "created_at_-1" });
ensureIndex('activities', { user_id: 1 }, { name: "user_id_1" });
ensureIndex('activities', { department: 1 }, { name: "department_1" });

// Conversations collection indexes
print("Collection: conversations");
ensureIndex('conversations', { user_id: 1 }, { name: "user_id_1" });
ensureIndex('conversations', { created_at: -1 }, { name: "created_at_-1" });
ensureIndex('conversations', { status: 1 }, { name: "status_1" });

// Analytics data collection indexes
print("Collection: analytics_data");
ensureIndex('analytics_data', { timestamp: -1 }, { name: "timestamp_-1" });
ensureIndex('analytics_data', { metric_type: 1 }, { name: "metric_type_1" });
ensureIndex('analytics_data', { department: 1 }, { name: "department_1" });

// System health collection indexes
print("Collection: system_health");
ensureIndex('system_health', { timestamp: -1 }, { name: "timestamp_-1" });
ensureIndex('system_health', { status: 1 }, { name: "status_1" });

// Notifications collection indexes
print("Collection: notifications");
ensureIndex('notifications', { user_id: 1 }, { name: "user_id_1" });
ensureIndex('notifications', { is_read: 1 }, { name: "is_read_1" });
ensureIndex('notifications', { created_at: -1 }, { name: "created_at_-1" });

// Audit logs collection indexes
print("Collection: audit_logs");
ensureIndex('audit_logs', { user_id: 1 }, { name: "user_id_1" });
ensureIndex('audit_logs', { action: 1 }, { name: "action_1" });
ensureIndex('audit_logs', { timestamp: -1 }, { name: "timestamp_-1" });

print("");

print("Step 3: Database Statistics");
print("----------------------------");
const stats = db.stats();
print("Database: " + stats.db);
print("Collections: " + stats.collections);
print("Data Size: " + (stats.dataSize / 1024 / 1024).toFixed(2) + " MB");
print("Storage Size: " + (stats.storageSize / 1024 / 1024).toFixed(2) + " MB");
print("Indexes: " + stats.indexes);
print("Index Size: " + (stats.indexSize / 1024 / 1024).toFixed(2) + " MB");
print("");

print("Step 4: Collection Document Counts");
print("------------------------------------");
db.getCollectionNames().forEach(col => {
    const count = db[col].countDocuments();
    print(col + ": " + count + " documents");
});
print("");

print("=================================================");
print("✅ MongoDB initialization complete!");
print("=================================================");
print("");
print("Next steps:");
print("1. Verify application connection");
print("2. Test authentication endpoints");
print("3. Run application health check");
print("");
