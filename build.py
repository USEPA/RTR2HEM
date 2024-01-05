import os
import json
import shutil
import subprocess

exe_fp = os.path.join(".", "RTR2HEM")
exe_name = "RTR2HEM"

# lib_fp = r"--paths=C:\Users\55586\.virtualenvs\Python_Tool-HlJboBwr\Lib\site-packages"
# pyinstaller --onefile --noconsole .\main.py


def create_folder():
    cleanup(True)
    os.mkdir(exe_fp)


def cleanup(include_exe=False):
    if include_exe and os.path.exists(exe_fp):
        shutil.rmtree(exe_fp)
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    try:
        os.remove("main.spec")
    except OSError:
        pass


def important_files_copy():
    srcs = ["static", "templates", "config.json"]
    for src in srcs:
        dst = os.path.join(exe_fp, src)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy(src, dst)

    exe_file_src = os.path.join("dist", "main.exe")
    exe_file_dst = os.path.join(exe_fp, f"{exe_name}.exe")
    shutil.copy(exe_file_src, exe_file_dst)

    # clear out json
    config_fp = os.path.join(exe_fp, "config.json")
    with open(config_fp, "r") as fh:
        config_file = json.load(fh)
        config_file["settings"]["source_category_name"] = ""
        config_file["settings"]["input_file"] = ""
        config_file["settings"]["input_table"] = ""
        config_file["settings"]["emission_abbr"]["file"] = ""
        config_file["settings"]["emission_abbr"]["table"] = ""
        config_file["settings"]["src_ids"]["file"] = ""
        config_file["settings"]["src_ids"]["table"] = ""
    with open(config_fp, "w") as fh:
        json.dump(config_file, fh, indent=4)


def run_pyinstaller():
    cmd = [
        "python",
        "-m",
        "PyInstaller",
        "--clean",
        "--onefile",
        "--noconsole",
        ".\main.py",
    ]
    with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, bufsize=1) as sp:
        for line in sp.stdout:
            print(line, flush=True)


if __name__ == "__main__":
    try:
        create_folder()
        run_pyinstaller()
        important_files_copy()
        cleanup()
    except Exception as e:
        cleanup(True)
        print(e)
