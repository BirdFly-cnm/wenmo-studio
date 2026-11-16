"""Extract references locally. The caller decides which reviewed text to send."""

import io
import os
import posixpath
import re
import shutil
import struct
import subprocess
import sys
import sysconfig
import tempfile
import threading
from contextlib import ExitStack
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

from office import A, P, REL, W

MAX_FILE = 12 * 1024 * 1024
MAX_OFFICE_FILE = 64 * 1024 * 1024
MAX_FILES = 5
MAX_EXTRACT = 16_000
MAX_MATERIAL = 24_000
MAX_PDF_PAGES = 60
MAX_OCR_PAGES = 8
MATERIAL_KINDS = {"slides", "proposal", "paper"}
TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".tsv"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
SUPPORTED = TEXT_EXTENSIONS | IMAGE_EXTENSIONS | {".docx", ".pptx", ".pdf"}
PDF_LOCK = threading.Lock()
OCR_SETUP = "扫描件需要本机 Tesseract OCR。请安装 Tesseract 及简体中文 chi_sim 或英文 eng 语言包，也可以手动粘贴文字。"


class MaterialError(ValueError):
    pass


def material_limit(filename):
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED:
        raise MaterialError("请选择 PDF、DOCX、PPTX、TXT、MD、CSV、TSV、JPG 或 PNG 文件。")
    return MAX_OFFICE_FILE if suffix in {".docx", ".pptx"} else MAX_FILE


def clean_text(value):
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff]", "", value)
    return re.sub(r"\n{4,}", "\n\n\n", value).strip()


def read_plain(data):
    encodings = ("utf-16",) if data.startswith((b"\xff\xfe", b"\xfe\xff")) else ("utf-8-sig", "gb18030")
    for encoding in encodings:
        try:
            return data.decode(encoding)
        except UnicodeError:
            continue
    raise MaterialError("无法识别文本编码，请将文件另存为 UTF-8。")


def small_xml(archive, name):
    info = archive.getinfo(name)
    if info.file_size > MAX_FILE:
        raise MaterialError("Office 文档的正文部分太大，请拆分后再上传。")
    return ET.fromstring(archive.read(info))


def paragraphs(node, namespace):
    for paragraph in node.iter(f"{{{namespace}}}p"):
        text = "".join(item.text or "" for item in paragraph.iter(f"{{{namespace}}}t")).strip()
        if text:
            yield text


def read_office(data, suffix, warnings):
    try:
        with ZipFile(io.BytesIO(data)) as archive:
            if suffix == ".docx":
                return "\n".join(paragraphs(small_xml(archive, "word/document.xml"), W))
            presentation = small_xml(archive, "ppt/presentation.xml")
            rels = small_xml(archive, "ppt/_rels/presentation.xml.rels")
            targets = {element.get("Id"): element.get("Target", "") for element in rels}
            slides = list(presentation.iter(f"{{{P}}}sldId"))
            if len(slides) > MAX_PDF_PAGES:
                warnings.append(f"只读取前 {MAX_PDF_PAGES} 张幻灯片。")
            result, size = [], 0
            for index, slide in enumerate(slides[:MAX_PDF_PAGES], 1):
                target = targets.get(slide.get(f"{{{REL}}}id"), "")
                part = posixpath.normpath(posixpath.join("ppt", target)) if not target.startswith("/") else target.lstrip("/")
                if not re.fullmatch(r"ppt/slides/[^/]+\.xml", part):
                    continue
                value = "\n".join(paragraphs(small_xml(archive, part), A))
                if value:
                    result.append(f"[第 {index} 页]\n{value}")
                    size += len(result[-1])
                if size > MAX_EXTRACT:
                    break
            return "\n\n".join(result)
    except (BadZipFile, KeyError, ET.ParseError, OSError, RuntimeError) as error:
        raise MaterialError("无法读取该 Office 文档。请确认文件完整，并另存为 DOCX 或 PPTX。") from error


def load_pdfium():
    vendor = Path(__file__).resolve().parent / "vendor"
    if sysconfig.get_platform() == "win-amd64" and vendor.is_dir() and str(vendor) not in sys.path:
        sys.path.insert(0, str(vendor))
    try:
        import pypdfium2 as pdfium
    except (ImportError, OSError) as error:
        raise MaterialError("缺少 PDF 读取组件。请使用完整 Windows 测试包，或运行 python -m pip install -r requirements.txt。") from error
    return pdfium


def tesseract_path():
    executable = shutil.which("tesseract")
    if not executable and os.name == "nt":
        executable = next((
            str(path) for key in ("ProgramFiles", "ProgramFiles(x86)")
            if (path := Path(os.environ.get(key, "C:/Program Files")) / "Tesseract-OCR" / "tesseract.exe").is_file()
        ), None)
    return executable


def run_tesseract(executable, *args, timeout=30):
    try:
        result = subprocess.run(
            [executable, *args], check=True, capture_output=True, timeout=timeout,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        return result.stdout.decode("utf-8", errors="replace")
    except (OSError, subprocess.SubprocessError) as error:
        raise MaterialError("本机 OCR 读取失败，请检查 Tesseract 和语言包，或手动粘贴文字。") from error


def ocr_settings():
    executable = tesseract_path()
    if not executable:
        return None
    installed = set(run_tesseract(executable, "--list-langs", timeout=8).splitlines())
    languages = [language for language in ("chi_sim", "chi_tra", "eng") if language in installed]
    return (executable, "+".join(languages)) if languages else None


def recognize(path, settings):
    executable, languages = settings
    return clean_text(run_tesseract(executable, str(path), "stdout", "-l", languages))


def bmp_page(page, pdfium, target):
    scale = min(2.5, 2000 / max(page.get_size()))
    bitmap = page.render(scale=scale, force_bitmap_format=pdfium.raw.FPDFBitmap_BGR)
    try:
        pixels = bytes(bitmap.buffer)
        height, width, stride = bitmap.height, bitmap.width, bitmap.stride
        # A top-down 24-bit BMP needs its scanlines padded to a multiple of four bytes.
        width_bytes = width * 3
        padding = b"\0" * ((-width_bytes) % 4)
        pixels = b"".join(pixels[row * stride:row * stride + width_bytes] + padding for row in range(height))
        header = struct.pack("<2sIHHI", b"BM", 54 + len(pixels), 0, 0, 54)
        info = struct.pack("<IiiHHIIiiII", 40, width, -height, 1, 24, 0, len(pixels), 0, 0, 0, 0)
        target.write_bytes(header + info + pixels)
    finally:
        bitmap.close()


def read_pdf(data, warnings, temporary):
    pdfium = load_pdfium()
    text, scan_paths = {}, []
    scratch = None
    with PDF_LOCK:  # PDFium's C API is not thread-safe, even across documents.
        try:
            document = pdfium.PdfDocument(data)
        except (pdfium.PdfiumError, ValueError) as error:
            raise MaterialError("无法读取 PDF。请确认文件完整，且未加密。") from error
        try:
            count = min(len(document), MAX_PDF_PAGES)
            if len(document) > count:
                warnings.append(f"只读取 PDF 前 {count} 页。")
            settings = None
            scanned = 0
            text_size = 0
            for index in range(count):
                page = document[index]
                try:
                    textpage = page.get_textpage()
                    try:
                        content = clean_text(textpage.get_text_bounded())
                    finally:
                        textpage.close()
                    if any(char.isalnum() for char in content):
                        text[index] = content[:MAX_EXTRACT + 1]
                        text_size += len(text[index])
                        if text_size > MAX_EXTRACT:
                            break
                        continue
                    scanned += 1
                    if scanned == 1:
                        try:
                            settings = ocr_settings()
                        except MaterialError as error:
                            warnings.append(str(error))
                        if not settings:
                            warnings.append(OCR_SETUP)
                    if settings and scanned <= MAX_OCR_PAGES:
                        if scratch is None:
                            scratch = Path(temporary.enter_context(tempfile.TemporaryDirectory(prefix="wenmo-material-")))
                        path = scratch / f"page-{index}.bmp"
                        bmp_page(page, pdfium, path)
                        scan_paths.append((index, path, settings))
                finally:
                    page.close()
            if scanned > MAX_OCR_PAGES and settings:
                warnings.append(f"扫描页只识别前 {MAX_OCR_PAGES} 页，其他扫描页请拆分后上传。")
        finally:
            document.close()
    for index, path, settings in scan_paths:
        try:
            value = recognize(path, settings)
            if value:
                text[index] = value
            else:
                warnings.append(f"第 {index + 1} 页的 OCR 未识别到文字。")
        except MaterialError:
            warnings.append(f"第 {index + 1} 页的 OCR 未完成。")
    return "\n\n".join(f"[第 {index + 1} 页]\n{text[index]}" for index in sorted(text)), bool(scan_paths)


def extract(filename, data):
    suffix = Path(filename).suffix.lower()
    limit = material_limit(filename)
    if not data or len(data) > limit:
        raise MaterialError(f"材料为空或超过 {limit // 1024 ** 2} MB。请拆分文件后重试。")
    warnings, used_ocr = [], False
    if suffix in TEXT_EXTENSIONS:
        text = read_plain(data)
    elif suffix in {".docx", ".pptx"}:
        text = read_office(data, suffix, warnings)
    else:
        try:
            if suffix == ".pdf":
                with ExitStack() as temporary:
                    text, used_ocr = read_pdf(data, warnings, temporary)
            else:
                settings = ocr_settings()
                if not settings:
                    raise MaterialError(OCR_SETUP)
                with tempfile.TemporaryDirectory(prefix="wenmo-material-") as directory:
                    path = Path(directory) / ("image" + suffix)
                    path.write_bytes(data)
                    text, used_ocr = recognize(path, settings), True
        except (OSError, RuntimeError) as error:
            raise MaterialError("本地材料读取失败，请检查临时目录或文档格式。") from error
    text = clean_text(text)
    if not text:
        raise MaterialError(warnings[0] if warnings else "没有读到文字。请检查文件内容，或手动粘贴文字。")
    if len(text) > MAX_EXTRACT:
        warnings.append(f"仅保留前 {MAX_EXTRACT:,} 字。请核对提取结果或拆分原文件。")
    return {"name": filename, "text": text[:MAX_EXTRACT], "warnings": warnings, "ocr": used_ocr}
