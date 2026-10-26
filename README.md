# 🚌 Cloud-Based Bus Pass Management System

A web-based bus pass management application built using **Python, Flask, and MySQL**. The system allows users to submit bus pass applications, track their application status, and download approved bus passes as PDF documents with QR-code verification.

> **Project Status:** Core functionality implemented and tested locally. Cloud deployment, production security hardening, and project documentation are planned next.

---

## 📌 Table of Contents

- [About the Project](#-about-the-project)
- [Project Objectives](#-project-objectives)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Database Information](#-database-information)
- [Prerequisites](#-prerequisites)
- [Installation and Setup](#-installation-and-setup)
- [Environment Variables](#-environment-variables)
- [Running the Application](#-running-the-application)
- [Application Routes](#-application-routes)
- [Testing and Verification](#-testing-and-verification)
- [Current Progress](#-current-progress)
- [Future Roadmap](#-future-roadmap)
- [Security Considerations](#-security-considerations)
- [Contributing](#-contributing)
- [License](#-license)

---

## 📖 About the Project

The Cloud-Based Bus Pass Management System is designed to simplify the process of applying for, managing, tracking, and verifying bus passes.

The application provides a user-facing interface for submitting applications and checking their status. An administrator can review applications and approve or reject them.

Approved applications can be used to generate downloadable PDF bus passes containing applicant details and a QR code for verification.

The application currently runs locally using Flask and a MySQL database. Cloud hosting and public internet access are planned future improvements.

---

## 🎯 Project Objectives

- Digitize the bus pass application process.
- Store application records in a MySQL database.
- Allow users to track application status.
- Provide an administrator interface for reviewing applications.
- Generate PDF bus passes for approved applicants.
- Use QR codes to make bus pass verification easier.
- Prepare the application for future cloud deployment.

---

## ✨ Features

### 1. Bus Pass Application

- Web-based application form.
- Collects applicant information, including name, phone number, email, category, address, route, pass type, and start date.
- Validates required fields and selected options.
- Saves new applications in MySQL.
- Generates an application ID for tracking.

### 2. Application Tracking

- Users can search for an application using its application ID.
- Displays application information and status.
- Supports checking pending, approved, and rejected applications.

### 3. Administrator Login

- Separate administrator login page.
- Session-based authentication.
- Password hashing for administrator password verification.
- Access control for administrator-only routes.

### 4. Admin Dashboard

- Displays submitted applications.
- Shows application statistics.
- Lists applications in descending ID order.
- Allows administrators to approve or reject applications.

### 5. PDF Bus Pass Generation

- Generates a downloadable PDF for approved applications.
- Includes applicant details, pass ID, route, pass type, start date, issue date, and approval status.
- Provides a QR code for verification.

### 6. QR Code Verification

- Generates a QR code linked to the bus pass verification route.
- Retrieves the corresponding application from MySQL.
- Displays pass details and status on the verification page.
- Returns a not-found response if the application does not exist.

### 7. MySQL Database Integration

- Uses MySQL instead of SQLite for the active application database.
- Centralizes database connection configuration in `db_config.py`.
- Reads the MySQL password from an environment variable.
- Migrated seven existing application records from the original SQLite database to MySQL.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web application framework |
| MySQL | Relational database |
| MySQL Connector/Python | Python-to-MySQL connectivity |
| HTML | Web page structure |
| CSS | Web page styling |
| Jinja2 | Flask HTML templating |
| Werkzeug Security | Password hashing and verification |
| ReportLab | PDF bus pass generation |
| qrcode | QR code generation |
| Git | Version control |
| GitHub | Source code hosting |
| Visual Studio Code | Development environment |

---

## 📂 Project Structure

```text
Cloud-Based-Bus-Pass-System/
│
├── app.py
├── app_backup.py
├── db_config.py
├── migrate_data.py
├── test_db_config.py
├── test_mysql.py
├── .gitignore
├── README.md
│
├── templates/
│   ├── index.html
│   ├── track.html
│   ├── admin_login.html
│   ├── admin.html
│   └── verify_pass.html
│
├── venv/                  # Local Python virtual environment
├── buspass.db             # Original SQLite database, if retained locally
└── buspass_backup.db      # SQLite backup, if retained locally
```

**Note:** The `venv/` directory and local SQLite database files should not be committed to GitHub. The database files are retained locally for backup and migration purposes.

---

## 🗄️ Database Information

### Database Name

```text
buspass_db
```

### Table Name

```text
applications
```

### Table Schema

| Column | Data Type | Description |
|---|---|---|
| `id` | INT, AUTO_INCREMENT, PRIMARY KEY | Unique application ID |
| `full_name` | VARCHAR(100) | Applicant's full name |
| `phone` | VARCHAR(20) | Contact number |
| `email` | VARCHAR(100) | Email address |
| `category` | VARCHAR(50) | Applicant category |
| `address` | TEXT | Applicant address |
| `route` | VARCHAR(100) | Selected bus route |
| `pass_type` | VARCHAR(50) | Type of bus pass |
| `start_date` | DATE | Requested start date |
| `status` | VARCHAR(20) | Application status |
| `created_at` | TIMESTAMP | Application creation time |

The `status` column defaults to `Pending`.

### Create the Database

Open MySQL Workbench and execute:

```sql
CREATE DATABASE IF NOT EXISTS buspass_db;
USE buspass_db;
```

If the `applications` table does not exist, create it using:

```sql
CREATE TABLE IF NOT EXISTS applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    category VARCHAR(50),
    address TEXT,
    route VARCHAR(100),
    pass_type VARCHAR(50),
    start_date DATE,
    status VARCHAR(20) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Important:** If you already have the database and table containing application records, do not drop or recreate them. The commands above use `IF NOT EXISTS` to preserve existing tables and records.

---

## 💻 Prerequisites

Install the following software before running the project:

- Python 3
- MySQL Server
- MySQL Workbench (recommended for database management)
- Git
- Visual Studio Code (recommended)

You also need a MySQL account with permission to access `buspass_db`.

---

## ⚙️ Installation and Setup

### Step 1: Clone the Repository

Replace the repository URL below if your GitHub repository has a different address.

```bash
git clone https://github.com/bhanukaushik1808-source/Cloud-Based-Bus-Pass-System-CodeAlpha-.git
```

Move into the project directory:

```bash
cd Cloud-Based-Bus-Pass-System-CodeAlpha-
```

### Step 2: Create a Virtual Environment

On Windows using Git Bash:

```bash
python -m venv venv
source venv/Scripts/activate
```

On Windows using Command Prompt:

```bat
venv\Scripts\activate
```

### Step 3: Install Python Dependencies

Run:

```bash
python -m pip install Flask mysql-connector-python qrcode[pil] reportlab
```

The project also uses Python standard-library modules and Werkzeug, which is installed as a Flask dependency.

### Step 4: Configure MySQL

1. Start MySQL Server.
2. Open MySQL Workbench.
3. Create or verify the `buspass_db` database.
4. Create or verify the `applications` table.
5. Ensure your MySQL account has the necessary permissions.

### Step 5: Configure Environment Variables

The application expects these environment variables:

| Variable | Purpose |
|---|---|
| `MYSQL_PASSWORD` | Password for the MySQL account |
| `FLASK_SECRET_KEY` | Flask session signing key |
| `BUSPASS_ADMIN_USER` | Administrator username |
| `BUSPASS_ADMIN_PASSWORD` | Administrator password |

For Git Bash, set them in the current terminal session.

Generate a Flask secret key:

```bash
export FLASK_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
```

Set the administrator username:

```bash
export BUSPASS_ADMIN_USER="admin"
```

Set the administrator password securely:

```bash
read -s -p "Admin password: " BUSPASS_ADMIN_PASSWORD
echo
export BUSPASS_ADMIN_PASSWORD
```

Set the MySQL password:

```bash
read -s -p "MySQL password: " MYSQL_PASSWORD
echo
export MYSQL_PASSWORD
```

Enter your actual passwords when prompted. Do not put passwords directly in source code or upload them to GitHub.

**Important:** These commands set variables only for the current terminal session. If you close the terminal, you may need to set them again.

### Step 6: Verify the Database Connection

Run:

```bash
python test_db_config.py
```

The test should confirm that the application can connect to MySQL and retrieve the application count.

If the connection fails, verify that MySQL is running, the database exists, and `MYSQL_PASSWORD` is correct.

---

## ▶️ Running the Application

Once the database is configured and the environment variables are set, run:

```bash
python app.py
```

Open the application in your browser:

**Home page**

http://65.2.37.2

**Application tracking**

http://65.2.37.2/track

**Administrator login**

http://65.2.37.2/admin/login

The application runs locally on port `5000`.

The Flask development server is intended for development and testing, not production hosting.

---

## 🔗 Application Routes

| Route | Method | Purpose |
|---|---|---|
| `/` | GET, POST | Display and submit the application form |
| `/track` | GET, POST | Track an application |
| `/admin/login` | GET, POST | Administrator login |
| `/admin` | GET | Administrator dashboard |
| `/admin/update/<application_id>` | POST | Approve or reject an application |
| `/download-pass/<application_id>` | GET | Download an approved bus pass as PDF |
| `/verify-pass/<application_id>` | GET | Verify a bus pass |
| `/admin/logout` | POST | Log out the administrator |

---

## 🧪 Testing and Verification

The following functionality has been tested locally:

- [x] Flask application starts successfully.
- [x] MySQL connection succeeds.
- [x] Seven existing application records were migrated from SQLite to MySQL.
- [x] New application submission works.
- [x] Application tracking works.
- [x] Administrator login works.
- [x] Application approval has been tested.
- [x] PDF bus pass download works.
- [x] QR code verification works after fixing a missing return statement.
- [x] Python syntax check passes using `python -m py_compile app.py`.

### Recommended Additional Tests

- [ ] Test rejection of an application.
- [ ] Verify all application statuses persist after restarting Flask.
- [ ] Test invalid and nonexistent application IDs.
- [ ] Test access to administrator routes without logging in.
- [ ] Test QR verification from another device on the same network.
- [ ] Perform a complete regression test after cloud deployment.

---

## 📈 Current Progress

### Completed

- Flask application and HTML templates.
- Application submission and tracking.
- Administrator authentication and dashboard.
- Approval and rejection workflow.
- MySQL connection configuration.
- Migration of existing SQLite records.
- PDF bus pass generation.
- QR code verification.
- Git repository initialization and initial source-code commit.

### In Progress / Planned

- Complete regression testing.
- Finalize repository documentation.
- Improve production security and configuration.
- Prepare a deployment-ready dependency file.
- Configure cloud hosting and a hosted MySQL database.
- Deploy and test the public website.
- Prepare final project diagrams and report.

---

## 🚀 Future Roadmap

### Phase 1: Complete Testing

- Test every user and administrator workflow.
- Verify database persistence.
- Validate error handling.
- Test application behavior with invalid inputs.

### Phase 2: Security Improvements

- Review session and authentication security.
- Keep all secrets outside source code.
- Disable Flask debug mode in production.
- Add CSRF protection to state-changing forms.
- Configure secure cookies and HTTPS for production.
- Review database permissions and input validation.
- Avoid exposing detailed exceptions to end users.

### Phase 3: Project Quality and Maintenance

- Add a `requirements.txt` file.
- Add automated tests.
- Improve error logging.
- Document database migration and backup procedures.
- Review accessibility and responsive design.

### Phase 4: Cloud Deployment

- Choose a suitable hosting provider.
- Configure a production WSGI server.
- Host the Flask application.
- Configure a managed or hosted MySQL database.
- Set production environment variables.
- Configure HTTPS and a public URL.
- Test the complete system after deployment.

### Phase 5: Final-Year Project Documentation

- Prepare the project report.
- Create the system architecture diagram.
- Create an Entity Relationship Diagram (ERD).
- Prepare Data Flow Diagrams (DFDs).
- Create a use-case diagram.
- Add application screenshots and test results.
- Prepare the presentation and viva questions.

### Phase 6: Potential Enhancements

- Email or SMS notifications.
- Search, filtering, and pagination in the admin dashboard.
- Application renewal workflow.
- Pass expiry and validity management.
- Audit logs for administrator actions.
- More detailed reporting and analytics.

These are planned enhancements and are not claimed as existing features.

---

## 🔐 Security Considerations

- Never commit passwords, database credentials, API keys, or secret environment files.
- Keep `.env`, virtual environments, and local database files out of public repositories.
- Use strong administrator credentials.
- Keep the Flask secret key private.
- Never deploy Flask with debug mode enabled.
- Use HTTPS and secure session settings in production.
- Restrict database access to trusted application hosts.
- Back up the database before performing migrations or schema changes.

The current application is configured for local development. Production deployment requires additional security and configuration work.

---

## 🤝 Contributing

Contributions, suggestions, and bug reports are welcome.

A suggested workflow:

1. Fork the repository.
2. Create a feature branch.
3. Make and test your changes.
4. Commit your changes with a descriptive message.
5. Submit a pull request.

---

## 📄 License

No license has been selected yet.

If you plan to publish this project for reuse, choose an appropriate open-source license and add a `LICENSE` file. Until then, do not assume that the repository grants permission to reuse or redistribute the code.

---

## 👨‍💻 Author

**Bhanu Kaushik**

GitHub: [bhanukaushik1808-source](https://github.com/bhanukaushik1808-source)

---

⭐ If you find this project useful, consider starring the repository.
