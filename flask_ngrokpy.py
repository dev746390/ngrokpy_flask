import json
import os
import platform
import shutil
import time
import zipfile
from pathlib import Path
import requests
from threading import Timer

home = Path.home()

# check os
def _get_command():
    system = platform.system()
    if system == "Darwin":
        command = "ngrok"
    elif system == "Windows":
        command = "ngrok.exe"
    elif system == "Linux":
        command = "ngrok"
    else:
        raise Exception("{system} is not supported".format(system=system))
    return command

def set_auth_token():
    token = input("Please enter your ngrok auth_token :")
    os.popen(f"ngrok/./ngrok authtoken {token}")
    print(f"Authtoken saved to configuration file: {home}/.ngrok2/ngrok.yml")

# run flask on port 500 and return ngrok url
def _run_ngrok(port,app):
    command = _get_command()
    ngrok_path = str(Path(app.root_path, "ngrok"))
    if os.path.isfile(os.path.join(ngrok_path, "ngrok")):
        print(" # ngrok found")
    _download_ngrok(ngrok_path,app)
    executable = str(Path(ngrok_path, command))
    os.chmod(executable, 0o777)
    if os.path.isfile(f"{home}/.ngrok2/ngrok.yml"):
        print(" # ngrok config file exits")
    else:
        set_auth_token()
    ngrok = os.popen(f"ngrok/./ngrok http {port}")
    time.sleep(8)
    localhost_url = "http://localhost:4041/api/tunnels"  # Url with tunnel details
    tunnel_url = requests.get(localhost_url).text  # Get the tunnel information
    j = json.loads(tunnel_url)

    try:
        tunnel_url = j['tunnels'][0]['public_url']  # Do the parsing of the get
    except IndexError:
        return " # may be internet not available or try again"  # Do the parsing of the get
    tunnel_url = tunnel_url.replace("https", "https")
    return tunnel_url

# if ngrok not available in flask root path  
def _download_ngrok(ngrok_path,app):
    if Path(ngrok_path).exists():
        return
    print(" # Downloading ngrok")
    system = platform.system()
    if system == "Darwin":
        url = "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-darwin-amd64.zip"
    elif system == "Windows":
        url = "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-windows-amd64.zip"
    elif system == "Linux":
        url = "https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip"
    else:
        raise Exception(f"{system} is not supported")
    download_path = _download_file(url,app)
    with zipfile.ZipFile(download_path, "r") as zip_ref:
        zip_ref.extractall(ngrok_path)

# download ngrok
def _download_file(url,app):
    local_filename = url.split('/')[-1]
    r = requests.get(url, stream=True)
    download_path = str(Path(app.root_path, local_filename))
    with open(download_path, 'wb') as f:
        shutil.copyfileobj(r.raw, f)
    return download_path


def start_ngrok(port,app):
    ngrok_address = _run_ngrok(port,app)
    print(f" # Running on {ngrok_address}")
    print(f" # Traffic stats available on http://127.0.0.1:4041")


def run_with_ngrok(app):
    """
    The provided Flask app will be securely exposed to https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip the public internet via ngrok when run,
    and the its ngrok address will be printed to stdout
    :param app: a Flask application object
    :return: None
    """
    old_run = app.run

    def new_run(*args, **kwargs):
        port = kwargs.get('port', 5000)
        thread = Timer(1, start_ngrok, args=(port,app))
        thread.setDaemon(True)
        thread.start()
        old_run(*args, **kwargs)
    app.run = new_run
