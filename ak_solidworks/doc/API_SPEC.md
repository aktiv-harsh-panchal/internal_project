# SolidWorks to Odoo 19 Integration Guide

This document defines the interface for pushing CAD data (Assemblies and Parts) from the SolidWorks CAD server to Odoo.

## 1. Authentication
Odoo uses **Native API Keys** for secure server-to-server communication.

*   **HTTP Header:** `Authorization`
*   **Format:** `Bearer <API_KEY>`
*   **How to get the Key:** In Odoo, go to **Settings > Users > [CAD Sync User] > Account Security > New API Key**.

## 2. Endpoint Details
*   **Method:** `POST`
*   **URL:** `https://<YOUR_ODOO_DOMAIN>/ak_solidworks/sync`
*   **Content-Type:** `application/json`

## 3. Data Format (JSON-RPC 2.0)
Odoo controllers with `type='json'` require the standard JSON-RPC 2.0 wrapper. Your data must be placed inside the `"params"` dictionary.

### Field Definitions:
| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `name` | String | Yes | Display name of the part/assembly. |
| `default_code` | String | **Yes** | **Unique Identifier** (e.g., Part Number). Used to prevent duplicates. |
| `type` | String | Yes | Value must be `"part"` or `"assembly"`. |
| `uom` | String | No | Unit of Measure (default: `"Units"`). |
| `quantity` | Float | No | Quantity in the parent assembly (default: 1). |
| `components` | List | No | Required for `type='assembly'`. Contains the children objects (recursive). |

## 4. Response Codes
*   **Success (200 OK):** `{"jsonrpc": "2.0", "result": {"status": "success", "data": { ... }}}`
*   **Error (200 OK):** `{"jsonrpc": "2.0", "result": {"status": "error", "message": "Detailed error message"}}`
*   **Auth Failure (403 Forbidden):** Invalid API Key.
