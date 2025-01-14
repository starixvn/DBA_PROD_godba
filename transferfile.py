import subprocess
import Applog

def map_network(network_path, username, password):
    net_use_command = [
        "net", "use", network_path, "/user:{}".format(username), password
    ]
    result = subprocess.run(net_use_command, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"Connected to {network_path} successfully.")
    else:
        print(f"Failed to connect to {network_path}: {result.stderr}")
    return result.returncode == 0

def unmap_network(network_path):
    net_use_delete_command = ["net", "use", network_path, "/delete"]
    result = subprocess.run(net_use_delete_command, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Disconnected {network_path} successfully.")
    else:
        print(f"Failed to disconnect {network_path}: {result.stderr}")

def copy_files_with_robocopy(source_path, dest_path, filename):
    robocopy_command = ["robocopy", f"{source_path}", f"{dest_path}", filename, fr"/LOG:.\log\copy_{filename}.txt", "/E", "/Z"]
    print(robocopy_command)
    result = subprocess.run(robocopy_command, capture_output=True, text=True)
    if result.returncode in [0, 1, 2, 3]:
        print("Files copied successfully.")
    else:
        print(f"Error during file copy:{result.returncode} - {result.stderr} - {result.stdout}")
        Applog.write_log(f"Error during file copy:{result.returncode} - {result.stderr} - {result.stdout}")

def transfer_files_between_servers(source_path, source_username, source_password, dest_path, dest_username, dest_password, filename):
    print("step 2: copy backup file to DR...")
    if map_network(source_path, source_username, source_password):
        if map_network(dest_path, dest_username, dest_password):
            copy_files_with_robocopy(source_path, dest_path, filename)
            unmap_network(dest_path)
        unmap_network(source_path)

