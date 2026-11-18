# BIGBREW Management System (Python + Flask + MySQL)

## What changed
- Brand changed from Brew & Bean to BIGBREW.
- Login page now says SIGN IN and links to SIGN UP.
- Staff can create an account; new accounts receive the `cashier` role.
- Logout is available in the navigation bar on every signed-in page.
- Responsive web interface works on desktop, tablet, and mobile browsers.
- Includes dashboard, POS, menu, inventory/restock, sales history, and reports.
- Menu flavors and prices follow the supplied poster.

## Setup in VS Code
1. Install Python 3.9+ and MySQL Server.
2. Start MySQL Server.
3. Open `main.py` and change `DB_CONFIG["password"]` to your MySQL password.
4. Open VS Code terminal in this folder:
   ```bash
   python -m pip install -r requirements.txt
   ```
5. Start:
   ```bash
   python main.py
   ```
6. On the same PC, visit `http://127.0.0.1:5000`.

## Open on a cellphone
- Connect the phone and computer to the same Wi-Fi network.
- Run the app on your computer.
- In the terminal, find the printed line `Phone on same Wi-Fi: http://...:5000`.
- Type that exact address into the phone's browser.
- If Windows Firewall asks, allow Python on Private networks.
- Keep the computer and Python server running while using it on the phone.

This is local-network access, not public internet hosting. For access outside the same Wi-Fi, deploy the app to a secure hosting service and configure production security.

## Demo admin account
- Username: `admin`
- Password: `admin123`

New staff accounts can register from the SIGN UP page. Registration creates cashier-level accounts only.

## Database notes
The app creates `coffee_shop_db` and the needed tables if they do not exist. Existing tables and sales are retained. Menu items are upserted by product code; old menu products not in the poster are marked unavailable rather than deleted.

The supplied poster prices are:
- Milk Tea: Regular ₱29, Large ₱39
- Coffee: Iced Regular ₱29, Iced Large ₱39, Hot ₱39
- Fruit Tea: Regular ₱29, Large ₱39
- BROSTY: Regular ₱49, Large ₱59
- Praf: Regular ₱49, Large ₱59
- Add-ons: ₱9 each; Extra Shot ₱5

The menu poster lists 8 add-ons at ₱9 plus Extra Shot at ₱5.

## Important
The app uses a simple SHA-256 password hash to remain compatible with the earlier academic project database. Before real commercial use, upgrade password storage to a dedicated password-hashing method, set a strong secret key, use HTTPS, add CSRF protection, backups, and access controls.
