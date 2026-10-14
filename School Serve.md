# Running Float for a whole school (one server, many PCs)

Float does not copy accounts between computers. **One computer holds every
account, class, chat and file; every other PC just opens it in a browser.** A
teacher is the same person on PC A today and PC F tomorrow because there is only
one copy to log in to. Wired or Wi-Fi both work (wired is steadier).

## 1. Set up the server PC (once)
1. Choose one always-on PC. Give it a fixed address in your router (a DHCP reservation).
2. Double-click **Start Float School Server.bat**. Float prints the address teachers use,
   for example `https://192.168.1.20:8765`.
3. **On that PC itself**, open Float and create the first account (the admin). Float refuses
   to create it from any other PC, so nobody on the network can claim the school.
4. Add teachers from the admin panel (or switch on self sign-up).
5. Allow the port (default 8765) through the Windows firewall for the **private network only**.

## 2. HTTPS (do this before real use)
Without it, passwords cross the network as plain text. Float warns you when it is off.
Make a certificate once (needs OpenSSL, or use the free `mkcert` tool):

    openssl req -x509 -newkey rsa:2048 -nodes -days 825 -keyout data/float.key -out data/float.crt -subj "/CN=float.school.lan"

Then remove `rem` from the two `FLOAT_TLS_...` lines in the .bat file. Browsers show a
one-time warning for a self-made certificate; install `float.crt` as trusted on lab PCs
(or use mkcert, which does this for you) to remove it.
Optional: `FLOAT_ALLOWED_HOSTS=float.school.lan` if teachers use a name instead of an IP.

## 3. Teachers
They open the address in any browser, sign in with their Float email and password,
and close the tab when done. Signing out is automatic after 20 idle minutes
(`FLOAT_IDLE_MINUTES` to change) and when the tab closes.

## Privacy rules built in
- Each teacher sees only their own classes, chats and files.
- **Computer control and "save to Desktop" work only for someone sitting at the server PC.**
  On every other PC Float hides them, and the server refuses them, so one teacher can never
  move another's mouse or see what is on the server screen.
- Google sign-in is removed. Google Drive is switched off in school-server mode, so no
  teacher's Drive login is stored on the shared server. Teachers use **Download**, which saves
  to the PC they are sitting at.
- The admin panel shows usage totals, not what teachers wrote.

## Looking after it
- Accounts and data live in `data/`; Float backs the database up into `data/backups/`.
  Also copy that folder to a USB drive or another PC regularly: a backup on the same disk
  does not survive a dead disk.
- Keep the server PC switched on in school hours. If it is off, nobody can sign in.
- Do not sync `float.sqlite3` with Dropbox, OneDrive or Syncthing: two computers writing to
  one database file corrupt it.

## Not yet tested by the author
Real lab PCs, Wi-Fi drops, many teachers at once, Windows Firewall prompts, and
installing the certificate on lab computers. Try with two or three teachers first.
