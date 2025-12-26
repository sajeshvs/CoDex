#!/usr/bin/env python3
"""
Microsoft Entra ID User and Group Information Extractor

This script connects to Microsoft Graph API to retrieve:
- User schema and attributes
- Required fields for user creation
- Group information and membership
- User creation requirements

Admin: sajesh.admin@mvlgroupusa.onmicrosoft.com
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.models.user import User
from msgraph.generated.models.group import Group
import requests

# Load environment variables
load_dotenv()


class EntraIDExtractor:
    """Extracts user and group information from Microsoft Entra ID"""

    def __init__(self):
        """Initialize the Entra ID extractor with credentials"""
        self.tenant_id = os.getenv('TENANT_ID')
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.admin_email = os.getenv('ADMIN_EMAIL', 'sajesh.admin@mvlgroupusa.onmicrosoft.com')

        if not all([self.tenant_id, self.client_id, self.client_secret]):
            raise ValueError(
                "Missing required credentials. Please set TENANT_ID, CLIENT_ID, "
                "and CLIENT_SECRET in your .env file"
            )

        # Initialize credentials
        self.credential = ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret
        )

        # Initialize Graph client
        self.client = GraphServiceClient(credentials=self.credential)
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"

    def get_access_token(self) -> str:
        """Get an access token for Microsoft Graph API"""
        token = self.credential.get_token("https://graph.microsoft.com/.default")
        return token.token

    async def get_user_schema(self) -> Dict[str, Any]:
        """
        Retrieve the user schema from Entra ID

        Returns:
            Dictionary containing user schema information
        """
        print("📋 Retrieving user schema from Entra ID...")

        # Get schema extensions
        token = self.get_access_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        # Get schema extensions
        schema_url = f"{self.graph_endpoint}/schemaExtensions"
        response = requests.get(schema_url, headers=headers)
        schema_extensions = response.json() if response.status_code == 200 else {}

        # Define standard user attributes based on Microsoft Graph User entity
        user_schema = {
            "standard_attributes": {
                "required": [
                    {
                        "name": "accountEnabled",
                        "type": "boolean",
                        "description": "Whether the account is enabled"
                    },
                    {
                        "name": "displayName",
                        "type": "string",
                        "description": "The name displayed in the address book"
                    },
                    {
                        "name": "mailNickname",
                        "type": "string",
                        "description": "The mail alias for the user"
                    },
                    {
                        "name": "userPrincipalName",
                        "type": "string",
                        "description": "The user principal name (user@domain.com)"
                    },
                    {
                        "name": "passwordProfile",
                        "type": "object",
                        "description": "Password profile with password and forceChangePasswordNextSignIn",
                        "properties": {
                            "password": "string (required)",
                            "forceChangePasswordNextSignIn": "boolean (optional)"
                        }
                    }
                ],
                "optional": [
                    {"name": "givenName", "type": "string", "description": "First name"},
                    {"name": "surname", "type": "string", "description": "Last name"},
                    {"name": "jobTitle", "type": "string", "description": "Job title"},
                    {"name": "department", "type": "string", "description": "Department"},
                    {"name": "officeLocation", "type": "string", "description": "Office location"},
                    {"name": "businessPhones", "type": "array[string]", "description": "Business phone numbers"},
                    {"name": "mobilePhone", "type": "string", "description": "Mobile phone number"},
                    {"name": "mail", "type": "string", "description": "SMTP email address"},
                    {"name": "city", "type": "string", "description": "City"},
                    {"name": "state", "type": "string", "description": "State/Province"},
                    {"name": "country", "type": "string", "description": "Country/Region"},
                    {"name": "postalCode", "type": "string", "description": "Postal code"},
                    {"name": "streetAddress", "type": "string", "description": "Street address"},
                    {"name": "usageLocation", "type": "string", "description": "Two-letter country code (ISO 3166)"},
                    {"name": "employeeId", "type": "string", "description": "Employee ID"},
                    {"name": "employeeType", "type": "string", "description": "Employee type"},
                    {"name": "companyName", "type": "string", "description": "Company name"},
                    {"name": "preferredLanguage", "type": "string", "description": "Preferred language (ISO 639-1)"},
                    {"name": "ageGroup", "type": "string", "description": "Age group (minor, notAdult, adult)"},
                    {"name": "consentProvidedForMinor", "type": "string", "description": "Consent for minor"},
                    {"name": "onPremisesImmutableId", "type": "string", "description": "Immutable ID for on-prem sync"},
                ]
            },
            "schema_extensions": schema_extensions.get('value', [])
        }

        return user_schema

    async def get_all_groups(self) -> List[Dict[str, Any]]:
        """
        Retrieve all groups from Entra ID

        Returns:
            List of group dictionaries with details
        """
        print("👥 Retrieving all groups from Entra ID...")

        groups = []
        token = self.get_access_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        # Get all groups with detailed information
        groups_url = f"{self.graph_endpoint}/groups?$select=id,displayName,description,groupTypes,mail,mailEnabled,mailNickname,securityEnabled,visibility,membershipRule,membershipRuleProcessingState"

        while groups_url:
            response = requests.get(groups_url, headers=headers)
            if response.status_code != 200:
                print(f"❌ Error retrieving groups: {response.status_code}")
                print(response.text)
                break

            data = response.json()
            groups.extend(data.get('value', []))
            groups_url = data.get('@odata.nextLink')

        print(f"✅ Retrieved {len(groups)} groups")
        return groups

    async def get_group_members(self, group_id: str) -> List[Dict[str, Any]]:
        """
        Get members of a specific group

        Args:
            group_id: The ID of the group

        Returns:
            List of group members
        """
        token = self.get_access_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        members_url = f"{self.graph_endpoint}/groups/{group_id}/members"
        members = []

        while members_url:
            response = requests.get(members_url, headers=headers)
            if response.status_code != 200:
                break

            data = response.json()
            members.extend(data.get('value', []))
            members_url = data.get('@odata.nextLink')

        return members

    async def get_sample_users(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve sample users to see actual attributes in use

        Args:
            limit: Number of sample users to retrieve

        Returns:
            List of user dictionaries
        """
        print(f"👤 Retrieving {limit} sample users to see actual attributes...")

        token = self.get_access_token()
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        users_url = f"{self.graph_endpoint}/users?$top={limit}"
        response = requests.get(users_url, headers=headers)

        if response.status_code != 200:
            print(f"❌ Error retrieving users: {response.status_code}")
            return []

        users = response.json().get('value', [])
        print(f"✅ Retrieved {len(users)} sample users")
        return users

    async def extract_all_information(self) -> Dict[str, Any]:
        """
        Extract all user and group information from Entra ID

        Returns:
            Comprehensive dictionary with all extracted information
        """
        print("\n" + "="*60)
        print("🚀 Starting Entra ID Information Extraction")
        print("="*60 + "\n")

        # Extract all information
        user_schema = await self.get_user_schema()
        groups = await self.get_all_groups()
        sample_users = await self.get_sample_users(limit=5)

        # Get group membership details for each group
        print("\n📊 Retrieving group membership details...")
        for group in groups:
            members = await self.get_group_members(group['id'])
            group['member_count'] = len(members)
            group['members_sample'] = members[:5]  # First 5 members as sample

        # Compile results
        results = {
            "extraction_timestamp": datetime.utcnow().isoformat(),
            "admin_account": self.admin_email,
            "tenant_id": self.tenant_id,
            "user_schema": user_schema,
            "groups": {
                "total_count": len(groups),
                "groups_list": groups
            },
            "sample_users": sample_users,
            "user_creation_requirements": {
                "minimum_required_fields": [
                    "accountEnabled",
                    "displayName",
                    "mailNickname",
                    "userPrincipalName",
                    "passwordProfile"
                ],
                "recommended_fields": [
                    "givenName",
                    "surname",
                    "jobTitle",
                    "department",
                    "usageLocation",
                    "employeeId"
                ],
                "password_requirements": {
                    "password": "Required - must meet password policy",
                    "forceChangePasswordNextSignIn": "Optional - boolean"
                }
            }
        }

        return results

    def save_results(self, results: Dict[str, Any], output_file: str = "entra_id_extraction.json"):
        """
        Save extraction results to a JSON file

        Args:
            results: The results dictionary to save
            output_file: Output filename
        """
        print(f"\n💾 Saving results to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"✅ Results saved successfully")

    def generate_markdown_report(self, results: Dict[str, Any], output_file: str = "ENTRA_ID_REPORT.md"):
        """
        Generate a human-readable markdown report

        Args:
            results: The results dictionary
            output_file: Output markdown filename
        """
        print(f"\n📄 Generating markdown report: {output_file}...")

        report = f"""# Microsoft Entra ID User and Group Information

**Extraction Date:** {results['extraction_timestamp']}
**Admin Account:** {results['admin_account']}
**Tenant ID:** {results['tenant_id']}

---

## 📋 User Creation Requirements

### Minimum Required Fields

"""
        for field in results['user_creation_requirements']['minimum_required_fields']:
            schema_info = None
            for attr in results['user_schema']['standard_attributes']['required']:
                if attr['name'] == field:
                    schema_info = attr
                    break

            if schema_info:
                report += f"- **{field}** (`{schema_info['type']}`): {schema_info['description']}\n"
            else:
                report += f"- **{field}**\n"

        report += "\n### Recommended Fields\n\n"

        for field in results['user_creation_requirements']['recommended_fields']:
            schema_info = None
            for attr in results['user_schema']['standard_attributes']['optional']:
                if attr['name'] == field:
                    schema_info = attr
                    break

            if schema_info:
                report += f"- **{field}** (`{schema_info['type']}`): {schema_info['description']}\n"
            else:
                report += f"- **{field}**\n"

        report += "\n---\n\n## 📚 Complete User Attribute Schema\n\n"
        report += "### Required Attributes\n\n"

        for attr in results['user_schema']['standard_attributes']['required']:
            report += f"#### {attr['name']}\n"
            report += f"- **Type:** `{attr['type']}`\n"
            report += f"- **Description:** {attr['description']}\n"
            if 'properties' in attr:
                report += f"- **Properties:** {json.dumps(attr['properties'], indent=2)}\n"
            report += "\n"

        report += "### Optional Attributes\n\n"

        for attr in results['user_schema']['standard_attributes']['optional']:
            report += f"- **{attr['name']}** (`{attr['type']}`): {attr['description']}\n"

        # Schema extensions
        if results['user_schema']['schema_extensions']:
            report += "\n### Schema Extensions\n\n"
            for ext in results['user_schema']['schema_extensions']:
                report += f"- **{ext.get('id', 'N/A')}**: {ext.get('description', 'No description')}\n"

        report += "\n---\n\n## 👥 Groups Information\n\n"
        report += f"**Total Groups:** {results['groups']['total_count']}\n\n"

        for group in results['groups']['groups_list']:
            report += f"### {group.get('displayName', 'Unnamed Group')}\n\n"
            report += f"- **ID:** `{group.get('id', 'N/A')}`\n"
            report += f"- **Description:** {group.get('description', 'No description')}\n"
            report += f"- **Group Types:** {', '.join(group.get('groupTypes', []))}\n"
            report += f"- **Mail:** {group.get('mail', 'N/A')}\n"
            report += f"- **Mail Enabled:** {group.get('mailEnabled', False)}\n"
            report += f"- **Security Enabled:** {group.get('securityEnabled', False)}\n"
            report += f"- **Visibility:** {group.get('visibility', 'N/A')}\n"
            report += f"- **Member Count:** {group.get('member_count', 0)}\n"

            if group.get('membershipRule'):
                report += f"- **Membership Rule:** `{group.get('membershipRule')}`\n"
                report += f"- **Rule Processing State:** {group.get('membershipRuleProcessingState', 'N/A')}\n"

            report += "\n"

        report += "\n---\n\n## 👤 Sample Users (Attributes in Use)\n\n"

        for i, user in enumerate(results['sample_users'], 1):
            report += f"### Sample User {i}\n\n"
            report += f"- **Display Name:** {user.get('displayName', 'N/A')}\n"
            report += f"- **UPN:** {user.get('userPrincipalName', 'N/A')}\n"
            report += f"- **Email:** {user.get('mail', 'N/A')}\n"
            report += f"- **Job Title:** {user.get('jobTitle', 'N/A')}\n"
            report += f"- **Department:** {user.get('department', 'N/A')}\n"
            report += f"- **Office Location:** {user.get('officeLocation', 'N/A')}\n"
            report += f"- **Account Enabled:** {user.get('accountEnabled', 'N/A')}\n"
            report += "\n"

        report += "\n---\n\n## 🔧 User Creation Example (JSON)\n\n```json\n"
        report += json.dumps({
            "accountEnabled": True,
            "displayName": "John Doe",
            "mailNickname": "johnd",
            "userPrincipalName": "john.doe@mvlgroupusa.onmicrosoft.com",
            "passwordProfile": {
                "forceChangePasswordNextSignIn": True,
                "password": "SecureP@ssw0rd123!"
            },
            "givenName": "John",
            "surname": "Doe",
            "jobTitle": "Software Engineer",
            "department": "Engineering",
            "usageLocation": "US",
            "employeeId": "EMP001"
        }, indent=2)
        report += "\n```\n\n"

        report += "---\n\n## 📝 Notes\n\n"
        report += "1. **Password Policy:** Passwords must meet your organization's password policy requirements\n"
        report += "2. **User Principal Name:** Must be unique across the tenant\n"
        report += "3. **Usage Location:** Required for license assignment (two-letter country code)\n"
        report += "4. **Group Membership:** Users can be added to groups after creation using the Groups API\n\n"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"✅ Markdown report generated successfully")


async def main():
    """Main execution function"""
    try:
        # Initialize extractor
        extractor = EntraIDExtractor()

        # Extract all information
        results = await extractor.extract_all_information()

        # Save results
        extractor.save_results(results, "entra_id_extraction.json")
        extractor.generate_markdown_report(results, "ENTRA_ID_REPORT.md")

        print("\n" + "="*60)
        print("✅ Extraction Complete!")
        print("="*60)
        print("\n📁 Output Files:")
        print("  - entra_id_extraction.json (raw data)")
        print("  - ENTRA_ID_REPORT.md (human-readable report)")
        print("\n")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
