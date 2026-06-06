// Client-side script for NileGov Citizen Consent Capture Web Form
// Digi-Verse Uganda Limited
// Prototype simulation only. No live Government registry or MDA systems connected.

frappe.ready(function() {
    // Inject Uganda flag colors and card styling
    const css = `
        .nilegov-consent-disclaimer {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 18px;
            margin-bottom: 20px;
            border-left: 5px solid #F5C000;
            font-size: 13px;
            line-height: 1.6;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
        }
        .nilegov-badge-ug {
            display: inline-block;
            background-color: #C8102E;
            color: #ffffff;
            font-weight: 700;
            font-size: 10px;
            padding: 3px 8px;
            border-radius: 50px;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
    `;
    const style = document.createElement('style');
    style.innerHTML = css;
    document.head.appendChild(style);
});

frappe.web_form.after_load = () => {
    // Standard warning banner
    frappe.web_form.set_intro(
        __('⚠ PROTOTYPE ONLY: This consent capture interface is a prototype. ' +
           'Registered consent records are for simulated demo purposes only. ' +
           'No live registry connections are initiated.'),
        'orange'
    );

    // Injected legal consent context box
    const formFieldsWrapper = $('.web-form');
    if ($('.nilegov-consent-disclaimer').length === 0) {
        const disclaimerHtml = `
            <div class="nilegov-consent-disclaimer">
                <span class="nilegov-badge-ug">Data Privacy Notice</span>
                <h4 style="margin-top:0; font-weight:700; color:#1A1A1A; font-size:12px; text-transform:uppercase;">
                    Data Processing Consent Record
                </h4>
                <p style="color:#555555; margin-bottom:0;">
                    Personal data processing requires explicit consent from the data subject. 
                    This record documents consent for processing identity profiles, mobile numbers, locations, 
                    and attachments relative to the requested public services.
                </p>
            </div>
        `;
        formFieldsWrapper.prepend(disclaimerHtml);
    }

    // Set default consent purpose if empty
    if (!frappe.web_form.get_value('consent_purpose')) {
        frappe.web_form.set_value('consent_purpose', 'Identity Verification and SLA Tracking');
    }
    
    // Set default status to Opt-In
    if (!frappe.web_form.get_value('consent_status')) {
        frappe.web_form.set_value('consent_status', 'Opt-In');
    }

    // Custom validation check
    frappe.web_form.validate = () => {
        const profile = frappe.web_form.get_value('citizen_profile');
        if (!profile) {
            frappe.msgprint(__('You must specify a valid Citizen Profile to bind this consent record.'));
            return false;
        }
        return true;
    };
};
