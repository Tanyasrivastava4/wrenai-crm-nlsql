import json

FILE = "/home/intileo/Desktop/wren-ai/WrenAI/docker/crm_mdl1_copied.json"

# Updated descriptions keyed by table name (last part after the dot)
descriptions = {
    "Activities": "CRM activities like calls, meetings, emails containing activityId, type, subject, startDateTime, assignedTo, dealId, leadId.",
    "ActivityColumns": "User preferences for which columns to display in the Activities list view.",
    "ActivitySettings": "Per-user configuration for activity popups, follow-up times, and deal-won activity behavior.",
    "ActivityTypes": "Lookup table for activity type definitions like call, meeting, email with icons and active status.",
    "Admins": "System administrator accounts with login credentials and OTP authentication.",
    "Attachments": "Email attachment files linked to emails with file metadata and storage path.",
    "AuditTrails": "System audit log tracking program-level operations, errors, and creator details.",
    "AutomationHistories": "Execution history of CRM automations with status, error messages and step-level logs.",
    "Automations": "CRM workflow automation rules with trigger/action configuration and active status.",
    "CampaignRecipients": "Individual email campaign recipients with delivery, open, click and bounce tracking per recipient.",
    "Campaigns": "Marketing campaigns containing campaignId, name, channel, status, send time, engagement stats and recipient counts.",
    "CampaignSenders": "SMTP/email sender accounts configured for campaigns with provider, credentials and verification status.",
    "CampaignTemplates": "Reusable email campaign templates with subject, body and HTML content.",
    "Cards": "Dashboard widget cards with position coordinates, type and owner.",
    "company_settings": "Company-level CRM configuration including name, domain, timezone and two-factor authentication settings.",
    "company_whatsapp_settings": "WhatsApp integration settings via Twilio including credentials, auto-reply and message statistics.",
    "ContactChangeLogs": "Detailed change log for contact sync operations between CRM and Google Contacts.",
    "ContactSyncConfigs": "Per-user Google Contacts sync configuration including direction, frequency, field mapping and OAuth tokens.",
    "ContactSyncHistories": "History of contact sync sessions with counts of created, updated, deleted and conflicted records.",
    "ContactSyncMappings": "Mapping between CRM persons and Google Contact IDs for sync tracking.",
    "Countries": "Lookup table of countries with ISO codes used for address and location fields.",
    "Currencies": "Supported currencies with symbol, decimal points, code and active status.",
    "CustomFields": "User-defined custom fields for deals, leads, persons and organizations with type, validation and display rules.",
    "CustomFieldValues": "Stored values for custom fields linked to specific entities like deals or leads.",
    "Dashboards": "User dashboards with layout, folder, type and ownership information.",
    "DealColumns": "User preferences for which columns to display in the Deals list view.",
    "DealDetails": "Extended additional details for deals including RFP dates, responsible person, won/lost time and project location.",
    "DealFiles": "Files and documents attached to deals with metadata, version history and access tracking.",
    "DealNotes": "Text notes written by users on specific deals.",
    "DealParticipants": "Persons and organizations participating in a deal as stakeholders.",
    "DealProducts": "Products linked to deals containing dealId, productId, quantity, unitPrice, discount, tax and total.",
    "Deals": "Main sales deals table containing dealId, title, value, currency, status (won/lost/open), pipelineId, stageId, owner and activity tracking.",
    "DealStageHistories": "History of deal stage changes containing dealId, stageName, enteredAt timestamp.",
    "DefaultEmails": "Default email accounts configured per user for sending emails from the CRM.",
    "Departments": "Lookup table of company departments used for user organization.",
    "Designations": "Lookup table of job designations/titles used for user profiles.",
    "DeviceActivities": "Device-level login and session activity tracking with IP and location.",
    "Emails": "Email messages sent and received in the CRM with threading, folder, read status, scheduling and deal/lead linking.",
    "EmailSignatures": "User-created email signatures with content and default status.",
    "EmailTemplates": "Reusable email templates with subject and HTML body for sending from the CRM.",
    "EntityFiles": "Generic file attachments linked to any entity type (deal, lead, person, organization).",
    "Goals": "Sales goals and targets containing goalId, type, value, period, assignee, pipeline and tracking metrics.",
    "GroupMemberships": "Membership records linking users to visibility groups with assignment tracking.",
    "GroupVisibilities": "Visibility groups controlling which users can see specific pipelines, deals, leads and persons.",
    "Histories": "General change history log for CRM records tracking field-level modifications.",
    "ImportDatas": "Data import sessions tracking file uploads, column mapping, validation errors and import progress.",
    "InsightPurchases": "Purchases of insight/report credits with transaction and payment details.",
    "ItemVisibilityRules": "Permission rules per group controlling CRUD and export access on entity types.",
    "Labels": "Color-coded labels applied to deals, leads, persons and organizations for categorization.",
    "LeadColumnPreferences": "User preferences for which columns to display in the Leads list view.",
    "LeadColumns": "Lookup table of lead column definitions used in list views.",
    "LeadDetails": "Extended details for leads including RFP dates, responsible person, address and next activity info.",
    "LeadFilters": "Saved filter configurations for leads list views with visibility and column settings.",
    "LeadNotes": "Text notes written by users on specific leads.",
    "LeadOrganizations": "Organizations linked to leads containing organizationId, name, address, deal counts and activity tracking.",
    "LeadPersons": "Persons/contacts linked to leads containing personId, name, email, phone, job title and deal counts.",
    "Leads": "Sales leads containing leadId, title, value, status, owner, pipeline information and qualification tracking.",
    "LoginHistories": "Full login/logout session history per user with device, IP, location and duration.",
    "LostReasons": "Configurable reasons for marking deals as lost with sort order and active status.",
    "LostReasonSettings": "Per-user settings controlling whether lost reason selection is required when closing deals.",
    "MasterUserPrivileges": "Permission records for CRM users defining their access rights.",
    "MasterUsers": "CRM system users containing masterUserID, name, email, role, department, designation and authentication settings.",
    "Meetings": "Meeting details linked to activities including timezone, recurrence, video URL and attendee management.",
    "MergeMaps": "Records of entity merges tracking which record was merged into which.",
    "MiscSettings": "System-level miscellaneous settings like image size limits and allowed file types.",
    "NotificationPreferences": "Per-user preferences for in-app, push and email notification types across all CRM events.",
    "Notifications": "In-app notification records for users with read status, priority and linked entity.",
    "OrganizationColumnPreferences": "User preferences for which columns to display in the Organizations list view.",
    "OrganizationFiles": "Files attached to organizations with metadata and version tracking.",
    "OrganizationNotes": "Text notes written by users on specific organizations.",
    "Organizations": "Lookup/reference table for organization type classifications used in the CRM.",
    "OrganizationSidebarPreferences": "Per-user sidebar section layout preferences for organization detail views.",
    "PermissionSets": "Named permission sets with grouped access rules assignable to users.",
    "PersonColumnPreferences": "User preferences for which columns to display in the Persons/Contacts list view.",
    "PersonFiles": "Files attached to persons/contacts with metadata and version tracking.",
    "PersonNotes": "Text notes written by users on specific persons or contacts.",
    "PersonSidebarPreferences": "Per-user sidebar section layout preferences for person detail views.",
    "Pipelines": "Sales pipelines containing pipelineId, pipelineName, description, isActive, isDefault, color and display order.",
    "PipelineStages": "Stages within sales pipelines containing stageId, pipelineId, stageName, stageOrder, probability and color.",
    "PipelineVisibilityRules": "Group-level permissions controlling view, edit, delete and deal creation access per pipeline.",
    "ProductColumns": "User preferences for which columns to display in the Products list view.",
    "ProductFiles": "Files attached to products with metadata and version tracking.",
    "Products": "Product catalog containing productId, name, price, description, category, tax, billing frequency and variations flag.",
    "ProductVariations": "Product variants with SKU, pricing, attributes and active status linked to parent products.",
    "Programs": "Lookup table of program classifications used in audit trails and histories.",
    "PushSubscriptions": "Browser push notification subscription tokens per user with device info and expiry.",
    "RecentLoginHistories": "Lightweight recent login records per user for quick session history display.",
    "RecentSearches": "Recent and recently viewed search terms and entity results per user.",
    "RecycleBins": "Soft-deleted CRM entities with full payload stored for restore capability.",
    "RefreshTokens": "JWT refresh tokens per user session with device info, expiry and revocation status.",
    "Regions": "Geographic regions linked to countries used for location-based data.",
    "ReportFolders": "Folders for organizing saved reports by owner.",
    "Reports": "Saved CRM reports with chart type, config, entity, filters and dashboard assignments.",
    "SchedulingLinks": "Shareable meeting booking links with availability, duration, buffer times and custom fields.",
    "Scopes": "Lookup table of scope classifications used for deals and projects.",
    "Sectoralscopes": "Lookup table of sectoral scope classifications used for deal categorization.",
    "StartupQuestions": "Onboarding survey responses collected when a new user first sets up the CRM.",
    "Statuses": "Lookup table of status definitions used across CRM entities.",
    "TagMaps": "Junction table linking tags to specific entities like deals, leads or persons.",
    "TemplatePurchases": "Purchase records for report/dashboard templates with transaction details.",
    "TemplateCartItems": "Items added to cart for template purchases with type and pricing info.",
    "Templates": "Email templates for individual user sending with subject, content and sharing settings.",
    "UserCredentials": "Per-user email account credentials for IMAP/SMTP sync with email tracking settings.",
    "UserFavorites": "Saved favorite users/colleagues per user with nickname and active status.",
    "UserGoogleTokens": "Google OAuth tokens per user for Google integrations like calendar and contacts.",
    "UserInterfacePreferences": "Per-user UI behavior preferences like default landing page, sidebar order and auto-open settings.",
    "UserNotInterestedReasons": "User-defined reasons for marking leads or deals as not interested.",
    "VisibilityGroups": "Hierarchical user groups controlling data visibility with parent-child relationships.",
    "WebFormFields": "Individual field definitions for web lead capture forms with mapping to CRM fields.",
    "WebForms": "Web-based lead capture forms with embed code, styling, submission tracking and GDPR settings.",
    "WebFormSubmissions": "Submitted web form data with lead creation, UTM tracking, spam scoring and processing status.",
    "WebFormTrackings": "Granular analytics events for web form interactions including field-level timing and device info.",
    "WhatsAppCampaigns": "WhatsApp bulk messaging campaigns with template, recipients, status and delivery statistics.",
    "whatsapp_messages": "Individual WhatsApp messages sent/received via Twilio with entity linking, status and media info.",
    "whatsapp_templates": "Reusable WhatsApp message templates with variables, category and usage count.",
}

# Load file
with open(FILE, "r") as f:
    data = json.load(f)

models = data.get("models", [])
updated = 0
skipped = 0

for m in models:
    display_name = m.get("display_name", "")
    # Extract table name after the dot
    table_name = display_name.split(".")[-1] if "." in display_name else display_name

    if table_name in descriptions:
        props = m.get("properties", {})
        # Parse if string
        if isinstance(props, str):
            props = json.loads(props)
            m["properties"] = json.dumps({**props, "description": descriptions[table_name]})
        else:
            props["description"] = descriptions[table_name]
            m["properties"] = props
        updated += 1
    else:
        skipped += 1
        print(f"⚠️  No description found for: {display_name}")

# Save back
with open(FILE, "w") as f:
    json.dump(data, f, indent=2)

print(f"\n✅ Done! Updated: {updated}, Skipped: {skipped}")
