# Float — Counter Staff Installation & Daily Shift Guide

This guide is written for counter staff and branch supervisors. You do not need any programming knowledge to install or run Float.

---

## 1. Installing and Opening Float (First Time)

### On Windows (10 or 11)
1. Unzip the **Float** folder onto your Desktop or `C:\Float`.
2. Double-click **`Start Float.bat`** (or **`Float.vbs`** for silent background mode without a command window).
3. If Python 3.10+ is not installed yet, Float will show a one-line message telling you where to install it from `python.org`. No extra packages (`pip`) or internet downloads are required.
4. Float opens automatically in your browser at **`http://127.0.0.1:8766`**.

### On macOS (Apple Silicon or Intel)
1. Open the **`Float-macOS.dmg`** disk image (or unzip **`Float-macOS.zip`**) and drag **`Float.app`** to **Applications**.
2. Double-click **`Float.app`** (or **`Start Float.command`**).
3. Your browser opens **`http://127.0.0.1:8766`** automatically.

### On a Multi-Desk Branch (Agency Server Mode)
If your branch manager runs Float on the main counter computer in Agency Server mode:
- Do **not** install anything on your desk PC.
- Open Chrome, Edge, or Safari and go to the address written on your counter card (for example `https://192.168.1.25:8766`).
- Sign in with the email and temporary password your manager gave you, choose your own password, and set a **4-to-8 digit Quick PIN** under **Settings → Security** for 1-second sign-in between customers.

---

## 2. Daily Counter Workflow

Click **Enterprise Ops Hub** in the top bar of Float to open the 6-tab operations console:

### Step A — Check Morning Alerts (`Fleet & Compliance` tab)
- At the start of your shift, check the **Compliance & Expiry Alerts** banner at the top of the **Fleet & Compliance** tab.
- Any vehicle with expiring **Insurance**, **PUC**, **Fitness Certificate**, **Permit**, low **FASTag** balance (< ₹500), or overdue **Periodic Service** is highlighted automatically so you do not dispatch a non-compliant car.

### Step B — Onboard the Customer (`Customers & DPDP` tab)
1. Enter the customer's **Full Name**, **Mobile Number**, **Driving Licence Number**, **DL Expiry Date**, and **Government ID Proof**.
2. Confirm the **DPDP Act, 2023 Consent** checkbox after informing the customer why their Driving Licence and ID are recorded.
3. Click **Save Customer Profile**.
   - *Note:* Float automatically blocks self-drive bookings if the customer's Driving Licence expires before the trip return date.

### Step C — Check Availability & Create a Booking (`Bookings & Timeline` tab)
1. Enter the **Pickup** and **Return** date/time and click **Search Available Vehicles** to see cars with zero schedule conflicts.
2. Select the **Vehicle** and **Customer**, enter Pickup and Return timestamps, and click **Confirm Booking**.
   - Float prevents double-booking the same vehicle or chauffeur across overlapping times.
   - If you apply a discount or change the daily rate, you must enter the **Override Reason** and **Approving Manager** (logged in the audit trail).

### Step D — Collect Advance & Security Deposit (`Money, GST & Shift` tab)
1. Select the booking, choose **Advance** or **Security Deposit**, pick the payment mode (**UPI**, **Cash**, **Card**, **NEFT**, **RTGS**), enter the **UTR / Reference No.**, and click **Record Payment**.

### Step E — Vehicle Handover (`Bookings & Timeline` & `Workshop, Damage & Sign` tabs)
1. Inspect the car with the customer. If there are existing scratches or dents, log them under **Workshop, Damage & Sign**.
2. Have the customer sign the signature pad under **Digital Signature Capture** and click **Capture & Seal Signature**.
3. In **Bookings & Timeline**, click **Mark Picked Up** on the booking.

### Step F — Vehicle Return, Settlement & GST Invoice
1. When the car returns, click **Return Vehicle** on the booking and enter the **Closing Odometer (km)**.
2. If new damage occurred, log it under **Workshop, Damage & Sign**.
3. Go to **Money, GST & Shift**:
   - Record the final settlement payment or security deposit refund.
   - Click **Issue Immutable GST Invoice** to generate the sequential GST invoice (`FLT/YYYY-YY/NNNNN`).
   - *Important:* Once issued, a GST invoice is locked and cannot be edited or deleted. If a billing correction is needed later, ask your Accountant or Manager to click **Issue Credit Note**.

### Step G — End-of-Shift Cash Drawer Handover (`Money, GST & Shift` tab)
1. Count the physical cash in your drawer.
2. Under **Daily Collections & Shift Reconciliation**, verify the **Opening Drawer Cash**, enter your **Counted Closing Cash**, and click **Close & Reconcile Shift**.
3. Float calculates expected cash (`Opening Cash + Cash Collected − Cash Refunded`) and logs any variance for the branch manager.

---

## 3. Troubleshooting at the Counter

- **Forgot your PIN or password?** Ask your Branch Owner/Admin to click **Reset password** next to your name in the **Admin → Team & Agents** tab.
- **Power cut or PC restart mid-shift?** Simply start Float again. Float uses crash-safe SQLite Write-Ahead Logging (`WAL`), so completed bookings, payments, and GST invoices are preserved automatically.
