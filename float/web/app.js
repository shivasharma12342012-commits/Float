/* Float — the working surface.
 *
 * One script, no build step, no framework. It has to start instantly on a
 * ₹28,000 school laptop, so everything here is plain DOM and one fetch stream.
 *
 * Layout of this file:
 *   1  state + plumbing
 *   2  boot and the greeting
 *   3  the conversation: sending, streaming, rendering
 *   4  markdown
 *   5  cards (files, steps, tasks)
 *   6  the drawer: toolkit, classes, to-do, files
 *   7  settings
 *   8  computer control
 */

/* ══════════════════════════════════ 1. state + plumbing ══════════════════ */

const TOKEN = sessionStorage.getItem("float.token");
if (!TOKEN) location.replace("/login");

const $ = (id) => document.getElementById(id);
const make = (tag, cls, text) => {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text !== undefined) node.textContent = text;
  return node;
};

const S = {
  boot: null,
  user: null,
  conv: null,           // current conversation id
  model: localStorage.getItem("float.model") || "",
  attachments: [],
  streaming: false,
  abort: null,
  driving: false,
};

async function api(path, options = {}) {
  const init = {
    method: options.method || (options.body === undefined ? "GET" : "POST"),
    headers: { Authorization: "Bearer " + TOKEN },
  };
  if (options.body !== undefined) {
    init.headers["Content-Type"] = "application/json";
    init.body = JSON.stringify(options.body);
  }
  let res;
  try {
    res = await FloatSecure.fetch(path, init);
  } catch (err) {
    // The browser could not reach Float at all (it was closed, or the laptop slept).
    throw new Error(OFFLINE_MESSAGE);
  }
  if (res.status === 401) { sessionStorage.removeItem("float.token"); location.replace("/login"); return; }
  const data = await res.json().catch(() => ({}));
  if (res.status === 403 && data.must_change) {
    if (!api.nagged) { api.nagged = true; openSettings("security"); }
    throw new Error(data.error);
  }
  if (!res.ok) throw new Error(data.error || "Something went wrong at Float's end. Please try again.");
  return data;
}

const OFFLINE_MESSAGE =
  "Float can't be reached right now. If you closed its window, open Float again. Your saved work is safe.";

/** Turn whatever went wrong into a sentence an operator can act on. */
function friendly(err) {
  const text = err && err.message ? String(err.message) : "";
  if (!text || /failed to fetch|networkerror|load failed|network request failed|aborted/i.test(text)) {
    return OFFLINE_MESSAGE;
  }
  return text;
}

// Safety net: an unexpected error should never fail silently or show raw jargon.
window.addEventListener("unhandledrejection", (event) => {
  event.preventDefault();
  if (event.reason && event.reason.name === "AbortError") return;
  try { toast(friendly(event.reason), true); } catch { /* the page itself is not ready yet */ }
});

let toastTimer = null;
function toast(text, bad = false) {
  const node = $("toast");
  node.textContent = text;
  node.className = "toast" + (bad ? " bad" : "");
  node.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (node.hidden = true), bad ? 5200 : 3200);
}

const escapeHtml = (text) =>
  String(text).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function bytes(n) {
  n = Math.max(0, Number(n) || 0);
  if (n < 1024) return n + " B";
  if (n < 1024 * 1024) return (n / 1024).toFixed(0) + " KB";
  return (n / 1048576).toFixed(1) + " MB";
}

function when(seconds) {
  const gap = Math.max(0, Date.now() / 1000 - (Number(seconds) || 0));
  if (gap < 90) return "just now";
  if (gap < 3600) return Math.round(gap / 60) + " min ago";
  if (gap < 86400) return Math.round(gap / 3600) + " h ago";
  if (gap < 7 * 86400) return Math.round(gap / 86400) + " d ago";
  return new Date(seconds * 1000).toLocaleDateString("en-IN", { day: "numeric", month: "short" });
}

/* ══════════════════════════════════ 2. boot ═════════════════════════════ */

async function boot() {
  let data;
  try {
    data = await api("/api/bootstrap");
  } catch (err) {
    document.body.innerHTML =
      '<div class="empty" style="padding-top:22vh"><b>Float could not start</b>' +
      escapeHtml(friendly(err)) +
      '<p><button class="btn" onclick="location.reload()">Try again</button></p></div>';
    return;
  }
  if (!data) return;

  S.boot = data;
  S.user = data.user;

  theme(data.user.appearance || "system");
  paintIdentity();
  paintGreeting(data.greeting, data.reflection);
  paintThreads(data.conversations);
  paintNotices(data.notices);
  paintCounts();
  paintModelChip();
  paintAssistChip();

  $("count-kit").textContent = data.toolkit.length;
  $("open-admin").hidden = data.user.role !== "admin";

  if (data.user.must_change || sessionStorage.getItem("float.must_change")) {
    sessionStorage.removeItem("float.must_change");
    openSettings("security");
    toast("Your admin gave you a temporary password. Set your own now.");
  } else if (!Object.keys(data.keys || {}).length && !data.models.some((m) => m.ready)) {
    openSettings("models");
  }

  pollComputer();
}

function paintIdentity() {
  const name = (S.user.name || S.user.email || "T").trim();
  $("me-name").textContent = name;
  $("me-avatar").textContent = (name.charAt(0) || "T").toUpperCase();
  $("me-sub").textContent = S.user.role === "admin" ? "Admin · Settings" : "Settings";
  $("school-tag").textContent = S.user.school || "";
}

/** The greeting. Times New Roman, no network, nothing to click through. */
function paintGreeting(greeting, reflection) {
  showGreeting(true);
  $("g-headline").textContent = greeting.headline;
  $("g-detail").textContent = greeting.detail || "";
  $("g-detail").className = "detail" + (greeting.tone === "urgent" ? " urgent" : "");

  if (reflection) {
    $("reflection").hidden = false;
    $("reflection-text").textContent = reflection;
  }
}

function paintThreads(list) {
  const box = $("threads");
  box.innerHTML = "";
  if (!list.length) {
    box.append(make("div", "rail-heading", "Nothing yet."));
    return;
  }
  list.forEach((conv) => {
    const row = make("button", "thread");
    row.type = "button";
    row.dataset.id = String(conv.id);
    row.setAttribute("aria-current", String(conv.id) === String(S.conv));
    row.append(make("span", null, conv.title || "Untitled"));

    const close = make("button", "x", "×");
    close.type = "button";
    close.setAttribute("aria-label", "Delete conversation");
    close.title = "Delete";
    close.addEventListener("click", async (event) => {
      event.stopPropagation();
      if (!confirm(`Delete "${conv.title}"? The files it made stay in Files.`)) return;
      await api(`/api/conversations/${conv.id}`, { method: "DELETE", body: {} });
      if (String(S.conv) === String(conv.id)) newThread();
      refreshThreads();
    });
    row.append(close);

    row.addEventListener("click", () => openThread(conv.id));
    box.append(row);
  });
}

async function refreshThreads() {
  const data = await api("/api/conversations");
  if (data) paintThreads(data.conversations);
}

function paintNotices(notices) {
  const strip = $("notice-strip");
  if (!notices || !notices.length) { strip.hidden = true; return; }
  strip.hidden = false;
  strip.innerHTML = "";
  strip.className = "notice-strip" + (notices[0].level === "warn" ? " warn" : "");
  notices.slice(0, 2).forEach((notice) => {
    strip.append(make("b", null, notice.title));
    if (notice.body) strip.append(make("span", null, notice.body));
  });
}

function paintCounts() {
  $("count-classes").textContent = S.boot.classes.length || "";
  $("count-tasks").textContent = S.boot.tasks.length || "";
  $("count-files").textContent = S.boot.artifacts.length || "";
}

function paintModelChip() {
  const models = S.boot.models || [];
  const ready = models.filter((m) => m.ready);
  const chosen = models.find((m) => m.id === S.model) || ready[0];
  if (chosen) {
    S.model = chosen.id;
    $("model-label").textContent = chosen.label;
    $("chip-model").classList.remove("on");
  } else {
    $("model-label").textContent = "Add a key";
    $("chip-model").classList.add("on");
  }
}

function paintAssistChip() {
  const levels = { coach: "Coach me", draft: "Draft it", full: "Do it all" };
  $("assist-label").textContent = levels[S.user.assist_level] || "Draft it";
}

/* ══════════════════════════════════ 3. the conversation ═════════════════ */

/** Landing layout (centred greeting + composer) only while the welcome shows. */
function showGreeting(on) {
  $("greeting").hidden = !on;
  document.querySelector(".main").classList.toggle("landing", on);
}

/* Back / forward between the home screen and the conversations opened this session. */
const NAV = { stack: [{ t: "home" }], i: 0, replaying: false };
function navPaint() {
  $("nav-back").disabled = NAV.i <= 0;
  $("nav-forward").disabled = NAV.i >= NAV.stack.length - 1;
}
function navPush(entry) {
  if (NAV.replaying) return;
  const cur = NAV.stack[NAV.i];
  if (cur && cur.t === entry.t && cur.id === entry.id) return;
  NAV.stack = NAV.stack.slice(0, NAV.i + 1);
  NAV.stack.push(entry);
  NAV.i = NAV.stack.length - 1;
  navPaint();
}
async function navGo(step) {
  const j = NAV.i + step;
  if (j < 0 || j >= NAV.stack.length) return;
  NAV.i = j;
  NAV.replaying = true;
  try {
    const e = NAV.stack[j];
    if (e.t === "home") newThread(); else await openThread(e.id);
  } finally { NAV.replaying = false; navPaint(); }
}

function newThread() {
  if (S.streaming && S.abort) S.abort.abort();
  navPush({ t: "home" });
  S.conv = null;
  $("composer-note").textContent = "";
  $("turns").innerHTML = "";
  showGreeting(true);
  $("chip-thread").hidden = true;
  document.querySelectorAll(".thread").forEach((t) => t.setAttribute("aria-current", "false"));
  $("input").focus();
}

let openSeq = 0;
async function openThread(convId) {
  if (S.streaming) { toast("Wait for this answer to finish, or press stop."); return; }
  const seq = ++openSeq;
  document.querySelectorAll(".thread").forEach((t) => t.setAttribute("aria-current", String(t.dataset.id === String(convId))));
  const data = await api(`/api/conversations/${convId}`);
  if (!data || seq !== openSeq) return;
  navPush({ t: "thread", id: convId });
  S.conv = convId;
  showGreeting(false);
  $("chip-thread").hidden = false;
  $("chip-thread-title").textContent = data.conversation.title;
  $("turns").innerHTML = "";

  const files = {};
  (data.artifacts || []).forEach((a) => (files[a.id] = a));

  data.messages.forEach((message) => {
    if (message.role === "user") addUserTurn(message.content);
    else {
      const turn = addFloatTurn();
      turn.prose.innerHTML = markdown(message.content);
    }
  });

  // File cards belong at the end of a reopened thread — the model's words
  // referring to them have already been read.
  const last = $("turns").lastElementChild;
  if (last && Object.keys(files).length) {
    Object.values(files).forEach((artifact) => last.append(fileCard(artifact)));
  }

  document.querySelectorAll(".thread").forEach((t) => t.setAttribute("aria-current", String(t.dataset.id === String(convId))));
  scrollDown();
  closeDrawer();
}

function addUserTurn(text, attachments) {
  const turn = make("div", "turn turn-user");
  const who = make("div", "turn-who");
  who.append(make("span", "avatar", (S.user.name || "?").charAt(0).toUpperCase()));
  who.append(make("span", null, "You"));
  turn.append(who);
  turn.append(make("div", "user-said", text));

  if (attachments && attachments.length) {
    const strip = make("div", "turn-files");
    attachments.forEach((file) => {
      if (file.kind === "image") {
        const img = document.createElement("img");
        img.src = `data:${file.mime};base64,${file.data}`;
        img.alt = file.name;
        strip.append(img);
      } else {
        strip.append(make("span", "doc", file.name));
      }
    });
    turn.append(strip);
  }

  $("turns").append(turn);
  scrollDown();
  return turn;
}

function addFloatTurn() {
  const turn = make("div", "turn");
  const who = make("div", "turn-who");
  const mark = make("img", "float-mark float-logo");
  mark.src = "/float.ico"; mark.alt = "";
  who.append(mark);
  who.append(make("span", null, "Float"));
  turn.append(who);

  const prose = make("div", "prose");
  turn.append(prose);
  $("turns").append(turn);
  return { node: turn, prose, append: (child) => turn.append(child) };
}

let stickToBottom = true;
function scrollDown(force = true) {
  const stream = $("stream");
  if (!force && !stickToBottom) return;
  stream.style.scrollBehavior = "auto";   // smooth-scroll made streaming lag
  stream.scrollTop = stream.scrollHeight;
  stickToBottom = true;
}
$("stream").addEventListener("scroll", () => {
  const s = $("stream");
  stickToBottom = s.scrollHeight - s.scrollTop - s.clientHeight < 80;
}, { passive: true });

/** Send whatever is in the composer (or a prompt handed in by the toolkit). */
async function send(prompt, convId) {
  if (S.streaming) return;
  const input = $("input");
  const text = (prompt !== undefined ? prompt : input.value).trim();
  const attachments = S.attachments.slice();
  if (!text && !attachments.length) return;

  if (convId !== undefined) S.conv = convId;
  if (prompt === undefined) { input.value = ""; grow(); }
  clearAttachments();

  showGreeting(false);
  addUserTurn(text, attachments);

  const turn = addFloatTurn();
  const waiting = make("div", "working");
  waiting.append(make("span", "pulse"));
  waiting.append(make("span", null, "Thinking…"));
  turn.node.append(waiting);
  scrollDown();

  setStreaming(true);
  let raw = "";
  let renderQueued = false;
  let stepsCard = null;

  try {
    S.abort = new AbortController();
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: "Bearer " + TOKEN },
      signal: S.abort.signal,
      body: JSON.stringify({
        message: LENSES[lens].rule ? text + "\n\n[Lens: " + LENSES[lens].rule + "]" : text,
        conv_id: S.conv,
        model: S.model,
        attachments,
        allow_computer: true,
      }),
    });

    if (!res.ok) {
      const problem = await res.json().catch(() => ({}));
      throw new Error(problem.error || "Float could not start that answer.");
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      let cut;
      while ((cut = buffer.indexOf("\n\n")) !== -1) {
        const frame = buffer.slice(0, cut);
        buffer = buffer.slice(cut + 2);
        const line = frame.split("\n").find((l) => l.startsWith("data:"));
        if (!line) continue;

        let event;
        try { event = JSON.parse(line.slice(5).trim()); } catch { continue; }

        if (event.type === "start") {
          S.conv = event.conv_id;
          navPush({ t: "thread", id: event.conv_id });
          $("chip-thread").hidden = false;
          $("chip-thread-title").textContent = event.title;
        } else if (event.type === "text") {
          waiting.remove();
          raw += event.text;
          // Render at most once per frame instead of once per token.
          if (!renderQueued) {
            renderQueued = true;
            requestAnimationFrame(() => {
              renderQueued = false;
              turn.prose.innerHTML = markdown(raw) + '<span class="caret"></span>';
              scrollDown(false);
            });
          }
        } else if (event.type === "tool") {
          waiting.hidden = false;
          waiting.lastChild.textContent = event.label + "…";
          turn.node.append(waiting);
          scrollDown();
        } else if (event.type === "computer_step") {
          stepsCard = stepsCard || stepCard(turn);
          stepsCard.add(event.text);
          $("driving-step").textContent = event.text;
          scrollDown();
        } else if (event.type === "card") {
          waiting.remove();
          turn.prose.innerHTML = markdown(raw);
          if (event.card.type === "file") {
            turn.node.append(fileCard(event.card));
            refreshFiles();
          } else if (event.card.type === "task") {
            turn.node.append(taskCard(event.card));
          } else if (event.card.type === "computer") {
            stepsCard = stepsCard || stepCard(turn);
            (event.card.steps || []).forEach((s) => stepsCard.add(s));
            stepsCard.finish(event.card.stopped);
          }
          scrollDown();
        } else if (event.type === "error") {
          waiting.remove();
          turn.node.append(errorCard(event.message));
        } else if (event.type === "done") {
          waiting.remove();
          turn.prose.innerHTML = markdown(raw);
          const usage = event.usage || {};
          $("composer-note").textContent =
            `${usage.seconds}s · ₹${((usage.paise || 0) / 100).toFixed(2)} (estimate)`;
        }
      }
    }
  } catch (err) {
    waiting.remove();
    if (err.name !== "AbortError") turn.node.append(errorCard(friendly(err)));
    else turn.node.append(errorCard("Stopped. Nothing was lost — the part above is saved."));
  } finally {
    setStreaming(false);
    turn.prose.innerHTML = markdown(raw);
    refreshThreads();
    scrollDown();
  }
}

function setStreaming(on) {
  S.streaming = on;
  const button = $("send");
  button.classList.toggle("stop", on);
  button.setAttribute("aria-label", on ? "Stop" : "Send");
  button.innerHTML = on
    ? '<svg viewBox="0 0 16 16" width="13" height="13" aria-hidden="true"><rect x="3.5" y="3.5" width="9" height="9" rx="1.8" fill="currentColor"/></svg>'
    : '<svg viewBox="0 0 16 16" width="15" height="15" aria-hidden="true"><path d="M8 13V3M3.6 7.2 8 2.8l4.4 4.4" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>';
  $("input").disabled = false;
  syncSend();
}

/* ══════════════════════════════════ 4. markdown ═════════════════════════ */

/** Small on purpose: headings, lists, tables, quotes, code, rules, inline runs. */
function markdown(src) {
  if (!src) return "";
  const lines = String(src).replace(/\r/g, "").split("\n");
  const out = [];
  let i = 0;

  const inline = (text) =>
    escapeHtml(text)
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/(^|[\s(])\*([^*\n]+)\*/g, "$1<em>$2</em>")
      .replace(/(^|[\s(])_([^_\n]+)_/g, "$1<em>$2</em>");

  while (i < lines.length) {
    const line = lines[i];

    if (!line.trim()) { i++; continue; }

    // fenced code
    if (/^```/.test(line)) {
      const body = [];
      i++;
      while (i < lines.length && !/^```/.test(lines[i])) body.push(lines[i++]);
      if (i < lines.length) i++;
      out.push(`<pre><code>${escapeHtml(body.join("\n"))}</code></pre>`);
      continue;
    }

    // heading
    const heading = line.match(/^(#{1,4})\s+(.*)$/);
    if (heading) {
      const level = heading[1].length;
      out.push(`<h${level}>${inline(heading[2].replace(/\s+#+\s*$/, ""))}</h${level}>`);
      i++;
      continue;
    }

    // rule
    if (/^\s*([-*_])\1{2,}\s*$/.test(line)) { out.push("<hr>"); i++; continue; }

    // table
    if (line.includes("|") && /^\s*\|?[\s:|-]+\|[\s:|-]*$/.test(lines[i + 1] || "")) {
      const cells = (row) => row.replace(/^\s*\|/, "").replace(/\|\s*$/, "").split("|");
      const head = cells(line).map((c) => `<th>${inline(c.trim())}</th>`).join("");
      i += 2;
      const body = [];
      while (i < lines.length && lines[i].includes("|") && lines[i].trim()) {
        body.push("<tr>" + cells(lines[i]).map((c) => `<td>${inline(c.trim())}</td>`).join("") + "</tr>");
        i++;
      }
      out.push(`<table><thead><tr>${head}</tr></thead><tbody>${body.join("")}</tbody></table>`);
      continue;
    }

    // quote
    if (/^>\s?/.test(line)) {
      const body = [];
      while (i < lines.length && /^>\s?/.test(lines[i])) body.push(lines[i++].replace(/^>\s?/, ""));
      out.push(`<blockquote>${inline(body.join(" "))}</blockquote>`);
      continue;
    }

    // lists
    if (/^\s*[-*+]\s+/.test(line) || /^\s*\d+[.)]\s+/.test(line)) {
      const ordered = /^\s*\d+[.)]\s+/.test(line);
      const items = [];
      while (i < lines.length &&
             (ordered ? /^\s*\d+[.)]\s+/ : /^\s*[-*+]\s+/).test(lines[i])) {
        let item = lines[i].replace(ordered ? /^\s*\d+[.)]\s+/ : /^\s*[-*+]\s+/, "");
        i++;
        // continuation lines that belong to the same bullet
        while (i < lines.length && lines[i].trim() &&
               !/^\s*([-*+]|\d+[.)])\s+/.test(lines[i]) && !/^#{1,4}\s/.test(lines[i])) {
          item += " " + lines[i++].trim();
        }
        items.push(`<li>${inline(item)}</li>`);
      }
      out.push(ordered ? `<ol>${items.join("")}</ol>` : `<ul>${items.join("")}</ul>`);
      continue;
    }

    // paragraph
    const body = [];
    while (i < lines.length && lines[i].trim() &&
           !/^(#{1,4}\s|>|```|\s*[-*+]\s|\s*\d+[.)]\s)/.test(lines[i])) {
      body.push(lines[i++]);
    }
    out.push(`<p>${inline(body.join(" "))}</p>`);
  }

  return out.join("");
}

/* ══════════════════════════════════ 5. cards ════════════════════════════ */

const GLYPH = { docx: "DOC", pdf: "PDF", xlsx: "XLS", csv: "CSV", html: "WEB", md: "MD", txt: "TXT" };

/** Float made a file. The teacher never asked where to put it — so ask here. */
function fileCard(artifact) {
  const card = make("div", "card-file");
  card.append(make("span", "glyph", GLYPH[artifact.kind] || "FILE"));

  const meta = make("div", "meta");
  meta.append(make("b", null, artifact.name));
  const line = make("small", null,
    `${artifact.label || (artifact.kind || "").toUpperCase()} · ${bytes(artifact.size || 0)}`);
  meta.append(line);
  if (artifact.saved_to) meta.append(make("em", null, " Saved"));
  card.append(meta);

  const acts = make("div", "acts");

  const caps = S.boot.capabilities;
  if (caps.local !== false) {   // on an agency-server PC only Download is offered
    const desktop = make("button", "btn gold", "Desktop");
    desktop.title = "Save into a Float folder on your Desktop";
    desktop.addEventListener("click", () => saveFile(artifact, "desktop", acts));
    acts.append(desktop);
  }
  if (!caps.lan) {
    const drive = make("button", "btn", "Drive");
    drive.title = caps.drive ? "Save to your Google Drive" : "Connect Google Drive first — Settings → Google";
    drive.addEventListener("click", () => saveFile(artifact, "drive", acts));
    acts.append(drive);
  }

  const down = make("button", "btn", "Download");
  down.addEventListener("click", () => {
    const link = document.createElement("a");
    link.href = `/api/artifacts/${artifact.id}/download`;
    link.rel = "noopener";
    // The download route needs the bearer token, so fetch and hand over a blob.
    fetch(link.href, { headers: { Authorization: "Bearer " + TOKEN } })
      .then((r) => {
        // Never save an error message as if it were the operator's document.
        if (!r.ok) throw new Error("download failed");
        return r.blob();
      })
      .then((blob) => {
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement("a");
        anchor.href = url;
        anchor.download = artifact.name;
        anchor.click();
        setTimeout(() => URL.revokeObjectURL(url), 4000);
      })
      .catch(() => toast("Could not download that file. Please try again.", true));
  });
  acts.append(down);

  card.append(acts);
  return card;
}

async function saveFile(artifact, where, acts) {
  acts.querySelectorAll("button").forEach((b) => (b.disabled = true));
  try {
    const result = await api(`/api/artifacts/${artifact.id}/save`, { body: { where } });
    toast(result.message);
    if (where === "drive" && result.link) window.open(result.link, "_blank", "noopener");
    refreshFiles();
  } catch (err) {
    toast(err.message, true);
  } finally {
    acts.querySelectorAll("button").forEach((b) => (b.disabled = false));
  }
}

function stepCard(turn) {
  const card = make("div", "card-steps");
  card.append(make("b", null, "On your computer"));
  const list = document.createElement("ol");
  card.append(list);
  turn.node.append(card);
  return {
    add: (text) => list.append(make("li", null, text)),
    finish: (stopped) => {
      if (stopped) card.append(make("b", null, "You stopped it here."));
    },
  };
}

function taskCard(card) {
  const node = make("div", "card-steps");
  node.append(make("b", null, "Added to your to-do"));
  node.append(make("div", null, card.title + (card.due ? ` — due ${card.due}` : "")));
  refreshTasks();
  return node;
}

function errorCard(message) {
  const node = make("div", "err");
  node.append(make("b", null, "That didn't go through"));
  node.append(make("span", null, message));
  return node;
}

async function refreshFiles() {
  const data = await api("/api/artifacts");
  if (!data) return;
  S.boot.artifacts = data.artifacts;
  paintCounts();
  if (currentPanel === "files") panelFiles();
}

async function refreshTasks() {
  const data = await api("/api/tasks");
  if (!data) return;
  S.boot.tasks = data.tasks;
  paintCounts();
  if (currentPanel === "tasks") panelTasks();
}

/* ══════════════════════════════════ 6. the drawer ═══════════════════════ */

let currentPanel = null;

let drawerTimer = null;
function openDrawer(title) {
  clearTimeout(drawerTimer);
  $("drawer-title").textContent = title;
  $("drawer").hidden = false;
  $("drawer-scrim").hidden = false;
  requestAnimationFrame(() => {
    $("drawer").classList.add("open");
    $("drawer-scrim").classList.add("on");
  });
}

function closeDrawer() {
  currentPanel = null;
  $("drawer").classList.remove("open");
  $("drawer-scrim").classList.remove("on");
  document.querySelectorAll(".rail-link").forEach((l) => l.setAttribute("aria-current", "false"));
  clearTimeout(drawerTimer);
  drawerTimer = setTimeout(() => { $("drawer").hidden = true; $("drawer-scrim").hidden = true; }, 260);
}

function showPanel(name) {
  currentPanel = name;
  document.querySelectorAll(".rail-link").forEach((l) =>
    l.setAttribute("aria-current", String(l.dataset.panel === name)));
  ({ toolkit: panelToolkit, classes: panelClasses, tasks: panelTasks, files: panelFiles }[name])();
}

/* ── toolkit ───────────────────────────────────────────────────────────── */

function panelToolkit(filter = "") {
  openDrawer("Toolkit");
  const body = $("drawer-body");
  body.innerHTML = "";

  const search = noAutofill(make("input", "kit-search"));
  search.type = "search";
  search.placeholder = "Search 19 tools — agreement, quote, checklist, damage…";
  search.value = filter;
  search.addEventListener("input", () => renderKit(search.value));
  body.append(search);

  const list = make("div");
  body.append(list);

  function renderKit(text) {
    list.innerHTML = "";
    const needle = text.trim().toLowerCase();
    S.boot.toolkit_groups.forEach((group) => {
      const entries = S.boot.toolkit.filter((entry) =>
        entry.group === group &&
        (!needle ||
          entry.name.toLowerCase().includes(needle) ||
          entry.blurb.toLowerCase().includes(needle)));
      if (!entries.length) return;
      list.append(make("div", "kit-group", group.toUpperCase()));
      entries.forEach((entry) => {
        const item = make("button", "kit-item");
        item.append(make("b", null, entry.name));
        item.append(make("small", null, entry.blurb));
        item.addEventListener("click", () => toolkitForm(entry));
        list.append(item);
      });
    });
    if (!list.children.length) {
      list.append(make("div", "empty", "Nothing matches that. Try 'agreement', 'quote', 'checklist' or 'damage'."));
    }
  }

  renderKit(filter);
  setTimeout(() => search.focus(), 80);
}

/** A tool's form. Built from the field list the server sent — no duplication. */
function toolkitForm(entry) {
  openDrawer(entry.name);
  const body = $("drawer-body");
  body.innerHTML = "";

  const back = make("button", "btn tiny", "‹ All tools");
  back.addEventListener("click", () => panelToolkit());
  body.append(back);

  body.append(make("p", "inline-note", entry.blurb));

  const values = {};
  const form = make("div");

  entry.fields.forEach((field) => {
    const wrap = make("div", "field");
    wrap.append(make("label", null, field.label));

    if (field.type === "select") {
      const select = document.createElement("select");
      (field.options || []).forEach((option) => {
        const node = document.createElement("option");
        node.value = option;
        node.textContent = option;
        select.append(node);
      });
      const preset = field.key === "board" ? S.user.board : field.value;
      if (preset) select.value = preset;
      values[field.key] = select.value;
      select.addEventListener("change", () => (values[field.key] = select.value));
      wrap.append(select);
    } else if (field.type === "textarea") {
      const area = noAutofill(document.createElement("textarea"));
      area.placeholder = field.placeholder || "";
      area.addEventListener("input", () => (values[field.key] = area.value));
      wrap.append(area);
    } else {
      const input = noAutofill(document.createElement("input"));
      input.type = field.type === "number" ? "number" : field.type === "date" ? "date" : "text";
      input.name = "float_tk_" + field.key;
      input.placeholder = field.placeholder || "";
      if (field.min !== undefined) input.min = field.min;
      if (field.max !== undefined) input.max = field.max;
      if (field.value !== undefined) { input.value = field.value; values[field.key] = String(field.value); }
      // Sensible defaults out of the operator's own profile.
      if (field.key === "subject" && !input.value && (S.user.subjects || [])[0]) {
        input.value = S.user.subjects[0];
        values.subject = input.value;
      }
      if (field.key === "klass" && !input.value && (S.boot.classes[0] || {}).name) {
        input.value = S.boot.classes[0].name;
        values.klass = input.value;
      }
      input.addEventListener("input", () => (values[field.key] = input.value));
      wrap.append(input);
    }

    if (field.hint) wrap.append(make("div", "hint", field.hint));
    form.append(wrap);
  });

  body.append(form);

  const go = make("button", "btn primary", `Make the ${entry.name.toLowerCase()}`);
  go.style.width = "100%";
  go.style.padding = "10px";
  go.addEventListener("click", async () => {
    go.disabled = true;
    go.textContent = "Setting it up…";
    try {
      const result = await api(`/api/toolkit/${entry.id}`, { body: { values } });
      closeDrawer();
      $("turns").innerHTML = "";
      send(result.prompt, result.conv_id);
    } catch (err) {
      toast(err.message, true);
      go.disabled = false;
      go.textContent = `Make the ${entry.name.toLowerCase()}`;
    }
  });
  body.append(go);
}

/* ── classes ───────────────────────────────────────────────────────────── */

function panelClasses() {
  openDrawer("Fleet & Bookings");
  const body = $("drawer-body");
  body.innerHTML = "";

  body.append(make("p", "inline-note",
    "Register a fleet group once and Float stops asking what is in it — plates, " +
    "inspection scores and availability come from here."));

  if (!S.boot.classes.length) {
    const empty = make("div", "empty");
    empty.append(make("b", null, "No fleet groups yet"));
    empty.append(make("span", null, "Add a fleet group below (e.g. SUV Fleet, Airport Bay 1). Paste your vehicles or bookings straight in."));
    body.append(empty);
  }

  S.boot.classes.forEach((klass) => {
    const panel = make("div", "panel");
    const head = make("div", "panel-head");
    head.append(make("b", null, klass.name));
    head.append(make("span", "spacer"));
    head.append(make("span", "pill", `${klass.students} vehicles`));
    panel.append(head);

    const inner = make("div", "panel-body");
    inner.append(make("div", "hint",
      [klass.subject, klass.grade && `Bay ${klass.grade}`, klass.section]
        .filter(Boolean).join(" · ")));

    const acts = make("div", "stack");
    const ask = make("button", "btn tiny", "Ask Float about this fleet group");
    ask.addEventListener("click", () => {
      closeDrawer();
      $("input").value = `Summarise ${klass.name} — inspection scores, availability, which vehicles need attention.`;
      send();
    });
    const drop = make("button", "btn tiny danger", "Remove group");
    drop.addEventListener("click", async () => {
      if (!confirm(`Remove ${klass.name} and its vehicle/booking list?`)) return;
      await api(`/api/classes/${klass.id}`, { method: "DELETE", body: {} });
      const data = await api("/api/classes");
      S.boot.classes = data.classes;
      paintCounts();
      panelClasses();
    });
    acts.append(ask, drop);
    inner.append(acts);
    panel.append(inner);
    body.append(panel);
  });

  // add form
  const panel = make("div", "panel");
  const head = make("div", "panel-head");
  head.append(make("b", null, "Add a fleet group / bay"));
  panel.append(head);
  const inner = make("div", "panel-body");

  const name = field(inner, "Fleet group / Bay name", "text", "SUV Fleet - Bay 2");
  const row = make("div", "field-row");
  inner.append(row);
  const grade = field(row, "Hub / Bay #", "text", "2");
  const section = field(row, "Zone / Tier", "text", "Prime");
  const subject = field(inner, "Vehicle category", "text", "Compact SUV");
  const roster = field(inner, "Vehicles or active bookings (optional)", "textarea",
    "1 MH-02-AB-1234 Hyundai Creta — Rahul Verma\n2 MH-02-CD-5678 Toyota Innova — Corp Lease\n3 MH-02-EF-9012 Tata Nexon EV — Available");

  const add = make("button", "btn primary", "Add fleet group");
  add.addEventListener("click", async () => {
    if (!name.value.trim()) { toast("Give the fleet group a name.", true); return; }
    add.disabled = true;
    try {
      await api("/api/classes", {
        body: {
          name: name.value, grade: grade.value, section: section.value,
          subject: subject.value, roster: roster.value,
        },
      });
      const data = await api("/api/classes");
      S.boot.classes = data.classes;
      paintCounts();
      panelClasses();
      toast("Fleet group added.");
    } catch (err) {
      toast(err.message, true);
      add.disabled = false;
    }
  });
  inner.append(add);
  panel.append(inner);
  body.append(panel);
}

function noAutofill(node, isCredential = false) {
  node.setAttribute("autocomplete", isCredential ? "new-password" : "off");
  node.setAttribute("autocorrect", "off");
  node.setAttribute("autocapitalize", "off");
  node.setAttribute("spellcheck", "false");
  node.setAttribute("data-lpignore", "true");
  node.setAttribute("data-1p-ignore", "true");
  node.setAttribute("data-bwignore", "true");
  node.setAttribute("data-form-type", "other");
  return node;
}

function field(parent, label, type, placeholder, value) {
  const wrap = make("div", "field");
  wrap.append(make("label", null, label));
  const node = document.createElement(type === "textarea" ? "textarea" : "input");
  if (type !== "textarea") node.type = type;
  node.placeholder = placeholder || "";
  if (value !== undefined) node.value = value;
  noAutofill(node, type === "password");
  wrap.append(node);
  parent.append(wrap);
  return node;
}

/* ── to-do ─────────────────────────────────────────────────────────────── */

function panelTasks() {
  openDrawer("Ops Checklist");
  const body = $("drawer-body");
  body.innerHTML = "";

  const panel = make("div", "panel");
  const inner = make("div", "panel-body");

  if (!S.boot.tasks.length) {
    const empty = make("div", "empty");
    empty.append(make("b", null, "Clear"));
    empty.append(make("span", null, "Float adds things here when you ask it to remember something."));
    inner.append(empty);
  }

  S.boot.tasks.forEach((task) => {
    const row = make("div", "row");
    const tick = document.createElement("input");
    tick.type = "checkbox";
    tick.checked = !!task.done;
    tick.addEventListener("change", async () => {
      await api(`/api/tasks/${task.id}`, { body: { done: tick.checked } });
      refreshTasks();
    });
    row.append(tick);

    const grow = make("div", "grow");
    grow.append(make("b", null, task.title));
    if (task.due || task.klass) {
      grow.append(make("small", null, [task.klass, task.due && `due ${task.due}`]
        .filter(Boolean).join(" · ")));
    }
    row.append(grow);

    const drop = make("button", "btn tiny", "×");
    drop.addEventListener("click", async () => {
      await api(`/api/tasks/${task.id}`, { method: "DELETE", body: {} });
      refreshTasks();
    });
    row.append(drop);
    inner.append(row);
  });

  panel.append(inner);
  body.append(panel);

  const add = make("div", "panel");
  const addBody = make("div", "panel-body");
  const title = field(addBody, "Add ops task", "text", "Refund ₹10,000 security deposit for MH-02-AB-1234");
  const due = field(addBody, "By when", "date");
  const save = make("button", "btn primary", "Add");
  save.addEventListener("click", async () => {
    if (!title.value.trim() || save.disabled) return;
    save.disabled = true;
    try {
      await api("/api/tasks", { body: { title: title.value, due: due.value } });
      await refreshTasks();
      panelTasks();
    } catch (err) { toast(friendly(err), true); save.disabled = false; }
  });
  title.addEventListener("keydown", (e) => { if (e.key === "Enter") save.click(); });
  addBody.append(save);
  add.append(addBody);
  body.append(add);
}

/* ── files ─────────────────────────────────────────────────────────────── */

function panelFiles() {
  openDrawer("Files");
  const body = $("drawer-body");
  body.innerHTML = "";

  body.append(make("p", "inline-note",
    "Everything Float has made for you. Files stay on this computer until you save them."));

  if (!S.boot.artifacts.length) {
    const empty = make("div", "empty");
    empty.append(make("b", null, "Nothing made yet"));
    empty.append(make("span", null, "Ask for a rental agreement, handover checklist, or quote and it will appear here."));
    body.append(empty);
    return;
  }

  S.boot.artifacts.forEach((artifact) => body.append(fileCard(artifact)));
}

/* ══════════════════════════════════ 7. settings ═════════════════════════ */

const TABS = [
  ["you", "You"],
  ["models", "Model & keys"],
  ["assist", "How Float helps"],
  ["mcp", "MCP Tools"],
  ["security", "Security"],
  ["google", "Google"],
  ["about", "About"],
];

function openSettings(tab = "you") {
  $("modal-scrim").hidden = false;
  $("modal-title").textContent = "Settings";

  let bar = document.querySelector(".modal .tabs");
  if (!bar) {
    bar = make("div", "tabs");
    document.querySelector(".modal-head").after(bar);
  }
  bar.innerHTML = "";
  TABS.forEach(([id, label]) => {
    const button = make("button", null, label);
    button.setAttribute("aria-selected", String(id === tab));
    button.addEventListener("click", () => openSettings(id));
    bar.append(button);
  });

  $("modal-foot").innerHTML = "";
  const close = make("button", "btn", "Close");
  close.addEventListener("click", closeModal);
  $("modal-foot").append(close);

  ({ you: tabYou, models: tabModels, assist: tabAssist, mcp: tabMcp,
     security: tabSecurity, google: tabGoogle, about: tabAbout }[tab])();
}

function closeModal() { $("modal-scrim").hidden = true; }

function tabYou() {
  const body = $("modal-body");
  body.innerHTML = "";
  body.append(make("p", "inline-note",
    "Float uses this to pitch its answers right — your service model, fleet and the language " +
    "you use with customers. Nothing here leaves your computer."));

  const name = field(body, "Name", "text", "", S.user.name);
  const school = field(body, "Rental agency / Branch", "text", "", S.user.school);

  const boardWrap = make("div", "field");
  boardWrap.append(make("label", null, "Primary service model"));
  const board = document.createElement("select");
  S.boot.options.boards.forEach((option) => {
    const node = document.createElement("option");
    node.value = option; node.textContent = option;
    board.append(node);
  });
  board.value = S.user.board || S.boot.options.boards[0];
  boardWrap.append(board);
  body.append(boardWrap);

  const langWrap = make("div", "field");
  langWrap.append(make("label", null, "Language for customer & driver messages"));
  const language = document.createElement("select");
  Object.entries(S.boot.options.languages).forEach(([code, label]) => {
    const node = document.createElement("option");
    node.value = code; node.textContent = label;
    language.append(node);
  });
  language.value = S.user.language || "en";
  langWrap.append(language);
  body.append(langWrap);

  const subjects = pickMany(body, "Vehicle categories in your fleet", S.boot.options.subjects, S.user.subjects || []);
  const grades = pickMany(body, "Fleet bays / hubs", S.boot.options.grades.map(String), S.user.grades || []);

  const appearanceWrap = make("div", "field");
  appearanceWrap.append(make("label", null, "Appearance"));
  const seg = make("div", "seg");
  [["system", "Match my computer"], ["light", "Light"], ["dark", "Dark"]].forEach(([id, label]) => {
    const button = make("button", null, label);
    button.setAttribute("aria-pressed", String((S.user.appearance || "system") === id));
    button.addEventListener("click", () => {
      S.user.appearance = id;
      theme(id);
      seg.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", "false"));
      button.setAttribute("aria-pressed", "true");
    });
    seg.append(button);
  });
  appearanceWrap.append(seg);
  body.append(appearanceWrap);

  const save = make("button", "btn primary", "Save");
  save.addEventListener("click", async () => {
    save.disabled = true;
    const data = await api("/api/me", {
      body: {
        name: name.value, school: school.value, board: board.value,
        language: language.value, appearance: S.user.appearance || "system",
        subjects: subjects(), grades: grades(),
      },
    });
    S.user = data.user;
    paintIdentity();
    toast("Saved.");
    save.disabled = false;
  });
  $("modal-foot").prepend(save);
}

function pickMany(parent, label, options, chosen) {
  const wrap = make("div", "field");
  wrap.append(make("label", null, label));
  const box = make("div", "tagbox");
  const picked = new Set(chosen);
  options.forEach((option) => {
    const tag = make("button", "tag", option);
    tag.setAttribute("aria-pressed", String(picked.has(option)));
    tag.addEventListener("click", () => {
      if (picked.has(option)) picked.delete(option); else picked.add(option);
      tag.setAttribute("aria-pressed", String(picked.has(option)));
    });
    box.append(tag);
  });
  wrap.append(box);
  parent.append(wrap);
  return () => [...picked];
}

function tabModels() {
  const body = $("modal-body");
  body.innerHTML = "";
  body.append(make("p", "inline-note",
    "Float runs on your own API key. The key is encrypted on this computer with a device " +
    "key that never leaves it, and Float only ever shows you the last four characters."));

  const chooser = make("div", "field");
  chooser.append(make("label", null, "Model for new answers"));
  const select = document.createElement("select");
  S.boot.models.forEach((model) => {
    const node = document.createElement("option");
    node.value = model.id;
    node.textContent = `${model.label} — ${model.provider_label}${model.ready ? "" : " (no key)"}`;
    node.disabled = !model.ready;
    select.append(node);
  });
  select.value = S.model;
  select.addEventListener("change", () => {
    S.model = select.value;
    localStorage.setItem("float.model", S.model);
    paintModelChip();
  });
  chooser.append(select);
  if (!S.boot.models.some((m) => m.ready)) {
    chooser.append(make("div", "hint", "Add a key below and this list comes alive."));
  }
  body.append(chooser);

  S.boot.providers.forEach((provider) => {
    const status = (S.boot.keys || {})[provider.id] || {};
    const panel = make("div", "panel");

    const head = make("div", "panel-head");
    head.append(make("b", null, provider.label));
    head.append(make("span", "spacer"));
    if (status.mine) head.append(make("span", "pill", "your key · " + status.mine.hint));
    else if (status.org) head.append(make("span", "pill admin", "agency key"));
    else head.append(make("span", "pill off", "no key"));
    panel.append(head);

    const inner = make("div", "panel-body");
    inner.append(make("div", "hint", provider.help));

    const input = noAutofill(document.createElement("input"));
    input.type = "text";
    input.name = "float_api_token_" + provider.id;
    input.placeholder = "Paste the key here";
    input.className = "mono key-input";
    input.style.width = "100%";
    input.style.padding = "8px 11px";
    input.style.marginTop = "8px";
    inner.append(input);

    const acts = make("div", "stack");
    acts.style.flexDirection = "row";
    acts.style.marginTop = "9px";

    const save = make("button", "btn primary", "Save & test");
    save.addEventListener("click", async () => {
      save.disabled = true;
      save.textContent = "Testing…";
      try {
        const result = await api("/api/keys", { body: { provider: provider.id, key: input.value } });
        S.boot.keys = result.keys;
        toast(result.detail || "Key saved.");
        const fresh = await api("/api/bootstrap");
        S.boot.models = fresh.models;
        paintModelChip();
        tabModels();
      } catch (err) {
        toast(err.message, true);
        save.disabled = false;
        save.textContent = "Save & test";
      }
    });
    acts.append(save);

    if (S.user.role === "admin") {
      const forSchool = make("button", "btn", "Save as agency key");
      forSchool.addEventListener("click", async () => {
        try {
          const result = await api("/api/keys", {
            body: { provider: provider.id, key: input.value, scope: "org" },
          });
          S.boot.keys = result.keys;
          toast("Agency key saved — every operator can use it.");
          tabModels();
        } catch (err) { toast(err.message, true); }
      });
      acts.append(forSchool);
    }

    if (status.mine) {
      const drop = make("button", "btn danger", "Remove mine");
      drop.addEventListener("click", async () => {
        const result = await api(`/api/keys/${provider.id}?scope=user`, { method: "DELETE", body: {} });
        S.boot.keys = result.keys;
        tabModels();
      });
      acts.append(drop);
    }

    const open = make("button", "btn", "Get a key ↗");
    open.addEventListener("click", () => window.open(provider.console, "_blank", "noopener"));
    acts.append(open);

    inner.append(acts);
    panel.append(inner);
    body.append(panel);
  });

  const usage = S.boot.usage || {};
  const spend = make("div", "panel");
  const spendBody = make("div", "panel-body");
  spendBody.append(make("b", null, "Your last 30 days"));
  const ledger = make("div", "ledger");
  ledger.append(make("span", null, ""));
  const one = make("span"); one.append(make("b", null, String(usage.calls || 0))); one.append(" answers");
  const two = make("span"); two.append(make("b", null, "₹" + ((usage.paise || 0) / 100).toFixed(2))); two.append(" (estimate)");
  ledger.append(one, two);
  spendBody.append(ledger);

  // Fair-share meter: every operator sees their own allowance, nobody else's.
  const capPaise = usage.cap_paise || 0, usedPaise = usage.month_paise || 0;
  const share = make("div", "hint");
  share.style.marginTop = "12px";
  if (capPaise > 0) {
    const pct = Math.min(100, Math.round((usedPaise / capPaise) * 100));
    share.append(make("b", null, "Your share this month: "));
    share.append(`₹${(usedPaise / 100).toFixed(2)} of ₹${(capPaise / 100).toFixed(2)} used (${pct}%) — estimate. Resets on the 1st.`);
    const track = make("div");
    track.style.cssText = "height:6px;border-radius:3px;background:var(--line);margin-top:6px;overflow:hidden";
    const fill = make("div");
    fill.style.cssText = `height:100%;width:${pct}%;background:${pct >= 100 ? "#B3412E" : "var(--accent)"}`;
    track.append(fill);
    share.append(track);
    if (pct >= 80) {
      share.append(make("div", null, pct >= 100
        ? "Limit reached. Fleet records, checklists and saved files still work. Ask your admin if you need more."
        : "Getting close. Ask your admin early if you have a heavy month."));
    }
    if (S.boot.capabilities && S.boot.capabilities.teacher_own_keys) {
      share.append(make("div", null, "Using your own API key below is never counted against this share."));
    }
  } else {
    share.append(make("b", null, "Your share this month: "));
    share.append("no limit set by your agency.");
  }
  spendBody.append(share);
  spendBody.append(make("div", "hint",
    "An estimate from published per-token prices. Your provider's bill is the real number."));
  spend.append(spendBody);
  body.append(spend);
}

function tabAssist() {
  const body = $("modal-body");
  body.innerHTML = "";
  body.append(make("p", "inline-note",
    "Float is meant to take the paperwork off your hands, not the fleet decisions. This setting " +
    "decides how much it does before handing back."));

  const levels = [
    ["coach", "Coach me",
      "Float asks questions, offers an outline and reacts to what you write. You do the writing."],
    ["draft", "Draft it",
      "Float writes a first version and says plainly what it guessed at, so you know where to look."],
    ["full", "Do it all",
      "Float finishes the job. Useful for routine paperwork — quotes, checklists, rosters."],
  ];

  levels.forEach(([id, title, blurb]) => {
    const panel = make("div", "panel");
    const inner = make("div", "panel-body");
    const row = make("div", "row");
    const radio = document.createElement("input");
    radio.type = "radio";
    radio.name = "assist";
    radio.checked = (S.user.assist_level || "draft") === id;
    radio.addEventListener("change", async () => {
      const data = await api("/api/me", { body: { assist_level: id } });
      S.user = data.user;
      paintAssistChip();
      toast("Float will " + title.toLowerCase() + " from now on.");
    });
    row.append(radio);
    const grow = make("div", "grow");
    grow.append(make("b", null, title));
    grow.append(make("small", null, blurb));
    row.append(grow);
    inner.append(row);
    panel.append(inner);
    body.append(panel);
  });

  const own = S.boot.own_work || {};
  const ledgerPanel = make("div", "panel");
  const ledgerBody = make("div", "panel-body");
  ledgerBody.append(make("b", null, "Your share this week"));
  const bar = make("div", "bar");
  const fill = make("i");
  fill.style.width = Math.max(3, own.own_share || 0) + "%";
  bar.append(fill);
  ledgerBody.append(bar);
  ledgerBody.append(make("div", "hint",
    `${own.own_share || 0}% of what went out this week was in your own words, across ` +
    `${own.n || 0} pieces. Float shows this because an operator who customises everything ` +
    "runs a sharper counter than one who forwards templates unchanged."));
  ledgerPanel.append(ledgerBody);
  body.append(ledgerPanel);
}

async function tabMcp() {
  const body = $("modal-body");
  body.innerHTML = '<div class="empty" style="padding:40px 0"><b>Loading MCP tools…</b></div>';

  let data;
  try {
    data = await api("/api/mcp");
  } catch (err) {
    body.innerHTML = '<div class="empty" style="padding:40px 0"><b>Could not load MCP tools</b><small>' + (err.message || "") + '</small></div>';
    return;
  }

  body.innerHTML = "";
  body.append(make("p", "inline-note",
    "Model Context Protocol (MCP) connects external tools and data sources to Float. " +
    "Local scripts or remote servers configured here are queried for tools and made available in chat."));

  const isAdmin = !!(S.user && S.user.role === "admin");
  const topRow = make("div", "row");
  topRow.style.marginBottom = "14px";
  const title = make("b", null, "Configured Servers (" + (data.servers ? data.servers.length : 0) + ")");
  topRow.append(title);
  topRow.append(make("span", "spacer"));

  if (isAdmin) {
    const refreshBtn = make("button", "btn", "Refresh");
    refreshBtn.addEventListener("click", async () => {
      refreshBtn.disabled = true;
      refreshBtn.textContent = "Refreshing…";
      try {
        await api("/api/mcp/refresh", { method: "POST" });
        toast("MCP tools refreshed.");
        tabMcp();
      } catch (err) {
        toast(err.message, true);
        refreshBtn.disabled = false;
        refreshBtn.textContent = "Refresh";
      }
    });
    topRow.append(refreshBtn);

    const addBtn = make("button", "btn primary", "Add Server");
    addBtn.style.marginLeft = "7px";
    addBtn.addEventListener("click", () => renderAddMcpForm(body));
    topRow.append(addBtn);
  }
  body.append(topRow);

  if (!data.servers || !data.servers.length) {
    const empty = make("div", "empty");
    empty.style.padding = "30px 10px";
    empty.append(make("b", null, "No MCP servers configured"));
    empty.append(make("small", null, isAdmin
      ? "Click 'Add Server' to connect an external tool via command or HTTP URL."
      : "Your workspace administrator has not configured any MCP servers yet."));
    body.append(empty);
    return;
  }

  data.servers.forEach((srv) => {
    const panel = make("div", "panel");
    panel.style.marginBottom = "12px";

    const head = make("div", "panel-head");
    head.append(make("b", null, srv.name));

    let statusCls = "pill";
    if (srv.disabled) statusCls = "pill off";
    else if (srv.status === "error") statusCls = "pill off";
    else if (srv.status !== "connected") statusCls = "pill warn";

    const statusPill = make("span", statusCls, srv.disabled ? "disabled" : (srv.status || "disconnected"));
    head.append(statusPill);

    const toolCount = make("span", "chip", (srv.tool_count || 0) + " tool" + (srv.tool_count === 1 ? "" : "s"));
    toolCount.style.marginLeft = "8px";
    head.append(toolCount);

    head.append(make("span", "spacer"));

    if (isAdmin) {
      const toggleBtn = make("button", "btn tiny", srv.disabled ? "Enable" : "Disable");
      toggleBtn.style.marginRight = "6px";
      toggleBtn.addEventListener("click", async () => {
        toggleBtn.disabled = true;
        try {
          await api("/api/mcp/servers/" + encodeURIComponent(srv.name) + "/toggle", {
            body: { enabled: !!srv.disabled },
          });
          toast((srv.disabled ? "Enabled " : "Disabled ") + srv.name + ".");
          tabMcp();
        } catch (err) {
          toast(err.message, true);
          toggleBtn.disabled = false;
        }
      });
      head.append(toggleBtn);

      const delBtn = make("button", "icon-btn", "");
      delBtn.title = "Remove server";
      delBtn.setAttribute("aria-label", "Remove server");
      delBtn.innerHTML = '<svg viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 4.5h10M6 4.5V3a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v1.5M4.5 4.5v8.5a1.5 1.5 0 0 0 1.5 1.5h4a1.5 1.5 0 0 0 1.5-1.5V4.5"/></svg>';
      delBtn.addEventListener("click", async () => {
        if (!confirm("Remove MCP server '" + srv.name + "'?")) return;
        try {
          await api("/api/mcp/servers/" + encodeURIComponent(srv.name), { method: "DELETE" });
          toast("Removed " + srv.name + ".");
          tabMcp();
        } catch (err) { toast(err.message, true); }
      });
      head.append(delBtn);
    }
    panel.append(head);

    const b = make("div", "panel-body");
    const cmdLine = srv.command ? (srv.command + " " + (srv.args || []).join(" ")) : (srv.url || "");
    const code = make("code", null, cmdLine);
    code.style.fontSize = "12px";
    code.style.opacity = "0.8";
    b.append(code);

    if (srv.error) {
      const errBox = make("div", "hint");
      errBox.style.color = "var(--rose)";
      errBox.style.marginTop = "6px";
      errBox.textContent = "Error: " + srv.error;
      b.append(errBox);
    }

    if (srv.tools && srv.tools.length) {
      const toolBox = make("div", null);
      toolBox.style.marginTop = "10px";
      srv.tools.forEach((t) => {
        const item = make("div", "row");
        item.style.padding = "5px 0";
        item.style.borderTop = "1px solid var(--border)";
        const gr = make("div", "grow");
        gr.append(make("b", null, t.name));
        if (t.description) {
          const d = make("small", null, t.description);
          d.style.display = "block";
          gr.append(d);
        }
        item.append(gr);
        toolBox.append(item);
      });
      b.append(toolBox);
    }
    panel.append(b);
    body.append(panel);
  });
}

function renderAddMcpForm(body) {
  body.innerHTML = "";
  body.append(make("p", "inline-note", "Add a new Model Context Protocol (MCP) server."));

  const nameInput = field(body, "Server Name", "text", "e.g. calculator or fleet_db");
  const typeWrap = make("div", "field");
  typeWrap.append(make("label", null, "Transport Type"));
  const typeSelect = document.createElement("select");
  typeSelect.innerHTML = '<option value="stdio">Local Command (stdio)</option><option value="http">Remote URL (HTTP)</option>';
  typeWrap.append(typeSelect);
  body.append(typeWrap);

  const cmdWrap = make("div", null);
  const cmdInput = field(cmdWrap, "Command", "text", "e.g. python, uvx, node");
  const argsInput = field(cmdWrap, "Arguments", "text", "e.g. -m calc_server or /path/to/server.py");
  body.append(cmdWrap);

  const urlWrap = make("div", null);
  urlWrap.hidden = true;
  const urlInput = field(urlWrap, "Server URL", "text", "e.g. http://localhost:8000/mcp");
  body.append(urlWrap);

  typeSelect.addEventListener("change", () => {
    const isStdio = typeSelect.value === "stdio";
    cmdWrap.hidden = !isStdio;
    urlWrap.hidden = isStdio;
  });

  const btnRow = make("div", "row");
  btnRow.style.marginTop = "16px";
  const cancelBtn = make("button", "btn", "Cancel");
  cancelBtn.addEventListener("click", tabMcp);
  btnRow.append(cancelBtn);

  const saveBtn = make("button", "btn primary", "Save & Connect");
  saveBtn.style.marginLeft = "8px";
  saveBtn.addEventListener("click", async () => {
    const name = nameInput.value.trim();
    if (!name) { toast("Server name is required", true); return; }
    const isStdio = typeSelect.value === "stdio";
    const payload = { name: name };
    if (isStdio) {
      if (!cmdInput.value.trim()) { toast("Command is required", true); return; }
      payload.command = cmdInput.value.trim();
      payload.args = argsInput.value.trim();
    } else {
      if (!urlInput.value.trim()) { toast("URL is required", true); return; }
      payload.url = urlInput.value.trim();
    }
    saveBtn.disabled = true;
    saveBtn.textContent = "Connecting…";
    try {
      await api("/api/mcp/servers", { body: payload });
      toast("Added MCP server '" + name + "'.");
      tabMcp();
    } catch (err) {
      toast(err.message, true);
      saveBtn.disabled = false;
      saveBtn.textContent = "Save & Connect";
    }
  });
  btnRow.append(saveBtn);
  body.append(btnRow);
}

function tabSecurity() {
  const body = $("modal-body");
  body.innerHTML = "";
  body.append(make("p", "inline-note",
    "Float signs you out the moment this window closes, and again when the app itself " +
    "restarts. Nobody who picks up your laptop later gets back in."));

  const passPanel = make("div", "panel");
  const passHead = make("div", "panel-head");
  passHead.append(make("b", null, "Password"));
  passPanel.append(passHead);
  const passBody = make("div", "panel-body");
  const current = field(passBody, "Current password", "password");
  const next = field(passBody, "New password", "password");
  passBody.append(make("div", "hint", "At least 10 characters. A short sentence beats a scramble."));
  const changePass = make("button", "btn primary", "Change password");
  changePass.addEventListener("click", async () => {
    try {
      await api("/api/me/password", { body: { current: current.value, next: next.value } });
      current.value = next.value = "";
      toast("Password changed.");
    } catch (err) { toast(err.message, true); }
  });
  passBody.append(changePass);
  passPanel.append(passBody);
  body.append(passPanel);

  const pinPanel = make("div", "panel");
  const pinHead = make("div", "panel-head");
  pinHead.append(make("b", null, "Quick PIN"));
  pinHead.append(make("span", "spacer"));
  pinHead.append(make("span", S.user.has_pin ? "pill" : "pill off",
    S.user.has_pin ? "set" : "not set"));
  pinPanel.append(pinHead);
  const pinBody = make("div", "panel-body");
  pinBody.append(make("div", "hint",
    "Between customers you don't want to type a password. Set a 4–8 digit PIN and Float " +
    "asks only for that on this computer. Your password still works everywhere."));
  const pinPass = field(pinBody, "Your password", "password");
  const pin = field(pinBody, "New PIN", "password", "4–8 digits");
  const setPin = make("button", "btn primary", "Set PIN");
  setPin.addEventListener("click", async () => {
    try {
      await api("/api/me/pin", { body: { password: pinPass.value, pin: pin.value } });
      S.user.has_pin = !!pin.value;
      pinPass.value = pin.value = "";
      toast(S.user.has_pin ? "PIN set." : "PIN removed.");
      tabSecurity();
    } catch (err) { toast(err.message, true); }
  });
  pinBody.append(setPin);
  if (S.user.has_pin) {
    const clear = make("button", "btn danger", "Remove PIN");
    clear.style.marginLeft = "7px";
    clear.addEventListener("click", async () => {
      try {
        await api("/api/me/pin", { body: { password: pinPass.value, pin: "" } });
        S.user.has_pin = false;
        toast("PIN removed.");
        tabSecurity();
      } catch (err) { toast(err.message, true); }
    });
    pinBody.append(clear);
  }
  pinPanel.append(pinBody);
  body.append(pinPanel);
}

function tabGoogle() {
  const body = $("modal-body");
  body.innerHTML = "";
  const caps = S.boot.capabilities;

  if (caps.lan) {
    body.append(make("p", "inline-note",
      "Google Drive is switched off on this agency server, so one operator's files never touch " +
      "another's account. Use Download to save a file to the computer you are sitting at."));
    return;
  }
  if (!caps.google) {
    body.append(make("p", "inline-note",
      "Google isn't set up on this installation. Float works perfectly without it — " +
      "files save to your Desktop instead. To switch it on, put a Google client ID and " +
      "secret in the .env file beside the app and restart."));
    return;
  }

  body.append(make("p", "inline-note",
    "Connecting Drive lets the Save to Drive button work. Float only ever sees the files " +
    "it puts there itself — it cannot read the rest of your Drive."));

  const panel = make("div", "panel");
  const inner = make("div", "panel-body");
  const row = make("div", "row");
  const grow = make("div", "grow");
  grow.append(make("b", null, "Google Drive"));
  grow.append(make("small", null, caps.drive
    ? "Connected for this session."
    : "Not connected. Files still save to your Desktop."));
  row.append(grow);

  const connect = make("button", "btn primary", caps.drive ? "Reconnect" : "Connect Drive");
  connect.addEventListener("click", async () => {
    try {
      const { url } = await api("/api/auth/google/start?drive=1");
      window.open(url, "float-drive", "width=520,height=640");
    } catch (err) { toast(err.message, true); }
  });
  row.append(connect);
  inner.append(row);
  inner.append(make("div", "hint",
    "The Drive connection lives in memory only. Closing Float disconnects it."));
  panel.append(inner);
  body.append(panel);
}

/** About, and — for one person — the way into the local runtime. */
let aboutTaps = 0;
function tabAbout() {
  const body = $("modal-body");
  body.innerHTML = "";

  body.append(make("p", "inline-note",
    "Float is an AI operations companion for car rental teams. It runs entirely on this computer: " +
    "your fleet groups, your drafts and your files never go anywhere except to the model " +
    "provider whose key you supplied."));

  const panel = make("div", "panel");
  const inner = make("div", "panel-body");

  const rows = [
    ["Version", "1.0.0"],
    ["Data", "data/float.sqlite3, beside the app"],
    ["Files", "data/files — until you save them elsewhere"],
    ["Sessions", "end when the app closes"],
  ];
  if (S.boot.capabilities && S.boot.capabilities.desk_ip) {
    rows.push(["Assigned Desk", S.boot.capabilities.desk_ip]);
  }
  rows.forEach(([label, value]) => {
    const row = make("div", "row");
    const grow = make("div", "grow");
    grow.append(make("b", null, label));
    row.append(grow);
    row.append(make("small", null, value));
    inner.append(row);
  });
  panel.append(inner);
  body.append(panel);

  if (S.user && S.user.role === "admin") {
    const srvPanel = make("div", "panel");
    srvPanel.style.marginTop = "14px";
    const srvBody = make("div", "panel-body");
    const srvRow = make("div", "row");
    const srvGrow = make("div", "grow");
    srvGrow.append(make("b", null, "Float Server"));
    srvGrow.append(make("small", null, "Stop the background server process on this computer."));
    srvRow.append(srvGrow);
    const stopBtn = make("button", "btn danger", "Shut down");
    stopBtn.addEventListener("click", async () => {
      if (!confirm("Shut down the Float server? You will be disconnected until it is started again.")) return;
      stopBtn.disabled = true;
      stopBtn.textContent = "Shutting down…";
      try {
        await api("/api/system/shutdown", { method: "POST" });
        closeModal();
        document.body.innerHTML = '<div class="empty" style="padding-top:25vh"><b>Float has been shut down</b>You can safely close this window. To start Float again, double-click Start Float.</div>';
      } catch (err) {
        toast(err.message, true);
        stopBtn.disabled = false;
        stopBtn.textContent = "Shut down";
      }
    });
    srvRow.append(stopBtn);
    srvBody.append(srvRow);
    srvPanel.append(srvBody);
    body.append(srvPanel);
  }

  const mark = make("p", "hint", "Float · Your fleet, faster.");
  mark.style.textAlign = "center";
  mark.style.cursor = "default";
  mark.addEventListener("click", () => {
    if (!S.user || S.user.role !== "admin") return;
    aboutTaps += 1;
    if (aboutTaps < 7) return;
    aboutTaps = 0;
    if (body.querySelector("#rt-phrase")) return;

    const gate = make("div", "field");
    gate.append(make("label", null, "Passphrase"));
    const input = noAutofill(document.createElement("input"));
    input.type = "text";
    input.className = "mono key-input";
    input.id = "rt-phrase";
    gate.append(input);
    const go = make("button", "btn", "Enter");
    go.addEventListener("click", async () => {
      try {
        const result = await api("/api/unlock", { body: { phrase: input.value, enable: true } });
        toast(result.enabled ? "Local models available. Reopen the model list." : "Off.");
        const fresh = await api("/api/bootstrap");
        S.boot.models = fresh.models;
        paintModelChip();
        closeModal();
      } catch {
        toast("Not recognised.", true);
      }
    });
    gate.append(go);
    body.append(gate);
    input.focus();
  });
  body.append(mark);
}

/* ══════════════════════════════════ 8. computer control ═════════════════ */

async function pollComputer() {
  if (!S.boot || !S.boot.capabilities || !S.boot.capabilities.computer) return;
  if (!document.hidden || S.driving) {
    try {
      const status = await api("/api/computer/status");
      if (!status) return;
      const running = !!status.running;
      if (running !== S.driving) {
        S.driving = running;
        $("driving").hidden = !running;
        if (running) $("driving-what").textContent = status.intent || "Float is using your computer";
        else $("driving-step").textContent = "";
      }
    } catch { /* the poll is a nicety; never let it break the app */ }
  }
  setTimeout(pollComputer, (S.driving || S.streaming) ? 900 : 15000);
}

async function stopComputer() {
  try {
    await api("/api/computer/stop", { body: {} });
    toast("Stopped. Float let go of the mouse.");
  } catch (err) { toast(err.message, true); }
}

/* ══════════════════════════════════ wiring ══════════════════════════════ */

function theme(choice) {
  const dark = window.matchMedia("(prefers-color-scheme: dark)");
  const apply = () => {
    document.documentElement.dataset.theme =
      choice === "system" ? (dark.matches ? "dark" : "light") : choice;
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = getComputedStyle(document.documentElement).getPropertyValue("--paper").trim() || "#000000";
  };
  dark.onchange = choice === "system" ? apply : null;
  apply();
}

function grow() {
  const input = $("input");
  input.style.height = "auto";
  if (input.value) input.style.height = Math.min(input.scrollHeight, window.innerHeight * 0.36) + "px";
  syncSend();
}

function syncSend() {
  const box = document.querySelector(".composer");
  box.classList.toggle("can-send", S.streaming || !!$("input").value.trim() || S.attachments.length > 0);
}

function clearAttachments() {
  S.attachments = [];
  $("attach-bar").innerHTML = "";
  $("attach-bar").hidden = true;
  syncSend();
}

async function attach(files) {
  for (const file of files) {
    if (file.size > 30 * 1024 * 1024) { toast(`${file.name} is too big (30 MB limit). Attach fewer pages or a smaller file.`, true); continue; }
    const already = S.attachments.reduce((n, a) => n + a.data.length * 0.75, 0);
    if (already + file.size > 30 * 1024 * 1024) { toast("Too much attached at once (30 MB total). Send the rest in a second message.", true); continue; }
    const data = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result).split(",")[1]);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
    const kind = file.type.startsWith("image/") ? "image" : "text";
    const entry = { name: file.name, mime: file.type || "text/plain", kind, data };
    S.attachments.push(entry);
    syncSend();

    const chip = make("div", "attach-chip");
    chip.append(make("span", null, file.name));
    const drop = make("button", null, "×");
    drop.type = "button";
    drop.setAttribute("aria-label", "Remove " + file.name);
    drop.addEventListener("click", () => {
      const idx = S.attachments.indexOf(entry);
      if (idx !== -1) S.attachments.splice(idx, 1);
      chip.remove();
      if (!S.attachments.length) $("attach-bar").hidden = true;
      syncSend();
    });
    chip.append(drop);
    $("attach-bar").hidden = false;
    $("attach-bar").append(chip);
  }
}

$("input").addEventListener("input", grow);
$("input").addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); send(); }
});

$("send").addEventListener("click", () => {
  if (S.streaming) { S.abort && S.abort.abort(); return; }
  send();
});

$("new-thread").addEventListener("click", newThread);
$("drawer-close").addEventListener("click", closeDrawer);
$("drawer-scrim").addEventListener("click", closeDrawer);
$("modal-close").addEventListener("click", closeModal);
$("modal-scrim").addEventListener("click", (event) => {
  if (event.target === $("modal-scrim")) closeModal();
});

document.querySelectorAll(".rail-link").forEach((link) =>
  link.addEventListener("click", () => showPanel(link.dataset.panel)));

$("open-settings").addEventListener("click", () => openSettings("you"));
$("chip-model").addEventListener("click", () => openSettings("models"));
$("chip-assist").addEventListener("click", () => openSettings("assist"));
$("open-admin").addEventListener("click", () => window.open("/admin", "_blank", "noopener"));

async function toggleTheme() {
  const now = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  S.user.appearance = now;
  theme(now);
  await api("/api/me", { body: { appearance: now } });
}

/* ── small pop-up menus: top-left menu and the + button ── */
function closePop() { const old = document.getElementById("pop"); if (old) old.remove(); }
function popMenu(anchor, items, up = false) {
  const again = document.getElementById("pop") && document.getElementById("pop").dataset.for === anchor.id;
  closePop();
  if (again) return;
  const box = make("div", "pop");
  box.id = "pop";
  box.dataset.for = anchor.id;
  items.forEach((item) => {
    if (item === "-") { box.append(document.createElement("hr")); return; }
    const row = make("button", null, item.label);
    row.type = "button";
    if (item.kbd) row.append(make("kbd", null, item.kbd));
    row.addEventListener("click", () => { closePop(); item.run(); });
    box.append(row);
  });
  document.body.append(box);
  const r = anchor.getBoundingClientRect();
  if (up) box.style.bottom = (window.innerHeight - r.top + 8) + "px";
  else box.style.top = (r.bottom + 6) + "px";
  box.style.left = Math.max(8, Math.min(r.left, window.innerWidth - (box.offsetWidth || 220) - 8)) + "px";
}

// ---- Lenses: change HOW Float thinks with you, not just what it knows. ----
// Each lens rides along as a short hidden instruction (a few tokens), so it costs almost nothing.
const LENSES = {
  plain:    { name: "Plain",    hint: "Straight answers, as usual.", rule: "" },
  socratic: { name: "Socratic", hint: "Guides you with questions before giving the answer.",
              rule: "Guide me Socratically: ask 2-3 short guiding questions first, give a hint, and only reveal the full answer if I ask." },
  skeptic:  { name: "Skeptic",  hint: "Answers, then attacks its own answer and rates confidence.",
              rule: "Answer, then add a 'Where I could be wrong' section (max 3 bullets) and a confidence rating (low/medium/high) with what to verify." },
  brief:    { name: "Brief",    hint: "Three bullets, then stops.",
              rule: "Reply in at most 3 short bullets. No preamble, no closing offer." },
};
let lens = "plain";
try { lens = localStorage.getItem("float.lens") || "plain"; } catch { /* ignore */ }
if (!LENSES[lens]) lens = "plain";
function paintLens() {
  $("lens-label").textContent = lens === "plain" ? "Style" : LENSES[lens].name;
  $("chip-lens").classList.toggle("lens-on", lens !== "plain");
}
function setLens(id) {
  lens = id;
  try { localStorage.setItem("float.lens", id); } catch { /* ignore */ }
  paintLens();
}
paintLens();
$("chip-lens").addEventListener("click", () => {
  popMenu($("chip-lens"), Object.entries(LENSES).map(([id, l]) => ({
    label: l.name, run: () => setLens(id),
  })), true);
  // add the one-line hint + a tick under the open menu
  const box = document.getElementById("pop");
  if (!box) return;
  [...box.querySelectorAll("button")].forEach((row, i) => {
    const id = Object.keys(LENSES)[i];
    row.append(make("small", null, LENSES[id].hint));
    if (id === lens) row.classList.add("on-lens");
  });
});

$("open-menu").addEventListener("click", () => {
  const dark = document.documentElement.dataset.theme === "dark";
  const items = [
    { label: "New task or quote", kbd: "Ctrl /", run: newThread },
    "-",
    { label: "Toolkit", kbd: "Ctrl K", run: () => showPanel("toolkit") },
    { label: "Enterprise Ops Hub", run: () => openOpsHub() },
    { label: "Fleet & Bookings", run: () => showPanel("classes") },
    { label: "Ops to-do", run: () => showPanel("tasks") },
    { label: "Files", run: () => showPanel("files") },
    "-",
    { label: "Settings", run: () => openSettings("you") },
    { label: dark ? "Switch to light mode" : "Switch to dark mode", run: toggleTheme },
  ];
  if (S.user && S.user.role === "admin") items.push({ label: "Admin panel", run: () => window.open("/admin", "_blank", "noopener") });
  items.push("-", { label: "Sign out", run: () => $("sign-out").click() });
  popMenu($("open-menu"), items);
});

$("attach").addEventListener("click", () => popMenu($("attach"), [
  { label: "Add a photo or file", run: () => $("file-input").click() },
  { label: "Open the toolkit", kbd: "Ctrl K", run: () => showPanel("toolkit") },
], true));

$("nav-back").addEventListener("click", () => navGo(-1));
$("nav-forward").addEventListener("click", () => navGo(1));

// Quick starters on the home screen: open the toolkit item or fill a prompt.
document.querySelectorAll(".starter").forEach((button) =>
  button.addEventListener("click", () => {
    if (button.dataset.kit && S.boot && S.boot.toolkit) {
      const wanted = button.dataset.kit.replace(/_/g, "-");
      const entry = S.boot.toolkit.find((t) => t.id === wanted || t.id === button.dataset.kit);
      if (entry) {
        currentPanel = "toolkit";
        document.querySelectorAll(".rail-link").forEach((l) =>
          l.setAttribute("aria-current", String(l.dataset.panel === "toolkit")));
        toolkitForm(entry);
        return;
      }
    }
    if (button.dataset.prompt) {
      const input = $("input");
      input.value = button.dataset.prompt;
      grow();
      input.focus();
      input.setSelectionRange(input.value.length, input.value.length);
    }
  }));

// Dictation: the browser's own speech recognition, so nothing leaves Float's code.
(function dictation() {
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const button = $("mic");
  if (!Recognition) return;                  // button stays hidden where it can't work
  button.hidden = false;
  let rec = null;
  button.addEventListener("click", () => {
    if (rec) { rec.stop(); return; }
    const code = (S.user && S.user.language) || "en";
    const base = $("input").value ? $("input").value.replace(/\s*$/, " ") : "";
    rec = new Recognition();
    rec.lang = code === "en" ? "en-IN" : code + "-IN";
    rec.interimResults = true;
    rec.continuous = true;
    rec.onresult = (event) => {
      let heard = "";
      for (let i = 0; i < event.results.length; i++) heard += event.results[i][0].transcript;
      $("input").value = base + heard;
      grow();
    };
    rec.onerror = (event) => {
      if (event.error === "not-allowed" || event.error === "service-not-allowed")
        toast("Allow the microphone to dictate.", true);
    };
    rec.onend = () => { rec = null; button.classList.remove("live"); };
    button.classList.add("live");
    rec.start();
  });
})();
$("file-input").addEventListener("change", (event) => {
  attach(event.target.files);
  event.target.value = "";
});

// Phone layout: the menu opens over the chat, so it must also close itself.
const closeRail = () => $("rail").classList.remove("open");
const shell = document.querySelector(".shell");
function setRail(mini) {
  shell.classList.toggle("rail-mini", mini);
  const btn = $("rail-toggle");
  btn.setAttribute("aria-expanded", String(!mini));
  btn.title = mini ? "Expand sidebar (Ctrl+B)" : "Collapse sidebar (Ctrl+B)";
  try { localStorage.setItem("float.rail", mini ? "mini" : "full"); } catch { /* private window */ }
}
function toggleRail() {
  if (window.innerWidth > 760) setRail(!shell.classList.contains("rail-mini"));
  else $("rail").classList.toggle("open");
}
let railPref = "full";
try { railPref = localStorage.getItem("float.rail") || "full"; } catch { /* ignore */ }
setRail(railPref === "mini");
$("rail-toggle").addEventListener("click", (event) => {
  event.stopPropagation();
  toggleRail();
});
$("rail").addEventListener("click", (event) => {
  if (event.target.closest("button")) closeRail();      // picked something
});
document.addEventListener("click", (event) => {
  if (!event.target.closest("#rail")) closeRail();      // tapped outside
  if (!event.target.closest("#pop, [data-pop]")) closePop();
});
window.addEventListener("resize", () => { if (window.innerWidth > 760) closeRail(); closePop(); });
$("driving-stop").addEventListener("click", stopComputer);

$("sign-out").addEventListener("click", async () => {
  try { await api("/api/auth/signout", { body: {} }); } catch { /* going anyway */ }
  sessionStorage.removeItem("float.token");
  location.replace("/login");
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    if (document.getElementById("pop")) { closePop(); return; }
    if ($("rail").classList.contains("open")) { closeRail(); return; }
    if (S.driving) { stopComputer(); return; }
    if ($("ops-modal-scrim") && !$("ops-modal-scrim").hidden) { closeOpsHub(); return; }
    if (!$("modal-scrim").hidden) { closeModal(); return; }
    if (!$("drawer").hidden) closeDrawer();
  }
  if ((event.metaKey || event.ctrlKey) && event.key === "k") {
    event.preventDefault();
    showPanel("toolkit");
  }
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "b") {
    event.preventDefault();
    toggleRail();
  }
  if (event.altKey && event.key.toLowerCase() === "l") {
    event.preventDefault();
    $("chip-lens").click();
  }
  if ((event.metaKey || event.ctrlKey) && event.key === "/") {
    event.preventDefault();
    newThread();
  }
});

// Drag a vehicle photo, RC/DL scan, or booking sheet straight onto the window.
document.addEventListener("dragover", (event) => event.preventDefault());
document.addEventListener("drop", (event) => {
  event.preventDefault();
  if (event.dataTransfer.files.length) attach(event.dataTransfer.files);
});


/* ══════════════════════════════════ pixel mascot controller ═════════════ */

function initMascot() {
  const mascot = $("float-mascot");
  if (!mascot) return;
  const bubble = $("mascot-bubble");

  const phrases = [
    "Beep bloop! Ready to roll! 🚘",
    "Vroom vroom! Jamming to fleet tunes 🎧",
    "Need a quote? Let's crunch it! ⚡",
    "Listening for counter requests! 🎵",
    "Fleet operations: 100% smooth! ✨",
    "Bloop! Your trusty fleet companion! 💚",
    "Checklists, keys, contracts... got 'em all! 📋",
    "All vehicles accounted for! 🔑",
    "Groovin' right by the Float logo! 🎶",
    "Click me for a dance! 💃",
    "Zero hallucinations, pure math! 🛡️"
  ];

  const excitedPhrases = [
    "Wheeeee! Let's go! 🚗💨",
    "Groovy fleet magic! 🎧✨",
    "Full throttle speed! ⚡",
    "You're awesome, operator! 🌟",
    "Top gear dispatch! 🔥"
  ];

  let phraseIdx = 0;
  let hideTimer = null;
  let blinkTimer = null;

  function speak(text, duration = 3000) {
    if (!bubble) return;
    bubble.textContent = text;
    mascot.classList.add("is-speaking", "is-active");
    clearTimeout(hideTimer);
    if (duration > 0) {
      hideTimer = setTimeout(() => {
        mascot.classList.remove("is-speaking");
        if (!mascot.matches(":hover")) mascot.classList.remove("is-active");
      }, duration);
    }
  }
  window.floatMascotSpeak = speak;

  // Hover response: cursor above mascot
  mascot.addEventListener("mouseenter", () => {
    phraseIdx = (phraseIdx + 1) % phrases.length;
    speak(phrases[phraseIdx], 3200);
  });

  mascot.addEventListener("mouseleave", () => {
    clearTimeout(hideTimer);
    hideTimer = setTimeout(() => {
      mascot.classList.remove("is-speaking", "is-active");
    }, 800);
  });

  // Click celebration spin
  mascot.addEventListener("click", (e) => {
    e.stopPropagation();
    if (!(reducedMotion && reducedMotion.matches)) mascot.classList.add("is-spinning");
    const pick = excitedPhrases[Math.floor(Math.random() * excitedPhrases.length)];
    speak(pick, 3500);
    setTimeout(() => {
      mascot.classList.remove("is-spinning");
    }, 680);
  });

  mascot.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      mascot.click();
    } else if (e.key === "Escape") {
      mascot.classList.remove("is-speaking", "is-active");
    }
  });

  mascot.addEventListener("focus", () => {
    mascot.classList.add("is-active");
  });
  mascot.addEventListener("blur", () => {
    if (!mascot.matches(":hover")) mascot.classList.remove("is-active");
  });

  // Natural living blink cycle
  function scheduleBlink() {
    clearTimeout(blinkTimer);
    const delay = 3200 + Math.random() * 3000;
    blinkTimer = setTimeout(() => {
      mascot.classList.add("is-blinking");
      setTimeout(() => {
        mascot.classList.remove("is-blinking");
        scheduleBlink();
      }, 160);
    }, delay);
  }
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) clearTimeout(blinkTimer);
    else scheduleBlink();
  });
  scheduleBlink();

  // Subtle pupil tracking when cursor moves inside the top rail
  const railTop = document.querySelector(".rail-top");
  const eyesNormal = $("mascot-eyes-normal");
  const reducedMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)");
  if (railTop && eyesNormal) {
    railTop.addEventListener("mousemove", (e) => {
      if (reducedMotion && reducedMotion.matches) return;
      const rect = mascot.getBoundingClientRect();
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height / 2;
      const dx = Math.max(-1, Math.min(1, (e.clientX - cx) / 48));
      const dy = Math.max(-1, Math.min(1, (e.clientY - cy) / 48));
      eyesNormal.style.transform = `translate(${dx.toFixed(2)}px, ${dy.toFixed(2)}px)`;
    });
    railTop.addEventListener("mouseleave", () => {
      eyesNormal.style.transform = "translate(0px, 0px)";
    });
  }

  // Also perk up mascot when hovering over the wordmark logo/title
  const wm = document.querySelector(".wordmark");
  if (wm) {
    wm.addEventListener("mouseenter", (e) => {
      if (e.target === mascot || mascot.contains(e.target)) return;
      mascot.classList.add("is-active");
    });
    wm.addEventListener("mouseleave", () => {
      if (!mascot.matches(":hover")) mascot.classList.remove("is-active");
    });
  }

  // Contextual reaction when starting a new quote or task thread
  const newBtn = $("new-thread");
  if (newBtn) {
    newBtn.addEventListener("click", () => {
      speak("Fresh counter sheet ready! 🧾", 2400);
    });
  }

  // Contextual reaction when opening fleet tools or schedule drawers
  document.querySelectorAll("[data-panel], [data-open]").forEach((btn) => {
    btn.addEventListener("click", () => {
      mascot.classList.add("is-cheering");
      setTimeout(() => mascot.classList.remove("is-cheering"), 850);
    });
  });
}


/* ═══════════════════════════ 9. Enterprise Rental Operations Hub ═════════ */
let OPS_DATA = null;
let OPS_TAB = "fleet";

const OPS_TABS = [
  ["fleet", "Fleet & Compliance"],
  ["bookings", "Bookings & Timeline"],
  ["customers", "Customers & DPDP"],
  ["money", "Money, GST & Shift"],
  ["workshop", "Workshop, Damage & Sign"],
  ["dashboard", "Dashboard & Import"],
];

function closeOpsHub() {
  const s = $("ops-modal-scrim");
  if (s) s.hidden = true;
}

async function refreshOpsSummary() {
  try {
    OPS_DATA = await api("/api/ops/summary");
    const badge = $("ops-alert-badge");
    if (badge && OPS_DATA && OPS_DATA.alerts) {
      const n = Number(OPS_DATA.alerts.total_alerts || 0);
      badge.textContent = `${n} alert${n === 1 ? "" : "s"}`;
      badge.hidden = n === 0;
    }
    const rolePill = $("ops-role-pill");
    if (rolePill && S.user) {
      rolePill.textContent = S.user.ops_role || (S.user.role === "admin" ? "owner" : "desk_agent");
    }
  } catch { /* ignore background summary errors */ }
}

async function openOpsHub(tab) {
  if (tab) OPS_TAB = tab;
  const scrim = $("ops-modal-scrim");
  if (!scrim) return;
  scrim.hidden = false;
  $("ops-modal-body").innerHTML = '<div class="empty"><b>Loading enterprise operations…</b></div>';
  await refreshOpsSummary();
  renderOpsHub();
}

function renderOpsHub() {
  const bar = $("ops-tabs");
  const body = $("ops-modal-body");
  if (!bar || !body) return;
  bar.innerHTML = "";
  OPS_TABS.forEach(([id, label]) => {
    const b = make("button", null, label);
    b.type = "button";
    b.setAttribute("role", "tab");
    b.setAttribute("aria-selected", String(id === OPS_TAB));
    b.addEventListener("click", () => { OPS_TAB = id; renderOpsHub(); });
    bar.append(b);
  });
  body.innerHTML = "";
  if (!OPS_DATA) {
    body.append(make("div", "empty", "Unable to load operational records."));
    return;
  }
  const views = {
    fleet: renderOpsFleet,
    bookings: renderOpsBookings,
    customers: renderOpsCustomers,
    money: renderOpsMoney,
    workshop: renderOpsWorkshop,
    dashboard: renderOpsDashboard,
  };
  (views[OPS_TAB] || renderOpsFleet)(body);
}

function opsField(parent, label, placeholder = "", type = "text", defaultVal = "") {
  const f = make("div", "field");
  f.append(make("label", null, label));
  const inp = noAutofill(document.createElement("input"));
  inp.type = type;
  inp.placeholder = placeholder;
  if (defaultVal !== "") inp.value = defaultVal;
  f.append(inp);
  parent.append(f);
  return inp;
}

function opsSelect(parent, label, options) {
  const f = make("div", "field");
  f.append(make("label", null, label));
  const sel = document.createElement("select");
  options.forEach(([val, text]) => {
    const o = document.createElement("option");
    o.value = val;
    o.textContent = text;
    sel.append(o);
  });
  f.append(sel);
  parent.append(f);
  return sel;
}

function renderOpsFleet(body) {
  const alerts = OPS_DATA.alerts || {};
  if (alerts.total_alerts > 0) {
    const ap = make("div", "panel");
    const ah = make("div", "panel-head");
    ah.append(make("b", null, `Compliance & Expiry Alerts (${alerts.total_alerts})`));
    ap.append(ah);
    const ab = make("div", "panel-body");
    (alerts.vehicle_compliance_alerts || []).forEach((a) => {
      const r = make("div", "row");
      r.append(make("span", "pill warn", a.severity));
      r.append(make("span", "grow", `${a.reg_number} · ${a.doc_type.toUpperCase()} (${a.doc_number || "no ref"}) — exp: ${a.expiry_date || "N/A"}`));
      ab.append(r);
    });
    (alerts.customer_dl_alerts || []).forEach((a) => {
      const r = make("div", "row");
      r.append(make("span", "pill off", a.severity));
      r.append(make("span", "grow", `Customer DL: ${a.full_name} (${a.dl_number}) — exp: ${a.dl_expiry}`));
      ab.append(r);
    });
    (alerts.maintenance_alerts || []).forEach((a) => {
      const r = make("div", "row");
      r.append(make("span", "pill warn", a.overdue ? "overdue" : "due soon"));
      r.append(make("span", "grow", `Service: ${a.reg_number} at ${a.odometer_km} km (due ${a.service_due_km} km / ${a.next_service_due_date || "N/A"})`));
      ab.append(r);
    });
    ap.append(ab);
    body.append(ap);
  }

  const grid = make("div", "ops-grid-2");

  // Add Vehicle Card
  const vp = make("div", "panel");
  const vh = make("div", "panel-head"); vh.append(make("b", null, "Add Vehicle to Master Fleet")); vp.append(vh);
  const vb = make("div", "panel-body");
  const r1 = make("div", "ops-grid-3");
  const reg = opsField(r1, "Registration No.", "MH-01-AB-1234");
  const makeIn = opsField(r1, "Make", "Toyota");
  const modelIn = opsField(r1, "Model", "Innova Hycross");
  vb.append(r1);
  const r2 = make("div", "ops-grid-3");
  const catIn = opsSelect(r2, "Category", [["SUV", "SUV"], ["Compact SUV", "Compact SUV"], ["Sedan", "Sedan"], ["Hatchback", "Hatchback"], ["MPV", "MPV"], ["Luxury", "Luxury"]]);
  const fuelIn = opsSelect(r2, "Fuel", [["Petrol", "Petrol"], ["Diesel", "Diesel"], ["Hybrid", "Hybrid"], ["EV", "EV"], ["CNG", "CNG"]]);
  const rateIn = opsField(r2, "Daily Rate (₹)", "3500", "number", "3500");
  vb.append(r2);
  const r3 = make("div", "ops-grid-3");
  const odoIn = opsField(r3, "Odometer (km)", "12000", "number", "0");
  const branchOpts = (OPS_DATA.branches || []).map((b) => [String(b.id), `${b.name} (${b.code})`]);
  const branchIn = opsSelect(r3, "Branch", branchOpts.length ? branchOpts : [["1", "HQ"]]);
  const statIn = opsSelect(r3, "Status", [["available", "Available"], ["reserved", "Reserved"], ["in_workshop", "In Workshop"], ["blocked", "Blocked"]]);
  vb.append(r3);
  const addVBtn = make("button", "btn primary", "Save Vehicle");
  addVBtn.addEventListener("click", async () => {
    try {
      await api("/api/ops/vehicles", {
        body: {
          reg_number: reg.value, make: makeIn.value, model: modelIn.value,
          category: catIn.value, fuel_type: fuelIn.value, daily_rate: Number(rateIn.value),
          odometer_km: Number(odoIn.value), branch_id: Number(branchIn.value), status: statIn.value,
        },
      });
      toast("Vehicle added to fleet master.");
      await refreshOpsSummary();
      renderOpsHub();
    } catch (err) { toast(err.message, true); }
  });
  vb.append(addVBtn);
  vp.append(vb);
  grid.append(vp);

  // Add Compliance & Branch Transfer Card
  const cp = make("div", "panel");
  const ch = make("div", "panel-head"); ch.append(make("b", null, "Vehicle Compliance & Branch Transfer")); cp.append(ch);
  const cb = make("div", "panel-body");
  const vehOpts = (OPS_DATA.vehicles || []).map((v) => [String(v.id), `${v.reg_number} · ${v.make} ${v.model}`]);
  const cVeh = opsSelect(cb, "Vehicle", vehOpts.length ? vehOpts : [["", "Add a vehicle first"]]);
  const cr1 = make("div", "ops-grid-3");
  const cType = opsSelect(cr1, "Document Type", [["insurance", "Insurance"], ["puc", "PUC"], ["fitness", "Fitness Cert"], ["permit", "Permit"], ["fastag", "FASTag"]]);
  const cNum = opsField(cr1, "Policy / Tag No.", "POL-998811");
  const cExp = opsField(cr1, "Expiry Date", "2027-05-01", "date");
  cb.append(cr1);
  const saveCompBtn = make("button", "btn", "Save Compliance Doc");
  saveCompBtn.addEventListener("click", async () => {
    if (!cVeh.value) { toast("Select a vehicle first.", true); return; }
    try {
      await api(`/api/ops/vehicles/${cVeh.value}/compliance`, {
        body: { doc_type: cType.value, doc_number: cNum.value, expiry_date: cExp.value, wallet_balance: 1000 },
      });
      toast("Compliance record saved.");
      await refreshOpsSummary();
      renderOpsHub();
    } catch (err) { toast(err.message, true); }
  });
  cb.append(saveCompBtn);

  const hr = document.createElement("hr");
  hr.style.cssText = "border:0;border-top:1px solid var(--line);margin:12px 0";
  cb.append(hr);
  const trRow = make("div", "ops-grid-3");
  const toBr = opsSelect(trRow, "Transfer To Branch", branchOpts.length ? branchOpts : [["1", "HQ"]]);
  const trReason = opsField(trRow, "Transfer Reason", "Weekend airport demand");
  const newBrName = opsField(trRow, "Or New Branch Name", "Pune Airport Desk");
  cb.append(trRow);
  const trBtnRow = make("div", "row");
  const trBtn = make("button", "btn", "Transfer Vehicle");
  trBtn.addEventListener("click", async () => {
    if (!cVeh.value) return;
    try {
      await api(`/api/ops/vehicles/${cVeh.value}/transfer`, {
        body: { to_branch_id: Number(toBr.value), reason: trReason.value },
      });
      toast("Vehicle transferred.");
      await refreshOpsSummary();
      renderOpsHub();
    } catch (err) { toast(err.message, true); }
  });
  const addBrBtn = make("button", "btn", "Create Branch");
  addBrBtn.addEventListener("click", async () => {
    if (!newBrName.value.trim()) { toast("Enter a branch name.", true); return; }
    try {
      const code = newBrName.value.trim().toUpperCase().replace(/[^A-Z0-9]/g, "").slice(0, 6) || "BR2";
      await api("/api/ops/branches", { body: { code, name: newBrName.value.trim() } });
      toast("Branch created.");
      await refreshOpsSummary();
      renderOpsHub();
    } catch (err) { toast(err.message, true); }
  });
  trBtnRow.append(trBtn, addBrBtn);
  cb.append(trBtnRow);
  cp.append(cb);
  grid.append(cp);
  body.append(grid);

  // Fleet Master Table
  const listP = make("div", "panel");
  const listH = make("div", "panel-head"); listH.append(make("b", null, `Fleet Master (${(OPS_DATA.vehicles || []).length} vehicles)`)); listP.append(listH);
  const listB = make("div", "panel-body");
  listB.style.overflowX = "auto";
  const tbl = document.createElement("table");
  tbl.className = "grid";
  tbl.innerHTML = "<thead><tr><th>Reg No.</th><th>Vehicle</th><th>Category</th><th>Branch</th><th>Odometer</th><th>Daily Rate</th><th>Status</th></tr></thead>";
  const tb = document.createElement("tbody");
  (OPS_DATA.vehicles || []).forEach((v) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td class="mono"><b>${escapeHtml(v.reg_number)}</b></td>` +
      `<td>${escapeHtml(v.make)} ${escapeHtml(v.model)} <small>(${escapeHtml(v.fuel_type)})</small></td>` +
      `<td>${escapeHtml(v.category)}</td>` +
      `<td>${escapeHtml(v.branch_name || "HQ")}</td>` +
      `<td class="num">${Number(v.odometer_km || 0).toLocaleString("en-IN")} km</td>` +
      `<td class="num">₹${Number(v.daily_rate || 0).toLocaleString("en-IN")}</td>` +
      `<td><span class="pill ${v.status === "available" ? "admin" : "warn"}">${escapeHtml(v.status)}</span></td>`;
    tb.append(tr);
  });
  tbl.append(tb);
  listB.append(tbl);
  listP.append(listB);
  body.append(listP);
}

function renderOpsBookings(body) {
  const grid = make("div", "ops-grid-2");

  // Create Booking with Overlap Protection
  const bp = make("div", "panel");
  const bh = make("div", "panel-head"); bh.append(make("b", null, "New Reservation (Overlap & DL Expiry Checked)")); bp.append(bh);
  const bb = make("div", "panel-body");
  const vehOpts = (OPS_DATA.vehicles || []).map((v) => [String(v.id), `${v.reg_number} · ${v.make} ${v.model} (₹${v.daily_rate}/day)`]);
  const custOpts = (OPS_DATA.customers || []).map((c) => [String(c.id), `${c.full_name} (${c.phone || "no phone"} · DL: ${c.dl_number || "N/A"})`]);
  const bVeh = opsSelect(bb, "Vehicle", vehOpts.length ? vehOpts : [["", "Add a vehicle in Fleet tab first"]]);
  const bCust = opsSelect(bb, "Customer", custOpts.length ? custOpts : [["", "Add a customer in Customers tab first"]]);
  const today = new Date().toISOString().slice(0, 10);
  const tom = new Date(Date.now() + 3 * 86400000).toISOString().slice(0, 10);
  const r1 = make("div", "ops-grid-2");
  const pAt = opsField(r1, "Pickup (YYYY-MM-DDTHH:MM)", `${today}T09:00`, "text", `${today}T09:00`);
  const rAt = opsField(r1, "Return (YYYY-MM-DDTHH:MM)", `${tom}T18:00`, "text", `${tom}T18:00`);
  bb.append(r1);
  const r2 = make("div", "ops-grid-3");
  const discIn = opsField(r2, "Discount (₹)", "0", "number", "0");
  const reasonIn = opsField(r2, "Override Reason (if discounted)", "Corporate repeat client");
  const appIn = opsField(r2, "Approved By", "Branch Manager");
  bb.append(r2);
  const createBtn = make("button", "btn primary", "Confirm Booking");
  createBtn.addEventListener("click", async () => {
    if (!bVeh.value || !bCust.value) { toast("Select both vehicle and customer.", true); return; }
    try {
      await api("/api/ops/bookings", {
        body: {
          vehicle_id: Number(bVeh.value),
          customer_id: Number(bCust.value),
          pickup_at: pAt.value,
          return_at: rAt.value,
          discount_amount: Number(discIn.value || 0),
          rate_override_reason: Number(discIn.value || 0) > 0 ? reasonIn.value : "",
          rate_approved_by: Number(discIn.value || 0) > 0 ? appIn.value : "",
        },
      });
      toast("Booking confirmed.");
      await refreshOpsSummary();
      renderOpsHub();
    } catch (err) { toast(err.message, true); }
  });
  bb.append(createBtn);
  bp.append(bb);
  grid.append(bp);

  // Availability Search & Vehicle Timeline
  const tp = make("div", "panel");
  const th = make("div", "panel-head"); th.append(make("b", null, "Availability Search & Vehicle Timeline")); tp.append(th);
  const tb = make("div", "panel-body");
  const sr = make("div", "ops-grid-2");
  const sPick = opsField(sr, "From", `${today}T09:00`, "text", `${today}T09:00`);
  const sRet = opsField(sr, "To", `${tom}T18:00`, "text", `${tom}T18:00`);
  tb.append(sr);
  const sOut = make("div", "hint", "Click Search to filter conflict-free vehicles.");
  const sBtn = make("button", "btn", "Search Available Vehicles");
  sBtn.addEventListener("click", async () => {
    try {
      const res = await api(`/api/ops/availability?pickup_at=${encodeURIComponent(sPick.value)}&return_at=${encodeURIComponent(sRet.value)}`);
      const avail = res.available || [];
      sOut.textContent = avail.length
        ? `Available (${avail.length}): ` + avail.map((v) => `${v.reg_number} (${v.make} ${v.model})`).join(", ")
        : "No vehicles available for that window.";
    } catch (err) { toast(err.message, true); }
  });
  tb.append(sBtn, sOut);

  (OPS_DATA.vehicles || []).forEach((v) => {
    const slots = (OPS_DATA.bookings || []).filter((b) => b.vehicle_id === v.id && ["confirmed", "picked_up"].includes(b.status));
    const row = make("div", "row");
    const g = make("div", "grow");
    g.append(make("b", null, `${v.reg_number} · ${v.make} ${v.model}`));
    if (!slots.length) {
      g.append(make("small", null, "No active bookings — free on timeline"));
    } else {
      slots.forEach((s) => {
        g.append(make("span", "timeline-slot", `${s.booking_ref}: ${s.pickup_at.slice(0, 10)} → ${s.return_at.slice(0, 10)} (${s.status})`));
      });
    }
    row.append(g);
    tb.append(row);
  });
  tp.append(tb);
  grid.append(tp);
  body.append(grid);

  // Active & Past Bookings Lifecycle Table
  const lp = make("div", "panel");
  const lh = make("div", "panel-head"); lh.append(make("b", null, "Reservation Lifecycle & Handover / Return / Cancellation")); lp.append(lh);
  const lb = make("div", "panel-body");
  lb.style.overflowX = "auto";
  const tbl = document.createElement("table");
  tbl.className = "grid";
  tbl.innerHTML = "<thead><tr><th>Ref</th><th>Vehicle</th><th>Customer</th><th>Pickup → Return</th><th>Status</th><th>Actions</th></tr></thead>";
  const tbody = document.createElement("tbody");
  (OPS_DATA.bookings || []).forEach((b) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td class="mono"><b>${escapeHtml(b.booking_ref)}</b></td>` +
      `<td>${escapeHtml(b.reg_number)}</td>` +
      `<td>${escapeHtml(b.customer_name)}</td>` +
      `<td><small>${escapeHtml(b.pickup_at)} → ${escapeHtml(b.return_at)}</small></td>` +
      `<td><span class="pill">${escapeHtml(b.status)}</span></td>`;
    const actTd = document.createElement("td");
    const step = (status, label, extra = {}) => {
      const btn = make("button", "btn tiny", label);
      btn.style.marginRight = "4px";
      btn.addEventListener("click", async () => {
        try {
          await api(`/api/ops/bookings/${b.id}/status`, { body: { status, ...extra } });
          toast(`Booking ${b.booking_ref} → ${status}`);
          await refreshOpsSummary();
          renderOpsHub();
        } catch (err) { toast(err.message, true); }
      });
      actTd.append(btn);
    };
    if (b.status === "enquiry") step("confirmed", "Confirm");
    if (b.status === "confirmed") {
      step("picked_up", "Mark Picked Up");
      step("cancelled", "Cancel");
      step("no_show", "No-Show");
    }
    if (b.status === "picked_up") {
      const retBtn = make("button", "btn tiny primary", "Return Vehicle");
      retBtn.addEventListener("click", async () => {
        const odo = prompt(`Closing odometer (km) for ${b.reg_number} (out: ${b.odometer_out} km):`, String(Number(b.odometer_out || 0) + 250));
        if (odo === null) return;
        try {
          await api(`/api/ops/bookings/${b.id}/status`, { body: { status: "returned", odometer_in: Number(odo) } });
          toast(`Booking ${b.booking_ref} returned.`);
          await refreshOpsSummary();
          renderOpsHub();
        } catch (err) { toast(err.message, true); }
      });
      actTd.append(retBtn);
    }
    if (b.status === "returned") step("closed", "Close File");
    tr.append(actTd);
    tbody.append(tr);
  });
  tbl.append(tbody);
  lb.append(tbl);
  lp.append(lb);
  body.append(lp);
}

function renderOpsCustomers(body) {
  const cp = make("div", "panel");
  const ch = make("div", "panel-head");
  ch.append(make("b", null, "Customer Onboarding, KYC & India DPDP Act 2023 Consent"));
  cp.append(ch);
  const cb = make("div", "panel-body");
  const r1 = make("div", "ops-grid-3");
  const nameIn = opsField(r1, "Full Name", "Aarav Deshmukh");
  const phoneIn = opsField(r1, "Mobile Phone", "9876543210");
  const emailIn = opsField(r1, "Email", "aarav@example.in");
  cb.append(r1);
  const r2 = make("div", "ops-grid-3");
  const dlIn = opsField(r2, "Driving Licence No.", "MH0220190012345");
  const dlExp = opsField(r2, "DL Expiry Date", "2030-06-15", "date", "2030-06-15");
  const idProof = opsField(r2, "ID Proof (Aadhaar last 4 / Passport)", "Aadhaar XXXX-4821");
  cb.append(r2);
  const consentRow = make("div", "row");
  const consentBox = document.createElement("input");
  consentBox.type = "checkbox";
  consentBox.checked = true;
  consentRow.append(consentBox);
  const cg = make("div", "grow");
  cg.append(make("b", null, "Explicit Consent under Section 6, Digital Personal Data Protection Act, 2023 (India)"));
  cg.append(make("small", null, "Customer consents to collection of Driving Licence & ID proof for rental verification, insurance, FASTag/challan settlement, and statutory GST invoicing."));
  consentRow.append(cg);
  cb.append(consentRow);

  const saveCustBtn = make("button", "btn primary", "Save Customer Profile");
  saveCustBtn.addEventListener("click", async () => {
    try {
      await api("/api/ops/customers", {
        body: {
          full_name: nameIn.value, phone: phoneIn.value, email: emailIn.value,
          dl_number: dlIn.value, dl_expiry: dlExp.value,
          id_proof_type: "Government ID", id_proof_number: idProof.value,
          dpdp_consent: consentBox.checked,
        },
      });
      toast("Customer profile saved with DPDP consent timestamp.");
      await refreshOpsSummary();
      renderOpsHub();
    } catch (err) { toast(err.message, true); }
  });
  cb.append(saveCustBtn);
  cp.append(cb);
  body.append(cp);

  // Customer Directory with DPDP Export & Erasure
  const lp = make("div", "panel");
  const lh = make("div", "panel-head"); lh.append(make("b", null, "Customer Directory & DPDP Act Rights (Portability Export / Erasure)")); lp.append(lh);
  const lb = make("div", "panel-body");
  lb.style.overflowX = "auto";
  const tbl = document.createElement("table");
  tbl.className = "grid";
  tbl.innerHTML = "<thead><tr><th>Customer</th><th>Phone</th><th>Driving Licence</th><th>DL Expiry</th><th>Trips</th><th>DPDP Act Actions</th></tr></thead>";
  const tb = document.createElement("tbody");
  (OPS_DATA.customers || []).forEach((c) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td><b>${escapeHtml(c.full_name)}</b></td>` +
      `<td class="mono">${escapeHtml(c.phone || "—")}</td>` +
      `<td class="mono">${escapeHtml(c.dl_number || "—")}</td>` +
      `<td>${escapeHtml(c.dl_expiry || "—")}</td>` +
      `<td class="num">${Number(c.total_bookings || 0)}</td>`;
    const actTd = document.createElement("td");
    const expBtn = make("button", "btn tiny", "Export Data (Sec 11)");
    expBtn.style.marginRight = "4px";
    expBtn.addEventListener("click", async () => {
      try {
        const pkg = await api(`/api/ops/customers/${c.id}/export`);
        const blob = new Blob([JSON.stringify(pkg, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `dpdp-customer-${c.id}.json`;
        a.click();
        setTimeout(() => URL.revokeObjectURL(url), 3000);
        toast("DPDP data summary exported & access logged.");
      } catch (err) { toast(err.message, true); }
    });
    const eraseBtn = make("button", "btn tiny danger", "Erase PII (Sec 12)");
    eraseBtn.addEventListener("click", async () => {
      const reason = prompt(`Erase personal data for ${c.full_name} under DPDP Act 2023 Section 12?\nEnter customer request reference / reason:`, "Customer withdrawal request");
      if (!reason) return;
      try {
        await api(`/api/ops/customers/${c.id}/erase`, { body: { reason } });
        toast("Customer PII anonymized; statutory GST invoices preserved.");
        await refreshOpsSummary();
        renderOpsHub();
      } catch (err) { toast(err.message, true); }
    });
    actTd.append(expBtn, eraseBtn);
    tr.append(actTd);
    tb.append(tr);
  });
  tbl.append(tb);
  lb.append(tbl);
  lp.append(lb);
  body.append(lp);
}

function renderOpsMoney(body) {
  const grid = make("div", "ops-grid-2");
  const bookOpts = (OPS_DATA.bookings || []).map((b) => [String(b.id), `${b.booking_ref} · ${b.reg_number} (${b.customer_name})`]);

  // Payment Ledger & Immutable GST Invoice
  const pp = make("div", "panel");
  const ph = make("div", "panel-head"); ph.append(make("b", null, "Payment Ledger & Sequential GST Invoice")); pp.append(ph);
  const pb = make("div", "panel-body");
  const pBook = opsSelect(pb, "Booking", bookOpts.length ? bookOpts : [["", "Create a booking first"]]);
  const r1 = make("div", "ops-grid-3");
  const pKind = opsSelect(r1, "Payment Type", [["advance", "Advance"], ["deposit", "Security Deposit"], ["partial", "Partial"], ["settlement", "Final Settlement"], ["deposit_refund", "Deposit Refund"], ["refund", "Refund"]]);
  const pMode = opsSelect(r1, "Mode", [["UPI", "UPI"], ["Cash", "Cash"], ["Card", "Card"], ["NEFT", "NEFT"], ["RTGS", "RTGS"]]);
  const pAmt = opsField(r1, "Amount (₹)", "5000", "number", "5000");
  pb.append(r1);
  const pRef = opsField(pb, "UTR / Reference Number", "UPI-431298765432");
  const btnRow = make("div", "row");
  const recBtn = make("button", "btn primary", "Record Payment");
  recBtn.addEventListener("click", async () => {
    if (!pBook.value) return;
    try {
      await api("/api/ops/payments", {
        body: { booking_id: Number(pBook.value), kind: pKind.value, mode: pMode.value, amount: Number(pAmt.value), reference_no: pRef.value },
      });
      toast("Payment recorded in ledger.");
      await refreshOpsSummary();
      renderOpsHub();
    } catch (err) { toast(err.message, true); }
  });
  const invBtn = make("button", "btn", "Issue Immutable GST Invoice");
  invBtn.addEventListener("click", async () => {
    if (!pBook.value) return;
    try {
      const res = await api("/api/ops/invoices", { body: { booking_id: Number(pBook.value) } });
      toast(`Issued GST Invoice ${res.invoice.invoice_number}`);
      await refreshOpsSummary();
      renderOpsHub();
    } catch (err) { toast(err.message, true); }
  });
  btnRow.append(recBtn, invBtn);
  pb.append(btnRow);
  pp.append(pb);
  grid.append(pp);

  // Daily Collection & Shift Cash Drawer Reconciliation
  const col = OPS_DATA.collections || {};
  const sp = make("div", "panel");
  const sh = make("div", "panel-head"); sh.append(make("b", null, `Daily Collections & Shift Reconciliation (${col.date || "Today"})`)); sp.append(sh);
  const sb = make("div", "panel-body");
  sb.append(make("p", "hint",
    `Net Cash: ₹${Number(col.net_cash || 0).toLocaleString("en-IN")} · UPI: ₹${Number(col.upi_collected || 0).toLocaleString("en-IN")} · Card: ₹${Number(col.card_collected || 0).toLocaleString("en-IN")} · Net Total: ₹${Number(col.net_collections || 0).toLocaleString("en-IN")}`));
  const sr = make("div", "ops-grid-2");
  const openCash = opsField(sr, "Opening Drawer Cash (₹)", "2000", "number", "2000");
  const closeCash = opsField(sr, "Counted Closing Cash (₹)", String(2000 + Number(col.net_cash || 0)), "number", String(2000 + Number(col.net_cash || 0)));
  sb.append(sr);
  const recShiftBtn = make("button", "btn primary", "Close & Reconcile Shift");
  recShiftBtn.addEventListener("click", async () => {
    try {
      const r = await api("/api/ops/reconcile", {
        body: { opening_cash: Number(openCash.value), actual_closing_cash: Number(closeCash.value), notes: "Counter shift handover" },
      });
      toast(`Shift closed. Variance: ₹${r.reconciliation.cash_variance}`);
    } catch (err) { toast(err.message, true); }
  });
  sb.append(recShiftBtn);
  sp.append(sb);
  grid.append(sp);
  body.append(grid);

  // Issued GST Invoices & Credit Notes
  const ip = make("div", "panel");
  const ih = make("div", "panel-head"); ih.append(make("b", null, "Sequential GST Invoices (Immutable) & Credit Notes")); ip.append(ih);
  const ib = make("div", "panel-body");
  ib.style.overflowX = "auto";
  const tbl = document.createElement("table");
  tbl.className = "grid";
  tbl.innerHTML = "<thead><tr><th>Invoice No.</th><th>Customer</th><th>Vehicle</th><th class=num>Taxable</th><th class=num>CGST+SGST/IGST</th><th class=num>Grand Total</th><th>Credit Note</th></tr></thead>";
  const tb = document.createElement("tbody");
  (OPS_DATA.invoices || []).forEach((inv) => {
    const tr = document.createElement("tr");
    const gst = Number(inv.cgst_amount || 0) + Number(inv.sgst_amount || 0) + Number(inv.igst_amount || 0);
    tr.innerHTML = `<td class="mono"><b>${escapeHtml(inv.invoice_number)}</b></td>` +
      `<td>${escapeHtml(inv.customer_name)}</td>` +
      `<td class="mono">${escapeHtml(inv.vehicle_reg)}</td>` +
      `<td class="num">₹${Number(inv.taxable_amount).toFixed(2)}</td>` +
      `<td class="num">₹${gst.toFixed(2)}</td>` +
      `<td class="num"><b>₹${Number(inv.grand_total).toFixed(2)}</b></td>`;
    const cnTd = document.createElement("td");
    const cnBtn = make("button", "btn tiny", "Issue Credit Note");
    cnBtn.addEventListener("click", async () => {
      const amt = prompt(`Issue GST Credit Note against ${inv.invoice_number} (max taxable ₹${inv.taxable_amount}):`, "500");
      if (!amt) return;
      const reason = prompt("Reason for Credit Note (required for GST audit):", "Post-return billing adjustment");
      if (!reason) return;
      try {
        const res = await api("/api/ops/credit-notes", {
          body: { invoice_id: inv.id, taxable_reversal: Number(amt), reason },
        });
        toast(`Issued Credit Note ${res.credit_note.credit_note_number}`);
        await refreshOpsSummary();
        renderOpsHub();
      } catch (err) { toast(err.message, true); }
    });
    cnTd.append(cnBtn);
    tr.append(cnTd);
    tb.append(tr);
  });
  tbl.append(tb);
  ib.append(tbl);
  ip.append(ib);
  body.append(ip);
}

function renderOpsWorkshop(body) {
  const grid = make("div", "ops-grid-2");
  const vehOpts = (OPS_DATA.vehicles || []).map((v) => [String(v.id), `${v.reg_number} · ${v.make} ${v.model}`]);
  const bookOpts = (OPS_DATA.bookings || []).map((b) => [String(b.id), `${b.booking_ref} (${b.reg_number})`]);

  // Maintenance Job Card & Damage Record
  const mp = make("div", "panel");
  const mh = make("div", "panel-head"); mh.append(make("b", null, "Workshop Job Cards & Annotated Damage Log")); mp.append(mh);
  const mb = make("div", "panel-body");
  const mVeh = opsSelect(mb, "Vehicle", vehOpts.length ? vehOpts : [["", "Add vehicle first"]]);
  const r1 = make("div", "ops-grid-3");
  const mType = opsField(r1, "Service / Panel", "10,000 km Periodic Service");
  const mCost = opsField(r1, "Cost / Est. Damage (₹)", "4500", "number", "4500");
  const mSev = opsSelect(r1, "Damage Severity (if damage)", [["scratch", "Scratch"], ["dent", "Dent"], ["crack", "Crack"], ["major", "Major"]]);
  mb.append(r1);
  const btnRow = make("div", "row");
  const jcBtn = make("button", "btn primary", "Open Workshop Job Card");
  jcBtn.addEventListener("click", async () => {
    if (!mVeh.value) return;
    try {
      await api("/api/ops/maintenance", {
        body: { vehicle_id: Number(mVeh.value), service_type: mType.value, parts_cost: Number(mCost.value), status: "in_progress" },
      });
      toast("Workshop job card created; vehicle marked In Workshop.");
      await refreshOpsSummary();
      renderOpsHub();
    } catch (err) { toast(err.message, true); }
  });
  const dmgBtn = make("button", "btn danger", "Log Vehicle Damage");
  dmgBtn.addEventListener("click", async () => {
    if (!mVeh.value) return;
    try {
      await api("/api/ops/damage", {
        body: {
          vehicle_id: Number(mVeh.value), panel_location: mType.value || "Front Bumper",
          severity: mSev.value, estimated_cost: Number(mCost.value),
          description: `Logged via Ops Hub (${mSev.value})`,
          annotation_json: [{ x: 120, y: 80, label: mType.value || "Damage" }],
        },
      });
      toast("Damage record saved to vehicle history.");
      await refreshOpsSummary();
      renderOpsHub();
    } catch (err) { toast(err.message, true); }
  });
  btnRow.append(jcBtn, dmgBtn);
  mb.append(btnRow);
  mp.append(mb);
  grid.append(mp);

  // Digital Signature Capture Pad
  const sp = make("div", "panel");
  const sh = make("div", "panel-head"); sh.append(make("b", null, "Digital Signature Capture (SHA-256 Timestamped)")); sp.append(sh);
  const sb = make("div", "panel-body");
  const sBook = opsSelect(sb, "Booking", bookOpts.length ? bookOpts : [["", "Create booking first"]]);
  const sName = opsField(sb, "Signer Full Name", "Aarav Deshmukh");
  const canvas = document.createElement("canvas");
  canvas.width = 360;
  canvas.height = 110;
  canvas.className = "sig-canvas";
  const ctx = canvas.getContext("2d");
  ctx.strokeStyle = "#14532d";
  ctx.lineWidth = 2;
  let drawing = false;
  let hasStroke = false;
  canvas.addEventListener("pointerdown", (e) => {
    drawing = true;
    hasStroke = true;
    ctx.beginPath();
    ctx.moveTo(e.offsetX, e.offsetY);
  });
  canvas.addEventListener("pointermove", (e) => {
    if (!drawing) return;
    ctx.lineTo(e.offsetX, e.offsetY);
    ctx.stroke();
  });
  window.addEventListener("pointerup", () => { drawing = false; });
  sb.append(canvas);
  const sRow = make("div", "row");
  const signBtn = make("button", "btn primary", "Capture & Seal Signature");
  signBtn.addEventListener("click", async () => {
    if (!sBook.value || !sName.value.trim()) { toast("Select a booking and signer name.", true); return; }
    try {
      const sigData = hasStroke ? canvas.toDataURL("image/png") : "data:image/png;base64,SIGNED";
      const res = await api("/api/ops/signatures", {
        body: { booking_id: Number(sBook.value), signer_name: sName.value, doc_kind: "agreement", signer_role: "customer", signature_data: sigData },
      });
      toast(`Signature sealed · SHA-256: ${res.signature.doc_hash.slice(0, 12)}…`);
    } catch (err) { toast(err.message, true); }
  });
  const clrBtn = make("button", "btn", "Clear Pad");
  clrBtn.addEventListener("click", () => { ctx.clearRect(0, 0, canvas.width, canvas.height); hasStroke = false; });
  sRow.append(signBtn, clrBtn);
  sb.append(sRow);
  sp.append(sb);
  grid.append(sp);
  body.append(grid);
}

function renderOpsDashboard(body) {
  const dash = OPS_DATA.dashboard || {};
  const sg = make("div", "stat-grid");
  [
    ["Fleet Utilization (30d)", `${dash.fleet_utilization_pct || 0}%`, `${dash.fleet_count || 0} vehicles`],
    ["Gross Revenue", `₹${Number(dash.total_gross_revenue || 0).toLocaleString("en-IN")}`, "taxable rental revenue"],
    ["Workshop & Chauffeur Cost", `₹${Number((dash.total_maintenance_cost || 0) + (dash.total_driver_cost || 0)).toLocaleString("en-IN")}`, "direct costs"],
    ["Net Fleet Profit", `₹${Number(dash.total_net_profit || 0).toLocaleString("en-IN")}`, "30-day net"],
  ].forEach(([label, val, sub]) => {
    const c = make("div", "stat");
    c.append(make("b", null, val), make("small", null, `${label} · ${sub}`));
    sg.append(c);
  });
  body.append(sg);

  // Profitability per vehicle table
  const dp = make("div", "panel");
  const dh = make("div", "panel-head"); dh.append(make("b", null, "Per-Vehicle Utilization, Idle Days & Profitability")); dp.append(dh);
  const db = make("div", "panel-body");
  db.style.overflowX = "auto";
  const tbl = document.createElement("table");
  tbl.className = "grid";
  tbl.innerHTML = "<thead><tr><th>Reg No.</th><th>Vehicle</th><th class=num>Rented Days</th><th class=num>Idle Days</th><th class=num>Utilization</th><th class=num>Revenue</th><th class=num>Maint. Cost</th><th class=num>Net Profit</th></tr></thead>";
  const tb = document.createElement("tbody");
  (dash.vehicles || []).forEach((v) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td class="mono"><b>${escapeHtml(v.reg_number)}</b></td>` +
      `<td>${escapeHtml(v.make)} ${escapeHtml(v.model)}</td>` +
      `<td class="num">${v.rented_days}</td>` +
      `<td class="num">${v.idle_days}</td>` +
      `<td class="num">${v.utilization_pct}%</td>` +
      `<td class="num">₹${Number(v.gross_revenue).toLocaleString("en-IN")}</td>` +
      `<td class="num">₹${Number(v.maintenance_cost).toLocaleString("en-IN")}</td>` +
      `<td class="num"><b>₹${Number(v.net_profit).toLocaleString("en-IN")}</b></td>`;
    tb.append(tr);
  });
  tbl.append(tb);
  db.append(tbl);
  dp.append(db);
  body.append(dp);

  // Bulk CSV / XLSX Importer with Preview
  const imp = make("div", "panel");
  const imh = make("div", "panel-head"); imh.append(make("b", null, "Bulk CSV / Excel (.xlsx) Importer with Dry-Run Preview")); imp.append(imh);
  const imb = make("div", "panel-body");
  const targetSel = opsSelect(imb, "Import Target", [["vehicles", "Vehicles (reg_number,make,model,category,fuel_type,daily_rate)"], ["customers", "Customers (full_name,phone,email,dl_number,dl_expiry)"]]);
  const csvArea = document.createElement("textarea");
  csvArea.rows = 4;
  csvArea.style.cssText = "width:100%;padding:8px 11px;border:1px solid var(--line);border-radius:var(--r-sm);background:var(--paper);font:12.5px var(--mono);margin-bottom:8px";
  csvArea.value = "reg_number,make,model,category,fuel_type,daily_rate\nMH-12-XY-8899,Hyundai,Creta,SUV,Diesel,2800";
  imb.append(csvArea);
  const previewOut = make("div", "hint", "Paste CSV rows above (or upload .csv/.xlsx) and click Preview.");
  let lastValidRows = [];
  const btnRow = make("div", "row");
  const prevBtn = make("button", "btn", "1. Preview & Validate");
  const commitBtn = make("button", "btn primary", "2. Commit Valid Rows");
  commitBtn.disabled = true;
  prevBtn.addEventListener("click", async () => {
    try {
      const res = await api("/api/ops/import/preview", {
        body: { target: targetSel.value, filename: "import.csv", content: csvArea.value },
      });
      lastValidRows = res.valid_rows || [];
      commitBtn.disabled = lastValidRows.length === 0;
      const errText = (res.errors || []).map((e) => `Row ${e.row}: ${e.errors.join("; ")}`).join(" | ");
      previewOut.textContent = `Preview: ${res.valid_count} valid, ${res.error_count} error(s). ${errText}`;
    } catch (err) { toast(err.message, true); }
  });
  commitBtn.addEventListener("click", async () => {
    try {
      const res = await api("/api/ops/import/commit", {
        body: { target: targetSel.value, valid_rows: lastValidRows },
      });
      toast(`Imported ${res.imported_count} record(s).`);
      commitBtn.disabled = true;
      await refreshOpsSummary();
      renderOpsHub();
    } catch (err) { toast(err.message, true); }
  });
  btnRow.append(prevBtn, commitBtn);
  imb.append(btnRow, previewOut);
  imp.append(imb);
  body.append(imp);
}

if ($("open-ops-hub")) $("open-ops-hub").addEventListener("click", () => openOpsHub());
if ($("ops-modal-close")) $("ops-modal-close").addEventListener("click", closeOpsHub);
if ($("ops-modal-scrim")) {
  $("ops-modal-scrim").addEventListener("click", (e) => {
    if (e.target === $("ops-modal-scrim")) closeOpsHub();
  });
}
setTimeout(refreshOpsSummary, 1200);

initMascot();
boot();
