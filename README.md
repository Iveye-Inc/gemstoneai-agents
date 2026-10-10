# GemstoneAI for Agents

GemstoneAI is a hosted remote MCP server that lets an AI assistant help someone with a piece of jewelry they own. The assistant can:

- analyze 1 to 5 photos of the piece and give a preliminary identification, with its alternatives, unknowns and the evidence that would settle them
- show photographed comparable listings and sales, each labelled as an asking price or a realized sale
- save the piece to the person's GemstoneAI collection, so it opens in the GemstoneAI app on their phone

```
https://api.gemstoneaiapp.com/mcp
```

There is nothing to install or run. Product page: [gemstoneaiapp.com/agents](https://gemstoneaiapp.com/agents).

## Connect

Add the URL as a remote (Streamable HTTP) MCP server in any client that supports one. The client discovers sign-in on its own. The person signs in with the email they use in the GemstoneAI app, so the collection is the same; a new email gets a free account. Each new analysis uses a scan from that account's plan, the same as in the app.

**Claude Code**, as a plugin (adds the server and a jewelry-research skill):

```
/plugin marketplace add Iveye-Inc/gemstoneai-agents
/plugin install gemstoneai@gemstoneai
```

**Claude Code**, server only:

```bash
claude mcp add --transport http gemstoneai https://api.gemstoneaiapp.com/mcp
```

Then run `/mcp` in Claude Code to sign in.

**Other clients** (Claude on the web and desktop, ChatGPT developer mode, Cursor, VS Code, MCP Inspector): add a remote MCP server with the URL above and sign in when prompted.

Client support is listed on the product page. A client is marked tested only after the full journey (photo, analysis, comparables, save, reopen in the app) has passed in it.

## Tools

| Tool | What it does | Annotations |
|---|---|---|
| `analyze_jewelry` | Preliminary analysis of 1 to 5 photos of one piece. Takes `photos` (attached files) or `image_urls` (public https), and an optional `idempotency_key`. With no photos it returns an upload link the person opens on their phone. | writes, not destructive, idempotent, open world |
| `get_jewelry_analysis` | Status or completed result of an analysis. Waits up to about 40 seconds while it is processing. | read-only |
| `find_jewelry_comparables` | Photographed market listings and sales with source, link, price, price type, date found and the material differences from this piece. | read-only, open world |
| `save_collection_item` | Saves the analyzed piece to the signed-in person's collection and returns a link that opens it in the app. | writes, not destructive, idempotent |

Results never carry numeric confidence. Uncertainty comes as alternatives, unknowns and next evidence. When GemstoneAI's own reads disagree about what the stone is, price context is withheld with the reason. When no priced comparables are found, the answer is "none found", never a value of zero.

## Protocol and authentication

- Streamable HTTP, stateless, JSON responses. Initialize-based clients (protocol 2024-11-05 to 2025-11-25) and 2026-07-28 clients are supported.
- OAuth 2.1 with PKCE (S256). Discovery: `/.well-known/oauth-protected-resource/mcp` and `/.well-known/oauth-authorization-server` on `api.gemstoneaiapp.com`.
- Clients register with Client ID Metadata Documents or dynamic client registration. Loopback redirects may use any port.
- Tokens are bound to one person, one client and this server (RFC 8707). Access tokens last an hour; refresh tokens rotate.
- Scopes: `jewelry:analyze` and `collection:write`.

## Latency and limits

- An analysis typically takes 20 to 45 seconds. `analyze_jewelry` waits up to about 40 seconds, then returns `processing` with a retry interval. Comparables usually follow within a minute.
- Repeating the same photos, or the same `idempotency_key`, returns the same analysis and is not charged twice.
- During the pilot there are daily evaluation limits per account and per integration. Developers can request pilot access on the [product page](https://gemstoneaiapp.com/agents#pilot).

## What it is not

Results are preliminary analyses from photographs. They are not appraisals and do not establish authenticity, treatment, origin or certified value. The server never buys, sells, lists or contacts anyone, and it saves to a collection only when asked.

## Privacy

Photos are used to analyze the piece and are kept with it in the person's GemstoneAI account, like a scan in the app. Location data is removed from every photo. See the [Privacy Policy](https://gemstoneaiapp.com/privacy) and [Terms](https://gemstoneaiapp.com/terms).

## Repository layout

- `.claude-plugin/marketplace.json`, `plugins/gemstoneai/`: the Claude Code plugin (MCP server config and the jewelry-research skill)
- `openai/`: the ChatGPT plugin package source; `python scripts/build_openai_zip.py` builds the ZIP
- `server.json`: the entry in the [official MCP Registry](https://registry.modelcontextprotocol.io/v0.1/servers?search=com.gemstoneaiapp), published with `scripts/publish_registry.py`

## Support

gemstoneaiapp@gmail.com
