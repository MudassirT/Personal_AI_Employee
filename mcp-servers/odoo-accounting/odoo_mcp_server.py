#!/usr/bin/env python3
"""
Odoo Accounting MCP Server

Provides MCP tools for integrating with Odoo Community (self-hosted) via JSON-RPC API.
Supports: invoices, payments, contacts, products, accounting reports, and more.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    TextContent,
    Tool,
)


class OdooClient:
    """JSON-RPC client for Odoo Community Edition."""
    
    def __init__(self, url: str, database: str, username: str, password: str):
        self.url = url.rstrip('/')
        self.database = database
        self.username = username
        self.password = password
        self.uid = None
        self.session = httpx.AsyncClient(timeout=30.0)
        self.common_url = f"{self.url}/jsonrpc"
        self.object_url = f"{self.url}/jsonrpc"
    
    async def authenticate(self) -> bool:
        """Authenticate with Odoo and get user ID."""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "common",
                "method": "authenticate",
                "args": [self.database, self.username, self.password, {}]
            },
            "id": 1
        }
        
        response = await self.session.post(self.common_url, json=payload)
        result = response.json()
        
        if "result" in result and result["result"]:
            self.uid = result["result"]
            return True
        return False
    
    async def execute_kw(self, model: str, method: str, args: list, kwargs: dict = None) -> Any:
        """Execute a method on an Odoo model via JSON-RPC."""
        if self.uid is None:
            await self.authenticate()
        
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [self.database, self.uid, self.password, model, method, args, kwargs or {}]
            },
            "id": 2
        }
        
        response = await self.session.post(self.object_url, json=payload)
        result = response.json()
        
        if "error" in result:
            raise Exception(f"Odoo error: {result['error']}")
        
        return result.get("result")
    
    async def search_read(self, model: str, domain: list, fields: list = None, limit: int = 80, offset: int = 0) -> List[Dict]:
        """Search and read records."""
        kwargs = {"limit": limit, "offset": offset}
        if fields:
            kwargs["fields"] = fields
        return await self.execute_kw(model, "search_read", [domain], kwargs)
    
    async def create(self, model: str, values: dict) -> int:
        """Create a new record."""
        return await self.execute_kw(model, "create", [values])
    
    async def write(self, model: str, ids: list, values: dict) -> bool:
        """Update records."""
        return await self.execute_kw(model, "write", [ids, values])
    
    async def unlink(self, model: str, ids: list) -> bool:
        """Delete records."""
        return await self.execute_kw(model, "unlink", [ids])
    
    async def close(self):
        """Close HTTP session."""
        await self.session.aclose()


# Global Odoo client instance
odoo_client: Optional[OdooClient] = None


def get_odoo_config() -> Dict[str, str]:
    """Get Odoo configuration from environment variables."""
    return {
        "url": os.getenv("ODOO_URL", "http://localhost:8069"),
        "database": os.getenv("ODOO_DATABASE", "odoo"),
        "username": os.getenv("ODOO_USERNAME", "admin"),
        "password": os.getenv("ODOO_PASSWORD", "admin"),
    }


async def get_odoo_client() -> OdooClient:
    """Get or create Odoo client instance."""
    global odoo_client
    if odoo_client is None:
        config = get_odoo_config()
        odoo_client = OdooClient(**config)
        await odoo_client.authenticate()
    return odoo_client


# Create MCP server
server = Server("odoo-accounting")


@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List available Odoo accounting tools."""
    return ListToolsResult(tools=[
        Tool(
            name="odoo_search_partners",
            description="Search for contacts/partners in Odoo",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {"type": "array", "description": "Odoo search domain", "default": []},
                    "fields": {"type": "array", "items": {"type": "string"}, "description": "Fields to return", "default": ["id", "name", "email", "phone", "is_company"]},
                    "limit": {"type": "integer", "default": 20}
                }
            }
        ),
        Tool(
            name="odoo_create_partner",
            description="Create a new contact/partner in Odoo",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Partner name"},
                    "email": {"type": "string", "description": "Email address"},
                    "phone": {"type": "string", "description": "Phone number"},
                    "is_company": {"type": "boolean", "default": False},
                    "street": {"type": "string", "description": "Street address"},
                    "city": {"type": "string", "description": "City"},
                    "zip": {"type": "string", "description": "Postal code"},
                    "country_id": {"type": "integer", "description": "Country ID"},
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="odoo_search_invoices",
            description="Search for invoices in Odoo",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {"type": "array", "description": "Odoo search domain", "default": []},
                    "fields": {"type": "array", "items": {"type": "string"}, "description": "Fields to return", "default": ["id", "name", "partner_id", "amount_total", "state", "invoice_date", "payment_state"]},
                    "limit": {"type": "integer", "default": 20}
                }
            }
        ),
        Tool(
            name="odoo_create_invoice",
            description="Create a new draft invoice in Odoo",
            inputSchema={
                "type": "object",
                "properties": {
                    "partner_id": {"type": "integer", "description": "Partner/customer ID"},
                    "invoice_line_ids": {"type": "array", "description": "Invoice lines", "items": {
                        "type": "object",
                        "properties": {
                            "product_id": {"type": "integer", "description": "Product ID"},
                            "name": {"type": "string", "description": "Line description"},
                            "quantity": {"type": "number", "default": 1},
                            "price_unit": {"type": "number", "description": "Unit price"},
                            "tax_ids": {"type": "array", "items": {"type": "integer"}, "description": "Tax IDs"}
                        },
                        "required": ["name", "price_unit"]
                    }},
                    "invoice_date": {"type": "string", "description": "Invoice date (YYYY-MM-DD)", "default": ""},
                    "move_type": {"type": "string", "enum": ["out_invoice", "out_refund", "in_invoice", "in_refund"], "default": "out_invoice"}
                },
                "required": ["partner_id", "invoice_line_ids"]
            }
        ),
        Tool(
            name="odoo_post_invoice",
            description="Post (validate) a draft invoice",
            inputSchema={
                "type": "object",
                "properties": {
                    "invoice_id": {"type": "integer", "description": "Invoice ID to post"}
                },
                "required": ["invoice_id"]
            }
        ),
        Tool(
            name="odoo_register_payment",
            description="Register payment for an invoice",
            inputSchema={
                "type": "object",
                "properties": {
                    "invoice_id": {"type": "integer", "description": "Invoice ID"},
                    "amount": {"type": "number", "description": "Payment amount"},
                    "payment_date": {"type": "string", "description": "Payment date (YYYY-MM-DD)", "default": ""},
                    "journal_id": {"type": "integer", "description": "Payment journal ID"},
                    "payment_method_id": {"type": "integer", "description": "Payment method ID"}
                },
                "required": ["invoice_id", "amount", "journal_id"]
            }
        ),
        Tool(
            name="odoo_search_products",
            description="Search for products in Odoo",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {"type": "array", "description": "Odoo search domain", "default": []},
                    "fields": {"type": "array", "items": {"type": "string"}, "description": "Fields to return", "default": ["id", "name", "list_price", "type", "categ_id"]},
                    "limit": {"type": "integer", "default": 20}
                }
            }
        ),
        Tool(
            name="odoo_create_product",
            description="Create a new product in Odoo",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Product name"},
                    "list_price": {"type": "number", "description": "Sales price", "default": 0},
                    "standard_price": {"type": "number", "description": "Cost price", "default": 0},
                    "type": {"type": "string", "enum": ["consu", "service", "product"], "default": "service"},
                    "categ_id": {"type": "integer", "description": "Product category ID"},
                    "taxes_id": {"type": "array", "items": {"type": "integer"}, "description": "Customer tax IDs"},
                    "supplier_taxes_id": {"type": "array", "items": {"type": "integer"}, "description": "Vendor tax IDs"}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="odoo_get_accounting_report",
            description="Get accounting report data (trial balance, profit loss, balance sheet)",
            inputSchema={
                "type": "object",
                "properties": {
                    "report_name": {"type": "string", "enum": ["trial_balance", "profit_loss", "balance_sheet", "general_ledger", "aged_receivable", "aged_payable"], "description": "Report type"},
                    "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "date_to": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "options": {"type": "object", "description": "Additional report options", "default": {}}
                },
                "required": ["report_name"]
            }
        ),
        Tool(
            name="odoo_search_payments",
            description="Search for payments in Odoo",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {"type": "array", "description": "Odoo search domain", "default": []},
                    "fields": {"type": "array", "items": {"type": "string"}, "description": "Fields to return", "default": ["id", "name", "partner_id", "amount", "date", "state", "journal_id"]},
                    "limit": {"type": "integer", "default": 20}
                }
            }
        ),
        Tool(
            name="odoo_get_dashboard_data",
            description="Get accounting dashboard summary data",
            inputSchema={
                "type": "object",
                "properties": {
                    "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "date_to": {"type": "string", "description": "End date (YYYY-MM-DD)"}
                }
            }
        ),
    ])


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    """Execute Odoo accounting tools."""
    try:
        client = await get_odoo_client()
        
        if name == "odoo_search_partners":
            result = await client.search_read("res.partner", arguments.get("domain", []), arguments.get("fields"), arguments.get("limit", 20))
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "odoo_create_partner":
            partner_id = await client.create("res.partner", arguments)
            return CallToolResult(content=[TextContent(type="text", text=json.dumps({"id": partner_id, "success": True}, indent=2))])
        
        elif name == "odoo_search_invoices":
            result = await client.search_read("account.move", arguments.get("domain", []), arguments.get("fields"), arguments.get("limit", 20))
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "odoo_create_invoice":
            # Prepare invoice lines
            invoice_lines = []
            for line in arguments["invoice_line_ids"]:
                line_vals = {
                    "name": line["name"],
                    "quantity": line.get("quantity", 1),
                    "price_unit": line["price_unit"],
                }
                if "product_id" in line:
                    line_vals["product_id"] = line["product_id"]
                if "tax_ids" in line:
                    line_vals["tax_ids"] = [(6, 0, line["tax_ids"])]
                invoice_lines.append((0, 0, line_vals))
            
            invoice_vals = {
                "partner_id": arguments["partner_id"],
                "move_type": arguments.get("move_type", "out_invoice"),
                "invoice_line_ids": invoice_lines,
            }
            if arguments.get("invoice_date"):
                invoice_vals["invoice_date"] = arguments["invoice_date"]
            
            invoice_id = await client.create("account.move", invoice_vals)
            return CallToolResult(content=[TextContent(type="text", text=json.dumps({"id": invoice_id, "success": True}, indent=2))])
        
        elif name == "odoo_post_invoice":
            await client.execute_kw("account.move", "action_post", [[arguments["invoice_id"]]])
            return CallToolResult(content=[TextContent(type="text", text=json.dumps({"success": True, "message": "Invoice posted"}, indent=2))])
        
        elif name == "odoo_register_payment":
            # Create payment wizard
            payment_vals = {
                "amount": arguments["amount"],
                "payment_date": arguments.get("payment_date") or datetime.now().strftime("%Y-%m-%d"),
                "journal_id": arguments["journal_id"],
                "payment_method_id": arguments.get("payment_method_id"),
                "partner_id": (await client.search_read("account.move", [["id", "=", arguments["invoice_id"]]], ["partner_id"]))[0]["partner_id"][0],
                "payment_type": "inbound",
                "partner_type": "customer",
            }
            payment_id = await client.create("account.payment", payment_vals)
            # Post the payment
            await client.execute_kw("account.payment", "action_post", [[payment_id]])
            return CallToolResult(content=[TextContent(type="text", text=json.dumps({"id": payment_id, "success": True}, indent=2))])
        
        elif name == "odoo_search_products":
            result = await client.search_read("product.product", arguments.get("domain", []), arguments.get("fields"), arguments.get("limit", 20))
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "odoo_create_product":
            product_id = await client.create("product.product", arguments)
            return CallToolResult(content=[TextContent(type="text", text=json.dumps({"id": product_id, "success": True}, indent=2))])
        
        elif name == "odoo_get_accounting_report":
            # This would require custom report logic based on Odoo version
            # For now, return a placeholder
            return CallToolResult(content=[TextContent(type="text", text=json.dumps({
                "report": arguments["report_name"],
                "date_from": arguments.get("date_from"),
                "date_to": arguments.get("date_to"),
                "message": "Accounting reports require Odoo 19+ with specific report models. Implement based on your Odoo version."
            }, indent=2))])
        
        elif name == "odoo_search_payments":
            result = await client.search_read("account.payment", arguments.get("domain", []), arguments.get("fields"), arguments.get("limit", 20))
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
        
        elif name == "odoo_get_dashboard_data":
            # Get key metrics
            date_from = arguments.get("date_from") or "2024-01-01"
            date_to = arguments.get("date_to") or datetime.now().strftime("%Y-%m-%d")
            
            # Total invoices
            invoices = await client.search_read("account.move", [
                ["move_type", "in", ["out_invoice", "out_refund"]],
                ["invoice_date", ">=", date_from],
                ["invoice_date", "<=", date_to],
                ["state", "!=", "cancel"]
            ], ["amount_total", "amount_residual", "state", "payment_state"])
            
            # Total payments
            payments = await client.search_read("account.payment", [
                ["date", ">=", date_from],
                ["date", "<=", date_to],
                ["state", "=", "posted"]
            ], ["amount"])
            
            total_invoiced = sum(inv["amount_total"] for inv in invoices)
            total_paid = sum(p["amount"] for p in payments)
            outstanding = sum(inv["amount_residual"] for inv in invoices if inv["payment_state"] != "paid")
            
            return CallToolResult(content=[TextContent(type="text", text=json.dumps({
                "period": {"from": date_from, "to": date_to},
                "total_invoiced": total_invoiced,
                "total_paid": total_paid,
                "outstanding": outstanding,
                "invoice_count": len(invoices),
                "payment_count": len(payments),
                "invoices_by_state": {},
                "invoices_by_payment_state": {}
            }, indent=2))])
        
        else:
            return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")])
    
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=f"Error: {str(e)}")])


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())