/* Float — encrypts passwords, PINs and API keys (ECDH P-256 + AES-256-GCM)
   before they leave the browser. Drop-in replacement for fetch(). */
(() => {
  "use strict";
  const SEALED = /^\/api\/(auth\/signin|auth\/signup|me\/password|me\/pin|keys|unlock|admin\/users(\/\d+)?)$/;
  const te = new TextEncoder(), td = new TextDecoder();
  const b64 = (buf) => { let s = ""; for (const b of new Uint8Array(buf)) s += String.fromCharCode(b); return btoa(s); };
  const unb64 = (s) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0));
  let cache = null;

  async function setup(force) {
    if (cache && !force) return cache;
    const keyRes = await fetch("/api/crypto/key", { cache: "no-store" });
    const info = keyRes.ok ? await keyRes.json() : {};
    if (!info.available || !(window.crypto && crypto.subtle)) {
      if (info.plaintext_allowed) return (cache = { plain: true });
      throw new Error(!info.available
        ? "Float can't protect passwords yet: its 'cryptography' add-on is missing. Ask your admin to run: pip install cryptography"
        : "This page was opened over an unsecured address, so passwords can't be protected. Open Float with its https:// address.");
    }
    const ec = { name: "ECDH", namedCurve: "P-256" };
    const pair = await crypto.subtle.generateKey(ec, false, ["deriveBits"]);
    const epk = await crypto.subtle.exportKey("raw", pair.publicKey);
    const srv = await crypto.subtle.importKey("raw", unb64(info.pub), ec, false, []);
    const bits = await crypto.subtle.deriveBits({ name: "ECDH", public: srv }, pair.privateKey, 256);
    const hk = await crypto.subtle.importKey("raw", bits, "HKDF", false, ["deriveKey"]);
    const aes = await crypto.subtle.deriveKey(
      { name: "HKDF", hash: "SHA-256", salt: te.encode("float-transport-v1"), info: te.encode("aes-256-gcm") },
      hk, { name: "AES-GCM", length: 256 }, false, ["encrypt", "decrypt"]);
    return (cache = { kid: info.kid, epk: b64(epk), aes });
  }

  const reply = (data, status) =>
    new Response(JSON.stringify(data), { status, headers: { "Content-Type": "application/json" } });

  async function secureFetch(path, init, retried) {
    const method = (init && init.method) || "GET";
    if (method !== "POST" || !SEALED.test(path) || !init.body) return fetch(path, init);
    const c = await setup(false);
    if (c.plain) return fetch(path, init);
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const nonce = b64(crypto.getRandomValues(new Uint8Array(18)));
    const msg = JSON.stringify({ ts: Date.now(), n: nonce, body: JSON.parse(init.body) });
    const ct = await crypto.subtle.encrypt(
      { name: "AES-GCM", iv, additionalData: te.encode("c2s|" + path) }, c.aes, te.encode(msg));
    const res = await fetch(path, {
      ...init,
      headers: { ...(init.headers || {}), "Content-Type": "application/json" },
      body: JSON.stringify({ enc: { v: 1, kid: c.kid, epk: c.epk, iv: b64(iv), ct: b64(ct) } }),
    });
    const data = await res.json().catch(() => ({}));
    if (res.status === 409 && data.rekey && !retried) {   // server restarted: new key, try once more
      await setup(true);
      return secureFetch(path, init, true);
    }
    if (res.ok && data.enc) {
      const plain = await crypto.subtle.decrypt(
        { name: "AES-GCM", iv: unb64(data.enc.iv), additionalData: te.encode("s2c|" + path) },
        c.aes, unb64(data.enc.ct));
      return reply(JSON.parse(td.decode(plain)), res.status);
    }
    return reply(data, res.status);
  }

  function hardenInput(node) {
    if (!node || typeof node.setAttribute !== "function") return node;
    node.setAttribute("autocomplete", "off");
    node.setAttribute("data-lpignore", "true");
    node.setAttribute("data-1p-ignore", "true");
    node.setAttribute("data-form-type", "other");
    return node;
  }

  function hardenAll(root = document) {
    if (!root || typeof root.querySelectorAll !== "function") return;
    root.querySelectorAll('input:not([type="password"]):not([type="email"]):not([type="checkbox"]), textarea').forEach(hardenInput);
  }

  window.FloatSecure = { fetch: secureFetch, hardenInput, hardenAll };
})();
