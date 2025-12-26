# Microsoft 365 / Entra ID Setup Guide

This guide will help you set up the M365 Entra ID user and group extraction tool.

## Prerequisites

- Python 3.8 or higher
- M365 Global Admin access: `sajesh.admin@mvlgroupusa.onmicrosoft.com`
- Azure AD App Registration (see below)

---

## Step 1: Azure AD App Registration

You need to create an App Registration in Azure AD to allow the script to access Microsoft Graph API.

### 1.1 Create App Registration

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations** → **New registration**
3. Fill in the details:
   - **Name:** `Entra ID User Extractor` (or any name you prefer)
   - **Supported account types:** `Accounts in this organizational directory only`
   - **Redirect URI:** Leave blank
4. Click **Register**

### 1.2 Note the Application (client) ID and Directory (tenant) ID

After registration, you'll see the **Overview** page:
- Copy the **Application (client) ID** → This is your `CLIENT_ID`
- Copy the **Directory (tenant) ID** → This is your `TENANT_ID`

### 1.3 Create a Client Secret

1. In the app registration, go to **Certificates & secrets** → **Client secrets** → **New client secret**
2. Add a description: `Entra ID Extractor Secret`
3. Choose an expiration period (recommended: 24 months)
4. Click **Add**
5. **IMPORTANT:** Copy the **Value** immediately → This is your `CLIENT_SECRET`
   - ⚠️ You won't be able to see it again after you leave this page!

### 1.4 Grant API Permissions

1. Go to **API permissions** → **Add a permission** → **Microsoft Graph** → **Application permissions**
2. Add the following permissions:
   - `User.Read.All` - Read all users' full profiles
   - `Group.Read.All` - Read all groups
   - `Directory.Read.All` - Read directory data
   - `GroupMember.Read.All` - Read group memberships
3. Click **Add permissions**
4. **CRITICAL:** Click **Grant admin consent for [Your Organization]**
   - You need Global Admin privileges to do this
   - Wait for the status to change to "✅ Granted"

---

## Step 2: Install Dependencies

### 2.1 Create a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2.2 Install Required Packages

```bash
pip install -r requirements.txt
```

---

## Step 3: Configure Environment Variables

### 3.1 Copy the Template

```bash
cp .env.template .env
```

### 3.2 Edit .env File

Open `.env` and fill in your actual values:

```bash
# Azure AD Application Registration Details
TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CLIENT_SECRET=your-client-secret-value-here

# Global Admin Account
ADMIN_EMAIL=sajesh.admin@mvlgroupusa.onmicrosoft.com

# Microsoft Graph API Configuration
GRAPH_API_ENDPOINT=https://graph.microsoft.com/v1.0
GRAPH_SCOPE=https://graph.microsoft.com/.default
```

**⚠️ SECURITY WARNING:**
- Never commit the `.env` file to version control
- The `.gitignore` file is configured to exclude it
- Keep your `CLIENT_SECRET` secure

---

## Step 4: Run the Extraction Script

```bash
python entra_user_extractor.py
```

### What the Script Does

1. ✅ Connects to Microsoft Graph API using your app registration
2. 📋 Retrieves the complete user schema with all attributes
3. 👥 Extracts all groups and their membership information
4. 👤 Gets sample users to show actual attributes in use
5. 💾 Saves raw data to `entra_id_extraction.json`
6. 📄 Generates a human-readable report in `ENTRA_ID_REPORT.md`

### Expected Output

```
============================================================
🚀 Starting Entra ID Information Extraction
============================================================

📋 Retrieving user schema from Entra ID...
👥 Retrieving all groups from Entra ID...
✅ Retrieved 15 groups
👤 Retrieving 5 sample users to see actual attributes...
✅ Retrieved 5 sample users

📊 Retrieving group membership details...

💾 Saving results to entra_id_extraction.json...
✅ Results saved successfully

📄 Generating markdown report: ENTRA_ID_REPORT.md...
✅ Markdown report generated successfully

============================================================
✅ Extraction Complete!
============================================================

📁 Output Files:
  - entra_id_extraction.json (raw data)
  - ENTRA_ID_REPORT.md (human-readable report)
```

---

## Step 5: Review the Results

### Output Files

1. **entra_id_extraction.json**
   - Raw JSON data with all extracted information
   - Machine-readable format for further processing
   - Includes timestamps and metadata

2. **ENTRA_ID_REPORT.md**
   - Human-readable markdown report
   - Contains:
     - ✅ User creation requirements (required & recommended fields)
     - 📚 Complete attribute schema with descriptions
     - 👥 All groups with membership details
     - 👤 Sample users showing actual attributes in use
     - 🔧 JSON example for creating a new user

---

## Troubleshooting

### Common Issues

#### 1. Authentication Errors

**Error:** `Missing required credentials`
- **Solution:** Ensure `.env` file exists and contains all required values

#### 2. Permission Denied

**Error:** `Insufficient privileges to complete the operation`
- **Solution:**
  - Verify that API permissions are granted in Azure AD
  - Ensure you clicked "Grant admin consent"
  - Wait a few minutes for permissions to propagate

#### 3. 401 Unauthorized

**Error:** `401 Unauthorized`
- **Solution:**
  - Verify `TENANT_ID`, `CLIENT_ID`, and `CLIENT_SECRET` are correct
  - Check if the client secret has expired
  - Ensure the app registration is in the correct tenant

#### 4. Network/Timeout Issues

- **Solution:** Check your internet connection and firewall settings

---

## Security Best Practices

1. ✅ **Never commit `.env` to version control**
2. ✅ **Rotate client secrets periodically** (every 6-12 months)
3. ✅ **Use certificate-based auth in production** (more secure than secrets)
4. ✅ **Limit API permissions** to only what's needed
5. ✅ **Review app registration regularly** for unused apps

---

## Next Steps

After extraction, you can use the data to:

1. 📊 **Analyze user attributes** currently in use
2. 👥 **Document group structure** and membership
3. 🔧 **Develop user provisioning automation**
4. 🔄 **Plan migration or integration** projects
5. 📋 **Create user onboarding templates**

---

## Additional Resources

- [Microsoft Graph API Documentation](https://learn.microsoft.com/en-us/graph/overview)
- [User Resource Type](https://learn.microsoft.com/en-us/graph/api/resources/user)
- [Group Resource Type](https://learn.microsoft.com/en-us/graph/api/resources/group)
- [Azure AD App Registration Guide](https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)

---

## Support

For issues or questions:
- Review the output logs for error messages
- Check Azure AD audit logs for API access attempts
- Verify all prerequisites are met

**Admin Contact:** sajesh.admin@mvlgroupusa.onmicrosoft.com
