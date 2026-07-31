# Odoo Accounting MCP Server

MCP server for integrating Odoo ERP accounting functions with the AI Employee.

## Features

- **Partner Management**: Search, create, update contacts and customers
- **Invoice Management**: Create, search, post, and manage invoices
- **Payment Processing**: Register payments for invoices
- **Product Catalog**: Search and create products/services
- **Accounting Reports**: Trial balance, P&L, balance sheet, aged receivables/payables
- **Dashboard Metrics**: Real-time financial summaries

## Prerequisites

1. **Odoo 17+** instance running (Community or Enterprise)
2. **External API** enabled in Odoo (Settings → General Settings → API)
3. **User with accounting permissions** (Accountant or Administrator role)

## Configuration

Set environment variables:

```bash
export ODOO_URL="http://localhost:8069"
export ODOO_DATABASE="your_database"
export ODOO_USERNAME="your_username"
export ODOO_PASSWORD="your_password"
```

Or create a `.env` file in this directory:

```env
ODOO_URL=http://localhost:8069
ODOO_DATABASE=my_company
ODOO_USERNAME=admin
ODOO_PASSWORD=secure_password
```

## Installation

```bash
cd mcp-servers/odoo-accounting
pip install -r requirements.txt
```

## MCP Configuration

Add to your MCP settings (e.g., `~/.config/claude-code/mcp.json`):

```json
{
  "mcpServers": {
    "odoo-accounting": {
      "command": "python",
      "args": ["mcp-servers/odoo-accounting/odoo_mcp_server.py"],
      "env": {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DATABASE": "my_company",
        "ODOO_USERNAME": "admin",
        "ODOO_PASSWORD": "your_password"
      }
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `odoo_search_partners` | Search contacts/customers |
| `odoo_create_partner` | Create new contact/customer |
| `odoo_search_invoices` | Search invoices |
| `odoo_create_invoice` | Create draft invoice |
| `odoo_post_invoice` | Post/validate invoice |
| `odoo_register_payment` | Register payment for invoice |
| `odoo_search_products` | Search products/services |
| `odoo_create_product` | Create new product/service |
| `odoo_get_accounting_report` | Get financial reports |
| `odoo_search_payments` | Search payments |
| `odoo_get_dashboard_data` | Get financial dashboard summary |

## Usage Examples

### Search for a customer
```json
{
  "name": "odoo_search_partners",
  "arguments": {
    "domain": [["name", "ilike", "Acme"]],
    "fields": ["id", "name", "email", "phone", "is_company"]
  }
}
```

### Create a new invoice
```json
{
  "name": "odoo_create_invoice",
  "arguments": {
    "partner_id": 12,
    "invoice_line_ids": [
      {
        "name": "Consulting Services - January",
        "quantity": 10,
        "price_unit": 150.00,
        "tax_ids": [1]
      }
    ],
    "invoice_date": "2026-01-15"
  }
}
```

### Post an invoice
```json
{
  "name": "odoo_post_invoice",
  "arguments": {
    "invoice_id": 456
  }
}
```

### Register payment
```json
{
  "name": "odoo_register_payment",
  "arguments": {
    "invoice_id": 456,
    "amount": 1500.00,
    "journal_id": 1,
    "payment_method_id": 1
  }
}
```

### Get dashboard summary
```json
{
  "name": "odoo_get_dashboard_data",
  "arguments": {
    "date_from": "2026-01-01",
    "date_to": "2026-01-31"
  }
}
```

## Odoo API Notes

This server uses Odoo's **External API (JSON-RPC)** via the `execute_kw` method.
Compatible with Odoo 17, 18, and 19+.

For Odoo 19+, consider using the new **JSON-2 API** for better performance.

## Security

- Never commit `.env` files or credentials to version control
- Use dedicated API users with minimal required permissions
- Consider using Odoo's API keys (available in Enterprise) instead of passwords
- Run Odoo behind HTTPS in production

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Check Odoo URL and port; ensure Odoo is running |
| Authentication failed | Verify database name, username, and password |
| Access denied | Ensure user has "Accountant" or "Administrator" group |
| Model not found | Check Odoo version compatibility; some models differ between versions |

## Development

To extend with custom tools, edit `odoo_mcp_server.py` and add new tools to the `list_tools` and `call_tool` handlers.

## License

MIT