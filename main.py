from flask import Flask, send_from_directory, render_template, request, redirect, flash, url_for
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

# Limit filesize to 10 MB
app.config["MAX_CONTENT_LENGTH"] = 10 * 1000 * 1000  # 10 MB in bytes, you only need to change the 10 to whatever size limit you'd like

app.secret_key = "your_secret_key" # I will need this to render messages, ex "file too large"

# The folder to be shared
SHARED_FOLDER = "./shared"

# Using this to set limits
limiter = Limiter(get_remote_address, app=app, default_limits=["100 per minute"])


# The following function will help when users upload files with the same name as existing files on the server
# It checks for file names, if the file exists, we will use a counter to add a number to the newly uploaded file
def secure_unique_filename(filename):
    """
    Ensures that the filename is unique by appending a counter if needed.
    """
    base, ext = os.path.splitext(filename)
    counter = 1
    unique_filename = filename

    while os.path.exists(os.path.join(SHARED_FOLDER, unique_filename)):
        unique_filename = f"{base}{counter}{ext}"
        counter += 1

    return unique_filename


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



@app.route("/upload2", methods=["GET", "POST"])
def upload_with_filesize_limit():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            # Generate a unique filename if necessary
            unique_filename = secure_unique_filename(file.filename)

            # Save the file
            file.save(os.path.join(SHARED_FOLDER, unique_filename))
            flash(f"File uploaded successfully as {unique_filename}")
            # file.save(os.path.join(SHARED_FOLDER, file.filename)) # Old code

            # Log information about the upload
            client_ip = request.remote_addr
            logging.info(f"File uploaded: {unique_filename} by {client_ip}. File uploaded successfully")

            return "File uploaded successfully!"
    return render_template("upload2.html")



@app.errorhandler(413)
def file_too_large(error):
    flash("File is too large. Maximum file size is 10 MB.")
    # Log information about the upload
    client_ip = request.remote_addr
    logging.info(f"{client_ip} tryed to upload a file too large. Maxium file size is 10 MB.")
    return redirect(url_for("upload_with_filesize_limit"))



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


@app.route("/test")
def view_test():
    filesArr = []
    files = os.listdir(SHARED_FOLDER)

    for file in files:
        file_path = os.path.join(SHARED_FOLDER, file)
        if os.path.isfile(file_path):  # Control that this is a file
            size = os.path.getsize(file_path)
            size_in_mb = round(size / 1000 / 1000, 4) # Convert to MB and round to 4 digits
            filesArr.append({"name": file, "size": size, "size_in_mb": size_in_mb})

    return render_template("test.html", files=filesArr)


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