/*
 * NileGov Visual Script Final — Visual Hardening and Stabilization
 * Digi-Verse Uganda Limited
 */

(function () {
  "use strict";

  console.info("NileGov final branding loaded");

  const ROUTES = {
    "Total Service Requests": "NileGov Service Request",
    "Service Requests": "NileGov Service Request",
    "Citizen Profiles": "NileGov Citizen Profile",
    "Payment Records": "NileGov Payment Record",
    "Evidence Documents": "NileGov Evidence Document",
    "SLA Events": "NileGov SLA Event",
    "Escalation Records": "NileGov Escalation Record",
    "Identity Verifications": "NileGov Simulated Identity Verification",
    "Integration Logs": "NileGov Integration Simulation Log"
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

  function enhanceNileGovKpiCards() {
    const wrappers = Array.from(document.querySelectorAll("div[number_card_name]"));
    wrappers.forEach(function (card) {
      const match = getRouteFromCard(card);
      if (!match) return;
      decorate(card, match);
    });
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
    const isLoginPage = 
      window.location.pathname.includes("/login") ||
      window.location.hash.includes("login") ||
      document.body.classList.contains("for-login") ||
      document.querySelector('.for-login, .login-content, .page-card, .login-container');

    if (!isLoginPage) return;

    const headings = Array.from(document.querySelectorAll('.page-card-head h4, .login-content h4, .for-login h4, .page-card h4, h1, h2, h3, h4'));
    let primaryHeadingSet = false;

    headings.forEach(function (heading) {
      const text = (heading.textContent || "").trim();
      if (
        (text.toLowerCase().includes("frappe") || text.toLowerCase().includes("login to") || text.toLowerCase() === "login") &&
        heading.getAttribute("data-nilegov-login-duplicate") !== "1"
      ) {
        if (!primaryHeadingSet) {
          heading.textContent = "Login to NileGov";
          heading.setAttribute("data-nilegov-login-heading", "primary");
          heading.style.setProperty("display", "", "important");
          primaryHeadingSet = true;
          console.info("NileGov login heading normalized");
        } else if (heading.getAttribute("data-nilegov-login-heading") !== "primary") {
          heading.setAttribute("data-nilegov-login-duplicate", "1");
          heading.style.setProperty("display", "none", "important");
        }
      }
    });

    if (document.body.innerText.includes("Login to Frappe")) {
      if (!window.nilegovLoginRetryCount) {
        window.nilegovLoginRetryCount = 0;
      }
      if (window.nilegovLoginRetryCount < 3) {
        window.nilegovLoginRetryCount++;
        const delays = [250, 750, 1500];
        setTimeout(enhanceNileGovLogin, delays[window.nilegovLoginRetryCount - 1]);
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
        trigger.setAttribute('aria-label', 'Open calendar');
        svgIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2A3138" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>`;
      } else {
        trigger.setAttribute('aria-label', 'Open date and time picker');
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

  function hideNileGovHelpAndFrappeBranding() {
    // Clean up dropdowns to hide only direct vendor support entries, keeping useful ERP navigation
    const dropdownItems = document.querySelectorAll('.dropdown-menu a, .dropdown-menu button, .navbar-user dropdown-item, .dropdown-menu li');
    dropdownItems.forEach(function (item) {
      const text = String(item.textContent || item.innerText).trim().toLowerCase();
      const href = String(item.getAttribute('href') || '').toLowerCase();
      
      // Hide only direct Frappe Support or related framework-facing entries, NOT general ERP actions
      const shouldHide = 
        text === 'frappe support' || 
        text.includes('frappe support') ||
        (text === 'support' && (href.includes('frappe') || href.includes('github.com/frappe'))) ||
        (text.includes('documentation') && (href.includes('frappe.io') || href.includes('erpnext.com'))) ||
        (text.includes('user forum') && href.includes('discuss.erpnext.com')) ||
        (text.includes('report an issue') && href.includes('github.com/frappe')) ||
        text === 'about frappe';

      if (shouldHide) {
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

  function cleanNileGovProfileMenu() {
    // Hide only the three specific Desk profile menu items: Session Defaults, Toggle Full Width, Toggle Theme
    const dropdownItems = document.querySelectorAll('.dropdown-menu a, .dropdown-menu button, .dropdown-menu .dropdown-item, .dropdown-menu li');
    dropdownItems.forEach(function (item) {
      const text = String(item.textContent || item.innerText).trim().toLowerCase();
      const isTarget = 
        text === 'session defaults' || 
        text === 'toggle full width' || 
        text === 'toggle theme';

      if (isTarget) {
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

  function normalizeNileGovFooterBranding() {
    // Scan all potential text containing elements for vendor credits
    const footerTargets = document.querySelectorAll('.page-footer, .web-footer, footer, .login-footer, .page-card-actions, .text-muted, a, p, span, small');
    footerTargets.forEach(function (el) {
      if (el.children.length === 0 || (el.tagName === 'A' && el.textContent.includes("Frappe"))) {
        const text = el.textContent || "";
        const hasVendorCredit = 
          text.includes("Built on Frappe") ||
          text.includes("Built by Frappe") ||
          text.includes("Powered by Frappe") ||
          text.includes("Built with Frappe");

        if (hasVendorCredit && el.dataset.nilegovFooterNormalized !== "1") {
          el.dataset.nilegovFooterNormalized = "1";
          el.textContent = "Built by Digi-Verse Uganda Limited";
          if (el.tagName === 'A') {
            el.href = "https://digiverse.co.ug";
          }
        }
      } else {
        const html = el.innerHTML || "";
        const hasVendorCreditHtml = 
          html.includes("Built on Frappe") ||
          html.includes("Built by Frappe") ||
          html.includes("Powered by Frappe") ||
          html.includes("Built with Frappe");

        if (hasVendorCreditHtml && el.dataset.nilegovFooterNormalized !== "1" && !el.querySelector('.page-footer, .web-footer, footer')) {
          el.dataset.nilegovFooterNormalized = "1";
          el.innerHTML = html
            .replace(/Built on Frappe/g, "Built by Digi-Verse Uganda Limited")
            .replace(/Built by Frappe/g, "Built by Digi-Verse Uganda Limited")
            .replace(/Powered by Frappe/g, "Built by Digi-Verse Uganda Limited")
            .replace(/Built with Frappe/g, "Built by Digi-Verse Uganda Limited");
        }
      }
    });
  }

  function runNileGovEnhancements() {
    enhanceNileGovKpiCards();
    enhanceNileGovSearch();
    enhanceNileGovLogin();
    enhanceNileGovDateFields();
    hideNileGovHelpAndFrappeBranding();
    cleanNileGovProfileMenu();
    normalizeNileGovFooterBranding();
  }

  function boot() {
    runNileGovEnhancements();

    let timer = null;
    const observer = new MutationObserver(function () {
      clearTimeout(timer);
      timer = setTimeout(runNileGovEnhancements, 150);
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
      runNileGovEnhancements();

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
