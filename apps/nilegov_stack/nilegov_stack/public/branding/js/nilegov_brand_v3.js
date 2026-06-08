/*
 * NileGov Visual Script v3 — Frappe Number Card Navigation
 * Front-end only. No API calls. No database writes. No record mutation.
 */

(function () {
  "use strict";

  const ROUTES = {
    "Total Service Requests": "nilegov-service-request",
    "Service Requests": "nilegov-service-request",
    "Citizen Profiles": "nilegov-citizen-profile",
    "Payment Records": "nilegov-payment-record",
    "Evidence Documents": "nilegov-evidence-document",
    "SLA Events": "nilegov-sla-event",
    "Escalation Records": "nilegov-escalation-record",
    "Identity Verifications": "nilegov-simulated-identity-verification",
    "Integration Logs": "nilegov-integration-simulation-log"
  };

  function normalize(value) {
    return String(value || "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function getRouteFromCard(card) {
    const directName = normalize(card.getAttribute("number_card_name"));
    if (ROUTES[directName]) {
      return {
        name: directName,
        route: ROUTES[directName]
      };
    }

    const text = normalize(card.innerText || card.textContent || "").toUpperCase();

    for (const [name, route] of Object.entries(ROUTES)) {
      if (text.includes(name.toUpperCase())) {
        return {
          name,
          route
        };
      }
    }

    return null;
  }

  function shouldIgnoreClick(event) {
    return Boolean(
      event.target.closest("button") ||
      event.target.closest("a") ||
      event.target.closest("input") ||
      event.target.closest("select") ||
      event.target.closest("textarea") ||
      event.target.closest(".dropdown") ||
      event.target.closest(".dropdown-menu") ||
      event.target.closest(".ellipsis") ||
      event.target.closest(".widget-control") ||
      event.target.closest("[role='button']")
    );
  }

  function goTo(route) {
    if (!route) return;

    if (window.frappe && typeof window.frappe.set_route === "function") {
      window.frappe.set_route("List", route);
      return;
    }

    window.location.href = "/app/" + route;
  }

  function decorate(card, match) {
    if (!card || !match) return false;

    if (card.dataset.nilegovClickable === "1") {
      return false;
    }

    card.dataset.nilegovClickable = "1";
    card.classList.add("nilegov-clickable-card");
    card.setAttribute("role", "link");
    card.setAttribute("tabindex", "0");
    card.setAttribute("title", "Open " + match.name);
    card.setAttribute("aria-label", "Open " + match.name);

    const innerWidget = card.querySelector(".widget, .number-widget-box, .widget-box, .widget-card");
    if (innerWidget) {
      innerWidget.classList.add("nilegov-clickable-card-inner");
    }

    card.addEventListener("click", function (event) {
      if (shouldIgnoreClick(event)) return;
      event.preventDefault();
      event.stopPropagation();
      goTo(match.route);
    });

    card.addEventListener("keydown", function (event) {
      if (event.key !== "Enter" && event.key !== " ") return;
      if (shouldIgnoreClick(event)) return;
      event.preventDefault();
      event.stopPropagation();
      goTo(match.route);
    });

    return true;
  }

  function scan() {
    const wrappers = Array.from(document.querySelectorAll("div[number_card_name]"));
    let decorated = 0;

    wrappers.forEach(function (card) {
      const match = getRouteFromCard(card);
      if (!match) return;

      if (decorate(card, match)) {
        decorated += 1;
      }
    });

    window.NileGovBrand = window.NileGovBrand || {};
    window.NileGovBrand.version = "v3";
    window.NileGovBrand.numberCardWrappers = wrappers.length;
    window.NileGovBrand.clickableCards = document.querySelectorAll(".nilegov-clickable-card").length;
    window.NileGovBrand.lastScan = new Date().toISOString();

    // Run custom UI enhancements on every scan (idempotent)
    runNileGovEnhancements();

    return window.NileGovBrand;
  }

  function enhanceNileGovSearch() {
    const inputs = document.querySelectorAll('.desk-header .navbar-search input, .desk-header .search-bar input, .navbar-search input, .search-bar input, input[placeholder*="Search or type a command"]');
    inputs.forEach(function (input) {
      if (input.dataset.nilegovSearchEnhanced === "1") return;
      input.dataset.nilegovSearchEnhanced = "1";
      input.setAttribute("placeholder", "Search NileGov records, cases, citizens...");
    });
  }

  function enhanceNileGovLogin() {
    if (window.location.pathname.indexOf("login") === -1 && document.body.className.indexOf("login") === -1) {
      return;
    }
    const heading = document.querySelector('.login-container h4, .for-login h4, .page-card-head h4, .login-content h4');
    if (heading && heading.dataset.nilegovLoginEnhanced !== "1") {
      heading.dataset.nilegovLoginEnhanced = "1";
      let html = heading.innerHTML;
      if (html.includes("Login to Frappe")) {
        heading.innerHTML = html.replace("Login to Frappe", "Login to NileGov");
      } else if (html.includes("Login to")) {
        heading.innerHTML = html.replace(/Login to\s+[a-zA-Z0-9_-]+/g, "Login to NileGov");
      } else {
        heading.textContent = "Login to NileGov";
      }
    }
  }

  function enhanceNileGovDateFields() {
    const wrappers = document.querySelectorAll('.frappe-control[data-fieldtype="Date"], .frappe-control[data-fieldtype="Datetime"]');
    wrappers.forEach(function (wrapper) {
      const input = wrapper.querySelector('input.form-control');
      if (!input) return;

      const inputWrapper = wrapper.querySelector('.control-input-wrapper, .control-input');
      if (!inputWrapper) return;

      // Idempotency: Check if the trigger is already present inside inputWrapper
      if (inputWrapper.querySelector('.nilegov-date-trigger')) {
        if (input.style.paddingRight !== '38px') {
          input.style.paddingRight = '38px';
        }
        return;
      }

      inputWrapper.style.position = 'relative';

      const trigger = document.createElement('button');
      trigger.type = 'button';
      trigger.className = 'nilegov-date-trigger';
      trigger.setAttribute('aria-label', 'Open calendar');
      trigger.style.position = 'absolute';
      trigger.style.right = '12px';
      trigger.style.top = '50%';
      trigger.style.transform = 'translateY(-50%)';
      trigger.style.background = 'none';
      trigger.style.border = 'none';
      trigger.style.padding = '0';
      trigger.style.cursor = 'pointer';
      trigger.style.display = 'flex';
      trigger.style.alignItems = 'center';
      trigger.style.zIndex = '5';

      const fieldType = wrapper.getAttribute('data-fieldtype');
      let svgIcon = '';
      if (fieldType === 'Date') {
        svgIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2A3138" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>`;
      } else {
        svgIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2A3138" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>`;
      }
      trigger.innerHTML = svgIcon;

      trigger.addEventListener('click', function(event) {
        event.preventDefault();
        event.stopPropagation();
        input.focus();
        const mousedownEvent = new MouseEvent('mousedown', {
          bubbles: true,
          cancelable: true,
          view: window
        });
        input.dispatchEvent(mousedownEvent);
        input.click();
      });

      inputWrapper.appendChild(trigger);
      input.style.paddingRight = '38px';
    });
  }

  function hideNileGovHelpMenu() {
    // Hide Help menu in navbar
    const helpItems = document.querySelectorAll('.desk-header .help-menu, .desk-header [data-label="Help"], .desk-header .dropdown-help, .navbar .help-menu, .navbar [data-label="Help"], .navbar .dropdown-help, .nav-item-help, [href="/app/help"], .navbar-nav a[href*="support"], .navbar-nav a[href*="help"]');
    helpItems.forEach(function (el) {
      if (el.style.display !== 'none') {
        el.style.setProperty('display', 'none', 'important');
      }
    });

    // Clean up dropdowns to hide "Frappe Support", "Keyboard Shortcuts", "About", and theme menu options
    const dropdownItems = document.querySelectorAll('.dropdown-menu a, .dropdown-menu button, .navbar-user dropdown-item, .dropdown-menu li');
    dropdownItems.forEach(function (item) {
      const text = String(item.textContent || item.innerText).trim().toLowerCase();
      if (
        text.indexOf('frappe support') !== -1 ||
        text.indexOf('keyboard shortcuts') !== -1 ||
        text.indexOf('about') !== -1 ||
        text.indexOf('support') !== -1 ||
        text.indexOf('toggle theme') !== -1 ||
        text.indexOf('switch theme') !== -1 ||
        text.indexOf('theme') !== -1
      ) {
        const parentLi = item.closest('li');
        if (parentLi) {
          if (parentLi.style.display !== 'none') {
            parentLi.style.setProperty('display', 'none', 'important');
          }
        } else {
          if (item.style.display !== 'none') {
            item.style.setProperty('display', 'none', 'important');
          }
        }
      }
    });
  }

  function runNileGovEnhancements() {
    enhanceNileGovSearch();
    enhanceNileGovLogin();
    enhanceNileGovDateFields();
    hideNileGovHelpMenu();
  }

  function boot() {
    scan();

    let timer = null;

    const observer = new MutationObserver(function () {
      clearTimeout(timer);
      timer = setTimeout(scan, 150);
    });

    if (document.body) {
      observer.observe(document.body, {
        childList: true,
        subtree: true
      });
    }

    let attempts = 0;
    const retry = setInterval(function () {
      attempts += 1;
      scan();

      if (attempts >= 40 || document.querySelectorAll(".nilegov-clickable-card").length >= 8) {
        clearInterval(retry);
      }
    }, 500);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
