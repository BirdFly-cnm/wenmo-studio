"""Build the offline Windows x64 setup from a CPython runtime and PDFium."""

import argparse
import hashlib
import shutil
import subprocess
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

WINDOWS = Path(__file__).resolve().parent
PROJECT = WINDOWS.parent
SOURCE = (
    "wenmo.py", "office.py", "materials.py", "README.md",
    "static/index.html", "static/app.js", "static/app.css",
)
EXCLUDED_STDLIB = {
    "__pycache__", "site-packages", "test", "tests", "idlelib", "tkinter", "turtledemo", "ensurepip", "venv",
}
PDFIUM_MODULES = ("pypdfium2", "pypdfium2_raw", "pypdfium2_cfg", "pypdfium2_cli")


def files_under(folder, excluded=()):
    for file in sorted(folder.rglob("*")):
        relative = file.relative_to(folder)
        if file.is_file() and file.suffix != ".pyc" and not set(relative.parts).intersection(excluded):
            yield file, relative


def add_runtime(source, target):
    if not (source / "python.exe").is_file() or not (source / "LICENSE.txt").is_file():
        raise ValueError("Provide a Windows x64 Python runtime with its LICENSE.txt.")
    core = [path for path in source.glob("python3[0-9][0-9].dll")]
    if len(core) != 1:
        raise ValueError("Cannot identify the embedded Python DLL version.")
    version = core[0].stem
    target.mkdir()
    for name in ("python.exe", "python3.dll", core[0].name, "vcruntime140.dll", "vcruntime140_1.dll", "LICENSE.txt"):
        shutil.copy2(source / name, target / name)
    (target / "DLLs").mkdir()
    for file in (source / "DLLs").iterdir():
        if file.suffix not in {".dll", ".pyd"} or file.name.startswith(("_test", "_ctypes_test", "_tkinter", "tcl", "tk")):
            continue
        shutil.copy2(file, target / "DLLs" / file.name)
    for file, relative in files_under(source / "Lib", EXCLUDED_STDLIB):
        path = target / "Lib" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, path)
    # A real Lib directory also lets this Windows distribution initialize TLS.
    (target / (version + "._pth")).write_text("Lib\nDLLs\n..\n", encoding="ascii")


def add_pdfium(source, target):
    if not (source / "pypdfium2_raw" / "pdfium.dll").is_file():
        raise ValueError("Provide a pypdfium2 installation for Windows x64.")
    metadata = list(source.glob("pypdfium2-*.dist-info"))
    if len(metadata) != 1 or not (metadata[0] / "licenses").is_dir():
        raise ValueError("Missing pypdfium2 and PDFium distribution notices.")
    for folder in [*(source / name for name in PDFIUM_MODULES), metadata[0]]:
        for file, relative in files_under(folder, {"__pycache__"}):
            path = target / folder.name / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, path)


def compile_exe(compiler, output, *, define=None, payload=None):
    args = [
        str(compiler), "/nologo", "/target:winexe", "/platform:x64", "/optimize+", "/codepage:65001",
        f"/out:{output}", f"/win32manifest:{WINDOWS / 'wenmo.manifest'}",
        "/reference:System.dll", "/reference:System.Core.dll", "/reference:System.Drawing.dll",
        "/reference:System.Windows.Forms.dll", "/reference:System.IO.Compression.dll",
        "/reference:System.IO.Compression.FileSystem.dll", "/reference:Microsoft.CSharp.dll",
    ]
    if define:
        args.append("/define:" + define)
    if payload:
        args.append(f"/resource:{payload},WenmoPayload.zip")
    args.append(str(WINDOWS / "Desktop.cs"))
    subprocess.run(args, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python-runtime", type=Path, required=True)
    parser.add_argument("--pdfium-site", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--csc", type=Path, default=Path(r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"))
    args = parser.parse_args()
    output = args.output.resolve()
    with tempfile.TemporaryDirectory(prefix="wenmo-build-", dir=args.work_dir.resolve()) as temporary:
        work = Path(temporary)
        stage = work / "WenmoStudio"
        stage.mkdir()
        for name in SOURCE:
            target = stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(PROJECT / name, target)
        (stage / ".wenmo-install").write_text("Wenmo Studio 4.2 beta\n", encoding="ascii")
        add_runtime(args.python_runtime, stage / "runtime")
        add_pdfium(args.pdfium_site, stage / "vendor")
        subprocess.run(
            [str(stage / "runtime" / "python.exe"), "-I", "-B", "-c",
             "import ssl; from materials import load_pdfium; load_pdfium(); assert ssl.create_default_context().cert_store_stats()['x509']"],
            cwd=stage, check=True,
        )
        compile_exe(args.csc, stage / "WenmoStudio.exe")
        compile_exe(args.csc, stage / "Uninstall.exe", define="REMOVE")
        payload = work / "payload.zip"
        with ZipFile(payload, "w", ZIP_DEFLATED, compresslevel=6) as bundle:
            for file, relative in files_under(stage):
                bundle.write(file, relative.as_posix())
        with ZipFile(payload) as bundle:
            if bundle.testzip() is not None:
                raise RuntimeError("Installer payload ZIP verification failed.")
        compile_exe(args.csc, output, define="SETUP", payload=payload)
    print(f"Built {output.name} ({output.stat().st_size:,} bytes)")
    print("SHA-256 " + hashlib.sha256(output.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
