/* Float — admin panel.
 *
 * One admin, one small school, one page. Nothing here is trying to be a
 * multi-tenant console — it's the handful of controls a head of department
 * actually reaches for: who's using it, what it's costing, and a switch to
 * turn a teacher's account off when they leave.
 */

const TOKEN = sessionStorage.getItem("float.token");
if (!TOKEN) location.replace("/login");

const $ = (id) => document.getElementById(id);
const make = (tag, cls, text) => {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text !== undefined) node.textContent = text;
  return node;
};

let DATA = null;
let TAB = "overview";

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
    throw new Error("Float can't be reached right now. If you closed its window, open Float again.");
  }
  if (res.status === 401) { sessionStorage.removeItem("float.token"); location.replace("/login"); return; }
  if (res.status === 403) {
    const blocked = await res.clone().json().catch(() => ({}));
    if (blocked.must_change) {
      document.body.innerHTML = '<div class="empty" style="padding-top:20vh"><b>Set your own password first</b>' +
        'You are using a temporary password. <a href="/">Open Float</a> and choose one in Settings.</div>';
      throw new Error("must change password");
    }
    document.body.innerHTML = '<div class="empty" style="padding-top:20vh"><b>Admins only</b>' +
      "This account can't open the admin panel.</div>";
    throw new Error("forbidden");
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "Something went wrong.");
  return data;
}

let toastTimer = null;
function toast(text, bad = false) {
  const node = $("toast");
  node.textContent = text;
  node.className = "toast" + (bad ? " bad" : "");
  node.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (node.hidden = true), bad ? 5200 : 3200);
}

function rupees(paise) { return "₹" + (paise / 100).toFixed(2); }

const TABS = [
  ["overview", "Overview"],
  ["teachers", "Teachers"],
  ["fair", "Fairness & privacy"],
  ["org", "School settings"],
  ["notices", "Notices"],
  ["audit", "Audit log"],
];

function paintTabs() {
  const bar = $("tabs");
  bar.innerHTML = "";
  TABS.forEach(([id, label]) => {
    const button = make("button", null, label);
    button.setAttribute("aria-selected", String(id === TAB));
    button.addEventListener("click", () => { TAB = id; render(); });
    bar.append(button);
  });
}

async function boot() {
  try {
    DATA = await api("/api/admin/overview");
  } catch {
    return;
  }
  paintTabs();
  render();
}

function render() {
  paintTabs();
  const wrap = $("wrap");
  wrap.innerHTML = "";
  ({ overview: viewOverview, teachers: viewTeachers, fair: viewFair, org: viewOrg,
     notices: viewNotices, audit: viewAudit }[TAB])(wrap);
}

/* ── overview ──────────────────────────────────────────────────────────── */

function viewOverview(wrap) {
  if (DATA.lan_url) {
    const lan = make("div", "panel");
    lan.append(
      make("h2", null, "School server address"),
      make("p", null, `Teachers on other PCs on the network open ${DATA.lan_url} in their browser.`),
    );
    wrap.append(lan);
  }
  const t = DATA.totals;
  const grid = make("div", "stat-grid");
  [
    ["Teachers", t.teachers, `${t.active} active`],
    ["Signed in now", t.signed_in, ""],
    ["Answers · 30 days", t.calls, ""],
    ["Tokens · 30 days", t.tokens.toLocaleString("en-IN"), ""],
    ["Spend (estimate)", "₹" + t.rupees.toFixed(2), "from listed prices"],
  ].forEach(([label, value, sub]) => {
    const card = make("div", "stat");
    card.append(make("b", null, String(value)));
    card.append(make("small", null, sub ? `${label} · ${sub}` : label));
    grid.append(card);
  });
  wrap.append(grid);
  addBackupPanel(wrap);
  addPricesPanel(wrap);

  const chart = make("div", "panel");
  const chartHead = make("div", "panel-head");
  chartHead.append(make("b", null, "Last 14 days"));
  chart.append(chartHead);
  const chartBody = make("div", "panel-body");
  const spark = make("div", "spark");
  const days = DATA.by_day || [];
  const max = Math.max(1, ...days.map((d) => d.calls));
  const byDay = {};
  days.forEach((d) => (byDay[d.day] = d));
  for (let i = 13; i >= 0; i--) {
    const day = new Date(Date.now() - i * 86400000).toISOString().slice(0, 10);
    const entry = byDay[day];
    const bar = make("i");
    const calls = entry ? entry.calls : 0;
    bar.style.height = Math.max(2, (calls / max) * 100) + "%";
    if (i === 0) bar.classList.add("hot");
    bar.title = `${day}: ${calls} answer${calls === 1 ? "" : "s"}`;
    spark.append(bar);
  }
  chartBody.append(spark);
  chart.append(chartBody);
  wrap.append(chart);

  const providers = make("div", "panel");
  const provHead = make("div", "panel-head");
  provHead.append(make("b", null, "Providers"));
  providers.append(provHead);
  const provBody = make("div", "panel-body");
  DATA.providers.forEach((provider) => {
    const row = make("div", "row");
    const grow = make("div", "grow");
    grow.append(make("b", null, provider.label));
    row.append(grow);
    row.append(make("span", provider.allowed ? "pill" : "pill off",
      provider.allowed ? "allowed" : "off"));
    row.append(make("span", provider.key ? "pill admin" : "pill off",
      provider.key ? "school key set" : "no school key"));
    provBody.append(row);
  });
  providers.append(provBody);
  wrap.append(providers);

  if (DATA.notices && DATA.notices.length) {
    const active = make("div", "panel");
    const head = make("div", "panel-head");
    head.append(make("b", null, "Active notices"));
    active.append(head);
    const body = make("div", "panel-body");
    DATA.notices.forEach((n) => {
      const row = make("div", "row");
      const grow = make("div", "grow");
      grow.append(make("b", null, n.title));
      if (n.body) grow.append(make("small", null, n.body));
      row.append(grow);
      body.append(row);
    });
    active.append(body);
    wrap.append(active);
  }
}

/* ── teachers ──────────────────────────────────────────────────────────── */

function addBackupPanel(wrap) {
  const b = DATA.backup || {};
  const panel = make("div", "panel");
  const head = make("div", "panel-head");
  head.append(make("b", null, "Backup"));
  panel.append(head);
  const body = make("div", "panel-body");
  const line = make("p", "hint", b.last ? `Last backup: ${b.last} (${b.count} kept)` : "Last backup: none yet");
  body.append(line);
  body.append(button("Back up now", async () => {
    try {
      const r = await api("/api/admin/backup", { body: {} });
      DATA.backup = r.backup;
      line.textContent = `Last backup: ${r.backup.last} (${r.backup.count} kept)`;
      toast("Backup saved.");
    } catch (err) { toast(err.message || "The backup did not work.", true); }
  }));
  body.append(make("p", "hint", "Float also backs up by itself when it opens, and once a day while open. " +
    "The newest 14 are kept in the data/backups folder. To restore one, close Float and run: python main.py restore"));
  panel.append(body);
  wrap.append(panel);
}

function addPricesPanel(wrap) {
  const pr = DATA.prices;
  if (!pr) return;
  const panel = make("div", "panel");
  const head = make("div", "panel-head");
  head.append(make("b", null, "Model prices (₹ per million tokens, estimate)"));
  panel.append(head);
  const body = make("div", "panel-body");
  if (pr.stale) {
    const warn = make("p", "hint", `Warning: prices were last checked on ${pr.checked} (${pr.age_days} days ago, more than ${pr.limit_days}). ` +
      "Rupee figures in Float may be out of date. Compare them with each provider's pricing page.");
    warn.style.color = "var(--danger, #b3261e)";
    body.append(warn);
  } else {
    body.append(make("p", "hint", `Prices last checked: ${pr.checked}.`));
  }
  const table = document.createElement("table");
  table.innerHTML = "<tr><th>Model</th><th class=num>In</th><th class=num>Out</th><th></th></tr>";
  pr.rows.forEach((row) => {
    const tr = document.createElement("tr");
    const name = make("td", null, row.label + (row.overridden ? " (your price)" : ""));
    const mk = (v) => { const i = document.createElement("input"); i.type = "number"; i.min = "0"; i.step = "any"; i.value = v; i.style.width = "80px"; return i; };
    const inI = mk(row.cost_in), outI = mk(row.cost_out);
    const a = make("td", "num"); a.append(inI);
    const o = make("td", "num"); o.append(outI);
    const act = make("td");
    act.append(button("Save", async () => {
      try {
        const r = await api("/api/admin/prices", { body: { provider: row.provider, model: row.model, cost_in: inI.value, cost_out: outI.value } });
        DATA.prices = r.prices; toast("Price saved."); render();
      } catch (err) { toast(err.message || "Could not save.", true); }
    }));
    tr.append(name, a, o, act);
    table.append(tr);
  });
  body.append(table);
  body.append(button("Mark prices as checked today", async () => {
    try { const r = await api("/api/admin/prices", { body: { checked: true } }); DATA.prices = r.prices; toast("Marked as checked."); render(); }
    catch (err) { toast(err.message || "Could not save.", true); }
  }));
  panel.append(body);
  wrap.append(panel);
}

function viewTeachers(wrap) {
  const head = make("div", "panel");
  const headBody = make("div", "panel-body");
  const row = make("div", "row");
  const grow = make("div", "grow");
  grow.append(make("b", null, "Add a teacher"));
  grow.append(make("small", null, "Float makes a temporary password — hand it over however you normally would."));
  row.append(grow);

  const email = document.createElement("input");
  email.placeholder = "teacher@school.edu.in";
  email.style.cssText = "padding:8px 11px;border:1px solid var(--line);border-radius:var(--r-sm);background:var(--paper);width:220px";
  const name = document.createElement("input");
  name.placeholder = "Name";
  name.style.cssText = email.style.cssText.replace("220px", "160px");
  const add = make("button", "btn primary", "Add");
  add.addEventListener("click", async () => {
    if (!email.value.includes("@")) { toast("That email doesn't look right.", true); return; }
    add.disabled = true;
    try {
      const result = await api("/api/admin/users", { body: { email: email.value, name: name.value } });
      DATA.users = result.users;
      alert(`Account created for ${email.value}.\n\nTemporary password: ${result.temp_password}\n\nThey'll be asked to set their own on first sign-in.`);
      email.value = name.value = "";
      render();
    } catch (err) {
      toast(err.message, true);
    } finally {
      add.disabled = false;
    }
  });
  head.append(headBody);
  headBody.append(row, name, email, add);
  row.style.marginBottom = "0";
  wrap.append(head);

  const table = document.createElement("table");
  table.className = "grid";
  const thead = document.createElement("thead");
  thead.innerHTML = "<tr><th>Teacher</th><th>Role</th><th>Usage</th><th class=num>Sign-ins</th>" +
    "<th class=num>Answers</th><th class=num>Tokens</th><th class=num>₹ (estimate)</th><th></th></tr>";
  table.append(thead);
  const tbody = document.createElement("tbody");

  DATA.users.forEach((user) => {
    const tr = document.createElement("tr");
    if (!user.active) tr.style.opacity = ".5";

    const nameTd = document.createElement("td");
    nameTd.innerHTML = `<b>${escapeHtml(user.name || "—")}</b><br><small style="color:var(--faint)">${escapeHtml(user.email)}</small>`;
    tr.append(nameTd);

    const roleTd = document.createElement("td");
    const pill = make("span", user.role === "admin" ? "pill admin" : "pill", user.role);
    roleTd.append(pill);
    if (!user.active) roleTd.append(make("span", "pill off", "off"));
    tr.append(roleTd);

    const bandTd = document.createElement("td");
    bandTd.textContent = user.band + (user.custom_cap ? " · custom limit" : "");
    tr.append(bandTd);

    [user.sign_ins, user.calls, user.calls === null ? null : user.tin + user.tout].forEach((value) => {
      const td = document.createElement("td");
      td.className = "num";
      td.textContent = value === null ? "—" : (value || 0).toLocaleString("en-IN");
      tr.append(td);
    });

    const rupeeTd = document.createElement("td");
    rupeeTd.className = "num";
    rupeeTd.textContent = user.paise === null ? "—" : rupees(user.paise || 0);
    tr.append(rupeeTd);

    const actTd = document.createElement("td");
    actTd.append(actionMenu(user));
    tr.append(actTd);

    tbody.append(tr);
  });

  table.append(tbody);
  const panel = make("div", "panel");
  const panelBody = make("div", "panel-body");
  panelBody.style.overflowX = "auto";
  panelBody.append(table);
  panel.append(panelBody);
  wrap.append(panel);
}

function actionMenu(user) {
  const wrap = make("div");
  wrap.style.cssText = "display:flex;gap:5px;flex-wrap:wrap;justify-content:flex-end";

  const act = async (action, confirmText) => {
    if (confirmText && !confirm(confirmText)) return;
    try {
      const result = await api(`/api/admin/users/${user.id}`, { body: { action } });
      DATA.users = result.users;
      toast(result.temp_password
        ? `New password for ${user.email}: ${result.temp_password}`
        : "Done.");
      render();
    } catch (err) { toast(err.message, true); }
  };

  if (user.active) {
    wrap.append(button("Reset password", () =>
      act("reset_password", `Reset ${user.email}'s password? They'll need the new one.`)));
    wrap.append(button("Adjust limit", async () => {
      const v = prompt(`Monthly AI limit for ${user.name || user.email}, in ₹.\nLeave empty to use the school default. 0 means no limit.`, "");
      if (v === null) return;
      let body = { action: "set_cap", paise: "" };
      if (v.trim() !== "") {
        const reason = prompt("Why? (recorded in the audit log so limits stay fair)", "");
        if (!reason) return;
        body = { action: "set_cap", paise: Math.round(parseFloat(v) * 100), reason };
      }
      try {
        const result = await api(`/api/admin/users/${user.id}`, { body });
        DATA.users = result.users; toast("Limit updated."); render();
      } catch (err) { toast(err.message, true); }
    }));
    wrap.append(button("Sign out", () => act("sign_out")));
    if (user.role === "teacher") wrap.append(button("Make admin", () => act("make_admin")));
    else wrap.append(button("Make teacher", () => act("make_teacher")));
    wrap.append(button("Deactivate", () => act("deactivate"), true));
  } else {
    wrap.append(button("Reactivate", () => act("activate")));
  }
  wrap.append(button("Delete", () =>
    act("delete", `Delete ${user.email} and everything they've made? This can't be undone.`), true));

  return wrap;
}

function button(label, onClick, danger) {
  const b = make("button", "btn tiny" + (danger ? " danger" : ""), label);
  b.addEventListener("click", onClick);
  return b;
}

function escapeHtml(text) {
  return String(text).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

/* ── school settings ───────────────────────────────────────────────────── */

/* ── fairness & privacy ────────────────────────────────────────────────── */

function viewFair(wrap) {
  const f = DATA.fairness, org = DATA.org;
  const grid = make("div", "stat-grid");
  const pct = f.pool_budget ? Math.round((f.pool_spent / f.pool_budget) * 100) + "% of pool" : "no pool set";
  [
    ["Yet to start", `${f.not_started} of ${f.accounts}`, "a walkthrough helps more than a nudge"],
    ["Top fifth's share of spend", f.top_fifth_share + "%", "near 20% would be even"],
    ["Near their limit", f.near_cap, "80% or more used"],
    ["School spend this month (estimate)", "₹" + (f.pool_spent / 100).toFixed(2), pct],
  ].forEach(([label, value, sub]) => {
    const card = make("div", "stat");
    card.append(make("b", null, String(value)));
    card.append(make("small", null, `${label} · ${sub}`));
    grid.append(card);
  });
  wrap.append(grid);

  const panel = make("div", "panel"), body = make("div", "panel-body");
  body.append(make("b", null, "Equal share, by default"));
  body.append(make("small", null, "Every teacher gets the same monthly allowance. Exceptions (for example a head of department "
    + "or a teacher with accessibility needs) are set per person from the Teachers tab and need a recorded reason. "
    + "Teachers using their own API key are never limited."));
  const mk = (label, value) => {
    const field = make("div", "field"); field.append(make("label", null, label));
    const input = document.createElement("input"); input.type = "number"; input.min = "0";
    input.value = value; field.append(input); body.append(field); return input;
  };
  const cap = mk("Monthly limit per teacher (₹, 0 = none)", Math.round(+(org.teacher_monthly_paise_cap || 0) / 100));
  const pool = mk("School monthly budget (₹, 0 = none) · shown as a warning, never blocks anyone", Math.round(+(org.monthly_paise_budget || 0) / 100));
  const vis = make("div", "field"); vis.append(make("label", null, "What you see about each teacher"));
  const sel = document.createElement("select");
  [["bands", "Usage band only (recommended)"], ["exact", "Exact counts and ₹"]].forEach(([v, t]) => {
    const o = document.createElement("option"); o.value = v; o.textContent = t;
    o.selected = (org.usage_detail || "bands") === v; sel.append(o);
  });
  vis.append(sel); body.append(vis);
  const save = make("button", "btn primary", "Save");
  save.addEventListener("click", async () => {
    try {
      const r = await api("/api/admin/org", { body: {
        teacher_monthly_paise_cap: Math.round(cap.value * 100) || 0,
        monthly_paise_budget: Math.round(pool.value * 100) || 0, usage_detail: sel.value } });
      DATA = await api("/api/admin/overview"); toast("Saved."); render();
    } catch (err) { toast(err.message, true); }
  });
  body.append(save); panel.append(body); wrap.append(panel);

  const priv = make("div", "panel"), pb = make("div", "panel-body");
  pb.append(make("b", null, "What this panel can and cannot see"));
  [
    "Can see: account names, roles, sign-in counts, and usage as a band or totals.",
    "Cannot see: any chat, draft, file, class list, mark, or attendance record. There is no screen or API for it.",
    "Never shown: rankings. Teachers are listed alphabetically, and fairness figures are school-wide, never named.",
    "Always logged: limit changes (with reason), exports, resets and role changes, visible in the Audit log.",
  ].forEach((t) => { const p = make("p", null, t); p.style.margin = "8px 0"; pb.append(p); });
  priv.append(pb); wrap.append(priv);
}

/* ── school settings ───────────────────────────────────────────────────── */

function viewOrg(wrap) {
  const org = DATA.org;

  const panel = make("div", "panel");
  const body = make("div", "panel-body");

  const nameField = make("div", "field");
  nameField.append(make("label", null, "School name"));
  const nameInput = document.createElement("input");
  nameInput.type = "text";
  nameInput.value = org.school_name || "";
  nameField.append(nameInput);
  body.append(nameField);

  const toggles = [
    ["computer_control", "Let Float use the computer", "Mouse and keyboard control for repetitive on-screen tasks."],
    ["teacher_own_keys", "Teachers may add their own API key", "Turn off if only the school key should be used."],
    ["self_signup", "Anyone with the right email can sign up", "Off means you add every teacher yourself, from this page."],
    ["require_pin", "Require a quick PIN", "Ask every teacher to set one, for faster sign-in between periods."],
  ];
  toggles.forEach(([key, label, hint]) => {
    const row = make("div", "row");
    const check = document.createElement("input");
    check.type = "checkbox";
    check.checked = org[key] === "1";
    check.dataset.key = key;
    row.append(check);
    const grow = make("div", "grow");
    grow.append(make("b", null, label));
    grow.append(make("small", null, hint));
    row.append(grow);
    body.append(row);
  });

  const providersField = make("div", "field");
  providersField.append(make("label", null, "Providers teachers may use"));
  const providersBox = make("div", "tagbox");
  const allowed = new Set(DATA.providers.filter((p) => p.allowed).map((p) => p.id));
  DATA.providers.forEach((p) => {
    const tag = make("button", "tag", p.label);
    tag.type = "button";
    tag.dataset.provider = p.id;
    tag.setAttribute("aria-pressed", String(allowed.has(p.id)));
    tag.addEventListener("click", () => {
      if (allowed.has(p.id)) allowed.delete(p.id); else allowed.add(p.id);
      tag.setAttribute("aria-pressed", String(allowed.has(p.id)));
    });
    providersBox.append(tag);
  });
  providersField.append(providersBox);
  body.append(providersField);

  const save = make("button", "btn primary", "Save settings");
  save.style.marginTop = "8px";
  save.addEventListener("click", async () => {
    save.disabled = true;
    const payload = { school_name: nameInput.value, allowed_providers: [...allowed] };
    body.querySelectorAll('input[type=checkbox]').forEach((box) => {
      payload[box.dataset.key] = box.checked ? "1" : "0";
    });
    try {
      const result = await api("/api/admin/org", { body: payload });
      DATA.org = result.org;
      toast("Saved.");
    } catch (err) {
      toast(err.message, true);
    } finally {
      save.disabled = false;
    }
  });
  body.append(save);

  panel.append(body);
  wrap.append(panel);

  const exportPanel = make("div", "panel");
  const exportBody = make("div", "panel-body");
  const exportRow = make("div", "row");
  const exportGrow = make("div", "grow");
  exportGrow.append(make("b", null, "Usage report"));
  exportGrow.append(make("small", null, "Last 30 days as an Excel sheet, without email addresses. Each download is logged."));
  exportRow.append(exportGrow);
  const exportBtn = make("button", "btn", "Download .xlsx");
  exportBtn.addEventListener("click", async () => {
    const res = await fetch("/api/admin/export", { headers: { Authorization: "Bearer " + TOKEN } });
    if (!res.ok) { toast("Could not build the report.", true); return; }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "float-usage.xlsx";
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 4000);
  });
  exportRow.append(exportBtn);
  exportBody.append(exportRow);
  exportPanel.append(exportBody);
  wrap.append(exportPanel);
}

/* ── notices ───────────────────────────────────────────────────────────── */

function viewNotices(wrap) {
  wrap.append(make("p", "inline-note",
    "A notice appears as a strip at the top of every teacher's Float, until you retire it."));

  const panel = make("div", "panel");
  const body = make("div", "panel-body");

  if (!DATA.notices.length) {
    const empty = make("div", "empty");
    empty.append(make("b", null, "Nothing posted"));
    body.append(empty);
  }
  DATA.notices.forEach((notice) => {
    const row = make("div", "row");
    const grow = make("div", "grow");
    grow.append(make("b", null, notice.title));
    if (notice.body) grow.append(make("small", null, notice.body));
    row.append(grow);
    const retire = make("button", "btn tiny", "Retire");
    retire.addEventListener("click", async () => {
      const result = await api("/api/admin/notice", { body: { retire: notice.id } });
      DATA.notices = result.notices;
      render();
    });
    row.append(retire);
    body.append(row);
  });
  panel.append(body);
  wrap.append(panel);

  const addPanel = make("div", "panel");
  const addBody = make("div", "panel-body");
  const title = document.createElement("input");
  title.placeholder = "Title — e.g. Report cards due Friday";
  title.style.cssText = "width:100%;padding:8px 11px;border:1px solid var(--line);border-radius:var(--r-sm);background:var(--paper);margin-bottom:9px";
  const text = document.createElement("textarea");
  text.placeholder = "A line or two of detail (optional)";
  text.style.cssText = "width:100%;padding:8px 11px;border:1px solid var(--line);border-radius:var(--r-sm);background:var(--paper);min-height:60px;margin-bottom:9px";
  addBody.append(title, text);
  const post = make("button", "btn primary", "Post notice");
  post.addEventListener("click", async () => {
    if (!title.value.trim()) { toast("Give it a title.", true); return; }
    try {
      const result = await api("/api/admin/notice", { body: { title: title.value, body: text.value } });
      DATA.notices = result.notices;
      title.value = text.value = "";
      toast("Posted.");
      render();
    } catch (err) { toast(err.message, true); }
  });
  addBody.append(post);
  addPanel.append(addBody);
  wrap.append(addPanel);
}

/* ── audit log ─────────────────────────────────────────────────────────── */

async function viewAudit(wrap) {
  wrap.append(make("p", "inline-note",
    "Sign-ins, key changes, deactivations and anything else that matters later. Nothing here is editable."));

  const panel = make("div", "panel");
  const body = make("div", "panel-body");
  const log = make("div", "log", "Loading…");
  body.append(log);
  panel.append(body);
  wrap.append(panel);

  try {
    const data = await api("/api/admin/audit?limit=300");
    log.innerHTML = "";
    if (!data.entries.length) { log.textContent = "Nothing logged yet."; return; }
    data.entries.forEach((entry) => {
      const row = make("div", entry.level !== "info" ? entry.level : "");
      const time = new Date(entry.created_at * 1000);
      row.append(make("time", null, time.toLocaleString("en-IN", {
        day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit",
      })));
      row.append(make("span", "who", entry.actor || "system"));
      row.append(make("span", "what", `${entry.action} — ${entry.detail || ""}`));
      log.append(row);
    });
  } catch {
    log.textContent = "Could not load the log.";
  }
}

/* ── chrome ────────────────────────────────────────────────────────────── */

$("back-app").addEventListener("click", () => (location.href = "/"));
$("toggle-theme").addEventListener("click", () => {
  document.documentElement.dataset.theme =
    document.documentElement.dataset.theme === "dark" ? "light" : "dark";
});

const dark = window.matchMedia("(prefers-color-scheme: dark)");
document.documentElement.dataset.theme = dark.matches ? "dark" : "light";

boot();
