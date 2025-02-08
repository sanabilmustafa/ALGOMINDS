from multiprocessing import Process
import os

def run_client():
    os.system("python3 client.py")

def run_app():
    # from app import app  # Assuming you are using Flask and your app instance is called 'app'
    # app.run(debug=True)
    os.system("python3 app.py")


if __name__ == '__main__':
    # Run client.py in a separate process
    client_process = Process(target=run_client)
    client_process.start()

    # Run the Flask app in the main process
    run_app()
        