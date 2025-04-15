import os
import random
from shutil import rmtree
import requests

def random_name(length=9):
    """Generate a random numeric string of given length."""
    return "".join(random.choices("0123456789", k=length))


def create_folder(name, path="."):
    """Create a folder if it does not exist."""
    full_path = os.path.join(path, name)
    if not os.path.exists(full_path):
        os.mkdir(full_path)
    return full_path


def check_user_folder(message, base_path="./Content"):
    """Ensure the user's folder exists; create it if necessary."""
    user_folder = os.path.join(base_path, str(message.chat.id))
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    return user_folder


def list_files_by_time(directory):
    """Return a list of file paths in the directory sorted by creation time."""
    if not os.path.exists(directory):
        return []
    entries = os.listdir(directory)
    sorted_entries = sorted(
        entries, key=lambda entry: os.path.getctime(os.path.join(directory, entry))
    )
    return [os.path.join(directory, entry) for entry in sorted_entries]


def save_file(file_content, path):
    """Save file_content to the specified path."""
    with open(path, "wb") as f:
        f.write(file_content)
    return path


def delete_file(file_path):
    """Delete the file at the given path."""
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")


def delete_user_content(message, base_path="./Content"):
    """Delete the folder corresponding to the user's content."""
    user_folder = os.path.join(base_path, str(message.chat.id))
    if os.path.exists(user_folder):
        try:
            rmtree(user_folder)
        except:
            pass

def file_extension(file_path):
    """Return file extension"""
    extension = file_path.split(".")[-1]
    return extension


def check_name_has_extension(name):
    """check that name has extension"""
    name_extension = name.split(".")[-1]
    return name not in name_extension

def rename_file(file_path, new_path):
    """Rename a file with extension recognition capability"""
    file_name = file_path.split("\\")[-1] # last file name
    extension = file_path.split(".")[-1] # last file extension
    
    # if new_path had extension mean user entered a name with optional extension else add default extension to end of new_path:
    if check_name_has_extension(new_path):
        new_path = file_path.replace(file_name, f"{new_path}")
    else:
        new_path = file_path.replace(file_name, f"{new_path}.{extension}")
        
    os.rename(file_path, new_path)
    return new_path

def download_link(url):
    response = requests.get(url)
    content = response.content
    return content