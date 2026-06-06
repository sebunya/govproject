// Client-side script for NileGov Evidence Supplement Metadata Web Form
// Digi-Verse Uganda Limited
// Prototype simulation only. No live police, court or NIRA databases connected.

frappe.ready(function() {
    // Inject custom styling
    const css = `
        .nilegov-evidence-guide {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 18px;
            margin-bottom: 20px;
            border-left: 5px solid #C8102E;
            font-size: 13px;
            line-height: 1.6;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
        }
        .nilegov-constraint-tag {
            display: inline-block;
            background-color: #1A1A1A;
            color: #F5C000;
            font-weight: 700;
            font-size: 10px;
            padding: 3px 8px;
            border-radius: 50px;
            margin-top: 5px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
    `;
    const style = document.createElement('style');
    style.innerHTML = css;
    document.head.appendChild(style);
});

frappe.web_form.after_load = () => {
    // Standard disclaimer banner
    frappe.web_form.set_intro(
        __('⚠ PROTOTYPE ONLY: This evidence submission metadata sheet is a prototype. ' +
           'Supplied metadata and file pointers are for simulated review operations only. ' +
           'No live verification against external registers is initiated.'),
        'orange'
    );

    // Injected guide and file attachment advice
    const formFieldsWrapper = $('.web-form');
    if ($('.nilegov-evidence-guide').length === 0) {
        const guideHtml = `
            <div class="nilegov-evidence-guide">
                <h4 style="margin-top:0; font-weight:700; color:#1A1A1A; font-size:12px; text-transform:uppercase;">
                    Evidence Upload Guidelines
                </h4>
                <p style="color:#555555; margin-bottom:5px;">
                    Please upload high-resolution scans of the supporting documents (e.g. Police Report, Loss Gazette Notice, Identity documents).
                </p>
                <div class="nilegov-constraint-tag">File Requirements: PDF, PNG, JPG under 5MB</div>
            </div>
        `;
        formFieldsWrapper.prepend(guideHtml);
    }

    // Custom validation check
    frappe.web_form.validate = () => {
        const serviceRequest = frappe.web_form.get_value('service_request');
        const docType = frappe.web_form.get_value('document_type');
        const docTitle = frappe.web_form.get_value('document_title');

        if (!serviceRequest) {
            frappe.msgprint(__('You must specify a valid Service Request reference number.'));
            return false;
        }
        if (!docType || !docTitle) {
            frappe.msgprint(__('Please supply the Document Type and Document Title.'));
            return false;
        }
        return true;
    };
};
