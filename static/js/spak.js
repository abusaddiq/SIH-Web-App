// SPAK platform JS — nav, reveal-on-scroll, AI widget, alerts.
(function () {
  "use strict";

  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function onReady(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  // ---------------------------------------------------------------- Theme (dark/light)
  var THEME_KEY = "spak-theme";
  function currentTheme() {
    var saved = null;
    try { saved = localStorage.getItem(THEME_KEY); } catch (e) {}
    if (saved === "dark" || saved === "light") return saved;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  function applyTheme(t) {
    document.documentElement.setAttribute("data-theme", t);
    var btn = document.getElementById("themeToggle");
    if (btn) btn.setAttribute("aria-label", t === "dark" ? "Switch to light mode" : "Switch to dark mode");
  }
  onReady(function () {
    applyTheme(currentTheme());
    var btn = document.getElementById("themeToggle");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      try { localStorage.setItem(THEME_KEY, next); } catch (e) {}
      applyTheme(next);
    });
  });

  // ---------------------------------------------------------------- Responsive sidebar
  // Single source of truth for the mode: the markup and CSS key off the
  // `data-mode` attribute (persistent/modal); the breakpoint lives once in
  // window.SPAK_SIDEBAR_BREAKPOINT (defined in base.html).
  onReady(function () {
    var app = document.getElementById("spak-app");
    var rail = document.getElementById("spakSidebar");
    var content = document.getElementById("pageContent");
    var scrim = document.getElementById("sidebarScrim");
    var trigger = document.getElementById("navToggle");
    if (!app || !rail || !content || !trigger || !window.SPAK_SIDEBAR_BREAKPOINT) return;

    var mq = window.matchMedia(window.SPAK_SIDEBAR_BREAKPOINT);
    var supportsInert = "inert" in HTMLElement.prototype;
    var open = false;
    var returnTo = null;

    function modal() { return !mq.matches; }

    function onKey(e) {
      if (e.key === "Escape" && open) setOpen(false);
    }

    function paint() {
      var modalHost = modal();
      app.setAttribute("data-mode", modalHost ? "modal" : "persistent");
      app.toggleAttribute("data-open", open);
      scrim.toggleAttribute("hidden", !(modalHost && open));
      trigger.setAttribute("aria-expanded", String(modalHost && open));
      trigger.setAttribute("aria-label", modalHost && open ? "Close navigation" : "Open navigation");
      rail.setAttribute("role", modalHost ? "dialog" : "complementary");
      if (modalHost) rail.setAttribute("aria-modal", "true");
      else rail.removeAttribute("aria-modal");
      var block = modalHost && open;
      document.body.classList.toggle("spak-nav-locked", block);
      if (supportsInert) content.inert = block;
      else content.setAttribute("aria-hidden", String(block));
    }

    function setOpen(next) {
      open = next;
      if (next) { returnTo = document.activeElement; document.addEventListener("keydown", onKey); }
      else document.removeEventListener("keydown", onKey);
      paint();
      if (next) {
        requestAnimationFrame(function () {
          var closeBtn = rail.querySelector("[data-spak-close]");
          if (closeBtn) closeBtn.focus();
        });
      } else if (returnTo) {
        returnTo.focus({ preventScroll: true });
        returnTo = null;
      }
    }

    function onModeChange() {
      if (open && !modal()) setOpen(false);
      else paint();
    }

    if (mq.addEventListener) mq.addEventListener("change", onModeChange);
    else if (mq.addListener) mq.addListener(onModeChange);

    trigger.addEventListener("click", function () {
      if (modal()) setOpen(!open);
    });

    if (scrim) scrim.addEventListener("click", function () { setOpen(false); });

    rail.querySelectorAll("[data-spak-close]").forEach(function (b) {
      b.addEventListener("click", function () { setOpen(false); });
    });

    // Close the drawer as soon as any sidebar link is activated (route change).
    rail.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        if (modal() && open) setOpen(false);
      });
    });

    paint();
    // matchMedia can report stale state at parse time, so settle again after first layout.
    requestAnimationFrame(paint);
  });

  // ---------------------------------------------------------------- Reveal
  onReady(function () {
    if (reduceMotion) return;
    var els = document.querySelectorAll(".reveal");
    if (!("IntersectionObserver" in window) || !els.length) {
      els.forEach(function (el) { el.classList.add("is-in"); });
      return;
    }
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) {
            en.target.classList.add("is-in");
            io.unobserve(en.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -6% 0px" }
    );
    els.forEach(function (el) { io.observe(el); });
  });

  // ---------------------------------------------------------------- Alerts
  onReady(function () {
    document.querySelectorAll(".site-alerts .alert").forEach(function (el) {
      setTimeout(function () {
        el.style.opacity = "0";
        el.style.transition = "opacity .5s";
        setTimeout(function () { el.style.display = "none"; }, 500);
      }, 7000);
    });
  });

  // ---------------------------------------------------------------- AI widget
  onReady(function () {
    var widget = document.getElementById("aiWidget");
    if (!widget) return;

    var open = false;
    var launcher = widget.querySelector(".ai-widget__launcher");
    var closeBtn = widget.querySelector(".ai-widget__close");
    var input = widget.querySelector('input[name="question"]');
    var chat = widget.querySelector(".ai-widget__chat");
    var form = widget.querySelector(".ai-widget__form");
    var askUrl = widget.getAttribute("data-endpoint") || "/ai/ask/";

    function toggle(v) {
      open = typeof v === "boolean" ? v : !open;
      widget.classList.toggle("open", open);
      launcher.setAttribute("aria-expanded", open ? "true" : "false");
      if (open && input) input.focus();
    }

    launcher.addEventListener("click", function () { toggle(); });
    if (closeBtn) closeBtn.addEventListener("click", function () { toggle(false); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && open) toggle(false);
    });

    function addMsg(text, who) {
      var div = document.createElement("div");
      div.className = "ai-widget__msg ai-widget__msg--" + who;
      div.textContent = text;
      chat.appendChild(div);
      chat.scrollTop = chat.scrollHeight;
      return div;
    }

    if (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var q = (input && input.value || "").trim();
        if (!q) return;
        addMsg(q, "user");
        input.value = "";
        var thinking = addMsg("Thinking…", "ai");
        widget.classList.add("is-thinking");

        var opts = {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8" },
          body: new URLSearchParams({ question: q }).toString()
        };
        var token = (document.querySelector('meta[name="csrf-token"]') || {}).content;
        if (token) opts.headers["X-CSRFToken"] = token;

        fetch(askUrl, opts)
          .then(function (r) { return r.ok ? r.json() : Promise.reject(new Error("HTTP " + r.status)); })
          .then(function (data) {
            thinking.textContent = data["answer"] || "I could not find an answer. Please contact SPAK directly.";
          })
          .catch(function () {
            thinking.textContent = "Sorry, I’m having trouble reaching the assistant right now. Try the full AI Assistant page.";
          })
          .finally(function () { widget.classList.remove("is-thinking"); chat.scrollTop = chat.scrollHeight; });
      });

      // Suggested prompts
      widget.querySelectorAll(".ai-widget__suggest button").forEach(function (btn) {
        btn.addEventListener("click", function () {
          if (input) input.value = btn.getAttribute("data-q") || btn.textContent;
          form.dispatchEvent(new Event("submit", { cancelable: true }));
        });
      });
    }
  });
})();