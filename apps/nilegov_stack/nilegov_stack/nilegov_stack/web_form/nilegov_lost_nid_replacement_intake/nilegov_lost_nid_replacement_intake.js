// Client-side script for NileGov Lost National ID Replacement Intake Web Form
// Digi-Verse Uganda Limited
// Prototype simulation only. No live NIRA, UGHub or production payment system is connected.

frappe.ready(function() {
    // Inject Uganda-themed styling and multi-step layout transitions
    const css = `
        .nilegov-stepper-container {
            display: flex;
            justify-content: space-between;
            margin-bottom: 25px;
            background: #1A1A1A;
            border-radius: 8px;
            padding: 12px;
            border-left: 5px solid #C8102E;
            box-shadow: 0 4px 6px rgba(0,0,0,0.15);
        }
        .nilegov-step {
            flex: 1;
            text-align: center;
            font-size: 13px;
            font-weight: 700;
            color: #888888;
            padding: 6px;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .nilegov-step.active {
            color: #F5C000;
            border-bottom: 3px solid #F5C000;
        }
        .nilegov-step.completed {
            color: #28a745;
            border-bottom: 3px solid #28a745;
        }
        .nilegov-banner {
            background-color: #fff3cd;
            color: #856404;
            border: 1px solid #ffeeba;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 20px;
            font-size: 13px;
            border-left: 5px solid #ffc107;
        }
        .nilegov-consent-box {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 18px;
            margin-bottom: 15px;
            border-left: 5px solid #C8102E;
            font-size: 13px;
            line-height: 1.6;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
        }
        .nilegov-verify-btn {
            background-color: #F5C000;
            color: #1A1A1A;
            font-weight: 700;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            margin-top: 8px;
            cursor: pointer;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.5px;
            transition: all 0.2s ease;
        }
        .nilegov-verify-btn:hover {
            background-color: #e0b000;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .nilegov-verify-btn:disabled {
            background-color: #cccccc;
            color: #666666;
            cursor: not-allowed;
        }
        .nira-status-alert {
            font-size: 12px;
            line-height: 1.4;
        }
    `;
    const style = document.createElement('style');
    style.innerHTML = css;
    document.head.appendChild(style);
});

frappe.web_form.after_load = () => {
    // Standard disclaimer banner above web form
    frappe.web_form.set_intro(
        __('⚠ PROTOTYPE ONLY: This intake portal is a prototype. ' +
           'All validations, NIRA queries, and payment options are simulated. ' +
           'No live government databases or real payment switches will be contacted.'),
        'orange'
    );

    // Group fields into logical wizard steps
    const step1Fields = ['citizen_full_name', 'nin', 'phone', 'email'];
    const step2Fields = ['location', 'reason_for_request'];
    const step3Fields = ['consent_confirmed'];

    let currentStep = 1;

    // Build the visual stepper progress indicator
    const stepperHtml = `
        <div class="nilegov-stepper-container">
            <div class="nilegov-step step-1 active">1. Identity & Contact</div>
            <div class="nilegov-step step-2">2. Details & Location</div>
            <div class="nilegov-step step-3">3. Legal Consent</div>
        </div>
    `;

    const webForm = $('.web-form');
    if ($('.nilegov-stepper-container').length === 0) {
        webForm.prepend(stepperHtml);
    }

    // Injected legal consent card
    const consentWrapper = $('[data-fieldname="consent_confirmed"]');
    if ($('.nilegov-consent-box').length === 0) {
        const consentBoxHtml = `
            <div class="nilegov-consent-box">
                <h4 style="margin-top:0; font-weight:700; color:#1A1A1A; text-transform:uppercase; font-size:12px; letter-spacing:0.5px;">
                    Data Processing Consent Notice
                </h4>
                <p style="color:#555555; margin-bottom:10px;">
                    By submitting this request, you consent to the processing unit collecting and processing the following details:
                </p>
                <ul style="color:#555555; padding-left:20px; margin-bottom:10px;">
                    <li>Personal Details: Full Name, National ID Number (NIN).</li>
                    <li>Contact Parameters: Phone Number, Email Address.</li>
                    <li>Intake Parameters: Physical Location, Reason for Request.</li>
                </ul>
                <p style="color:#555555; margin-bottom:0;">
                    Your data is solely used to process this lost NID replacement request.
                    A secure timestamp will be recorded to register your consent.
                </p>
            </div>
        `;
        consentWrapper.before(consentBoxHtml);
    }

    // NIRA Simulated Verification Trigger
    const ninWrapper = $('[data-fieldname="nin"]');
    if ($('.nilegov-verify-btn').length === 0) {
        const verifyBtnHtml = `
            <button type="button" class="nilegov-verify-btn">Verify Identity (Simulated NIRA)</button>
            <div class="nira-status-alert" style="display:none; margin-top:10px;"></div>
        `;
        ninWrapper.append(verifyBtnHtml);

        $('.nilegov-verify-btn').on('click', function() {
            const ninVal = frappe.web_form.get_value('nin');
            const alertDiv = $('.nira-status-alert');

            if (!ninVal) {
                alertDiv.html('<span style="color:#d9534f; font-weight:bold;">Please enter a NIN to verify. (e.g. CM93019100ABC1J)</span>').show();
                return;
            }

            alertDiv.html('<span style="color:#856404; font-style:italic;">Querying NIRA registry simulation...</span>').show();

            setTimeout(() => {
                if (ninVal === 'CM93019100ABC1J') {
                    alertDiv.html(
                        '<div style="background:#d4edda; border:1px solid #c3e6cb; padding:10px; border-radius:4px; color:#155724; font-size:12px; margin-top:8px;">' +
                        '<strong>✓ IDENTITY VERIFIED (SIMULATED NIRA)</strong><br>' +
                        'Name: John Mugisha<br>' +
                        'DOB: 1993-01-01' +
                        '</div>'
                    );
                    frappe.web_form.set_value('citizen_full_name', 'John Mugisha');
                    frappe.web_form.set_df_property('citizen_full_name', 'read_only', 1);
                } else {
                    alertDiv.html(
                        '<div style="background:#f8d7da; border:1px solid #f5c6cb; padding:10px; border-radius:4px; color:#721c24; font-size:12px; margin-top:8px;">' +
                        '<strong>✗ Verification Failed</strong><br>' +
                        'The NIN is not found in the simulated NIRA database. Please use the demo NIN: CM93019100ABC1J.' +
                        '</div>'
                    );
                }
            }, 1000);
        });
    }

    // Hide standard save/submit actions
    const submitBtn = $('.btn-form-submit');
    submitBtn.hide();

    // Append custom Next/Back wizard buttons
    const navHtml = `
        <div class="nilegov-nav-buttons" style="display: flex; justify-content: space-between; margin-top: 20px; border-top: 1px solid #eaeaea; padding-top: 15px;">
            <button type="button" class="btn btn-default btn-back" style="display: none;">Back</button>
            <button type="button" class="btn btn-primary btn-next">Next Step</button>
        </div>
    `;
    if ($('.nilegov-nav-buttons').length === 0) {
        $('.form-actions').before(navHtml);
    }

    const updateFormSteps = () => {
        // Toggle step indicators
        $('.nilegov-step').removeClass('active completed');
        for (let i = 1; i <= 3; i++) {
            const stepEl = $(`.step-${i}`);
            if (i === currentStep) {
                stepEl.addClass('active');
            } else if (i < currentStep) {
                stepEl.addClass('completed');
            }
        }

        // Toggle field visibilities
        const toggleFields = (fields, show) => {
            fields.forEach(f => {
                frappe.web_form.set_df_property(f, 'hidden', show ? 0 : 1);
            });
        };

        toggleFields(step1Fields, currentStep === 1);
        toggleFields(step2Fields, currentStep === 2);
        toggleFields(step3Fields, currentStep === 3);

        // Adjust navigation actions
        if (currentStep === 1) {
            $('.btn-back').hide();
            $('.btn-next').show().text('Next Step');
            submitBtn.hide();
        } else if (currentStep === 2) {
            $('.btn-back').show();
            $('.btn-next').show().text('Next Step');
            submitBtn.hide();
        } else if (currentStep === 3) {
            $('.btn-back').show();
            $('.btn-next').hide();
            submitBtn.show();
        }
    };

    // Initialize Visibility
    updateFormSteps();

    // Button event listeners
    $('.btn-next').off('click').on('click', () => {
        if (currentStep === 1) {
            const name = frappe.web_form.get_value('citizen_full_name');
            const nin = frappe.web_form.get_value('nin');
            const phone = frappe.web_form.get_value('phone');
            if (!name || !nin || !phone) {
                frappe.msgprint(__('Please fill in all mandatory fields: Citizen Name, NIN, and Phone Number.'));
                return;
            }
        } else if (currentStep === 2) {
            const location = frappe.web_form.get_value('location');
            const reason = frappe.web_form.get_value('reason_for_request');
            if (!location || !reason) {
                frappe.msgprint(__('Please supply your location and the reason for this NID replacement request.'));
                return;
            }
        }

        if (currentStep < 3) {
            currentStep++;
            updateFormSteps();
        }
    });

    $('.btn-back').off('click').on('click', () => {
        if (currentStep > 1) {
            currentStep--;
            updateFormSteps();
        }
    });

    // Form submission validation check
    frappe.web_form.validate = () => {
        const consent = frappe.web_form.get_value('consent_confirmed');
        if (!consent) {
            frappe.msgprint(__('Submission Blocked: You must check the box to confirm privacy consent.'));
            return false;
        }
        return true;
    };
};
