
# Indian Banks API

This project provides a comprehensive API for accessing information about Indian bank branches. It offers both RESTful and GraphQL endpoints, allowing for flexible querying of a dataset containing over 127,000 bank branches across India.

The application is built with Flask and uses a SQLite database to store the bank branch data. On the first run, it automatically downloads the necessary data from a public GitHub repository.

## Features

- **RESTful API:** A set of REST endpoints for standard CRUD operations.
- **GraphQL API:** A GraphQL endpoint for more flexible and efficient data querying.
- **Data-rich:** Provides detailed information for each branch, including IFSC, branch name, address, city, district, and state.
- **Search Functionality:** Endpoints for searching branches based on various criteria.
- **Pagination:** Support for paginating through large result sets.
- **Statistics:** An endpoint to get statistics about the dataset.
- **Automatic Data Loading:** Automatically downloads and loads the bank branch data on the first run.

## Project Structure

```
/app
  /config.py
  /database.py
  /models.py
  /routes.py
  /schema.py
/__init__.py
/run.py
```

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8+
- Git

## Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/surajssc1232/indian_banks_api.git
   cd your-repo-name
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

    or

   ```bash
   uv pip install -r requirements.txt
   ```

## Running the Application

To start the Flask server, run the following command:

```bash
python run.py
```

The application will be available at `http://0.0.0.0:5000`.

## API Endpoints

### REST API

- `GET /api/banks`: Get all banks (with pagination).
- `GET /api/banks/<bank_id>/branches`: Get branches for a specific bank.
- `GET /api/branches`: Get all branches (supports filtering & pagination).
- `GET /api/branches/<ifsc>`: Get a specific branch by IFSC code.
- `GET /api/search?q=<term>`: Search across all fields.
- `GET /api/stats`: Get database statistics.

### GraphQL API

- `POST /gql`: GraphQL endpoint.
- `GET /gql`: GraphiQL interface for testing.

## Data

The bank branch data is sourced from the [indian_banks](https://github.com/snarayanank2/indian_banks) GitHub repository. The application automatically downloads and loads the data from the `bank_branches.csv` file in that repository into a local SQLite database (`indian_banks.db`).
