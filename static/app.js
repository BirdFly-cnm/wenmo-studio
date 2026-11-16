"use strict";

const $ = (id) => document.getElementById(id);
const nodes = {
  topic: $("topic"), prompt: $("prompt"), editor: $("editor"), paper: $("document"),
  settings: $("settings"), history: $("history"), generate: $("generate"),
};
const templates = {
  resume: {
    name: "简历", description: "先选目标岗位，再填写经历和成绩。",
    topicLabel: "目标岗位", topic: "产品实习生",
    help: "目标岗位、工作经历、项目成果、技能",
    prompt: "用一页中文简历呈现，突出用户调研和流程设计。",
    answers: {
      "resume-name": "林同学", "resume-school": "示例大学 · 信息管理 · 2027 届",
      "resume-grades": "GPA 3.6/4.0", "resume-awards": "2025 年校级创新竞赛二等奖",
      "resume-honors": "2025 年院系优秀学生", "resume-strengths": "Figma、Excel、用户访谈",
      "resume-experience": "校园二手交易调研。访谈 12 位同学，整理 3 类常见问题，独立绘制发布和搜索流程。",
    },
    sample: "# 林同学\n\n## 求职意向\nB 端产品实习生\n\n## 教育背景\n**示例大学 · 信息管理 · 2027 届**\nGPA 3.6 / 4.0\n\n## 项目经历\n**校园二手交易调研**\n- 访谈 12 位同学，整理 3 类常见问题。\n- 使用 Figma 绘制商品发布和搜索流程。\n\n## 技能\nFigma、Excel、用户访谈、流程梳理\n\n## 获奖与荣誉\n校级创新竞赛二等奖、院系优秀学生",
  },
  application: {
    name: "申请书", description: "整理申请事项、理由和执行计划。",
    topicLabel: "申请事项", topic: "借用学院教室",
    help: "收件人、申请事项、原因、时间与署名",
    prompt: "给学院写一份借用教室申请。我们是校读书会，希望下周三晚上使用一间可容纳 25 人的教室举办分享交流。活动结束后会清洁并恢复桌椅原位。具体日期和联系人留空。",
    sample: "# 教室借用申请书\n\n尊敬的学院老师：\n\n校读书会拟于[具体日期]晚间举办读书分享活动，预计参与人数为 25 人，现申请借用一间可容纳 25 人的教室。\n\n活动期间将由指定成员维护现场秩序。活动结束后，我们会清理场地并恢复桌椅原位。\n\n恳请批准。\n\n申请人：[待补充]\n\n联系人：[待补充]",
  },
  proposal: {
    name: "开题报告", description: "把选题整理成可以讨论和执行的研究方案。",
    topicLabel: "研究选题", topic: "高校食堂排队体验",
    help: "选题、研究问题、方法、进度安排",
    prompt: "围绕高校食堂排队体验写一份开题报告。计划观察不同时段的排队时间，做 10–15 次访谈，并对比校内两个食堂。请留出文献与参考资料占位。",
    sample: "# 高校食堂排队体验研究\n\n## 研究背景\n本研究拟了解不同就餐时段的排队情况，以及学生对等待过程的评价。\n\n## 研究问题\n- 两处食堂在不同时段的排队时间有何差异？\n- 学生如何权衡等待时间与餐品选择？\n\n## 研究方法\n记录两个食堂在不同时段的排队时间，并完成 10–15 次学生访谈。\n\n## 进度安排\n第 1 周确定观察方案，第 2–3 周收集资料，第 4 周整理和讨论。\n\n## 文献综述\n[待补充并核实相关文献]",
  },
  slides: {
    name: "PPT", description: "从主题和受众出发，生成分页面的演示文稿。",
    topicLabel: "演示主题", topic: "校园旧物交换日",
    help: "主题、受众、预计时长、页数与关键观点",
    prompt: "做一份面向新社团成员的 5 页 PPT，主题是校园旧物交换活动。介绍为什么做、现场流程、岗位分工和安全规则。语气轻松，内容落地。",
    sample: "# 校园旧物交换日\n新成员活动说明\n\n## 为什么做\n- 让闲置物品继续被使用。\n- 给同学提供一个认识彼此的机会。\n\n## 现场流程\n- 入场登记并给物品贴签。\n- 在展示区浏览，双方同意后交换。\n\n## 岗位分工\n- 签到组维护登记和标签。\n- 巡场组协助交换、记录问题。\n\n## 现场规则\n- 提前检查物品状态。\n- 活动结束后清点物品、恢复场地。",
  },
  paper: {
    name: "论文", description: "根据已有论点、资料和数据起草论文。",
    topicLabel: "论文主题", topic: "共享单车与地铁短距离接驳",
    help: "研究主题、核心论点、已有资料、引用格式",
    prompt: "起草一篇关于城市共享单车与地铁接驳的短论文。核心论点是单车补足短距离接驳，但受到停放管理和高峰供需错配的影响。先写论证框架，没有给出的数据和文献用占位符。",
    sample: "# 共享单车在地铁短距离接驳中的作用\n\n## 摘要\n本文讨论共享单车在地铁短距离接驳中的潜在价值，并从停放管理和高峰供需两个方面梳理限制。\n\n**关键词：**共享单车；地铁接驳；出行\n\n## 引言\n地铁站至目的地之间的短距离出行需要多种接驳方式。本文聚焦共享单车在这一环节的作用。\n\n## 论证框架\n- 讨论步行距离、骑行时间和可获得车辆之间的关系。\n- 分析停放点设置与高峰时段车辆调度。\n\n## 参考文献\n[待补充并核实引用来源]",
  },
};
const longForm = new Set(["proposal", "paper"]);
const materialKinds = new Set(["proposal", "slides", "paper"]);
const materialInputs = new Map();
const readingMaterials = new Set();
const materialLimit = 24000;
const materialFileLimit = 12 * 1024 * 1024;
const officeFileLimit = 64 * 1024 * 1024;
const styleButtons = [...document.querySelectorAll("[data-resume-style]")];
const resumeStyleNames = { classic: "简洁色条", sidebar: "深蓝双栏", jade: "青绿页眉", form: "表格登记" };
const resumeInputs = [...document.querySelectorAll("[data-resume]")];
const counts = new Intl.NumberFormat("zh-CN");
const dates = new Intl.DateTimeFormat("zh-CN", { dateStyle: "short", timeStyle: "short" });
const calendarDates = new Intl.DateTimeFormat("zh-CN", { dateStyle: "short" });
const drafts = new Map();
const outputs = new Map();
const defaultApi = "https://api.openai.com/v1";
const offline = location.protocol === "file:";
let kind = "resume";
let editing = false;
let pending = false;
let exporting = false;
let resumePhoto = null;
let photoSelection = 0;
let resumeStyle = "classic";
let config = { api: defaultApi, model: "", key: "" };
try {
  config.api = localStorage.getItem("wenmo.api") || defaultApi;
  config.model = localStorage.getItem("wenmo.model") || "";
  const savedStyle = localStorage.getItem("wenmo.resumeStyle");
  if (Object.hasOwn(resumeStyleNames, savedStyle)) resumeStyle = savedStyle;
} catch {
  // The app also works with browser storage disabled.
}

function feedback(id, message = "", error = false) {
  const element = $(id);
  element.textContent = message;
  element.classList.toggle("error", error);
}

function newElement(tag, text, className) {
  const element = document.createElement(tag);
  if (text !== undefined) element.textContent = text;
  if (className) element.className = className;
  return element;
}

function inline(element, text) {
  const cleaned = text.replace(/\[([^\]]+)\]\([^)]+\)/g, "$1");
  for (const part of cleaned.split(/(\*\*.+?\*\*|__.+?__|`[^`]+`)/g)) {
    if (part.startsWith("**") && part.endsWith("**") && part.length > 4 ||
        part.startsWith("__") && part.endsWith("__") && part.length > 4) {
      element.append(newElement("strong", part.slice(2, -2)));
    } else if (part.startsWith("`") && part.endsWith("`") && part.length > 2) {
      element.append(newElement("code", part.slice(1, -1)));
    } else {
      element.append(document.createTextNode(part));
    }
  }
  return element;
}

function markdown(container, text) {
  let list = null;
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim();
    const match = line.match(/^(#{1,6})\s+(.+)$/);
    const item = line.match(/^([-*+]|\d+[.)])\s+(.+)$/);
    if (item) {
      const tag = /\d/.test(item[1]) ? "ol" : "ul";
      if (list?.localName !== tag) {
        list = newElement(tag);
        container.append(list);
      }
      list.append(inline(newElement("li"), item[2]));
      continue;
    }
    list = null;
    if (match) container.append(inline(newElement("h" + Math.min(match[1].length, 3)), match[2]));
    else if (line && !/^`{3}|^-{3,}$/.test(line)) container.append(inline(newElement("p"), line));
  }
}

function plain(text) {
  return text.replace(/\[([^\]]+)\]\([^)]+\)/g, "$1").replace(/\*\*|__|`|\*/g, "");
}

function resumeSections(text) {
  const lines = text.split(/\r?\n/).map((line) => line.trim()).filter((line) =>
    line && !/^`{3}|^-{3,}$/.test(line));
  const first = lines[0]?.match(/^#\s+(.+)$/);
  if (first) lines.shift();
  const sections = [];
  let label = "";
  let body = [];
  for (const line of lines) {
    const heading = line.match(/^#{1,2}\s+(.+)$/);
    if (heading) {
      if (label || body.length) sections.push({ label, body });
      label = heading[1];
      body = [];
    } else {
      body.push(line);
    }
  }
  if (label || body.length) sections.push({ label, body });
  return { title: first?.[1] || "个人简历", sections };
}

function resumePreview(container, result) {
  const { title, sections } = resumeSections(result.content);
  const header = newElement("header", undefined, "resume-banner");
  if (result.photo) {
    const picture = newElement("img", undefined, "resume-photo");
    picture.src = "data:image/jpeg;base64," + result.photo;
    picture.alt = "简历照片";
    header.append(picture);
  }
  header.append(inline(newElement("h1"), title));

  const body = newElement("div", undefined, "resume-body");
  container.classList.add("resume-document", "resume-" + resumeStyle);
  if (resumeStyle !== "sidebar") container.append(header, body);
  for (const item of sections) {
    const block = newElement("section", undefined, "resume-section");
    if (item.label || resumeStyle === "form") block.append(inline(newElement("h2"), item.label || "基本资料"));
    const content = newElement("div", undefined, "resume-section-body");
    markdown(content, item.body.join("\n"));
    block.append(content);
    const sideInfo = !item.label || /意向|联系|资料|技能|荣誉|获奖|特长|证书|语言|评价/.test(item.label);
    (resumeStyle === "sidebar" && sideInfo ? header : body).append(block);
  }
  if (resumeStyle === "sidebar") container.append(header, body);
}

function letterLines(text) {
  return text.split(/\r?\n/).map((line) => line.trim()).filter((line) =>
    line && !/^`{3}|^-{3,}$/.test(line)).map((line, index) => {
    const value = plain(line.replace(/^(?:#{1,6}|[-*+]|\d+[.)])\s+/, ""));
    const signature = /^(?:申请人|联系人|日期)[：:]|^\[日期\]$|^(?:\d{4}|[〇零一二三四五六七八九]{4})年/.test(value);
    const greeting = /[：:]$|^(?:此致(?:敬礼[！!]?)?|敬礼[！!]?)$/.test(value);
    return { value, role: index === 0 ? "title" : signature ? "signature" : greeting ? "greeting" : "body" };
  });
}

function letterPreview(container, text) {
  container.classList.add("letter-document");
  for (const { value, role } of letterLines(text)) {
    container.append(newElement(role === "title" ? "h1" : "p", value, "letter-" + role));
  }
}

function materialsFor(current = kind) {
  if (!materialInputs.has(current)) materialInputs.set(current, []);
  return materialInputs.get(current);
}

function reviewedMaterials() {
  return materialsFor().map(({ name, text }) => ({ name, text: text.trim() })).filter(({ text }) => text);
}

function updateMaterialCount() {
  const items = materialsFor();
  const materialSize = reviewedMaterials().reduce((sum, item) => sum + Array.from(item.text).length, 0);
  const usage = $("material-count");
  usage.hidden = !items.length;
  usage.textContent = "参考材料 " + counts.format(materialSize) + " / 24,000 字";
  usage.classList.toggle("error", materialSize > materialLimit);
  const optional = kind === "resume" || (materialKinds.has(kind) && (materialSize > 0 || nodes.topic.value.trim()));
  nodes.prompt.required = !optional;
  $("prompt-status").textContent = optional ? "选填" : "必填";
  return materialSize;
}

function renderMaterials(openItem) {
  const entries = materialsFor();
  const list = $("material-list");
  list.replaceChildren();
  for (const item of entries) {
    const card = newElement("details", undefined, "material-card");
    const head = newElement("summary");
    head.append(newElement("strong", item.name), newElement("span", item.ocr ? "OCR" : "查看正文"));
    card.append(head);
    const fields = newElement("div", undefined, "material-body");
    for (const note of item.warnings || []) fields.append(newElement("p", note, "material-warning"));
    const text = newElement("textarea");
    text.setAttribute("aria-label", item.name + " 的材料文字");
    text.maxLength = materialLimit;
    text.rows = 5;
    text.value = item.text;
    text.addEventListener("input", () => {
      item.text = text.value;
      updateMaterialCount();
    });
    const remove = newElement("button", "移除材料", "text-button");
    remove.type = "button";
    remove.addEventListener("click", () => {
      entries.splice(entries.indexOf(item), 1);
      renderMaterials();
    });
    fields.append(text, remove);
    card.append(fields);
    list.append(card);
    if (item === openItem) {
      card.open = true;
      text.focus();
    }
  }
  const busy = readingMaterials.has(kind);
  $("material-input").disabled = offline || busy || pending || entries.length >= 5;
  $("material-choose").disabled = $("material-input").disabled;
  $("paste-material").disabled = pending || busy || entries.length >= 5;
  $("material-hint").textContent = offline ? "启动 Python 工作台后可读取文件。也可以先粘贴文字。" :
    "最多 5 份。Word 和 PPT 单份 64 MB，其余单份 12 MB。";
  updateMaterialCount();
}

async function importMaterials(files) {
  const source = kind;
  if (offline || pending || readingMaterials.has(source) || !materialKinds.has(source)) return;
  const entries = materialsFor(source);
  const selected = Array.from(files);
  const errors = [];
  const accepted = selected.slice(0, Math.max(0, 5 - entries.length));
  if (accepted.length < selected.length) errors.push("每个模块最多保留 5 份参考材料。");
  readingMaterials.add(source);
  renderMaterials();
  feedback("material-status", "正在本机读取材料…");
  try {
    for (const file of accepted) {
      const limit = /\.(docx|pptx)$/i.test(file.name) ? officeFileLimit : materialFileLimit;
      if (!file.size || file.size > limit) {
        errors.push(file.name + " 为空或超过 " + limit / (1024 * 1024) + " MB。");
        continue;
      }
      try {
        const response = await fetchResponse("/api/material", {
          method: "POST", headers: { "Content-Type": "application/octet-stream", "X-Material-Name": encodeURIComponent(file.name) },
          body: file,
        });
        entries.push(await response.json());
      } catch (error) {
        errors.push(file.name + " · " + error.message);
      }
    }
  } finally {
    readingMaterials.delete(source);
    if (kind === source) {
      renderMaterials();
      feedback("material-status", errors.join("\n") || "读取完成。请展开材料核对识别结果。", Boolean(errors.length));
    }
  }
}

function slides(container, text) {
  let title = "文墨演示文稿";
  const coverLines = [];
  const sections = [];
  let lines = coverLines;
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || /^`{3}|^-{3,}$/.test(line)) continue;
    const heading = line.match(/^(#{1,6})\s+(.+)$/);
    if (heading?.[1].length === 1 && !sections.length) {
      title = plain(heading[2]);
    } else if (heading) {
      lines = [];
      sections.push([plain(heading[2]), lines]);
    } else {
      const value = plain(line.replace(/^(?:[-*+]|\d+[.)])\s+/, ""));
      if (value.trim()) lines.push(value);
    }
  }
  const cover = newElement("section", undefined, "slide cover");
  cover.append(newElement("h1", title));
  if (coverLines.length) cover.append(newElement("p", coverLines[0]));
  container.append(cover);
  if (coverLines.length > 1) sections.unshift([sections.length ? "内容概览" : "正文", coverLines.slice(1)]);
  for (const [heading, items] of sections) {
    const chunks = items.flatMap((item) => item.match(/[\s\S]{1,94}/gu) || []);
    for (let offset = 0; offset < Math.max(1, chunks.length); offset += 5) {
      const page = newElement("section", undefined, "slide");
      page.append(newElement("h2", heading + (offset ? "（续）" : "")));
      const bullets = newElement("ul");
      for (const item of chunks.slice(offset, offset + 5)) bullets.append(newElement("li", item));
      if (bullets.childElementCount) page.append(bullets);
      container.append(page);
    }
  }
}

function updateCounter() {
  const length = submissionPrompt().length;
  $("counter").textContent = counts.format(length) + " / 16,000";
  $("counter").classList.toggle("error", length > 16000);
}

function submissionPrompt() {
  const topic = nodes.topic.value.trim();
  const requirements = nodes.prompt.value.trim();
  if (kind === "resume") {
    const answers = resumeInputs.filter((input) => input.value.trim())
      .map((input) => input.dataset.resume + "：" + input.value.trim());
    if (topic) answers.unshift("目标岗位：" + topic);
    if (requirements) answers.push("补充要求：" + requirements);
    return answers.join("\n\n");
  }
  return topic ? templates[kind].topicLabel + "：" + topic + "\n\n" + requirements : requirements;
}

function showKind(next) {
  drafts.set(kind, { topic: nodes.topic.value, prompt: nodes.prompt.value });
  kind = next;
  editing = false;
  const template = templates[kind];
  const resume = kind === "resume";
  for (const button of document.querySelectorAll("[data-kind]")) {
    button.setAttribute("aria-pressed", String(button.dataset.kind === kind));
  }
  $("crumb").textContent = template.name;
  $("page-title").textContent = "生成" + (kind === "slides" ? " PPT" : template.name);
  $("kind-description").textContent = template.description;
  $("compose-title").textContent = resume ? "简历问卷" : "撰写要求";
  $("resume-fields").hidden = !resume;
  $("resume-templates").hidden = !resume;
  $("material-fields").hidden = !materialKinds.has(kind);
  $("topic-status").textContent = resume ? "必填" : "选填";
  $("prompt-label").textContent = resume ? "补充要求" : "生成要求";
  nodes.topic.required = resume;
  $("topic-label").textContent = template.topicLabel;
  $("prompt-help").textContent = resume ? "例如：控制在一页，突出项目经历。" : "建议提供 " + template.help;
  $("recommended-openai").textContent = longForm.has(kind) ? "gpt-5.4" : "gpt-5.4-mini";
  $("recommended-deepseek").textContent = longForm.has(kind) ? "deepseek-v4-pro" : "deepseek-flash";
  nodes.topic.placeholder = "例如：" + template.topic;
  nodes.prompt.placeholder = resume ? "补充语言、风格、篇幅或岗位要求。" :
    template.help + "。也可以说明文稿的语言、风格和篇幅。";
  nodes.topic.value = drafts.get(kind)?.topic || "";
  nodes.prompt.value = drafts.get(kind)?.prompt || "";
  $("web-search").checked = false;
  refreshSearchOption();
  feedback("material-status");
  renderMaterials();
  $("format-label").textContent = offline ? "离线可下载 Markdown" :
    "可导出 " + (kind === "slides" ? "PPTX" : "Word") + " / Markdown";
  $("download-office").textContent = kind === "slides" ? "下载 PPTX" : "下载 Word";
  updateCounter();
  feedback("generate-status");
  feedback("export-status");
  render();
}

function render() {
  const result = outputs.get(kind);
  nodes.paper.replaceChildren();
  nodes.paper.className = "document";
  nodes.paper.classList.toggle("deck", kind === "slides");
  $("empty").hidden = Boolean(result);
  nodes.paper.hidden = !result || editing;
  nodes.editor.hidden = !result || !editing;
  $("edit").disabled = !result;
  $("edit").textContent = editing ? "完成编辑" : "编辑";
  $("preview-meta").textContent = result?.meta || "生成后可编辑并导出";
  for (const button of styleButtons) {
    button.setAttribute("aria-pressed", String(button.dataset.resumeStyle === resumeStyle));
  }
  if (result && !editing) {
    if (kind === "resume") resumePreview(nodes.paper, result);
    else if (kind === "application") letterPreview(nodes.paper, result.content);
    else (kind === "slides" ? slides : markdown)(nodes.paper, result.content);
  }
  renderSearchSources(result);
  syncDownloads();
}

function refreshSearchOption() {
  const controls = $("search-option");
  const option = $("web-search");
  controls.hidden = !materialKinds.has(kind);
  let eligible = false;
  try {
    const url = new URL(config.api);
    const path = url.pathname.replace(/\/+$/, "");
    eligible = !offline && !controls.hidden && config.model === "deepseek-flash" &&
      url.origin === "https://api.deepseek.com" && !url.username && !url.password && !url.search && !url.hash &&
      ["", "/v1", "/chat/completions", "/v1/chat/completions"].includes(path);
  } catch {
    // The configuration dialog and backend handle invalid URLs.
  }
  option.disabled = !eligible || pending;
  if (!eligible) option.checked = false;
  $("search-help").textContent = eligible
    ? "适合近期政策、统计和研究。DeepSeek 会根据主题决定是否搜索，搜索另计费。"
    : "需要近期政策、数据或研究资料时，推荐在 API 设置使用 DeepSeek 官方地址和 deepseek-flash。";
}

function renderSearchSources(result) {
  const panel = $("search-sources");
  const list = $("search-source-list");
  const search = result?.search;
  panel.hidden = !search;
  list.replaceChildren();
  if (!search) return;
  const sources = search.sources || [];
  const count = Number.isInteger(search.calls) ? "计费搜索 " + counts.format(search.calls) + " 次。 " : "";
  const time = result.created_at ? "查证时间 " + dates.format(new Date(result.created_at)) + "。 " : "";
  $("search-summary").textContent = time + count +
    (sources.length ? "可打开来源核对数字、日期和原文。" : "本次没有可核对的网页引用。");
  for (const { title, url, date } of sources) {
    if (!/^https?:\/\//i.test(url)) continue;
    const link = newElement("a", title);
    link.href = url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    const row = newElement("li");
    row.append(link);
    if (date) {
      const label = newElement("small", date.includes("T") ? calendarDates.format(new Date(date)) : date);
      label.title = "日期由服务商提供，以来源原文为准。";
      row.append(label);
    }
    list.append(row);
  }
}

function syncDownloads() {
  const enabled = !exporting && Boolean(outputs.get(kind)?.content.trim());
  $("download-md").disabled = !enabled;
  $("download-office").disabled = offline || !enabled;
  $("copy-letter").hidden = kind !== "application";
  $("copy-letter").disabled = !enabled;
}

async function fetchResponse(path, options = {}) {
  let response;
  try {
    response = await fetch(path, options);
  } catch {
    throw new Error("无法连接本地工作台。请确认运行窗口仍然开启。");
  }
  if (!response.ok) {
    const failure = await response.json().catch(() => ({}));
    throw new Error(failure.error || "操作失败，请重试。");
  }
  return response;
}

function request(path, data) {
  return fetchResponse(path, data === undefined ? {} : {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data),
  });
}

function outputLabel(record) {
  const amount = record.total_tokens === null ? "用量未回传" : counts.format(record.total_tokens) + " Tokens";
  return record.model + " · " + amount + (record.truncated ? " · 输出已截断" : "");
}

function showOutput(result) {
  outputs.set(kind, result);
  editing = false;
  feedback("export-status");
  render();
}

function refreshSettings() {
  $("api-label").textContent = offline ? "启动与 API 配置" : config.model ? "模型 · " + config.model : "配置 API";
  $("api-dot").classList.toggle("ready", !offline && Boolean(config.model));
  refreshSearchOption();
}

function openSettings() {
  if (!offline) {
    $("api").value = config.api;
    $("model").value = config.model;
    $("key").value = config.key;
  }
  nodes.settings.showModal();
}

function setPhoto(encoded) {
  resumePhoto = encoded;
  const thumb = $("photo-thumb");
  thumb.hidden = !encoded;
  $("photo-remove").hidden = !encoded;
  if (encoded) thumb.src = "data:image/jpeg;base64," + encoded;
  else thumb.removeAttribute("src");
  const result = outputs.get("resume");
  if (result) result.photo = encoded;
  if (kind === "resume") render();
}

async function normalizePhoto(file) {
  if (!["image/jpeg", "image/png"].includes(file.type) || file.size > 5 * 1024 * 1024) {
    throw new Error("请选择小于或等于 5 MB 的 JPG 或 PNG 图片。");
  }
  let bitmap;
  try {
    bitmap = await createImageBitmap(file);
    const scale = Math.min(1, 960 / Math.max(bitmap.width, bitmap.height));
    const canvas = document.createElement("canvas");
    canvas.width = Math.max(1, Math.round(bitmap.width * scale));
    canvas.height = Math.max(1, Math.round(bitmap.height * scale));
    const context = canvas.getContext("2d", { alpha: false });
    context.fillStyle = "#ffffff";
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
    for (const quality of [0.85, 0.68, 0.5]) {
      const encoded = canvas.toDataURL("image/jpeg", quality).split(",")[1];
      if (encoded && encoded.length <= 360000) return encoded;
    }
  } catch {
    throw new Error("读不到这张图片，请重新选择 JPG 或 PNG。");
  } finally {
    bitmap?.close();
  }
  throw new Error("照片压缩后仍过大，请换一张尺寸较小的图片。");
}

async function refreshHistory(showList = false) {
  const { items, stats } = await (await request("/api/history")).json();
  $("total-tokens").textContent = counts.format(stats.total_tokens);
  $("prompt-tokens").textContent = counts.format(stats.prompt_tokens);
  $("completion-tokens").textContent = counts.format(stats.completion_tokens);
  $("usage-note").textContent = "本机已记录 " + counts.format(stats.requests) + " 次生成。" +
    (stats.unknown ? counts.format(stats.unknown) + " 次未回传完整总用量。" : "按 API 回传用量累计。");
  if (!showList) return;
  const list = $("history-list");
  list.replaceChildren();
  feedback("history-status", items.length ? "" : "暂无生成记录。");
  for (const record of items) {
    const row = newElement("li");
    const open = newElement("button", undefined, "load-record");
    open.type = "button";
    open.append(newElement("strong", record.title), newElement("small",
      templates[record.kind].name + " · " + dates.format(new Date(record.created_at)) + " · " + outputLabel(record)));
    open.addEventListener("click", async () => {
      try {
        const saved = await (await request("/api/history/" + record.id)).json();
        showKind(saved.kind);
        if (saved.kind === "resume") {
          photoSelection += 1;
          setPhoto(saved.photo || null);
          feedback("photo-status");
        }
        showOutput({ ...saved, meta: outputLabel(saved) + " · 历史记录" });
        nodes.history.close();
      } catch (error) {
        feedback("history-status", error.message, true);
      }
    });
    const remove = newElement("button", "删除正文", "button secondary");
    remove.type = "button";
    remove.addEventListener("click", async () => {
      if (!confirm("删除这份历史文稿的正文？对应的 Token 用量会保留。")) return;
      try {
        await request("/api/history/delete", { id: record.id });
        if (outputs.get(record.kind)?.id === record.id) {
          outputs.delete(record.kind);
          if (record.kind === "resume") setPhoto(null);
          if (record.kind === kind) {
            editing = false;
            nodes.editor.value = "";
            render();
          }
        }
        await refreshHistory(true);
      } catch (error) {
        feedback("history-status", error.message, true);
      }
    });
    row.append(open, remove);
    list.append(row);
  }
}

async function download(format) {
  const result = outputs.get(kind);
  if (!result || exporting) return;
  const heading = result.content.match(/^#\s+(.+)$/m)?.[1];
  const title = Array.from(heading || result.title || templates[kind].name).slice(0, 100).join("");
  feedback("export-status", "正在准备文件…");
  exporting = true;
  syncDownloads();
  try {
    let file;
    let filename = (title.replace(/[<>:"/\\|?*]/g, "_").trim() || "wenmo") + "." + format;
    if (format === "md") {
      const links = (result.search?.sources || []).map(({ title, date, url }) =>
        "- " + title + (date ? "（" + date + "）" : "") + " <" + url.replaceAll("<", "%3C").replaceAll(">", "%3E") + ">");
      const sources = links.length ? "\n\n## 联网来源\n\n" + links.join("\n") : "";
      file = new Blob([result.content.trim() + sources + "\n"], { type: "text/markdown;charset=utf-8" });
    } else {
      const response = await request("/api/export", {
        format, content: result.content, title, photo: result.photo || "",
        resume_style: kind === "resume" ? resumeStyle : "",
        application: kind === "application",
      });
      const headerFilename = response.headers.get("Content-Disposition")?.match(/filename\*=UTF-8''(.+)$/)?.[1];
      if (headerFilename) filename = decodeURIComponent(headerFilename);
      file = await response.blob();
    }
    const url = URL.createObjectURL(file);
    const link = newElement("a");
    link.href = url;
    link.download = filename;
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 30000);
    feedback("export-status", "文件已交给浏览器下载。");
  } catch (error) {
    feedback("export-status", error.message, true);
  } finally {
    exporting = false;
    syncDownloads();
  }
}

for (const button of document.querySelectorAll("[data-kind]")) {
  button.addEventListener("click", () => showKind(button.dataset.kind));
}
for (const button of styleButtons) {
  button.addEventListener("click", () => {
    resumeStyle = button.dataset.resumeStyle;
    try { localStorage.setItem("wenmo.resumeStyle", resumeStyle); } catch { /* temporary selection */ }
    if (!outputs.has("resume")) showExample();
    else render();
  });
}
for (const button of document.querySelectorAll("[data-close]")) {
  button.addEventListener("click", () => $(button.dataset.close).close());
}
$("settings-open").addEventListener("click", openSettings);
nodes.settings.addEventListener("close", () => { $("key").value = ""; });
$("settings-form").addEventListener("submit", (event) => {
  event.preventDefault();
  if (offline) return;
  config = { api: $("api").value.trim(), model: $("model").value.trim(), key: $("key").value.trim() };
  try {
    localStorage.setItem("wenmo.api", config.api);
    localStorage.setItem("wenmo.model", config.model);
  } catch {
    // Keep the configuration in memory if browser storage is disabled.
  }
  refreshSettings();
  nodes.settings.close();
});
$("history-open").addEventListener("click", async () => {
  $("history-list").replaceChildren();
  feedback("history-status", "正在读取本地记录…");
  nodes.history.showModal();
  try {
    await refreshHistory(true);
  } catch (error) {
    feedback("history-status", error.message, true);
  }
});
nodes.prompt.addEventListener("input", updateCounter);
nodes.topic.addEventListener("input", () => {
  updateCounter();
  updateMaterialCount();
});
$("material-input").addEventListener("change", async (event) => {
  const files = Array.from(event.target.files);
  event.target.value = "";
  if (files.length) await importMaterials(files);
});
$("material-choose").addEventListener("click", () => $("material-input").click());
$("paste-material").addEventListener("click", () => {
  if (!materialKinds.has(kind) || pending) return;
  const items = materialsFor();
  if (items.length >= 5) return;
  const item = { name: "粘贴文字", text: "", warnings: [] };
  items.push(item);
  renderMaterials(item);
});
for (const input of resumeInputs) input.addEventListener("input", updateCounter);
$("photo-input").addEventListener("change", async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  const selected = ++photoSelection;
  event.target.value = "";
  feedback("photo-status", "正在读取图片…");
  try {
    const encoded = await normalizePhoto(file);
    if (selected === photoSelection) {
      setPhoto(encoded);
      feedback("photo-status", "照片已选好，仅用于本地简历。");
    }
  } catch (error) {
    if (selected === photoSelection) feedback("photo-status", error.message, true);
  }
});
$("photo-remove").addEventListener("click", () => {
  photoSelection += 1;
  setPhoto(null);
  feedback("photo-status", "已移除照片。");
});
$("fill-example").addEventListener("click", () => {
  const hasAnswers = kind === "resume" && resumeInputs.some((input) => input.value.trim());
  if ((hasAnswers || nodes.topic.value.trim() || nodes.prompt.value.trim()) && !confirm("用示例替换当前表单内容？")) return;
  const template = templates[kind];
  nodes.topic.value = template.topic;
  nodes.prompt.value = template.prompt;
  if (kind === "resume") {
    for (const input of resumeInputs) input.value = template.answers[input.id] || "";
  }
  updateCounter();
  updateMaterialCount();
  nodes.prompt.focus();
});
function showExample() {
  const template = templates[kind];
  showOutput({ content: template.sample, title: template.name + "示例", meta: "内置示例 · 0 Tokens",
    demo: true, photo: kind === "resume" ? resumePhoto : null });
}
$("demo").addEventListener("click", () => {
  if (outputs.has(kind) && !confirm("在预览区打开示例？当前预览会被替换。")) return;
  showExample();
});
$("compose-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (pending || offline) return;
  if (readingMaterials.has(kind)) {
    feedback("generate-status", "请等参考材料读取完成。", true);
    return;
  }
  if (!config.model) {
    openSettings();
    return;
  }
  const materials = materialKinds.has(kind) ? reviewedMaterials() : [];
  if (kind === "resume" ? !nodes.topic.value.trim() :
      !nodes.prompt.value.trim() && !(materialKinds.has(kind) && (nodes.topic.value.trim() || materials.length))) {
    feedback("generate-status", kind === "resume" ? "请填写目标岗位。" : "请填写生成要求或补充参考材料。", true);
    return;
  }
  if (updateMaterialCount() > materialLimit) {
    feedback("generate-status", "参考材料合计超过 24,000 字，请删减后再生成。", true);
    return;
  }
  const prompt = submissionPrompt();
  if (prompt.length > 16000) {
    feedback("generate-status", "请将表单内容缩短至 16,000 字以内。", true);
    return;
  }
  if (outputs.get(kind)?.edited && !confirm("生成新的文稿会替换当前编辑中的内容。继续生成？")) return;
  pending = true;
  const sourceKind = kind;
  const search = $("web-search").checked && !$("web-search").disabled;
  const controls = [...document.querySelectorAll("[data-kind]"), $("demo"), $("history-open"),
    $("photo-input"), $("photo-remove"), $("material-input"), $("material-choose"), $("paste-material"), $("web-search"), nodes.generate];
  controls.forEach((control) => { control.disabled = true; });
  feedback("generate-status", "正在等待模型返回文稿…");
  try {
    const generation = { ...config, kind: sourceKind, prompt };
    if (sourceKind === "resume" && resumePhoto) generation.photo = resumePhoto;
    if (search) generation.web_search = true;
    if (materials.length) generation.materials = materials;
    const record = await (await request("/api/generate", generation)).json();
    showOutput({ ...record, meta: outputLabel(record) });
    feedback("generate-status", record.unsaved ? "生成完成，但未能保存到本地历史。请先导出文稿。" : "文稿已生成并保存到历史。", record.unsaved);
    await refreshHistory().catch(() => { $("usage-note").textContent = "暂时无法读取本地用量。"; });
  } catch (error) {
    feedback("generate-status", error.message, true);
  } finally {
    pending = false;
    controls.forEach((control) => { control.disabled = false; });
    refreshSearchOption();
    renderMaterials();
  }
});
$("edit").addEventListener("click", () => {
  editing = !editing;
  const result = outputs.get(kind);
  if (editing) nodes.editor.value = result.content;
  render();
  if (editing) nodes.editor.focus();
});
nodes.editor.addEventListener("input", () => {
  const result = outputs.get(kind);
  result.content = nodes.editor.value;
  result.edited = true;
  result.meta = result.meta.replace(/ · 已编辑$/, "") + " · 已编辑";
  $("preview-meta").textContent = result.meta;
  syncDownloads();
});
$("download-md").addEventListener("click", () => download("md"));
$("download-office").addEventListener("click", () => download(kind === "slides" ? "pptx" : "docx"));
$("copy-letter").addEventListener("click", async () => {
  const result = outputs.get("application");
  if (!result) return;
  const text = letterLines(result.content)
    .map(({ value, role }) => (role === "body" ? "　　" : "") + value).join("\n\n");
  try {
    await navigator.clipboard.writeText(text);
    feedback("export-status", "已复制誊写稿。");
  } catch {
    feedback("export-status", "浏览器未允许复制，可以选中誊写稿正文手动复制。", true);
  }
});

refreshSettings();
showKind(kind);
if (offline) {
  $("offline-note").hidden = false;
  $("settings-live").hidden = true;
  $("settings-offline").hidden = false;
  $("history-open").disabled = true;
  nodes.generate.disabled = true;
  $("usage-note").textContent = "启动工作台后可查看实际用量。";
} else {
  refreshHistory().catch(() => { $("usage-note").textContent = "暂时无法读取本地用量。"; });
}
