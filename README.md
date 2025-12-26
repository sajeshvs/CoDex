# M365 Entra ID User Management System

**Global Admin:** `sajesh.admin@mvlgroupusa.onmicrosoft.com`

## 📋 Overview

This repository contains tools and scripts for managing Microsoft 365 / Entra ID (formerly Azure AD) user accounts and groups.

## 🚀 Quick Start

1. **Setup Azure AD App Registration** (one-time setup)
   - Follow the detailed instructions in [SETUP_GUIDE.md](SETUP_GUIDE.md)
   - You'll need Global Admin access to grant API permissions

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.template .env
   # Edit .env with your actual credentials
   ```

4. **Extract User & Group Information**
   ```bash
   python entra_user_extractor.py
   ```

## 📁 Files in This Repository

### Configuration Files
- **`.env.template`** - Template for environment variables (copy to `.env`)
- **`.gitignore`** - Prevents sensitive files from being committed
- **`requirements.txt`** - Python package dependencies

### Scripts
- **`entra_user_extractor.py`** - Main script to extract user schema, attributes, and group information from Entra ID

### Documentation
- **`SETUP_GUIDE.md`** - Comprehensive setup and troubleshooting guide
- **`user_creation_template.json`** - JSON template for creating new users

### Generated Output (after running extraction)
- **`entra_id_extraction.json`** - Raw JSON data with all extracted information
- **`ENTRA_ID_REPORT.md`** - Human-readable markdown report

## 🎯 Features

### ✅ User Schema Extraction
- Retrieves all standard user attributes (required and optional)
- Identifies custom schema extensions
- Documents data types and descriptions for each field

### ✅ Group Information
- Lists all groups in the organization
- Includes group types (Microsoft 365, Security, Distribution)
- Shows membership counts and sample members
- Displays dynamic membership rules (if applicable)

### ✅ Sample Users
- Retrieves sample users to show attributes actually in use
- Helps identify which optional fields are commonly populated

### ✅ User Creation Requirements
- Documents minimum required fields for new user creation
- Lists recommended fields for complete user profiles
- Provides password policy information

## 📊 User Creation Requirements

### Minimum Required Fields
1. **accountEnabled** (boolean) - Whether the account is enabled
2. **displayName** (string) - Name shown in address book
3. **mailNickname** (string) - Mail alias
4. **userPrincipalName** (string) - User login (user@domain.com)
5. **passwordProfile** (object) - Password and settings

### Recommended Fields
- givenName, surname (first/last name)
- jobTitle, department
- usageLocation (required for license assignment)
- employeeId
- businessPhones, mobilePhone
- Office location and address fields

See [user_creation_template.json](user_creation_template.json) for a complete example.

## 🔐 Security

- All credentials are stored in `.env` (excluded from git)
- Uses Azure AD App Registration with least-privilege permissions
- Supports both client secret and certificate authentication
- All API calls use HTTPS

## 📖 API Permissions Required

The Azure AD app registration needs these Microsoft Graph **Application permissions**:

- `User.Read.All` - Read all users' full profiles
- `Group.Read.All` - Read all groups
- `Directory.Read.All` - Read directory data
- `GroupMember.Read.All` - Read group memberships

**Note:** These are read-only permissions. No write operations are performed.

## 🛠️ Troubleshooting

See [SETUP_GUIDE.md](SETUP_GUIDE.md#troubleshooting) for common issues and solutions.

### Quick Checks
- ✅ Verify `.env` file exists with correct credentials
- ✅ Ensure API permissions are granted with admin consent
- ✅ Check that client secret hasn't expired
- ✅ Confirm you're using the correct tenant ID

## 📚 Additional Resources

- [Microsoft Graph API Documentation](https://learn.microsoft.com/en-us/graph/overview)
- [User Resource Type Reference](https://learn.microsoft.com/en-us/graph/api/resources/user)
- [Azure AD App Registration Guide](https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)

## 🔄 Workflow

```
┌─────────────────────────────────────────────┐
│  1. Setup Azure AD App Registration        │
│     - Create app in Azure Portal           │
│     - Grant API permissions                │
│     - Generate client secret               │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  2. Configure Environment                   │
│     - Copy .env.template to .env           │
│     - Add credentials                       │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  3. Run Extraction Script                   │
│     python entra_user_extractor.py         │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  4. Review Output                           │
│     - entra_id_extraction.json (raw)       │
│     - ENTRA_ID_REPORT.md (readable)        │
└─────────────────────────────────────────────┘
```

## 👤 Contact

**Global Admin:** sajesh.admin@mvlgroupusa.onmicrosoft.com

---

**Repository Branch:** `claude/setup-m365-admin-B1hzt`
