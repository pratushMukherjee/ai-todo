# Running the Backend

To run the backend from inside the backend directory, use the provided script:

```sh
cd backend
sh run_backend.sh
```

Or, you can run manually with:

```sh
cd backend
PYTHONPATH=.. uvicorn main:app --reload
```

Alternatively, you can run from the project root with:

```sh
uvicorn backend.main:app --reload
```

This ensures all Python imports work correctly.
