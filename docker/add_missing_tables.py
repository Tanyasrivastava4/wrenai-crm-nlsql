import json

FILE = "/home/intileo/Desktop/wren-ai/WrenAI/docker/crm_mdl1_copied.json"
SCHEMA = "crm_r_tech_solution_101"

# Helper to build a column entry
def make_col(col_id, model_id, col_name, data_type, is_nullable, is_pk, description):
    type_map = {
        "int": "INTEGER", "bigint": "INTEGER", "tinyint": "BOOLEAN",
        "varchar": "VARCHAR", "text": "VARCHAR", "longtext": "VARCHAR",
        "datetime": "TIMESTAMP", "decimal": "NUMERIC", "enum": "VARCHAR",
    }
    crm_type = type_map.get(data_type.lower(), "VARCHAR")
    not_null = 0 if is_nullable == "YES" else 1
    pk = 1 if is_pk == "PRI" else 0
    props = json.dumps({"description": description})
    return {
        "id": col_id,
        "model_id": model_id,
        "is_calculated": 0,
        "display_name": col_name,
        "source_column_name": col_name,
        "reference_name": col_name,
        "aggregation": None,
        "lineage": None,
        "type": crm_type,
        "not_null": not_null,
        "is_pk": pk,
        "properties": props,
        "created_at": "2026-04-18 07:35:26",
        "updated_at": "2026-04-18 07:35:26",
    }

# Helper to build a model entry
def make_model(model_id, table_name, description, columns):
    display_name = f"{SCHEMA}.{table_name}"
    reference_name = f"{SCHEMA}_{table_name}"
    props = json.dumps({
        "schema": SCHEMA,
        "catalog": "",
        "table": table_name,
        "path": None,
        "description": description
    })
    return {
        "id": model_id,
        "project_id": 6,
        "display_name": display_name,
        "source_table_name": display_name,
        "reference_name": reference_name,
        "ref_sql": None,
        "cached": 0,
        "refresh_time": None,
        "properties": props,
        "created_at": "2026-04-18 07:35:26",
        "updated_at": "2026-04-18 07:35:26",
        "columns": columns,
    }

# Load existing file to get max IDs
with open(FILE) as f:
    data = json.load(f)

models = data.get("models", [])

# Find max existing model_id and column_id
max_model_id = max(m["id"] for m in models)
max_col_id = max(
    col["id"]
    for m in models
    for col in m.get("columns", [])
)

print(f"Max existing model_id: {max_model_id}")
print(f"Max existing column_id: {max_col_id}")

mid = max_model_id + 1
cid = max_col_id + 1

new_models = []

# ── CampaignRecipients ──────────────────────────────────────────
cols = []
for col_name, data_type, is_nullable, is_pk, desc in [
    ("id", "int", "NO", "PRI", "Unique identifier for the campaign recipient record."),
    ("campaignId", "int", "NO", "MUL", "ID of the campaign this recipient belongs to."),
    ("email", "varchar", "NO", "MUL", "Email address of the recipient."),
    ("name", "varchar", "YES", "", "Full name of the recipient."),
    ("trackingId", "varchar", "NO", "UNI", "Unique tracking ID for monitoring email opens and clicks."),
    ("isDelivered", "tinyint", "YES", "", "Flag indicating whether the email was delivered successfully."),
    ("isOpened", "tinyint", "YES", "", "Flag indicating whether the recipient opened the email."),
    ("isClicked", "tinyint", "YES", "", "Flag indicating whether the recipient clicked a link in the email."),
    ("isBounced", "tinyint", "YES", "", "Flag indicating whether the email bounced."),
    ("isUnsubscribed", "tinyint", "YES", "", "Flag indicating whether the recipient unsubscribed."),
    ("deliveredAt", "datetime", "YES", "", "Timestamp when the email was delivered."),
    ("openedAt", "datetime", "YES", "", "Timestamp when the recipient first opened the email."),
    ("clickedAt", "datetime", "YES", "", "Timestamp when the recipient first clicked a link."),
    ("bouncedAt", "datetime", "YES", "", "Timestamp when the email bounced."),
    ("unsubscribedAt", "datetime", "YES", "", "Timestamp when the recipient unsubscribed."),
    ("bounceReason", "varchar", "YES", "", "Reason why the email bounced."),
    ("createdAt", "datetime", "NO", "", "Timestamp when the recipient record was created."),
    ("updatedAt", "datetime", "NO", "", "Timestamp when the recipient record was last updated."),
]:
    cols.append(make_col(cid, mid, col_name, data_type, is_nullable, is_pk, desc)); cid += 1
new_models.append(make_model(mid, "CampaignRecipients", "Individual email campaign recipients with delivery, open, click and bounce tracking per recipient.", cols)); mid += 1

# ── CampaignTemplates ───────────────────────────────────────────
cols = []
for col_name, data_type, is_nullable, is_pk, desc in [
    ("templateId", "int", "NO", "PRI", "Unique identifier for the campaign template."),
    ("templateName", "varchar", "NO", "", "Name of the campaign template."),
    ("subject", "varchar", "NO", "", "Email subject line for the template."),
    ("body", "longtext", "NO", "", "Plain text body content of the template."),
    ("html", "longtext", "YES", "", "HTML formatted content of the template."),
    ("createdAt", "datetime", "NO", "", "Timestamp when the template was created."),
    ("updatedAt", "datetime", "NO", "", "Timestamp when the template was last updated."),
]:
    cols.append(make_col(cid, mid, col_name, data_type, is_nullable, is_pk, desc)); cid += 1
new_models.append(make_model(mid, "CampaignTemplates", "Reusable email campaign templates with subject, body and HTML content.", cols)); mid += 1

# ── company_whatsapp_settings ───────────────────────────────────
cols = []
for col_name, data_type, is_nullable, is_pk, desc in [
    ("settingId", "int", "NO", "PRI", "Unique identifier for the WhatsApp settings record."),
    ("clientId", "varchar", "NO", "UNI", "Client identifier for the WhatsApp integration."),
    ("twilioAccountSid", "varchar", "NO", "", "Twilio account SID for WhatsApp messaging."),
    ("twilioAuthToken", "varchar", "NO", "", "Twilio authentication token for API access."),
    ("twilioWhatsappNumber", "varchar", "NO", "MUL", "WhatsApp number provisioned via Twilio."),
    ("isActive", "tinyint", "YES", "MUL", "Flag indicating whether WhatsApp integration is active."),
    ("isVerified", "tinyint", "YES", "MUL", "Flag indicating whether the WhatsApp number is verified."),
    ("businessName", "varchar", "YES", "", "Business name shown in WhatsApp messages."),
    ("businessDescription", "text", "YES", "", "Business description for the WhatsApp profile."),
    ("webhookUrl", "varchar", "YES", "", "Webhook URL for receiving incoming WhatsApp messages."),
    ("messagesSentCount", "int", "YES", "", "Total number of WhatsApp messages sent."),
    ("messagesReceivedCount", "int", "YES", "", "Total number of WhatsApp messages received."),
    ("lastMessageAt", "datetime", "YES", "MUL", "Timestamp of the most recent WhatsApp message."),
    ("autoReplyEnabled", "tinyint", "YES", "", "Flag enabling automatic replies to incoming messages."),
    ("autoReplyMessage", "text", "YES", "", "Message text sent as automatic reply."),
    ("createdBy", "int", "YES", "", "ID of the user who configured the WhatsApp settings."),
    ("verifiedAt", "datetime", "YES", "", "Timestamp when the WhatsApp number was verified."),
    ("verifiedBy", "int", "YES", "", "ID of the user who verified the WhatsApp number."),
    ("createdAt", "datetime", "NO", "", "Timestamp when the settings record was created."),
    ("updatedAt", "datetime", "NO", "", "Timestamp when the settings record was last updated."),
]:
    cols.append(make_col(cid, mid, col_name, data_type, is_nullable, is_pk, desc)); cid += 1
new_models.append(make_model(mid, "company_whatsapp_settings", "WhatsApp integration settings via Twilio including credentials, auto-reply and message statistics.", cols)); mid += 1

# ── EmailSignatures ─────────────────────────────────────────────
cols = []
for col_name, data_type, is_nullable, is_pk, desc in [
    ("signatureId", "int", "NO", "PRI", "Unique identifier for the email signature."),
    ("signatureName", "varchar", "NO", "", "Name of the email signature."),
    ("content", "longtext", "NO", "", "HTML content of the email signature."),
    ("isDefault", "tinyint", "NO", "", "Flag indicating whether this is the default signature."),
    ("createdBy", "int", "NO", "MUL", "ID of the user who created the signature."),
    ("createdAt", "datetime", "NO", "", "Timestamp when the signature was created."),
    ("updatedAt", "datetime", "NO", "", "Timestamp when the signature was last updated."),
]:
    cols.append(make_col(cid, mid, col_name, data_type, is_nullable, is_pk, desc)); cid += 1
new_models.append(make_model(mid, "EmailSignatures", "User-created email signatures with HTML content and default status.", cols)); mid += 1

# ── InsightPurchases ────────────────────────────────────────────
cols = []
for col_name, data_type, is_nullable, is_pk, desc in [
    ("id", "int", "NO", "PRI", "Unique identifier for the insight purchase."),
    ("type", "varchar", "NO", "", "Type of insight purchased."),
    ("reportsCount", "int", "NO", "", "Number of reports included in the purchase."),
    ("price", "decimal", "NO", "", "Price paid for the purchase."),
    ("txnid", "varchar", "YES", "", "Internal transaction ID."),
    ("payuTxnId", "varchar", "YES", "", "PayU payment gateway transaction ID."),
    ("purchasedBy", "int", "NO", "", "ID of the user who made the purchase."),
    ("purchasedAt", "datetime", "NO", "", "Timestamp when the purchase was made."),
    ("status", "enum", "NO", "", "Status of the purchase such as completed or failed."),
    ("createdAt", "datetime", "NO", "", "Timestamp when the purchase record was created."),
    ("updatedAt", "datetime", "NO", "", "Timestamp when the purchase record was last updated."),
]:
    cols.append(make_col(cid, mid, col_name, data_type, is_nullable, is_pk, desc)); cid += 1
new_models.append(make_model(mid, "InsightPurchases", "Purchases of insight/report credits with transaction and payment details.", cols)); mid += 1

# ── ProductFiles ────────────────────────────────────────────────
cols = []
for col_name, data_type, is_nullable, is_pk, desc in [
    ("fileId", "int", "NO", "PRI", "Unique identifier for the product file."),
    ("productId", "int", "NO", "MUL", "ID of the product this file is attached to."),
    ("fileName", "varchar", "NO", "", "Internal stored filename."),
    ("fileDisplayName", "varchar", "YES", "", "Display name shown to users for the file."),
    ("filePath", "varchar", "NO", "", "Storage path where the file is saved."),
    ("fileSize", "bigint", "NO", "", "Size of the file in bytes."),
    ("mimeType", "varchar", "NO", "", "MIME type of the file."),
    ("fileExtension", "varchar", "YES", "", "File extension such as pdf or docx."),
    ("fileCategory", "enum", "YES", "MUL", "Category of the file such as proposal or contract."),
    ("description", "text", "YES", "", "Description or notes about the file."),
    ("tags", "longtext", "YES", "", "Tags for searching and categorizing the file."),
    ("isPublic", "tinyint", "YES", "", "Flag indicating whether the file is publicly accessible."),
    ("uploadedBy", "int", "NO", "MUL", "ID of the user who uploaded the file."),
    ("lastAccessedAt", "datetime", "YES", "", "Timestamp when the file was last accessed."),
    ("downloadCount", "int", "YES", "", "Number of times the file has been downloaded."),
    ("version", "int", "YES", "", "Version number of the file."),
    ("previousVersionId", "int", "YES", "MUL", "ID of the previous version of this file."),
    ("isActive", "tinyint", "YES", "MUL", "Flag indicating whether this file is active."),
    ("masterUserID", "int", "NO", "MUL", "ID of the user who owns this file."),
    ("createdAt", "datetime", "NO", "", "Timestamp when the file record was created."),
    ("updatedAt", "datetime", "NO", "", "Timestamp when the file record was last updated."),
]:
    cols.append(make_col(cid, mid, col_name, data_type, is_nullable, is_pk, desc)); cid += 1
new_models.append(make_model(mid, "ProductFiles", "Files attached to products with metadata, version history and access tracking.", cols)); mid += 1

# ── RecycleBins ─────────────────────────────────────────────────
cols = []
for col_name, data_type, is_nullable, is_pk, desc in [
    ("recycleId", "int", "NO", "PRI", "Unique identifier for the recycle bin record."),
    ("entityType", "varchar", "NO", "MUL", "Type of deleted entity such as deal, lead, or person."),
    ("entityId", "varchar", "NO", "", "ID of the deleted entity."),
    ("entityName", "varchar", "YES", "", "Name or title of the deleted entity."),
    ("payload", "longtext", "NO", "", "Full JSON snapshot of the deleted record for restore."),
    ("deletedBy", "int", "YES", "", "ID of the user who deleted the record."),
    ("deletedByName", "varchar", "YES", "", "Name of the user who deleted the record."),
    ("deletionType", "varchar", "NO", "", "Type of deletion such as manual or automated."),
    ("metadata", "longtext", "YES", "", "Additional metadata about the deletion."),
    ("isRestored", "tinyint", "NO", "MUL", "Flag indicating whether the record has been restored."),
    ("deletedAt", "datetime", "NO", "MUL", "Timestamp when the record was deleted."),
    ("restoredAt", "datetime", "YES", "", "Timestamp when the record was restored."),
    ("restoredBy", "int", "YES", "", "ID of the user who restored the record."),
    ("createdAt", "datetime", "NO", "", "Timestamp when the recycle bin entry was created."),
    ("updatedAt", "datetime", "NO", "", "Timestamp when the recycle bin entry was last updated."),
]:
    cols.append(make_col(cid, mid, col_name, data_type, is_nullable, is_pk, desc)); cid += 1
new_models.append(make_model(mid, "RecycleBins", "Soft-deleted CRM entities with full payload stored for restore capability.", cols)); mid += 1

# ── TemplateCartItems ───────────────────────────────────────────
cols = []
for col_name, data_type, is_nullable, is_pk, desc in [
    ("id", "int", "NO", "PRI", "Unique identifier for the cart item."),
    ("templateId", "varchar", "YES", "", "ID of the template added to the cart."),
    ("templateName", "varchar", "YES", "", "Name of the template."),
    ("itemType", "enum", "NO", "", "Type of item in the cart."),
    ("reportsCount", "int", "YES", "", "Number of reports included in the template."),
    ("price", "decimal", "NO", "", "Price of the template."),
    ("thumbnailUrl", "text", "YES", "", "URL of the template thumbnail image."),
    ("addedBy", "int", "NO", "", "ID of the user who added the item to the cart."),
    ("createdAt", "datetime", "NO", "", "Timestamp when the cart item was created."),
]:
    cols.append(make_col(cid, mid, col_name, data_type, is_nullable, is_pk, desc)); cid += 1
new_models.append(make_model(mid, "TemplateCartItems", "Items added to cart for template purchases with type and pricing info.", cols)); mid += 1

# ── TemplatePurchases ───────────────────────────────────────────
cols = []
for col_name, data_type, is_nullable, is_pk, desc in [
    ("id", "int", "NO", "PRI", "Unique identifier for the template purchase."),
    ("templateId", "varchar", "NO", "", "ID of the purchased template."),
    ("templateName", "varchar", "YES", "", "Name of the purchased template."),
    ("price", "decimal", "NO", "", "Price paid for the template."),
    ("txnid", "varchar", "YES", "", "Internal transaction ID."),
    ("payuTxnId", "varchar", "YES", "", "PayU payment gateway transaction ID."),
    ("purchasedBy", "int", "NO", "", "ID of the user who purchased the template."),
    ("purchasedAt", "datetime", "NO", "", "Timestamp when the purchase was made."),
    ("status", "enum", "NO", "", "Status of the purchase such as completed or failed."),
    ("createdAt", "datetime", "NO", "", "Timestamp when the purchase record was created."),
    ("updatedAt", "datetime", "NO", "", "Timestamp when the purchase record was last updated."),
]:
    cols.append(make_col(cid, mid, col_name, data_type, is_nullable, is_pk, desc)); cid += 1
new_models.append(make_model(mid, "TemplatePurchases", "Purchase records for report/dashboard templates with transaction details.", cols)); mid += 1

# ── WhatsAppCampaigns ───────────────────────────────────────────
cols = []
for col_name, data_type, is_nullable, is_pk, desc in [
    ("campaignId", "int", "NO", "PRI", "Unique identifier for the WhatsApp campaign."),
    ("campaignName", "varchar", "NO", "", "Name of the WhatsApp campaign."),
    ("messageBody", "text", "NO", "", "Body text of the WhatsApp message."),
    ("receivers", "text", "NO", "", "JSON list of recipient filter criteria."),
    ("templateId", "int", "YES", "MUL", "ID of the WhatsApp template used."),
    ("sendingTime", "longtext", "YES", "", "Scheduled time to send the campaign."),
    ("isActive", "tinyint", "NO", "", "Flag indicating whether the campaign is active."),
    ("status", "enum", "YES", "MUL", "Current status of the campaign."),
    ("totalReceivers", "int", "YES", "", "Total number of recipients targeted."),
    ("messagesSent", "int", "YES", "", "Number of messages successfully sent."),
    ("messagesFailed", "int", "YES", "", "Number of messages that failed to send."),
    ("lastProcessedAt", "datetime", "YES", "", "Timestamp when the campaign was last processed."),
    ("completedAt", "datetime", "YES", "", "Timestamp when the campaign sending completed."),
    ("entityType", "enum", "YES", "", "Type of entity targeted such as leads or contacts."),
    ("mediaUrl", "varchar", "YES", "", "URL of media file attached to the campaign."),
    ("personId", "int", "YES", "", "ID of a specific person targeted by the campaign."),
    ("personName", "varchar", "YES", "", "Name of a specific person targeted by the campaign."),
    ("filterName", "varchar", "YES", "", "Name of the filter used to select recipients."),
    ("recipientFilterName", "varchar", "YES", "", "Name of the recipient filter."),
    ("filterId", "int", "YES", "", "ID of the saved filter used for recipients."),
    ("filterType", "varchar", "YES", "", "Type of filter applied."),
    ("createdBy", "int", "NO", "MUL", "ID of the user who created the campaign."),
    ("createdAt", "datetime", "NO", "", "Timestamp when the campaign was created."),
    ("updatedAt", "datetime", "NO", "", "Timestamp when the campaign was last updated."),
]:
    cols.append(make_col(cid, mid, col_name, data_type, is_nullable, is_pk, desc)); cid += 1
new_models.append(make_model(mid, "WhatsAppCampaigns", "WhatsApp bulk messaging campaigns with template, recipients, status and delivery statistics.", cols)); mid += 1

# ── whatsapp_messages ───────────────────────────────────────────
cols = []
for col_name, data_type, is_nullable, is_pk, desc in [
    ("messageId", "int", "NO", "PRI", "Unique identifier for the WhatsApp message."),
    ("twilioMessageSid", "varchar", "NO", "UNI", "Twilio message SID for tracking."),
    ("twilioAccountSid", "varchar", "YES", "", "Twilio account SID used to send the message."),
    ("entityType", "enum", "YES", "MUL", "Type of entity this message is linked to such as deal or lead."),
    ("entityId", "int", "YES", "", "ID of the entity this message is linked to."),
    ("leadId", "int", "YES", "MUL", "ID of the lead this message is linked to."),
    ("dealId", "int", "YES", "MUL", "ID of the deal this message is linked to."),
    ("personId", "int", "YES", "MUL", "ID of the person this message is linked to."),
    ("masterUserID", "int", "NO", "MUL", "ID of the CRM user associated with this message."),
    ("ownerId", "int", "YES", "", "ID of the user who owns this message."),
    ("fromPhone", "varchar", "NO", "", "Phone number the message was sent from."),
    ("toPhone", "varchar", "NO", "MUL", "Phone number the message was sent to."),
    ("direction", "enum", "NO", "MUL", "Direction of the message such as inbound or outbound."),
    ("messageType", "varchar", "YES", "", "Type of message such as text or media."),
    ("status", "varchar", "YES", "MUL", "Delivery status of the message."),
    ("twilioStatus", "varchar", "YES", "", "Status reported by Twilio for the message."),
    ("errorCode", "varchar", "YES", "", "Error code if the message failed."),
    ("errorMessage", "text", "YES", "", "Error message if the message failed."),
    ("hasMedia", "tinyint", "YES", "", "Flag indicating whether the message contains media."),
    ("mediaCount", "int", "YES", "", "Number of media files attached to the message."),
    ("bodyPreview", "varchar", "YES", "", "Preview text of the message body."),
    ("visibility", "varchar", "YES", "", "Visibility setting of the message."),
    ("isArchived", "tinyint", "YES", "", "Flag indicating whether the message is archived."),
    ("sentAt", "datetime", "YES", "", "Timestamp when the message was sent."),
    ("deliveredAt", "datetime", "YES", "", "Timestamp when the message was delivered."),
    ("readAt", "datetime", "YES", "", "Timestamp when the message was read."),
    ("createdAt", "datetime", "NO", "MUL", "Timestamp when the message record was created."),
    ("updatedAt", "datetime", "NO", "", "Timestamp when the message record was last updated."),
]:
    cols.append(make_col(cid, mid, col_name, data_type, is_nullable, is_pk, desc)); cid += 1
new_models.append(make_model(mid, "whatsapp_messages", "Individual WhatsApp messages sent/received via Twilio with entity linking, status and media info.", cols)); mid += 1

# ── whatsapp_templates ──────────────────────────────────────────
cols = []
for col_name, data_type, is_nullable, is_pk, desc in [
    ("templateId", "int", "NO", "PRI", "Unique identifier for the WhatsApp template."),
    ("masterUserID", "int", "NO", "MUL", "ID of the user who created the template."),
    ("templateName", "varchar", "NO", "", "Name of the WhatsApp template."),
    ("templateBody", "text", "NO", "", "Body text of the template with variable placeholders."),
    ("category", "varchar", "YES", "MUL", "Category of the template such as marketing or utility."),
    ("variables", "longtext", "YES", "", "JSON list of variable names used in the template."),
    ("isActive", "tinyint", "YES", "MUL", "Flag indicating whether the template is active."),
    ("usageCount", "int", "YES", "", "Number of times this template has been used."),
    ("createdAt", "datetime", "NO", "", "Timestamp when the template was created."),
    ("updatedAt", "datetime", "NO", "", "Timestamp when the template was last updated."),
]:
    cols.append(make_col(cid, mid, col_name, data_type, is_nullable, is_pk, desc)); cid += 1
new_models.append(make_model(mid, "whatsapp_templates", "Reusable WhatsApp message templates with variables, category and usage count.", cols)); mid += 1

# Append new models to existing data
data["models"].extend(new_models)

with open(FILE, "w") as f:
    json.dump(data, f, indent=2)

print(f"✅ Done! Added {len(new_models)} new tables.")
print(f"   Total tables now: {len(data['models'])}")
print(f"   New model IDs: {max_model_id + 1} to {mid - 1}")
print(f"   New column IDs: {max_col_id + 1} to {cid - 1}")
