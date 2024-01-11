import sys
import subprocess
import threading
import json
import os
from huggingface_hub import HfApi, create_repo

def run_script(path, bpw_values, upload):
    folder_name = os.path.basename(os.path.normpath(path))
    for bpw in bpw_values:
        command = ["python", "EasyEXL.py", path, "--bpw", str(bpw)]
        subprocess.run(command)

    if upload:
        upload_thread = threading.Thread(target=upload_models, args=(folder_name, bpw_values))
        upload_thread.start()

def upload_models(folder_name, bpw_values):
    with open("settings.json", "r") as file:
        settings = json.load(file)
    userhf = settings.get("userhf", "")
    api = HfApi()

    for bpw in bpw_values:
        repo_name = f"{userhf}/{folder_name}-{bpw}bpw-exl2"
        create_repo(repo_name, private=True)
        model_folder_path = f"{folder_name}/{folder_name}-{bpw}bpw-exl2"
        api.upload_folder(
            folder_path=model_folder_path,
            repo_id=repo_name,
            repo_type="model",
        )

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python batch.py /path/to/model/ --bpw 8,6,5,4 [--upload]")
        sys.exit(1)

    model_path = sys.argv[1]
    bpw_arg_index = sys.argv.index("--bpw") + 1 if "--bpw" in sys.argv else None
    upload = "--upload" in sys.argv

    if bpw_arg_index is None or bpw_arg_index >= len(sys.argv):
        print("Invalid or missing bpw argument")
        sys.exit(1)

    bpw_values = sys.argv[bpw_arg_index].split(',')

    run_script(model_path, bpw_values, upload)
