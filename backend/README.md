**Backend Setup**
   1. Open a new terminal and navigate to the backend directory
      ```bash
      cd backend
       ```
   2. Create and activate a Python virtual environment:
      ```bash
      python -m venv .venv
       .venv\Scripts\activate  # On Windows
       # source venv/bin/activate  # On macOS/Linux
       ```
   3. Install Python dependencies
      ```bash
      pip install -r requirements.txt
       ```
   4. Start the backend server
       ```bash
       fastapi dev main.py
       ```
   The backend will be available at http://127.0.0.1:8000/.