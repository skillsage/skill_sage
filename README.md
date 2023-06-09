# skill_sage

This repository contains a FastAPI project for skill recommendation. FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints.

## Skill Sage Setup

To set up the project after cloning, please follow the instructions below:

### Prerequisites

Make sure you have the following prerequisites installed on your system:

- Python 3.7+
- pip (Python package installer)

### Installation

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/your-username/fastapi-project.git
   ```

2. Change into the project directory:
    ```bash
    cd fastapi-project
    ```

### Running Skill Sage

1. Create a virtual environment (optional but recommended):

    ```bash
    python3 -m venv venv
    ```

2. Activate the virtual environment:

    ```bash
    source venv/bin/activate   # On Unix or Linux
    .\venv\Scripts\activate    # On Windows
    ```

3. Install the project dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Start the FastAPI development server:

    ```bash
    uvicorn main:app --reload
    ```

5. Open a web browser and visit [doc](http://localhost:8000/docs) to access the automatically generated Swagger UI documentation for the API. The server runs on port 8000 by default, but you can modify this in the main.py file if necessary.



