# 文墨工作台 · Wenmo Studio

**v4.2 测试版**

一个自带 API 的本地文档生成客户端。选择文档类型、填写要求，用自己的模型生成初稿。可以预览、编辑、下载，并查看模型服务回传的 Token 用量。

## 启动

需要 Python 3.10 或更高版本。Windows x64 测试包带有 PDF 读取组件和本地前端资源。直接运行源码或在其他平台使用 PDF 功能时，请先运行 `python -m pip install -r requirements.txt`。

- Windows 双击 `start.cmd`，或在项目目录运行 `python wenmo.py`。
- macOS 和 Linux 在项目目录运行 `python3 wenmo.py`。
- 页面默认会在浏览器打开。也可访问 [本地工作台](http://127.0.0.1:8765/)。
- 默认端口被占用时会自动换用空闲端口，当前地址会显示在启动窗口。也可运行 `python wenmo.py --port 8766` 指定端口，或使用 `--no-browser` 跳过自动打开浏览器。
- 关闭客户端时，在启动窗口按 Ctrl+C。

可以先点「查看示例」，体验预览、编辑和下载。示例不会调用 API。测试包里的 `preview.html` 也可以直接双击打开，离线体验模板、示例、编辑和 Markdown 下载。

## 接入自己的模型

1. 点「配置 API」，填入服务商提供的 API 基础地址、模型 ID 和 API Key。默认地址为 `https://api.openai.com/v1`，也支持其他提供兼容接口的服务商。
2. 使用服务商实际提供的基础路径，例如 `https://api.example.com/v1`，或直接填写以 `/chat/completions` 结尾的地址。远程地址使用 HTTPS。本机服务可使用 HTTP，例如 `http://127.0.0.1:11434/v1`。无需鉴权的服务可留空 API Key。
3. 选择类型，填写生成要求，也可以加一个标题或主题，再点「生成文稿」。主题和生成要求会随模板发送到所选 API。

| 类型 | 导出格式 |
| --- | --- |
| 简历、申请书、开题报告、论文 | Word（.docx）、Markdown（.md） |
| PPT | PowerPoint（.pptx）、Markdown（.md） |

简历先填写目标岗位，再按需填写联系方式、成绩、获奖、荣誉、特长及经历。简洁色条、深蓝双栏、青绿页眉和表格登记四套版式可随时切换和导出。可以选择 JPG 或 PNG 照片，预览和 Word 导出会使用该照片。照片只交给本地 Python 工作台处理，有照片的生成记录会保存该照片，删除正文时也会删除记录中的照片。

申请书提供通用模板。可用「复制誊写稿」获取适合手抄的纯文本。每种文档都有模型建议，实际使用的模型以你配置的模型 ID 为准。 [OpenAI 模型文档](https://developers.openai.com/api/docs/models/all) · [DeepSeek 模型文档](https://api-docs.deepseek.com/api/create-chat-completion/)

## 查证时效性信息

生成涉及近期统计、政策或研究的 PPT、开题报告和论文时，可配置 DeepSeek 官方地址 `https://api.deepseek.com` 和模型 `deepseek-flash`，然后勾选「联网查证」。它默认关闭，勾选后模型会按题目决定是否搜索。搜索会按次数另行计费，来源可以在预览和生成历史中点开核对，也随 Markdown 下载。页面标注查证时间，并在服务商提供时显示来源发布日期。 [DeepSeek 联网文档](https://api-docs.deepseek.com/zh-cn/guides/web_tools/) · [搜索计费说明](https://api-docs.deepseek.com/zh-cn/guides/search/#计费)

## 使用参考材料

PPT、开题报告和论文的表单顶部都有「上传参考材料」。可上传 PDF、DOCX、PPTX、TXT、MD、CSV、TSV、JPG 和 PNG，或者直接粘贴文字。每个模块最多保留 5 份文件，Word 和 PPT 单文件不超过 64 MB，其他文件不超过 12 MB。点开材料可以校对或删减提取文字，合计最多 24,000 字。文件格式和内容截取情况会显示在材料卡片上。

- 文本型 PDF、Office 和文本文件在本机直接提取文字。PDF 和 PPTX 最多读取前 60 页。
- 没有文字层的扫描页和图片由本机 Tesseract 处理。安装 Tesseract 和 `chi_sim`、`chi_tra` 或 `eng` 语言包，确保 `tesseract` 在 PATH 里，Windows 默认安装目录也可自动识别。每份 PDF 最多 OCR 前 8 张扫描页。 [Tesseract 安装文档](https://tesseract-ocr.github.io/tessdoc/Installation)
- 原文件交给本机 Python 读取。点击生成后，客户端把你保留的材料文字和名称随生成要求发给你配置的模型。材料区随当前页面保留，生成历史保存生成的文稿和用量。

Word 导出支持基本标题、段落、列表和加粗。PPT 把一级标题当作封面、二级标题当作各页标题，导出可编辑的纯文本版式。生成结果会保存到历史，预览中的后续编辑只用于当前页面和导出。

## 用量与本地数据

- 用量来自 Chat Completions 响应的 `usage` 字段。API 只返回输入和输出时，客户端用两者相加得到总量。缺失的数据不会估算。统计范围是本机成功保存的生成请求，与服务商的账户账单范围可能不同。 [Chat Completions 接口参考](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create)
- 生成历史和用量存放在 `data/wenmo.sqlite3`，可通过 `--data` 指定其他位置。界面展示最近 50 份文稿。删除正文后会保留用量。
- 浏览器仅保存 API 地址和模型名称。API Key 留在当前页面内存中，刷新后需要重新填写。运行数据已列入 Git 忽略规则。
- 客户端只监听本机回环地址。文稿会由你选择的模型服务处理，提交前可自行检查材料中的个人信息。

## 开发与验证

```sh
python -m unittest discover -s tests -v
```

本地自动测试覆盖 11 个用例，包括生成、Token 记录、参考材料读取、联网引用、历史和 Office 导出。运行这些测试无需真实 API Key。

**已用 DeepSeek 官方 API 实测。** 使用 `deepseek-flash` 跑通了简历、通用申请书、开题报告、PPT 和论文五个模块。开题报告、PPT 和论文使用了本地提取的虚构参考材料，联网查证实测返回了可打开的网页引用。导出的 Word 和 PPT 文件已用独立库重新读取检查。桌面 Office 排版、中文扫描件 OCR 和 Windows 安装包仍待验收。

| 文件 | 用途 |
| --- | --- |
| `wenmo.py` | 本地 HTTP 服务、模型 API 调用和 SQLite 记录 |
| `office.py` | Word 和 PowerPoint 导出 |
| `materials.py` | 本地材料解析与扫描件 OCR |
| `static/` | 浏览器客户端 |
| `tests/` | 端到端 HTTP 测试和文件结构校验 |
