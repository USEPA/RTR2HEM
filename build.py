import os
import shutil
import subprocess

exe_fp = os.path.join(".", "RTR2HEM")
exe_name = "RTR2HEM"

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


def run_pyinstaller():
    cmd = [
        "python",
        "-m",
        "PyInstaller",
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
