# Import uvicorn, the program that runs our web server
import uvicorn

# This block runs only when we start this file directly with: python run.py
if __name__ == "__main__":
    # Start the server from the file app/main.py, object "app". reload=True restarts it when we save a file
    uvicorn.run("app.main:app", reload=True)