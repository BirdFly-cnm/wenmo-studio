"""Export the supported Markdown subset to editable Office Open XML files."""

import re
from html import escape
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

FORMATS = {
    "md": "text/markdown; charset=utf-8",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}
OFFICE = "http://schemas.openxmlformats.org"
PACKAGE_REL = f"{OFFICE}/package/2006/relationships"
REL = f"{OFFICE}/officeDocument/2006/relationships"
W = f"{OFFICE}/wordprocessingml/2006/main"
P = f"{OFFICE}/presentationml/2006/main"
A = f"{OFFICE}/drawingml/2006/main"
WP = f"{OFFICE}/drawingml/2006/wordprocessingDrawing"
PIC = f"{OFFICE}/drawingml/2006/picture"
PPT_NS = f'xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{REL}"'
PPT_TYPE = "application/vnd.openxmlformats-officedocument.presentationml."
FONT = "Microsoft YaHei"
RESUME_STYLES = {
    "classic": ("2D5D60", "EAF3F3"),
    "sidebar": ("214158", "EEF4F8"),
    "jade": ("087E78", "E0F3EF"),
    "form": ("303641", "F0F1F3"),
}


def xml_text(value):
    return escape(re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff\ufffe\uffff]", "", value))


def package(parts, types):
    overrides = "".join(f'<Override PartName="/{name}" ContentType="{mime}"/>' for name, mime in types.items())
    parts["[Content_Types].xml"] = (
        f'<Types xmlns="{OFFICE}/package/2006/content-types">'
        f'<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        f'<Default Extension="xml" ContentType="application/xml"/>{overrides}</Types>'
    )
    stream = BytesIO()
    with ZipFile(stream, "w", ZIP_DEFLATED) as zip_file:
        for name, source in parts.items():
            if isinstance(source, str):
                source = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + source
            zip_file.writestr(name, source)
    return stream.getvalue()


def relationships(*entries):
    nodes = "".join(
        f'<Relationship Id="rId{index}" Type="{REL}/{kind}" Target="{target}"/>'
        for index, (kind, target) in enumerate(entries, 1)
    )
    return f'<Relationships xmlns="{PACKAGE_REL}">{nodes}</Relationships>'


def plain(text):
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return re.sub(r"(\*\*|__|`|\*)", "", text)


def jpeg_size(photo):
    if not photo.startswith(b"\xff\xd8") or not photo.endswith(b"\xff\xd9"):
        raise ValueError("无效的 JPEG。")
    offset = 2
    while offset + 3 < len(photo) and photo[offset] == 0xFF:
        while offset < len(photo) and photo[offset] == 0xFF:
            offset += 1
        if offset + 3 >= len(photo):
            break
        marker = photo[offset]
        if marker in {0xDA, 0xD9}:
            break
        start = offset + 1
        length = int.from_bytes(photo[start:start + 2], "big")
        if length < 2 or start + length > len(photo):
            break
        if marker in {0xC0, 0xC1, 0xC2} and length >= 8:
            height = int.from_bytes(photo[start + 3:start + 5], "big")
            width = int.from_bytes(photo[start + 5:start + 7], "big")
            if width and height:
                return width, height
            break
        offset = start + length
    raise ValueError("无法读取 JPEG 尺寸。")


def photo_paragraph(photo, align="right"):
    source_width, source_height = jpeg_size(photo)
    scale = min(950_000 / source_width, 1_170_000 / source_height)
    width, height = round(source_width * scale), round(source_height * scale)
    return (
        f'<w:p><w:pPr><w:jc w:val="{align}"/></w:pPr><w:r><w:drawing>'
        f'<wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{width}" cy="{height}"/>'
        '<wp:docPr id="1" name="简历照片"/><wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/>'
        f'</wp:cNvGraphicFramePr><a:graphic><a:graphicData uri="{PIC}"><pic:pic>'
        '<pic:nvPicPr><pic:cNvPr id="0" name="简历照片"/><pic:cNvPicPr/></pic:nvPicPr>'
        '<pic:blipFill><a:blip r:embed="rId2"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{width}" cy="{height}"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
        '</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'
    )
def word_table(widths, rows, *, borders=False, padding=136):
    grid = "".join(f'<w:gridCol w:w="{width}"/>' for width in widths)
    border_xml = ""
    if borders:
        borders = "".join(f'<w:{edge} w:val="single" w:sz="5" w:color="AEB6BC"/>'
                          for edge in ("top", "left", "bottom", "right", "insideH", "insideV"))
        border_xml = f"<w:tblBorders>{borders}</w:tblBorders>"
    cell_margins = "".join(f'<w:{edge} w:w="{padding}" w:type="dxa"/>' for edge in ("top", "left", "bottom", "right"))
    entries = []
    for row in rows:
        cells = []
        for width, (body, fill) in zip(widths, row):
            shade = f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>' if fill else ""
            cells.append(
                f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>{shade}</w:tcPr>{body or "<w:p/>"}</w:tc>'
            )
        entries.append(f"<w:tr>{''.join(cells)}</w:tr>")
    return (
        f'<w:tbl><w:tblPr><w:tblW w:w="{sum(widths)}" w:type="dxa"/>{border_xml}<w:tblLayout w:type="fixed"/>'
        f'<w:tblCellMar>{cell_margins}</w:tblCellMar></w:tblPr><w:tblGrid>{grid}</w:tblGrid>{"".join(entries)}</w:tbl>'
    )


def word_paragraph(line, style):
    line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
    runs = []
    for part in re.split(r"(\*\*.+?\*\*|__.+?__)", line):
        bold = part.startswith(("**", "__")) and part.endswith(("**", "__")) and len(part) > 4
        props = "<w:rPr><w:b/></w:rPr>" if bold else ""
        value = xml_text(plain(part))
        if value:
            runs.append(f'<w:r>{props}<w:t xml:space="preserve">{value}</w:t></w:r>')
    return f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr>{"".join(runs)}</w:p>'


def resume_sections(lines):
    title = lines[0][1] if lines and lines[0][0] == "Heading1" else "个人简历"
    if lines and lines[0][0] == "Heading1":
        lines = lines[1:]
    sections = []
    label, paragraphs = "", []
    for style, text in lines:
        if style in {"Heading1", "Heading2"}:
            if label or paragraphs:
                sections.append((label, paragraphs))
            label, paragraphs = text, []
        else:
            paragraphs.append((style, text))
    if label or paragraphs:
        sections.append((label, paragraphs))
    return title, sections


def resume_body(lines, style, photo):
    title, sections = resume_sections(lines)
    accent, pale = RESUME_STYLES[style]

    def content(items, dark=False):
        result = []
        for label, body in items:
            if label:
                result.append(word_paragraph(label, "SideHeading" if dark else "Heading2"))
            result.extend(word_paragraph(text, "SideNormal" if dark else kind) for kind, text in body)
        return "".join(result)

    if style == "sidebar":
        side, main = [], []
        for section in sections:
            target = side if not section[0] or re.search(r"意向|联系|资料|技能|荣誉|获奖|特长|证书|语言|评价", section[0]) else main
            target.append(section)
        panel = (photo_paragraph(photo, "left") if photo else "") + word_paragraph(title, "SideTitle") + content(side, True)
        return word_table((3020, 6294), [[(panel, accent), (content(main), None)]], padding=230)

    heading = word_paragraph(title, "SideTitle" if style == "jade" else "Heading1")
    if style == "form":
        rows = [[(heading, pale), (photo_paragraph(photo) if photo else "", pale)]]
        table_head = word_table((7450, 1864), rows, borders=True)
        table_rows = [[
            (word_paragraph(label or "基本资料", "Heading2"), pale),
            ("".join(word_paragraph(text, kind) for kind, text in body), None),
        ] for label, body in sections]
        return table_head + "<w:p/>" + (word_table((1850, 7464), table_rows, borders=True) if table_rows else "")

    fill = accent if style == "jade" else pale
    heading = word_table((7450, 1864), [[(heading, fill), (photo_paragraph(photo) if photo else "", fill)]], padding=230)
    return heading + content(sections)


def application_style(text):
    if text.endswith(("：", ":")) or text in {"此致", "敬礼", "敬礼！", "此致敬礼", "此致敬礼！"}:
        return "Normal"
    if re.match(r"^(?:申请人|联系人|日期)[：:]|^\[日期\]$|^(?:\d{4}|[〇零一二三四五六七八九]{4})年", text):
        return "LetterSignature"
    return "LetterBody"


def docx(content, photo=None, *, resume_style="", application=False):
    lines = []
    accent, pale = RESUME_STYLES.get(resume_style, ("294CB3", "FFFFFF"))
    styles = [
        ("Normal", "Normal", 21 if resume_style else 22, "25344E", 0, 95 if resume_style else 145, False),
        ("Heading1", "heading 1", 43, accent if resume_style else "182644", 210, 195, True),
        ("Heading2", "heading 2", 25 if resume_style else 30, accent, 170, 95, True),
        ("Heading3", "heading 3", 25, "25344E", 165, 100, True),
        ("SideTitle", "Sidebar title", 38, "FFFFFF", 140, 130, True),
        ("SideHeading", "Sidebar heading", 23, "E0F3EF", 140, 70, True),
        ("SideNormal", "Sidebar body", 19, "F5F9FD", 0, 85, False),
        ("LetterBody", "Letter body", 24, "25344E", 0, 180, False),
        ("LetterSignature", "Letter signature", 24, "25344E", 0, 115, False),
    ]
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("```") or re.fullmatch(r"-{3,}", line):
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)", line)
        style = f"Heading{min(len(heading[1]), 3)}" if heading else "Normal"
        list_prefix = r"^(?:[-*+]|\d+[.)])\s+" if application else r"^[-*+]\s+"
        line = heading[2] if heading else re.sub(list_prefix, "" if application else "•  ", line)
        if application:
            style = application_style(plain(line)) if lines else "Heading1"
        lines.append((style, line))
    if resume_style:
        body = resume_body(lines, resume_style, photo)
    else:
        paragraphs = [word_paragraph(line, style) for style, line in lines]
        if photo:
            title = paragraphs.pop(0) if lines and lines[0][0] == "Heading1" else "<w:p/>"
            paragraphs.insert(0, word_table((7450, 1864), [[(title, None), (photo_paragraph(photo), None)]]))
        body = "".join(paragraphs)
    document = (
        f'<w:document xmlns:w="{W}" xmlns:r="{REL}" xmlns:a="{A}" xmlns:wp="{WP}" xmlns:pic="{PIC}">'
        f'<w:body>{body}'
        '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1296" w:right="1296" w:bottom="1296" w:left="1296" w:header="600" w:footer="600" w:gutter="0"/>'
        '</w:sectPr></w:body></w:document>'
    )
    style_xml = []
    for style_id, name, size, color, before, after, bold in styles:
        heading_options = '<w:keepNext/>' if bold else ""
        outline = f'<w:outlineLvl w:val="{int(style_id[-1]) - 1}"/>' if style_id.startswith("Heading") else ""
        weight = "<w:b/>" if bold else ""
        default = ' w:default="1"' if style_id == "Normal" else ""
        based_on = '<w:basedOn w:val="Normal"/>' if style_id != "Normal" else ""
        shade = f'<w:shd w:val="clear" w:color="auto" w:fill="{pale}"/>' if resume_style and style_id == "Heading2" else ""
        line_height = 280 if resume_style else 375 if application else 340
        indent = '<w:ind w:firstLine="420"/>' if style_id == "LetterBody" else ""
        align = '<w:jc w:val="right"/>' if style_id == "LetterSignature" else ""
        if (application or resume_style == "form") and style_id == "Heading1":
            align = '<w:jc w:val="center"/>'
        style_xml.append(
            f'<w:style w:type="paragraph" w:styleId="{style_id}"{default}><w:name w:val="{name}"/>{based_on}'
            f'<w:pPr>{heading_options}{shade}<w:spacing w:before="{before}" w:after="{after}" w:line="{line_height}" w:lineRule="auto"/>'
            f'{indent}{align}{outline}</w:pPr><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:eastAsia="{FONT}"/>'
            f'{weight}<w:color w:val="{color}"/><w:sz w:val="{size}"/><w:szCs w:val="{size}"/></w:rPr></w:style>'
        )
    document_rels = [("styles", "styles.xml")]
    parts = {
        "_rels/.rels": relationships(("officeDocument", "word/document.xml")),
        "word/document.xml": document,
        "word/styles.xml": f'<w:styles xmlns:w="{W}">{"".join(style_xml)}</w:styles>',
    }
    types = {
        "word/document.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml",
        "word/styles.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml",
    }
    if photo:
        document_rels.append(("image", "media/resume-photo.jpg"))
        parts["word/media/resume-photo.jpg"] = photo
        types["word/media/resume-photo.jpg"] = "image/jpeg"
    parts["word/_rels/document.xml.rels"] = relationships(*document_rels)
    return package(parts, types)


def slide_sections(content):
    title = "文墨演示文稿"
    cover = []
    sections = []
    current = cover
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("```") or re.fullmatch(r"-{3,}", line):
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)", line)
        if heading and len(heading[1]) == 1 and not sections:
            title = plain(heading[2])
        elif heading:
            current = []
            sections.append((plain(heading[2]), current))
        else:
            stripped = re.sub(r"^(?:[-*+]|\d+[.)])\s+", "", line)
            if plain(stripped).strip():
                current.append(plain(stripped))
    if not sections and len(cover) > 1:
        sections.append(("正文", cover[1:]))
        cover = cover[:1]
    result = [(title, cover[:1])]
    if len(cover) > 1:
        sections.insert(0, ("内容概览", cover[1:]))
    for heading, lines in sections:
        chunks = [line[i:i + 94] for line in lines for i in range(0, len(line), 94)]
        for offset in range(0, max(1, len(chunks)), 5):
            result.append((heading + ("（续）" if offset else ""), chunks[offset:offset + 5]))
    if len(result) > 80:
        raise ValueError("演示稿超过 80 页。请删减内容后再导出。")
    return result


GROUP = (
    '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
    '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
    '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
)
COLOR_MAP = (
    '<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" '
    'accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>'
)
MASTER_COLORS = '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>'


def text_box(index, x, y, width, height, lines, size, color, *, bold=False, bullets=False):
    items = []
    bullet = '<a:pPr marL="330000" indent="-250000"><a:buChar char="•"/></a:pPr>' if bullets else ""
    weight = ' b="1"' if bold else ""
    for line in lines:
        items.append(
            f'<a:p>{bullet}<a:r><a:rPr lang="zh-CN" sz="{size}"{weight}><a:solidFill><a:srgbClr val="{color}"/>'
            f'</a:solidFill><a:latin typeface="Calibri"/><a:ea typeface="{FONT}"/></a:rPr>'
            f'<a:t>{xml_text(line)}</a:t></a:r></a:p>'
        )
    return (
        f'<p:sp><p:nvSpPr><p:cNvPr id="{index}" name="Text {index}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{width}" cy="{height}"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln><a:noFill/></a:ln></p:spPr>'
        '<p:txBody><a:bodyPr lIns="0" tIns="0" rIns="0" bIns="0" wrap="square"><a:normAutofit/></a:bodyPr>'
        f'<a:lstStyle/>{"".join(items) or "<a:p/>"}</p:txBody></p:sp>'
    )


def theme():
    colors = {
        "dk1": "14223C", "lt1": "FFFFFF", "dk2": "23385F", "lt2": "F5F3EC",
        "accent1": "3158D6", "accent2": "B8D6CD", "accent3": "E2B586", "accent4": "677BA7",
        "accent5": "8E92CE", "accent6": "D9A4A8", "hlink": "3158D6", "folHlink": "695996",
    }
    palette = "".join(f'<a:{name}><a:srgbClr val="{color}"/></a:{name}>' for name, color in colors.items())
    fonts = f'<a:latin typeface="Calibri"/><a:ea typeface="{FONT}"/><a:cs typeface="Calibri"/>'
    fill = '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
    lines = "".join(f'<a:ln w="{width}">{fill}<a:prstDash val="solid"/></a:ln>' for width in (6350, 12700, 19050))
    return (
        f'<a:theme xmlns:a="{A}" name="Wenmo"><a:themeElements><a:clrScheme name="Wenmo">{palette}</a:clrScheme>'
        f'<a:fontScheme name="Wenmo"><a:majorFont>{fonts}</a:majorFont><a:minorFont>{fonts}</a:minorFont></a:fontScheme>'
        f'<a:fmtScheme name="Wenmo"><a:fillStyleLst>{fill * 3}</a:fillStyleLst><a:lnStyleLst>{lines}</a:lnStyleLst>'
        f'<a:effectStyleLst>{"<a:effectStyle><a:effectLst/></a:effectStyle>" * 3}</a:effectStyleLst>'
        f'<a:bgFillStyleLst>{fill * 3}</a:bgFillStyleLst></a:fmtScheme></a:themeElements></a:theme>'
    )


def pptx(content):
    slides = slide_sections(content)
    empty_tree = f"<p:cSld><p:spTree>{GROUP}</p:spTree></p:cSld>"
    slide_ids = "".join(f'<p:sldId id="{255 + i}" r:id="rId{i + 1}"/>' for i in range(1, len(slides) + 1))
    parts = {
        "_rels/.rels": relationships(("officeDocument", "ppt/presentation.xml")),
        "ppt/presentation.xml": (
            f'<p:presentation {PPT_NS}><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/>'
            f'</p:sldMasterIdLst><p:sldIdLst>{slide_ids}</p:sldIdLst>'
            '<p:sldSz cx="12192000" cy="6858000" type="screen16x9"/><p:notesSz cx="6858000" cy="9144000"/>'
            '</p:presentation>'
        ),
        "ppt/_rels/presentation.xml.rels": relationships(
            ("slideMaster", "slideMasters/slideMaster1.xml"),
            *(("slide", f"slides/slide{i}.xml") for i in range(1, len(slides) + 1)),
        ),
        "ppt/slideMasters/slideMaster1.xml": (
            f'<p:sldMaster {PPT_NS}>{empty_tree}{COLOR_MAP}<p:sldLayoutIdLst>'
            '<p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst></p:sldMaster>'
        ),
        "ppt/slideMasters/_rels/slideMaster1.xml.rels": relationships(
            ("slideLayout", "../slideLayouts/slideLayout1.xml"), ("theme", "../theme/theme1.xml")
        ),
        "ppt/slideLayouts/slideLayout1.xml": (
            f'<p:sldLayout {PPT_NS} type="blank" preserve="1">{empty_tree}{MASTER_COLORS}</p:sldLayout>'
        ),
        "ppt/slideLayouts/_rels/slideLayout1.xml.rels": relationships(("slideMaster", "../slideMasters/slideMaster1.xml")),
        "ppt/theme/theme1.xml": theme(),
    }
    types = {
        "ppt/presentation.xml": PPT_TYPE + "presentation.main+xml",
        "ppt/slideMasters/slideMaster1.xml": PPT_TYPE + "slideMaster+xml",
        "ppt/slideLayouts/slideLayout1.xml": PPT_TYPE + "slideLayout+xml",
        "ppt/theme/theme1.xml": "application/vnd.openxmlformats-officedocument.theme+xml",
    }
    for index, (title, lines) in enumerate(slides, 1):
        if index == 1:
            background = "14223C"
            shapes = text_box(2, 850000, 1450000, 10400000, 2500000, [title], 4650, "F5F3EC", bold=True)
            shapes += text_box(3, 880000, 4230000, 10100000, 1400000, lines, 2200, "B8D6CD")
        else:
            background = "F5F3EC"
            shapes = text_box(2, 820000, 570000, 10500000, 1250000, [title], 3350, "294CB3", bold=True)
            shapes += text_box(3, 840000, 2060000, 10500000, 3900000, lines, 2100, "25344E", bullets=True)
            shapes += text_box(4, 11000000, 6170000, 770000, 380000, [str(index)], 1300, "677BA7")
        name = f"ppt/slides/slide{index}.xml"
        parts[name] = (
            f'<p:sld {PPT_NS}><p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="{background}"/>'
            f'</a:solidFill><a:effectLst/></p:bgPr></p:bg><p:spTree>{GROUP}{shapes}</p:spTree>'
            f'</p:cSld>{MASTER_COLORS}</p:sld>'
        )
        parts[f"ppt/slides/_rels/slide{index}.xml.rels"] = relationships(("slideLayout", "../slideLayouts/slideLayout1.xml"))
        types[name] = PPT_TYPE + "slide+xml"
    return package(parts, types)


def make_export(fmt, content, photo=None, *, resume_style="", application=False):
    if fmt == "md":
        return (content + "\n").encode("utf-8")
    if fmt == "docx":
        return docx(content, photo, resume_style=resume_style, application=application)
    if fmt == "pptx":
        return pptx(content)
    raise ValueError("不支持此导出格式。")
