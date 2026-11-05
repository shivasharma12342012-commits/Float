# Float Agency Server Guide (LAN Deployment for Car Rental Branches)

Float can run as a **central branch server** on one office PC so every desk agent, dispatcher, and fleet manager on your local network can access the workspace in their browser without installing Python or managing API keys.

---

## 1. Starting the Agency Server

Run from PowerShell or Command Prompt:

```powershell
python main.py --lan
```

Or double-click **`Start Float Agency Server.bat`** on Windows, or **`Start Float Agency Server.command`** on macOS.

Float will bind to `0.0.0.0:8766` and display the local network URL (for example `http://192.168.1.40:8766`).

---

## 2. First-Time Fleet Admin Setup

1. Visit `/login` from the host machine.
2. Create the initial **Admin** account for your rental branch.
3. Open `/admin` to configure:
   - **Agency Name** (e.g. *Apex Car Rentals — Airport Desk*)
   - **Shared AI Key** (OpenRouter, Gemini, OpenAI, Anthropic, Groq, or Local Ollama)
   - **Operator Accounts** (single creation or bulk CSV import)
   - **Default Rental Mode & Vehicle Category**

---

## 3. Resetting an Operator Password from the Host PC

If a desk operator forgets their password, run:

```powershell
python main.py set-password agent@agency.local NewPass123!
```

---

## 4. Security & Backups

- All credentials and API keys are encrypted at rest with machine-bound encryption in `data/float.sqlite3`.
- **Fixed-Desk IP Session Binding (`desk_ip`)**: Every desk operator's login session is locked to their physical counter workstation IP (`desk_ip`), preventing session hijacking across desks.
- **Least-Privilege Controls**: Regular desk operators cannot stop the branch server, view raw agency API keys, unlock host-side computer automation, or alter MCP server configurations.
- Download a complete SQLite backup (`data/float.sqlite3`) or CSV audit log at any time from `/admin`.

---

## 5. CLI Administration & Troubleshooting

Run these commands from the host computer terminal at any time:

```powershell
# Check server health, active PID, and listening address
python main.py status

# Gracefully stop the running Float server
python main.py stop

# Run environment and SQLite diagnostics
python main.py doctor
```
