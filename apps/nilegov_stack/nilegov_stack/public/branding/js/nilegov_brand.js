/*
 * NileGov Visual Script — KPI Action Tiles Navigation
 * Digi-Verse Uganda Limited
 * Prototype branding simulation.
 */

(function() {
  'use strict';

  // Prevent execution outside of browser/Frappe Desk context
  if (typeof window === 'undefined' || !window.frappe) {
    return;
  }

  // Exact mapping of title text patterns to their DocType names
  const DOCTYPE_MAP = {
    "TOTAL SERVICE REQUESTS": "NileGov Service Request",
    "TOTAL REQUESTS": "NileGov Service Request",
    "OPEN REQUESTS": "NileGov Service Request",
    "CITIZEN PROFILES": "NileGov Citizen Profile",
    "PAYMENT RECORDS": "NileGov Payment Record",
    "PENDING PAYMENTS": "NileGov Payment Record",
    "VERIFIED PAYMENTS": "NileGov Payment Record",
    "EVIDENCE DOCUMENTS": "NileGov Evidence Document",
    "EVIDENCE INCOMPLETE": "NileGov Evidence Document",
    "SLA EVENTS": "NileGov SLA Event",
    "OVERDUE SLA": "NileGov SLA Event",
    "OVERDUE SLA CASES": "NileGov SLA Event",
    "ESCALATION RECORDS": "NileGov Escalation Record",
    "ESCALATED CASES": "NileGov Escalation Record",
    "IDENTITY VERIFICATIONS": "NileGov Simulated Identity Verification",
    "INTEGRATION LOGS": "NileGov Integration Simulation Log"
  };

  /**
   * Identifies the target DocType based on normalized title string
   */
  function getDoctypeForTitle(titleText) {
    const normalized = titleText.trim().toUpperCase();
    for (const key in DOCTYPE_MAP) {
      if (normalized.indexOf(key) !== -1) {
        return DOCTYPE_MAP[key];
      }
    }
    return null;
  }

  /**
   * Scans the workspace DOM and decorates number cards to be clickable
   */
  function decorateNumberCards() {
    // Select number cards or general widget boxes containing KPI values
    const cards = document.querySelectorAll('.widget-box, .number-card, .widget-card');
    
    cards.forEach(card => {
      // Avoid processing same card multiple times (Idempotence)
      if (card.classList.contains('nilegov-clickable-card')) {
        return;
      }

      // Detect card label/title element
      const labelEl = card.querySelector('.widget-title, .widget-label, .card-label, .number-card-title, h4');
      if (!labelEl) {
        return;
      }

      const titleText = labelEl.textContent || '';
      const doctypeName = getDoctypeForTitle(titleText);
      if (!doctypeName) {
        return;
      }

      // Apply clickable role, styling attributes, and accessibility descriptors
      card.classList.add('nilegov-clickable-card');
      card.setAttribute('role', 'link');
      card.setAttribute('tabindex', '0');
      card.setAttribute('aria-label', `Open ${doctypeName}`);
      card.setAttribute('title', `Open ${doctypeName}`);

      // Handle Mouse Click
      card.addEventListener('click', function(event) {
        // Prevent hijacking clicks on buttons, edit menus, dropdowns, ellipsis controls
        if (event.target.closest('.widget-control') || 
            event.target.closest('.dropdown') || 
            event.target.closest('a') || 
            event.target.closest('button') ||
            event.target.closest('.ellipsis')) {
          return;
        }
        
        event.stopPropagation();
        frappe.set_route("List", doctypeName);
      });

      // Handle Keyboard Navigation (Enter/Space)
      card.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' || event.key === ' ') {
          if (event.target.closest('.widget-control') || 
              event.target.closest('.dropdown') || 
              event.target.closest('a') || 
              event.target.closest('button') ||
              event.target.closest('.ellipsis')) {
            return;
          }
          
          event.preventDefault();
          event.stopPropagation();
          frappe.set_route("List", doctypeName);
        }
      });
    });
  }

  // Use a debounced MutationObserver to watch DOM updates defensively
  let debounceTimeout = null;
  const domObserver = new MutationObserver(() => {
    if (debounceTimeout) {
      clearTimeout(debounceTimeout);
    }
    debounceTimeout = setTimeout(() => {
      decorateNumberCards();
    }, 150);
  });

  // Start observing when document body becomes available
  if (document.body) {
    domObserver.observe(document.body, { childList: true, subtree: true });
    decorateNumberCards();
  } else {
    document.addEventListener('DOMContentLoaded', () => {
      domObserver.observe(document.body, { childList: true, subtree: true });
      decorateNumberCards();
    });
  }
})();
