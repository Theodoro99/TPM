# PreventPlus Database Schema Design

## Overview

This document outlines the detailed database schema for the PreventPlus application. The schema is designed to efficiently store and retrieve all data required for the technical intervention logbook system while maintaining data integrity, security, and performance.

## Entity Relationship Diagram

```
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│     Users     │       │   Logbook     │       │  Attachments  │
│               │       │   Entries     │       │               │
│ PK: user_id   │       │ PK: entry_id  │       │ PK: attach_id │
│               │◄──────┤ FK: user_id   │◄──────┤ FK: entry_id  │
└───────────────┘       └───────────────┘       └───────────────┘
        ▲                       ▲                       ▲
        │                       │                       │
        │                       │                       │
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│    Roles      │       │   Locations   │       │   Categories  │
│               │       │               │       │               │
│ PK: role_id   │       │ PK: location_id│      │ PK: category_id│
│               │       │               │       │               │
└───────────────┘       └───────────────┘       └───────────────┘
```

## Table Definitions

### Users

Stores information about system users including authentication details and role assignments.

| Column Name     | Data Type      | Constraints       | Description                           |
|-----------------|----------------|-------------------|---------------------------------------|
| user_id         | UUID           | PK, NOT NULL      | Unique identifier for the user        |
| username        | VARCHAR(50)    | UNIQUE, NOT NULL  | Username for login                    |
| email           | VARCHAR(100)   | UNIQUE, NOT NULL  | Email address                         |
| password_hash   | VARCHAR(255)   | NOT NULL          | Bcrypt hashed password                |
| full_name       | VARCHAR(100)   | NOT NULL          | User's full name                      |
| role_id         | INT            | FK, NOT NULL      | Reference to Roles table              |
| department      | VARCHAR(100)   |                   | User's department                     |
| phone_number    | VARCHAR(20)    |                   | Contact phone number                  |
| is_active       | BOOLEAN        | DEFAULT TRUE      | Whether user account is active        |
| created_at      | TIMESTAMP      | DEFAULT NOW()     | Account creation timestamp            |
| updated_at      | TIMESTAMP      | DEFAULT NOW()     | Last update timestamp                 |
| last_login      | TIMESTAMP      |                   | Last successful login timestamp       |
| failed_attempts | INT            | DEFAULT 0         | Count of failed login attempts        |
| reset_token     | VARCHAR(255)   |                   | Password reset token                  |
| token_expiry    | TIMESTAMP      |                   | Expiration time for reset token       |

### Roles

Defines user roles and their associated permissions.

| Column Name     | Data Type      | Constraints       | Description                           |
|-----------------|----------------|-------------------|---------------------------------------|
| role_id         | INT            | PK, NOT NULL      | Unique identifier for the role        |
| role_name       | VARCHAR(50)    | UNIQUE, NOT NULL  | Name of the role (Admin, Manager, etc)|
| description     | TEXT           |                   | Description of role permissions       |
| created_at      | TIMESTAMP      | DEFAULT NOW()     | Creation timestamp                    |
| updated_at      | TIMESTAMP      | DEFAULT NOW()     | Last update timestamp                 |

### LogbookEntries

Core table storing all technical intervention records.

| Column Name         | Data Type      | Constraints       | Description                           |
|--------------------|----------------|-------------------|---------------------------------------|
| entry_id           | UUID           | PK, NOT NULL      | Unique identifier for the entry       |
| user_id            | UUID           | FK, NOT NULL      | Reference to Users table              |
| start_date         | DATE           | NOT NULL          | Date when intervention started        |
| end_date           | DATE           |                   | Date when intervention completed      |
| responsible_person | VARCHAR(100)   | NOT NULL          | Name of person responsible            |
| location_id        | INT            | FK, NOT NULL      | Reference to Locations table          |
| device             | VARCHAR(100)   | NOT NULL          | Device/machine name                   |
| call_description   | TEXT           | NOT NULL          | Description of the problem/call       |
| solution_description| TEXT          |                   | Description of the solution applied   |
| status             | VARCHAR(20)    | NOT NULL          | Status (Open, Completed, Escalation)  |
| downtime_hours     | DECIMAL(10,2)  |                   | Downtime duration in hours            |
| category_id        | INT            | FK                | Reference to Categories table         |
| priority           | VARCHAR(20)    |                   | Priority level (Low, Medium, High)    |
| created_at         | TIMESTAMP      | DEFAULT NOW()     | Record creation timestamp             |
| updated_at         | TIMESTAMP      | DEFAULT NOW()     | Last update timestamp                 |
| completed_by       | UUID           | FK                | User who completed the intervention   |
| is_deleted         | BOOLEAN        | DEFAULT FALSE     | Soft delete flag                      |

### Attachments

Stores metadata for files attached to logbook entries.

| Column Name     | Data Type      | Constraints       | Description                           |
|-----------------|----------------|-------------------|---------------------------------------|
| attach_id       | UUID           | PK, NOT NULL      | Unique identifier for the attachment  |
| entry_id        | UUID           | FK, NOT NULL      | Reference to LogbookEntries table     |
| file_name       | VARCHAR(255)   | NOT NULL          | Original filename                     |
| file_path       | VARCHAR(255)   | NOT NULL          | Path to stored file                   |
| file_type       | VARCHAR(50)    | NOT NULL          | MIME type of the file                 |
| file_size       | INT            | NOT NULL          | Size in bytes                         |
| description     | TEXT           |                   | Optional description of the file      |
| uploaded_by     | UUID           | FK, NOT NULL      | User who uploaded the file            |
| uploaded_at     | TIMESTAMP      | DEFAULT NOW()     | Upload timestamp                      |
| is_deleted      | BOOLEAN        | DEFAULT FALSE     | Soft delete flag                      |

### Locations

Standardized list of locations where interventions can occur.

| Column Name     | Data Type      | Constraints       | Description                           |
|-----------------|----------------|-------------------|---------------------------------------|
| location_id     | INT            | PK, NOT NULL      | Unique identifier for the location    |
| location_name   | VARCHAR(100)   | UNIQUE, NOT NULL  | Name of the location                  |
| description     | TEXT           |                   | Description of the location           |
| parent_id       | INT            | FK                | Parent location (for hierarchical)    |
| created_at      | TIMESTAMP      | DEFAULT NOW()     | Creation timestamp                    |
| updated_at      | TIMESTAMP      | DEFAULT NOW()     | Last update timestamp                 |
| created_by      | UUID           | FK, NOT NULL      | User who created the location         |
| is_active       | BOOLEAN        | DEFAULT TRUE      | Whether location is active            |

### Categories

Categories for classifying intervention types.

| Column Name     | Data Type      | Constraints       | Description                           |
|-----------------|----------------|-------------------|---------------------------------------|
| category_id     | INT            | PK, NOT NULL      | Unique identifier for the category    |
| category_name   | VARCHAR(100)   | UNIQUE, NOT NULL  | Name of the category                  |
| description     | TEXT           |                   | Description of the category           |
| color_code      | VARCHAR(7)     |                   | Color for UI representation           |
| created_at      | TIMESTAMP      | DEFAULT NOW()     | Creation timestamp                    |
| updated_at      | TIMESTAMP      | DEFAULT NOW()     | Last update timestamp                 |
| created_by      | UUID           | FK, NOT NULL      | User who created the category         |
| is_active       | BOOLEAN        | DEFAULT TRUE      | Whether category is active            |

### Settings

System-wide configuration settings.

| Column Name     | Data Type      | Constraints       | Description                           |
|-----------------|----------------|-------------------|---------------------------------------|
| setting_id      | INT            | PK, NOT NULL      | Unique identifier for the setting     |
| setting_key     | VARCHAR(100)   | UNIQUE, NOT NULL  | Setting key name                      |
| setting_value   | TEXT           | NOT NULL          | Setting value                         |
| description     | TEXT           |                   | Description of the setting            |
| is_system       | BOOLEAN        | DEFAULT FALSE     | Whether it's a system setting         |
| created_at      | TIMESTAMP      | DEFAULT NOW()     | Creation timestamp                    |
| updated_at      | TIMESTAMP      | DEFAULT NOW()     | Last update timestamp                 |
| updated_by      | UUID           | FK                | User who last updated the setting     |

### AuditLog

Tracks all significant system actions for security and compliance.

| Column Name     | Data Type      | Constraints       | Description                           |
|-----------------|----------------|-------------------|---------------------------------------|
| log_id          | UUID           | PK, NOT NULL      | Unique identifier for the log entry   |
| user_id         | UUID           | FK, NOT NULL      | User who performed the action         |
| action          | VARCHAR(50)    | NOT NULL          | Type of action performed              |
| entity_type     | VARCHAR(50)    | NOT NULL          | Type of entity affected               |
| entity_id       | VARCHAR(50)    | NOT NULL          | ID of the affected entity             |
| details         | JSONB          |                   | Additional details about the action   |
| ip_address      | VARCHAR(45)    |                   | IP address of the user                |
| user_agent      | TEXT           |                   | User agent information                |
| created_at      | TIMESTAMP      | DEFAULT NOW()     | When the action occurred              |

## Indexes

### Users Table
- Index on `email` (for login lookups)
- Index on `username` (for login lookups)
- Index on `role_id` (for role-based queries)

### LogbookEntries Table
- Index on `user_id` (for filtering by user)
- Index on `start_date` (for date range queries)
- Index on `status` (for filtering by status)
- Index on `location_id` (for filtering by location)
- Index on `device` (for searching by device name)
- Composite index on (`start_date`, `status`) for common queries
- Full-text search index on `call_description` and `solution_description`

### Attachments Table
- Index on `entry_id` (for retrieving attachments for an entry)
- Index on `file_type` (for filtering by file type)

## Constraints

### Foreign Keys
- `Users.role_id` references `Roles.role_id`
- `LogbookEntries.user_id` references `Users.user_id`
- `LogbookEntries.location_id` references `Locations.location_id`
- `LogbookEntries.category_id` references `Categories.category_id`
- `LogbookEntries.completed_by` references `Users.user_id`
- `Attachments.entry_id` references `LogbookEntries.entry_id`
- `Attachments.uploaded_by` references `Users.user_id`
- `Locations.parent_id` references `Locations.location_id`
- `Locations.created_by` references `Users.user_id`
- `Categories.created_by` references `Users.user_id`
- `Settings.updated_by` references `Users.user_id`
- `AuditLog.user_id` references `Users.user_id`

### Check Constraints
- `LogbookEntries.status` must be one of ('Open', 'Completed', 'Escalation')
- `LogbookEntries.priority` must be one of ('Low', 'Medium', 'High')
- `LogbookEntries.downtime_hours` must be >= 0
- `LogbookEntries.end_date` must be >= `start_date` when not null

## Triggers

1. **Updated Timestamp Trigger**
   - Automatically updates the `updated_at` column whenever a record is modified

2. **Audit Log Trigger**
   - Records changes to sensitive tables in the AuditLog table

3. **Soft Delete Trigger**
   - Handles cascading soft deletes for related records

## Initial Data

The database will be initialized with the following data:

### Roles
- Admin: Full system access
- Manager: Access to all logs and limited settings
- Technician: Access to own logs only

### Default Admin User
- Username: admin
- Password: [generated secure password]
- Role: Admin

## Migration Strategy

Database migrations will be managed using Alembic with the following approach:

1. Initial schema creation
2. Incremental schema updates
3. Data migrations from the Excel-based system
4. Ongoing schema evolution

## Performance Considerations

1. **Partitioning**
   - Consider partitioning the LogbookEntries table by date for improved performance with large datasets

2. **Archiving Strategy**
   - Implement a strategy for archiving old entries to maintain performance

3. **Query Optimization**
   - Design queries to utilize indexes effectively
   - Use materialized views for complex reporting queries

## Security Measures

1. **Data Encryption**
   - Sensitive data will be encrypted at rest
   - Password hashes stored using bcrypt

2. **Row-Level Security**
   - Implement PostgreSQL row-level security policies to enforce access control at the database level

3. **Audit Logging**
   - Comprehensive audit logging for all data modifications

## Backup Strategy

1. **Regular Backups**
   - Daily full database backups
   - Hourly incremental backups
   - Point-in-time recovery capability

2. **Retention Policy**
   - Daily backups retained for 30 days
   - Weekly backups retained for 3 months
   - Monthly backups retained for 1 year
