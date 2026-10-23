/* Float — opening screen. Shows the Float logo once each time the app is opened
 * (sessionStorage is cleared when the app window closes), then fades away. */
(function () {
  "use strict";
  var KEY = "float.splash", MIN_MS = 1200, started = Date.now();
  try { if (sessionStorage.getItem(KEY)) return; sessionStorage.setItem(KEY, "1"); } catch (e) {}

  var css = document.createElement("style");
  css.textContent =
    "#float-splash{position:fixed;inset:0;z-index:2147483647;display:flex;flex-direction:column;" +
    "align-items:center;justify-content:center;gap:22px;background:#FAF9F5;color:#141413;" +
    "transition:opacity .45s ease,visibility .45s ease}" +
    "@media (prefers-color-scheme:dark){#float-splash{background:#000000;color:#EDEBE4}}" +
    "#float-splash.out{opacity:0;visibility:hidden}" +
    "#float-splash img{width:112px;height:112px;object-fit:contain;animation:fsPop .7s ease both,fsBob 2.4s ease-in-out .7s infinite}" +
    "#float-splash b{font:600 30px/1 'Times New Roman',Georgia,serif;letter-spacing:.04em;animation:fsFade .9s ease .2s both}" +
    "#float-splash i{display:block;width:88px;height:3px;border-radius:3px;overflow:hidden;background:rgba(128,128,128,.25)}" +
    "#float-splash i::after{content:'';display:block;height:100%;width:40%;border-radius:3px;background:#D97757;animation:fsBar 1.1s ease-in-out infinite}" +
    "@keyframes fsPop{from{opacity:0;transform:scale(.7)}to{opacity:1;transform:scale(1)}}" +
    "@keyframes fsBob{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}" +
    "@keyframes fsFade{from{opacity:0}to{opacity:1}}" +
    "@keyframes fsBar{0%{transform:translateX(-110%)}100%{transform:translateX(280%)}}" +
    "@media (prefers-reduced-motion:reduce){#float-splash *{animation:none!important}}";
  document.documentElement.appendChild(css);

  var box = document.createElement("div");
  box.id = "float-splash";
  box.setAttribute("role", "status");
  box.setAttribute("aria-label", "Float is loading");
  box.innerHTML = '<img src="/float.ico" alt=""><b>Float</b><i></i>';
  document.documentElement.appendChild(box);

  var done = false;
  function hide() {
    if (done) return; done = true;
    box.classList.add("out");
    setTimeout(function () { box.remove(); css.remove(); }, 600);
  }
  function ready() { setTimeout(hide, Math.max(0, MIN_MS - (Date.now() - started))); }
  if (document.readyState === "complete") ready(); else window.addEventListener("load", ready);
  setTimeout(hide, 8000);   // never trap the user behind the splash
})();
