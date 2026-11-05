# Float Agency Server (LAN Multi-Operator Mode)

Run Float on one central counter or back-office PC so every rental desk agent and fleet manager on the branch Wi-Fi/LAN can sign in from their browser.

## Quick Start

1. Double-click **`Start Float Agency Server.bat`** on Windows, **`Start Float Agency Server.command`** on macOS, or run `python main.py --lan`.
2. Open the printed LAN URL (e.g. `http://192.168.1.25:8766`) on any counter PC or tablet.
3. On first launch, create the **Fleet Admin** account.
4. Open **`/admin`** to set a shared AI API key for the agency and add desk operator accounts (each employee session is automatically bound to their assigned `desk_ip`, and all data is persisted in `data/float.sqlite3`).
5. To stop the server cleanly at the end of the shift, double-click **`Stop Float.bat`** (Windows), **`Stop Float.command`** (macOS), or run `python main.py stop`.
