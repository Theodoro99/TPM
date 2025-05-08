# PreventPlus(TPM)

A professional Python-based application for managing technical interventions and maintenance logs.

## Features

- Digital logbook for technical interventions
- User management with role-based access control
- File attachments for documentation
- Reporting and analytics
- Search and filtering capabilities
- Modern, responsive UI

## Technology Stack

- **Backend**: Python with FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: Flet (Python UI framework)
- **Authentication**: JWT-based authentication

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables (see `.env.example`)
4. Initialize the database:
   ```
   alembic upgrade head
   ```
5. Run the application:
   ```
   python main.py
   ```

## Project Structure

```
preventplus/
├── alembic/              # Database migrations
├── app/
│   ├── api/              # API endpoints
│   ├── core/             # Core functionality
│   ├── db/               # Database models and connections
│   ├── schemas/          # Pydantic models
│   ├── services/         # Business logic
│   └── ui/               # Flet UI components
├── static/               # Static files
├── tests/                # Test cases
├── .env.example          # Example environment variables
├── alembic.ini           # Alembic configuration
├── main.py               # Application entry point
└── requirements.txt      # Dependencies
```

## Development

### Setting Up Development Environment

1. Create a virtual environment:
   ```
   python -m venv venv
   ```
2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
3. Install development dependencies:
   ```
   pip install -r requirements-dev.txt
   ```

### Running Tests

```
pytest
```

## License

This project is proprietary and confidential.

## Contact

For support or inquiries, please contact the development team.