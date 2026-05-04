# Spendly – Expense Tracker

A simple, user-friendly expense tracking application built with Flask and SQLite. Track your spending by category, filter expenses by date range, and manage your personal finances with ease.

## Features

- **User Authentication**: Secure registration and login with password hashing
- **Expense Management**: Add, view, and track expenses by category
- **Dashboard**: Profile page showing:
  - Total spending and expense count
  - Recent expenses (latest 6)
  - Spending breakdown by category
  - Member since date
- **Date Filtering**: Filter expenses by custom date ranges
- **Categories**: Pre-defined expense categories (Food, Transport, Bills, Health, Entertainment, Shopping, Other)
- **Data Persistence**: SQLite database for reliable data storage

## Tech Stack

- **Backend**: Python 3 with Flask 3.1.3
- **Database**: SQLite
- **Security**: Werkzeug for password hashing and session management
- **Testing**: pytest and pytest-flask

## Project Structure

```
expense-tracker/
├── app.py                  # Main Flask application and routes
├── database/
│   ├── __init__.py
│   ├── db.py              # Database initialization and seeding
│   └── seed_user.py       # User seeding utilities
├── templates/
│   ├── base.html          # Base template with navigation
│   ├── landing.html       # Public landing page
│   ├── register.html      # User registration form
│   ├── login.html         # User login form
│   ├── profile.html       # User dashboard and expense overview
│   ├── terms.html         # Terms of service
│   └── privacy.html       # Privacy policy
├── requirements.txt       # Python dependencies
├── spendly.db            # SQLite database (generated at runtime)
└── README.md             # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone or navigate to the project directory**
   ```bash
   cd expense-tracker
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv myvenv
   ```

3. **Activate the virtual environment**
   - **Windows**:
     ```bash
     myvenv\Scripts\Activate.ps1
     ```
   - **macOS/Linux**:
     ```bash
     source myvenv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the development server**
   ```bash
   python app.py
   ```
   The application will be available at `http://localhost:5001`

2. **Demo login credentials** (auto-seeded)
   - Email: `demo@spendly.com`
   - Password: `demo123`

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
)
```

### Expenses Table
```sql
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    date TEXT NOT NULL,
    description TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```

## API Routes

### Public Routes
- `GET /` – Landing page
- `GET /terms` – Terms of service
- `GET /privacy` – Privacy policy
- `GET /register` – Registration page
- `POST /register` – Submit registration form
- `GET /login` – Login page
- `POST /login` – Submit login credentials

### Authenticated Routes
- `GET /profile` – User dashboard and expense overview
- `GET /logout` – Clear session and redirect to landing page
- `GET /expenses/add` – Add new expense (in development)
- `GET /expenses/<id>/edit` – Edit existing expense (in development)
- `GET /expenses/<id>/delete` – Delete expense (in development)

### Profile Route Parameters
The profile page supports optional query parameters for date filtering:
- `start_date=YYYY-MM-DD` – Filter expenses from this date onward
- `end_date=YYYY-MM-DD` – Filter expenses up to this date

Example: `/profile?start_date=2026-04-01&end_date=2026-04-30`

## Form Validation

### Registration
- Name: Required, max 100 characters
- Email: Required, must contain "@", max 255 characters
- Password: Required, minimum 8 characters
- Email uniqueness: Enforced (prevents duplicate accounts)

### Login
- Email and password: Both required
- Authentication: Uses secure password hashing

## Session Management

- Sessions use Flask's session object with a secret key
- User ID and username stored in session upon login
- Sessions cleared on logout
- Unauthenticated users redirected to login page when accessing protected routes

## Development Notes

- **Secret Key**: Currently set to a development key. Change this in production.
- **Debug Mode**: Enabled by default in `app.py`
- **Port**: Application runs on port 5001
- **Database Location**: `spendly.db` created in the project root directory

## Testing

Run tests with pytest:
```bash
pytest
```

## Future Features

- Expense add, edit, and delete functionality
- Export expenses to CSV
- Monthly spending reports
- Budget goals and alerts
- Multi-currency support
- Recurring expense templates

## Security Considerations

- Passwords are hashed using Werkzeug's `generate_password_hash()`
- SQL injections prevented through parameterized queries
- Session-based authentication
- **Production Note**: Change `app.secret_key` to a secure, randomly generated value for production deployment

## License

This project is provided as-is for educational and personal use.

## Support

For issues, questions, or contributions, please refer to the project repository or contact the development team.
