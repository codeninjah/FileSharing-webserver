# File sharing web server written in Python and Flask
This is a file sharing web server that you can use to share files from your computer. It works (as of now) when you access it locally through the same network.
Below are the steps of how to run this script. 
If you'd like to access it from other devices, such as computers and phones, in the same network, you need to get your IPv4 Address.
In Windows you would need to run the Command prompt and prompt `ipconfig`. You would then to find which network your computer is connected to. And you will need to use that IPv4 Address to access it from another device.

An example would be `192.168.0.2`. With the script on, you could navigate from the other device to `192.168.0.2:8000` (we are using port number **8000** in this project and example). No `https://` supported yet!


## Steps
1.  run the command `pip install flask`
2.  run the command `pip install flask-limiter`


## About
You will be able to run this app as a filesharing web server in your network.
You need to run `python main.py`

In this script we have chosen to upload everything to a folder called `shared` that is also within this folder
If you don't have a folder called `shared`, one will automatically be created with a test txt file in it
If you have that folder but it's empty, a txt file will be created. I am uploading this project with an empty folder called `shared`


## Endpoints
The endpoints are:
`localhost:8000` - this will list all the files in the folder
`localhost:8000/upload` - this will allow you to upload files to the server
`localhost:8000/logs` - you will be able to see all kind of logs, who downloaded which file and who uploaded which file and other detailed logs.
The logs are saved in a file called `file_server.log` in the root directory.


## Features
Other features:
- You are protected from **path traversal attacks**. 
>A path traversal attack (also known as directory traversal) aims to access files and directories that are stored outside the web root folder.
Source: [OWASP](https://owasp.org/www-community/attacks/Path_Traversal)
- You can **limit numbers of downloads per minute**. As of now is 5 per minute from one client. You can change that number.


## Issues/bugs
I notice that sometimes when you run the script and navigate to `localhost:8000`, it may give an 500 error. You just need to rerun the script and refresh the page.