from flask import Flask, send_from_directory, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

import logging

# Configure logging
logging.basicConfig(
    filename="file_server.log",  # The file where the logs are saved
    level=logging.INFO,          # Log level (INFO is good for this purpose)
    format="%(asctime)s - %(message)s",  # Format for log messages
    datefmt="%Y-%m-%d %H:%M:%S",  # Timeformat
)

app = Flask(__name__)

# The folder to be shared
SHARED_FOLDER = "./shared"

# Using this to set limits
limiter = Limiter(get_remote_address, app=app, default_limits=["100 per minute"])


# The default landing page
@app.route("/")
def index():
    try:
        # List all files in the shared folder
        files = os.listdir(SHARED_FOLDER)

        # Log info about the visist
        client_ip = request.remote_addr  # Get the IP adress of the client
        logging.info(f"{client_ip} has visited the index")

        # Visit index - this is the default path to see the list of files
        return render_template("index.html", files=files)
    except Exception as e:
        logging.error(f"{client_ip} has failed to acces index. Error: {e}")
        return "An error occurred while accessing index.", 500
        

# Download files
@app.route("/download/<filename>")
@limiter.limit("5 per minute") # This means you can only have 5 downloads per minute, change the number if you need it
def download_file(filename):
    try:
        # Log information about the download
        client_ip = request.remote_addr  # Get the ip adress of the client
        logging.info(f"File downloaded: {filename} by {client_ip}")

        # The following lines are protecting against path traversal attacks
        filepath = os.path.abspath(os.path.join(SHARED_FOLDER, filename))
        if not filepath.startswith(os.path.abspath(SHARED_FOLDER)):
            logging.info(f"Path traversal attack tryed by {client_ip}!") # Logg the IP where the attack comes from
            return "Unauthorized access!", 403

        # Download the file
        return send_from_directory(SHARED_FOLDER, filename, as_attachment=True)
    except Exception as e:
        logging.error(f"Error downloading file: {filename} by {client_ip}. Error: {e}")
        return "An error occurred while downloading the file.", 500


# Upload files
@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    try:
        if request.method == "POST":
            file = request.files["file"]
            if file:
                file.save(os.path.join(SHARED_FOLDER, file.filename))

                # Log information about the upload
                client_ip = request.remote_addr
                logging.info(f"File uploaded: {file.filename} by {client_ip}. File uploaded successfully")

                return "File uploaded successfully!"
        return '''
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <input type="submit" value="Upload">
        </form>
        '''
    except Exception as e:
        logging.error(f"Error uploading file: {file.filename} by {client_ip}. Error: {e}")
        return "An error occurred while uploading the file.", 500


# This is for the logs
# It basically create a log file and writes info to it
# You can then view all the information
@app.route("/logs")
def view_logs():
    try:
        client_ip = request.remote_addr
        logging.info(f"{client_ip} has viewed the logfiles")
        with open("file_server.log", "r") as f:
            logs = f.readlines()
        return "<br>".join(logs).replace("\n", "<br>")
    except Exception as e:
        client_ip = request.remote_addr
        logging.info(f"{client_ip} has not been able to view the logfiles")
        return f"Could not read log file: {e}", 500


if __name__ == "__main__":
    # Make sure the SHARED_FOLDER exists
    # if not
    if not os.path.exists(SHARED_FOLDER):
        # The app will then create it
        os.makedirs(SHARED_FOLDER)

        # Navigate to the directory
        os.chdir('./shared')

        # Create a test file in there
        f = open("testfile.txt", "x")
        f = open("testfile.txt", "w")
        f.write("This is a test file")
        f.close()

    # If it exists
    if os.path.exists(SHARED_FOLDER):
        # List the files
        files = os.listdir(SHARED_FOLDER)

        # If there are no files
        if len(files) == 0:

            # Navigate to the directory
            os.chdir('./shared')

            # Create a test file in there
            f = open("newfile.txt", "x")
            f = open("newfile.txt", "w")
            f.write("This is your first shared file")
            f.close()  

    # Run the app
    app.run(host="0.0.0.0", port=8000)