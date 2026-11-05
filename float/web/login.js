/* Float — the gate.
 *
 * Three ways in, in the order a real operator meets them:
 *   quick   a PIN, because this is the same laptop as yesterday
 *   signin  email and password, or Google
 *   signup  the first account on the machine, or a rental agency that allows self sign-up
 *
 * The session token lives in sessionStorage and nowhere else. Close the window,
 * close the app, and the token is gone — which is the whole of the
 * "log out when the operator closes the app" requirement, done honestly.
 * The server backs it up with a per-process boot nonce, so even a copied token
 * is dead once Float restarts.
 */

const KNOWN = "float.known";      // { name, email } — a convenience, never a credential
const TOKEN = "float.token";

const el = (id) => document.getElementById(id);
const modes = { quick: el("mode-quick"), signin: el("mode-signin"), signup: el("mode-signup") };

let state = { google: false, self_signup: false, setup_needed: false, school: "" };
let busy = false;

/* ---------------------------------------------------------------- plumbing */

async function api(path, body) {
  let res;
  try {
    res = await FloatSecure.fetch(path, {
      method: body === undefined ? "GET" : "POST",
      headers: { "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body || {}),
    });
  } catch (err) {
    throw new Error("Float can't be reached right now. If you closed its window, open Float again.");
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "Float could not reach its own server.");
  return data;
}

function say(text, kind = "bad") {
  const box = el("gate-msg");
  box.className = "gate-msg " + kind;
  box.textContent = text;
  box.hidden = false;
}

function clearSay() {
  const box = el("gate-msg");
  box.hidden = true;
  box.textContent = "";
  box.className = "";
}

function show(name) {
  clearSay();
  for (const [key, node] of Object.entries(modes)) node.hidden = key !== name;
  const focus = modes[name].querySelector("input:not([hidden])");
  if (focus) setTimeout(() => focus.focus(), 60);
}

function lock(on) {
  busy = on;
  document.querySelectorAll(".gate-submit, .gate-google, #mode-signup input").forEach((b) => (b.disabled = on));
}

function known() {
  try {
    const v = JSON.parse(localStorage.getItem(KNOWN) || "null");
    return v && typeof v === "object" ? v : null;
  } catch { return null; }
}

function remember(user) {
  try {
    localStorage.setItem(KNOWN, JSON.stringify({ name: user.name, email: user.email }));
  } catch { /* private window; not important */ }
}

function enter(data) {
  sessionStorage.setItem(TOKEN, data.token);
  if (data.user) remember(data.user);
  if (data.must_change) sessionStorage.setItem("float.must_change", "1");
  location.replace("/");
}

/* -------------------------------------------------------------------- boot */

async function boot() {
  if (sessionStorage.getItem(TOKEN)) { location.replace("/"); return; }

  try {
    state = await api("/api/auth/state", {});
  } catch {
    say("Float's server isn't answering. Close the window and start Float again.");
    return;
  }

  if (state.school) {
    el("pull-cite").textContent = state.school;
    document.title = `Sign in · Float · ${state.school}`;
  }


  if (state.setup_needed) {
    el("signup-switch").hidden = true;
    show("signup");
    if (state.local === false) {
      say("Create the first account (the admin) on the Float computer itself. Once that is done, refresh this page to sign in.");
      lock(true);
    }
    return;
  }

  el("signup-title").textContent = "Join your rental desk.";
  el("signup-sub").textContent = "Float keeps your fleet groups, contracts and drafts to yourself.";
  el("su-school-field").hidden = true;
  el("signin-switch").hidden = !state.self_signup;

  const who = known();
  if (who && who.email) {
    el("quick-name").textContent = who.name || who.email;
    el("quick-email").textContent = who.email;
    el("quick-avatar").textContent = (who.name || who.email).trim().charAt(0).toUpperCase();
    show("quick");
  } else {
    show("signin");
  }
}

/* ------------------------------------------------------------ quick / PIN */

el("form-quick").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (busy) return;
  const who = known();
  const pin = el("quick-pin").value.trim();
  if (!who || !pin) return;

  lock(true);
  try {
    enter(await api("/api/auth/signin", { email: who.email, pin }));
  } catch (err) {
    el("quick-pin").value = "";
    el("quick-pin").focus();
    say(/match/.test(err.message)
      ? "That PIN didn't work. Try again, or use your password."
      : err.message);
  } finally {
    lock(false);
  }
});

el("forget-device").addEventListener("click", () => {
  localStorage.removeItem(KNOWN);
  el("si-email").value = "";
  show("signin");
});

/* --------------------------------------------------------- password signin */

el("form-signin").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (busy) return;
  lock(true);
  try {
    enter(await api("/api/auth/signin", {
      email: el("si-email").value.trim(),
      password: el("si-password").value,
    }));
  } catch (err) {
    el("si-password").value = "";
    say(err.message);
  } finally {
    lock(false);
  }
});

/* -------------------------------------------------------------- signing up */

el("form-signup").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (busy) return;
  lock(true);
  try {
    enter(await api("/api/auth/signup", {
      name: el("su-name").value.trim(),
      school: el("su-school").value.trim(),
      email: el("su-email").value.trim(),
      password: el("su-password").value,
    }));
  } catch (err) {
    say(err.message);
  } finally {
    lock(false);
  }
});

/* ------------------------------------------------------------------ chrome */

document.querySelectorAll("[data-go]").forEach((button) => {
  button.addEventListener("click", () => show(button.dataset.go));
});

// Follow the machine's own light/dark preference. No switch on the gate —
// there is nothing here worth a decision.
const dark = window.matchMedia("(prefers-color-scheme: dark)");
const paint = () => {
  document.documentElement.dataset.theme = dark.matches ? "dark" : "light";
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.content = dark.matches ? "#000000" : "#FAF9F5";
};
dark.addEventListener("change", paint);
paint();

boot();

/* ------------------------------------------------------------------ mascot */

(function initLoginMascot() {
  const mascot = el("float-mascot");
  const bubble = el("mascot-bubble");
  if (!mascot || !bubble) return;
  const quips = ["Ready for shift?", "Welcome to the desk!", "Keys & quotes ready!", "Have a smooth shift!"];
  let idx = 0;
  let timer = null;
  const react = () => {
    bubble.textContent = quips[idx % quips.length];
    idx += 1;
    mascot.classList.add("is-talking");
    clearTimeout(timer);
    timer = setTimeout(() => mascot.classList.remove("is-talking"), 2200);
  };
  mascot.addEventListener("mouseenter", react);
  mascot.addEventListener("click", react);
})();
