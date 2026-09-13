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

  // ---------------------------------------------------------------- Mobile nav
  onReady(function () {
    var burger = document.getElementById("navToggle");
    var body = document.body;
    if (!burger) return;

    function setOpen(open) {
      body.classList.toggle("nav-open", open);
      burger.setAttribute("aria-expanded", open ? "true" : "false");
      burger.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
    }

    burger.addEventListener("click", function () {
      setOpen(!body.classList.contains("nav-open"));
    });

    // Close on Escape
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && body.classList.contains("nav-open")) setOpen(false);
    });

    // Close on focus change leaving nav? Keep simple: close when a mobile link is clicked.
    document.querySelectorAll(".mobile-nav a").forEach(function (a) {
      a.addEventListener("click", function () {
        if (body.classList.contains("nav-open")) setOpen(false);
      });
    });

    setOpen(false);
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