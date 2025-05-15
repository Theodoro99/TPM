# PreventPlus - Total Preventive Maintenance System

![PreventPlus Logo](https://img.shields.io/badge/PreventPlus-TPM-orange)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## Overview

PreventPlus is a comprehensive Total Preventive Maintenance (TPM) system designed to streamline maintenance operations, track equipment status, and improve overall operational efficiency. Built with a modern, responsive UI and a robust backend, PreventPlus helps organizations manage maintenance tasks, track equipment history, and generate insightful reports.

## Features

- **User Management**: Role-based access control with admin, manager, and technician roles
- **Maintenance Logbook**: Track all maintenance activities with detailed entries
- **Dashboard**: Real-time overview of maintenance status with key metrics
- **Equipment Tracking**: Monitor equipment status, downtime, and maintenance history
- **Location Management**: Organize equipment by location with hierarchical structure
- **Reporting System**: Generate customized reports with scheduling capabilities
- **File Attachments**: Attach relevant documents and images to maintenance entries
- **Audit Logging**: Track all system activities for compliance and security

## Technology Stack

- **Frontend**: Flet (Flutter-based Python UI framework)
- **Backend**: Python with SQLAlchemy ORM
- **Database**: SQLite (default) with support for PostgreSQL
- **Authentication**: Built-in user authentication system

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/TPM.git
   cd TPM
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (optional):
   Create a `.env` file in the project root with the following variables:
   ```
   DATABASE_URL=sqlite:///./preventplus.db
   PORT=8558
   ```

5. Run the application:
   ```bash
   python main.py
   ```

## Usage

1. Access the application at `http://localhost:8558` (or the port you configured)
2. Log in with the default admin credentials:
   - Username: `admin`
   - Password: `admin`
3. Navigate through the dashboard to access different features

## Project Structure

```
TPM/
├── app/                    # Application code
│   ├── api/                # API endpoints
│   ├── core/               # Core functionality
│   ├── db/                 # Database models and connection
│   ├── schemas/            # Data validation schemas
│   ├── services/           # Business logic services
│   ├── ui/                 # User interface components
│   │   └── views/          # UI views
│   └── utils/              # Utility functions
├── main.py                 # Application entry point
├── preventplus.db          # SQLite database
└── README.md               # Project documentation
```

## Development

### Adding New Features

1. Create appropriate models in `app/db/models.py`
2. Implement business logic in `app/services/`
3. Create UI components in `app/ui/`
4. Update the main application flow in `main.py`

### Database Migrations

The application uses SQLAlchemy's declarative base for database models. When changing models:

1. Update the model definitions in `app/db/models.py`
2. The changes will be applied automatically when the application starts

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, feature requests, or bug reports, please open an issue on the GitHub repository or contact the development team.

---

 2025 PreventPlus. All rights reserved.