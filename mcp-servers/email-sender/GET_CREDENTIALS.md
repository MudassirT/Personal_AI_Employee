Gmail API Credential Setup

1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create or select a project
3. Enable the Gmail API for the project
4. Create OAuth 2.0 Client Credentials (Application type: Desktop)
5. Download the `credentials.json` file and place it in this folder:

   mcp-servers/email-sender/credentials.json

6. Run the Email MCP server once; it will open a browser to authorize and
   create `token.json` in this folder:

```bash
cd mcp-servers/email-sender
python email_mcp_server.py
```

7. After authorization, the server can be run as an HTTP MCP server:

```bash
python email_mcp_server.py
# POST to http://127.0.0.1:8765/tool with JSON {"tool":"send_email","args":{...}}
```

Notes:
- Keep `credentials.json` and `token.json` secure and do not commit them to git.
- If you prefer SMTP, set `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, and `SMTP_PASSWORD` as environment variables.
