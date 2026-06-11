frappe.pages['nilegov-command-centre-v3'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Executive Command Centre V3',
        single_column: true
    });

    console.log('[NileGov Command Centre V3] on_page_load fired');

    if (!page || !page.main) {
        console.error('[NileGov Command Centre V3] page.main missing');
        wrapper.innerHTML = '<div style="padding:24px"><h3>Command Centre Render Error</h3><p>page.main missing.</p></div>';
        return;
    }

    var html = '' +
        '<div id="nilegov-command-centre-v3-root" style="padding: 32px; background: #f3f4f6; min-height: 100vh; font-family: \'Inter\', -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, Helvetica, Arial, sans-serif;">' +

            '<div class="d-flex justify-content-between align-items-center mb-4">' +
                '<div>' +
                    '<h3 class="font-weight-bold mb-1" style="color: #111827; letter-spacing: -0.5px;">NileGov Case Operations Command Centre</h3>' +
                    '<div style="font-size: 13px; color: #6b7280; font-weight: 500;">' +
                        'Build: recovery-2026-06-11-v3-layer12-demo-polish-r1' +
                    '</div>' +
                '</div>' +
            '</div>' +

            '<!-- Filter Warning -->' +
            '<div id="filter-warning" style="display:none; color:#92400e; background:#fef3c7; border:1px solid #f59e0b; border-radius:8px; padding:12px 16px; margin-bottom:20px; font-weight: 500; font-size: 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">' +
                '<i class="fa fa-exclamation-triangle mr-2"></i>Filter options could not be loaded. Using default options. KPI data is still available.' +
            '</div>' +

            '<!-- Filter Bar -->' +
            '<div class="row filter-bar mb-5" style="background:#ffffff; padding:24px; border-radius:12px; border:1px solid #e5e7eb; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);">' +
                '<div class="col-md-2 col-sm-4 mb-3 mb-md-0">' +
                    '<div class="form-group mb-0">' +
                        '<label class="text-muted small font-weight-bold" style="letter-spacing: 0.5px; text-transform: uppercase;">From Date</label>' +
                        '<input type="date" id="filter-from-date" class="form-control" style="border-radius: 6px; border: 1px solid #d1d5db; box-shadow: inset 0 1px 2px rgba(0,0,0,0.02);">' +
                    '</div>' +
                '</div>' +
                '<div class="col-md-2 col-sm-4 mb-3 mb-md-0">' +
                    '<div class="form-group mb-0">' +
                        '<label class="text-muted small font-weight-bold" style="letter-spacing: 0.5px; text-transform: uppercase;">To Date</label>' +
                        '<input type="date" id="filter-to-date" class="form-control" style="border-radius: 6px; border: 1px solid #d1d5db; box-shadow: inset 0 1px 2px rgba(0,0,0,0.02);">' +
                    '</div>' +
                '</div>' +
                '<div class="col-md-2 col-sm-4 mb-3 mb-md-0">' +
                    '<div class="form-group mb-0">' +
                        '<label class="text-muted small font-weight-bold" style="letter-spacing: 0.5px; text-transform: uppercase;">Service</label>' +
                        '<select id="filter-service" class="form-control" style="border-radius: 6px; border: 1px solid #d1d5db; box-shadow: inset 0 1px 2px rgba(0,0,0,0.02);"><option value="">All Services</option></select>' +
                    '</div>' +
                '</div>' +
                '<div class="col-md-2 col-sm-4 mb-3 mb-md-0">' +
                    '<div class="form-group mb-0">' +
                        '<label class="text-muted small font-weight-bold" style="letter-spacing: 0.5px; text-transform: uppercase;">Status</label>' +
                        '<select id="filter-status" class="form-control" style="border-radius: 6px; border: 1px solid #d1d5db; box-shadow: inset 0 1px 2px rgba(0,0,0,0.02);"><option value="">All Statuses</option></select>' +
                    '</div>' +
                '</div>' +
                '<div class="col-md-2 col-sm-4 mb-3 mb-md-0">' +
                    '<div class="form-group mb-0">' +
                        '<label class="text-muted small font-weight-bold" style="letter-spacing: 0.5px; text-transform: uppercase;">Location</label>' +
                        '<select id="filter-location" class="form-control" style="border-radius: 6px; border: 1px solid #d1d5db; box-shadow: inset 0 1px 2px rgba(0,0,0,0.02);"><option value="">All Locations</option></select>' +
                    '</div>' +
                '</div>' +
                '<div class="col-md-2 col-sm-4 d-flex align-items-end mt-2 mt-md-0">' +
                    '<button id="btn-refresh" class="btn btn-primary w-100 font-weight-bold" style="border-radius: 6px; padding: 10px 16px; background-color: #2563eb; border-color: #2563eb; box-shadow: 0 1px 2px rgba(0,0,0,0.05); transition: all 0.2s;">Refresh Data</button>' +
                '</div>' +
            '</div>' +

            '<!-- Overview KPI Section -->' +
            '<h5 class="mb-4 font-weight-bold" style="color: #1f2937; letter-spacing: -0.3px;">Overview</h5>' +
            '<div id="kpi-error-state" style="display:none; color:#ef4444; margin-bottom:20px; padding:12px 16px; background:#fee2e2; border-radius:8px; font-weight: 500; font-size: 14px; border: 1px solid #fca5a5;">' +
                '<i class="fa fa-exclamation-circle mr-2"></i>Unable to load Overview KPIs. Please try refreshing.' +
            '</div>' +
            '<div class="row mb-5">' +
                '<div class="col-xl-3 col-lg-4 col-md-6 mb-4">' +
                    '<div class="kpi-card" style="background:#ffffff; padding:24px; border-radius:12px; border:1px solid #e5e7eb; border-top:4px solid #2563eb; box-shadow: 0 1px 3px rgba(0,0,0,0.05); transition: transform 0.2s, box-shadow 0.2s;">' +
                        '<div class="text-muted small text-uppercase font-weight-bold" style="letter-spacing: 0.5px;">Total Requests</div>' +
                        '<h2 id="kpi-total" class="mt-2 mb-0 font-weight-bold" style="color: #111827;">-</h2>' +
                    '</div>' +
                '</div>' +
                '<div class="col-xl-3 col-lg-4 col-md-6 mb-4">' +
                    '<div class="kpi-card" style="background:#ffffff; padding:24px; border-radius:12px; border:1px solid #e5e7eb; border-top:4px solid #f59e0b; box-shadow: 0 1px 3px rgba(0,0,0,0.05); transition: transform 0.2s, box-shadow 0.2s;">' +
                        '<div class="text-muted small text-uppercase font-weight-bold" style="letter-spacing: 0.5px;">Open Requests</div>' +
                        '<h2 id="kpi-active-backlog" class="mt-2 mb-0 font-weight-bold" style="color: #111827;">-</h2>' +
                    '</div>' +
                '</div>' +
                '<div class="col-xl-3 col-lg-4 col-md-6 mb-4">' +
                    '<div class="kpi-card" style="background:#ffffff; padding:24px; border-radius:12px; border:1px solid #e5e7eb; border-top:4px solid #10b981; box-shadow: 0 1px 3px rgba(0,0,0,0.05); transition: transform 0.2s, box-shadow 0.2s;">' +
                        '<div class="text-muted small text-uppercase font-weight-bold" style="letter-spacing: 0.5px;">Closed Requests</div>' +
                        '<h2 id="kpi-completed" class="mt-2 mb-0 font-weight-bold" style="color: #111827;">-</h2>' +
                    '</div>' +
                '</div>' +
                '<div class="col-xl-3 col-lg-4 col-md-6 mb-4">' +
                    '<div class="kpi-card" style="background:#ffffff; padding:24px; border-radius:12px; border:1px solid #e5e7eb; border-top:4px solid #ef4444; box-shadow: 0 1px 3px rgba(0,0,0,0.05); transition: transform 0.2s, box-shadow 0.2s;">' +
                        '<div class="text-muted small text-uppercase font-weight-bold" style="letter-spacing: 0.5px;">Escalated Cases</div>' +
                        '<h2 id="kpi-escalated" class="mt-2 mb-0 font-weight-bold" style="color: #111827;">-</h2>' +
                    '</div>' +
                '</div>' +
                '<div class="col-xl-3 col-lg-4 col-md-6 mb-4">' +
                    '<div class="kpi-card" style="background:#ffffff; padding:24px; border-radius:12px; border:1px solid #e5e7eb; border-top:4px solid #8b5cf6; box-shadow: 0 1px 3px rgba(0,0,0,0.05); transition: transform 0.2s, box-shadow 0.2s;">' +
                        '<div class="text-muted small text-uppercase font-weight-bold" style="letter-spacing: 0.5px;">SLA Compliance</div>' +
                        '<h2 id="kpi-sla-compliance" class="mt-2 mb-0 font-weight-bold" style="color: #111827;">-</h2>' +
                    '</div>' +
                '</div>' +
                '<div class="col-xl-3 col-lg-4 col-md-6 mb-4">' +
                    '<div class="kpi-card" style="background:#ffffff; padding:24px; border-radius:12px; border:1px solid #e5e7eb; border-top:4px solid #ec4899; box-shadow: 0 1px 3px rgba(0,0,0,0.05); transition: transform 0.2s, box-shadow 0.2s;">' +
                        '<div class="text-muted small text-uppercase font-weight-bold" style="letter-spacing: 0.5px;">SLA Breaches</div>' +
                        '<h2 id="kpi-sla-breaches" class="mt-2 mb-0 font-weight-bold" style="color: #111827;">-</h2>' +
                    '</div>' +
                '</div>' +
                '<div class="col-xl-3 col-lg-4 col-md-6 mb-4">' +
                    '<div class="kpi-card" style="background:#ffffff; padding:24px; border-radius:12px; border:1px solid #e5e7eb; border-top:4px solid #14b8a6; box-shadow: 0 1px 3px rgba(0,0,0,0.05); transition: transform 0.2s, box-shadow 0.2s;">' +
                        '<div class="text-muted small text-uppercase font-weight-bold" style="letter-spacing: 0.5px;">Payments Collected</div>' +
                        '<h2 id="kpi-payments-collected" class="mt-2 mb-0 font-weight-bold" style="color: #111827;">-</h2>' +
                    '</div>' +
                '</div>' +
                '<div class="col-xl-3 col-lg-4 col-md-6 mb-4">' +
                    '<div class="kpi-card" style="background:#ffffff; padding:24px; border-radius:12px; border:1px solid #e5e7eb; border-top:4px solid #f97316; box-shadow: 0 1px 3px rgba(0,0,0,0.05); transition: transform 0.2s, box-shadow 0.2s;">' +
                        '<div class="text-muted small text-uppercase font-weight-bold" style="letter-spacing: 0.5px;">Pending Payments</div>' +
                        '<h2 id="kpi-payments-pending" class="mt-2 mb-0 font-weight-bold" style="color: #111827;">-</h2>' +
                    '</div>' +
                '</div>' +
            '</div>' +

            '<!-- Service Delivery Analytics (Layer 4) -->' +
            '<h5 class="mb-4 font-weight-bold" style="color: #1f2937; letter-spacing: -0.3px;">Service Delivery Analytics</h5>' +
            '<div id="service-delivery-error" style="display:none; color:#92400e; background:#fef3c7; border:1px solid #f59e0b; border-radius:8px; padding:12px 16px; margin-bottom:20px; font-weight: 500; font-size: 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">' +
                '<i class="fa fa-info-circle mr-2"></i>Service Delivery Analytics could not be loaded. KPI cards above are not affected.' +
            '</div>' +
            '<div class="row mb-4">' +
                '<div class="col-lg-6 mb-4">' +
                    '<div style="background:#ffffff; padding:24px; border-radius:12px; border:1px solid #e5e7eb; min-height:300px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">' +
                        '<h6 class="font-weight-bold mb-4" style="color: #374151;">Service Demand Trend</h6>' +
                        '<div id="trend-container"></div>' +
                    '</div>' +
                '</div>' +
                '<div class="col-lg-6 mb-4">' +
                    '<div style="background:#ffffff; padding:24px; border-radius:12px; border:1px solid #e5e7eb; min-height:300px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">' +
                        '<h6 class="font-weight-bold mb-4" style="color: #374151;">Requests by Type</h6>' +
                        '<div id="by-type-container"></div>' +
                    '</div>' +
                '</div>' +
            '</div>' +
            '<div class="row mb-5">' +
                '<div class="col-lg-6 mb-4">' +
                    '<div style="background:#ffffff; padding:24px; border-radius:12px; border:1px solid #e5e7eb; min-height:300px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">' +
                        '<h6 class="font-weight-bold mb-4" style="color: #374151;">Requests by Status</h6>' +
                        '<div id="by-status-container"></div>' +
                    '</div>' +
                '</div>' +
                '<div class="col-lg-6 mb-4">' +
                    '<div style="background:#ffffff; padding:24px; border-radius:12px; border:1px solid #e5e7eb; min-height:300px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">' +
                        '<h6 class="font-weight-bold mb-4" style="color: #374151;">Oldest Open Backlog</h6>' +
                        '<div id="backlog-container"></div>' +
                    '</div>' +
                '</div>' +
            '</div>' +

            '<!-- SLA / Risk Analytics (Layer 5) -->' +
            '<h5 class="mb-4 font-weight-bold" style="color: #1f2937; letter-spacing: -0.3px;">SLA &amp; Risk Analytics</h5>' +
            '<div id="sla-risk-error" style="display:none; color:#92400e; background:#fef3c7; border:1px solid #f59e0b; border-radius:8px; padding:12px 16px; margin-bottom:20px; font-weight: 500; font-size: 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">' +
                '<i class="fa fa-info-circle mr-2"></i>SLA &amp; Risk Analytics could not be loaded. All other sections above are not affected.' +
            '</div>' +
            '<div class="row mb-4">' +
                '<div class="col-lg-6 mb-4">' +
                    '<div style="background:#ffffff; padding:24px; border-radius:12px; border:1px solid #e5e7eb; min-height:300px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">' +
                        '<h6 class="font-weight-bold mb-4" style="color: #374151;">SLA Breaches by Service</h6>' +
                        '<div id="sla-breaches-container"></div>' +
                    '</div>' +
                '</div>' +
                '<div class="col-lg-6 mb-4">' +
                    '<div style="background:#ffffff; padding:24px; border-radius:12px; border:1px solid #e5e7eb; min-height:300px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">' +
                        '<h6 class="font-weight-bold mb-4" style="color: #374151;">Escalations by Status</h6>' +
                        '<div id="escalations-status-container"></div>' +
                    '</div>' +
                '</div>' +
            '</div>' +
            '<div class="row mb-5">' +
                '<div class="col-12">' +
                    '<div style="background:#ffffff; padding:24px; border-radius:12px; border:1px solid #e5e7eb; min-height:200px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">' +
                        '<h6 class="font-weight-bold mb-4" style="color: #374151;">Oldest Unresolved Escalations</h6>' +
                        '<div id="oldest-escalations-container"></div>' +
                    '</div>' +
                '</div>' +
            '</div>' +

            '<!-- Payments & Reconciliation (Layer 6) -->' +
            '<h5 class="mb-4 font-weight-bold" style="color: #1f2937; letter-spacing: -0.3px;">Payments &amp; Reconciliation</h5>' +
            '<div id="payments-error" style="display:none; color:#92400e; background:#fef3c7; border:1px solid #f59e0b; border-radius:8px; padding:12px 16px; margin-bottom:20px; font-weight: 500; font-size: 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">' +
                '<i class="fa fa-info-circle mr-2"></i>Payments &amp; Reconciliation Analytics could not be loaded. All other sections above are not affected.' +
            '</div>' +
            '<div class="row mb-5">' +
                '<div class="col-lg-4 mb-4">' +
                    '<div style="background:#ffffff; padding:24px; border-radius:12px; border:1px solid #e5e7eb; min-height:300px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">' +
                        '<h6 class="font-weight-bold mb-4" style="color: #374151;">Payment Status Summary</h6>' +
                        '<div id="payment-status-container"></div>' +
                    '</div>' +
                '</div>' +
                '<div class="col-lg-4 mb-4">' +
                    '<div style="background:#ffffff; padding:24px; border-radius:12px; border:1px solid #e5e7eb; min-height:300px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">' +
                        '<h6 class="font-weight-bold mb-4" style="color: #374151;">Failed Payments</h6>' +
                        '<div id="failed-payments-container"></div>' +
                    '</div>' +
                '</div>' +
                '<div class="col-lg-4 mb-4">' +
                    '<div style="background:#ffffff; padding:24px; border-radius:12px; border:1px solid #e5e7eb; min-height:300px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">' +
                        '<h6 class="font-weight-bold mb-4" style="color: #374151;">Pending Payments</h6>' +
                        '<div id="pending-payments-container"></div>' +
                    '</div>' +
                '</div>' +
            '</div>' +

            '<!-- Officer Workload Analytics (Layer 7) -->' +
            '<h5 class="mb-4 font-weight-bold" style="color: #1f2937; letter-spacing: -0.3px;">Officer Workload Analytics</h5>' +
            '<div id="officer-workload-error" style="display:none; color:#92400e; background:#fef3c7; border:1px solid #f59e0b; border-radius:8px; padding:12px 16px; margin-bottom:20px; font-weight: 500; font-size: 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">' +
                '<i class="fa fa-info-circle mr-2"></i>Officer Workload Analytics could not be loaded. All other sections above are not affected.' +
            '</div>' +
            '<div class="row mb-5">' +
                '<div class="col-12">' +
                    '<div style="background:#ffffff; padding:24px; border-radius:12px; border:1px solid #e5e7eb; min-height:300px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">' +
                        '<h6 class="font-weight-bold mb-4" style="color: #374151;">Officer Workload Summary</h6>' +
                        '<div id="officer-workload-container"></div>' +
                    '</div>' +
                '</div>' +
            '</div>' +

            '<!-- Location Performance (Layer 8) -->' +
            '<h5 class="mb-4 font-weight-bold" style="color: #1f2937; letter-spacing: -0.3px;">Location Performance</h5>' +
            '<div class="row mb-5">' +
                '<div class="col-12">' +
                    '<div style="background:#ffffff; padding:24px; border-radius:12px; border:1px solid #e5e7eb; min-height:300px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">' +
                        '<h6 class="font-weight-bold mb-4" style="color: #374151;">Location Analytics</h6>' +
                        '<div id="location-performance-error" style="display:none; color:#ef4444; background:#fee2e2; border:1px solid #fca5a5; border-radius:8px; padding:12px 16px; margin-bottom:20px; font-weight: 500; font-size: 14px;">' +
                            '<i class="fa fa-exclamation-circle mr-2"></i>Failed to load Location Performance data. Please try again.' +
                        '</div>' +
                        '<div id="location-performance-container"></div>' +
                    '</div>' +
                '</div>' +
            '</div>' +

            '<!-- Policy & M&E Analytics (Layer 9) -->' +
            '<h5 class="mb-4 font-weight-bold" style="color: #1f2937; letter-spacing: -0.3px;">Policy &amp; M&amp;E Summary</h5>' +
            '<div class="row mb-5">' +
                '<div class="col-12">' +
                    '<div style="background:#ffffff; padding:24px; border-radius:12px; border:1px solid #e5e7eb; min-height:200px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">' +
                        '<h6 class="font-weight-bold mb-4" style="color: #374151;">Policy &amp; M&amp;E Analytics</h6>' +
                        '<div id="policy-me-error" style="display:none; color:#ef4444; background:#fee2e2; border:1px solid #fca5a5; border-radius:8px; padding:12px 16px; margin-bottom:20px; font-weight: 500; font-size: 14px;">' +
                            '<i class="fa fa-exclamation-circle mr-2"></i>Failed to load Policy &amp; M&amp;E data. Please try again.' +
                        '</div>' +
                        '<div id="policy-me-container"></div>' +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>';

    $(page.main).empty().append(html);

    // ── First Paint Checks ───────────────────────────────────────────────────

    if (!$('#filter-service').length) {
        console.error('[NileGov Command Centre V3] filter-service select missing after first paint');
    }

    // ── Independent section hydrations (non-blocking) ─────────────────────────
    hydrate_filters();
    refresh_overview_kpis();
    refresh_service_delivery();
    refresh_sla_risk();
    refresh_payments_reconciliation();
    refresh_officer_workload();
    refresh_location_performance();
    refresh_policy_me();

    // ── Filter hydration ──────────────────────────────────────────────────────

    function debug_json(value) {
        try {
            return JSON.stringify(value);
        } catch (e) {
            return String(value);
        }
    }

    function resolve_message(response) {
        if (!response) {
            return {};
        }

        var current = response;
        while (current && current.message !== undefined) {
            if (typeof current.message === 'object' && !Array.isArray(current.message)) {
                current = current.message;
            } else if (typeof current.message === 'string') {
                try {
                    var parsed = JSON.parse(current.message);
                    if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
                        current = parsed;
                    } else {
                        break;
                    }
                } catch (e) {
                    break;
                }
            } else {
                break;
            }
        }

        if (typeof current === 'object' && !Array.isArray(current)) {
            return current;
        }

        return {};
    }



    function force_populate_service_select(services) {
        var service_select = $('#filter-service');
        var safe_services = Array.isArray(services) ? services : [];

        if (!service_select.length) {
            return {
                service_select_count: 0,
                service_option_count: 0
            };
        }

        var option_count = service_select.find('option').length;

        if (safe_services.length > 0 && option_count <= 1) {
            console.warn('[NileGov Command Centre V3] service select fallback population triggered');

            service_select.empty();
            service_select.append($('<option>', {
                value: '',
                text: 'All Services'
            }));

            safe_services
                .map(normalize_option)
                .filter(Boolean)
                .forEach(function(option) {
                    service_select.append($('<option>', {
                        value: option.value,
                        text: option.label
                    }));
                });

            option_count = service_select.find('option').length;
        }
        return {
            service_select_count: service_select.length,
            service_option_count: option_count
        };
    }

    function hydrate_filters() {
        console.log('[NileGov Command Centre V3] filter hydration started');

        frappe.call({
            method: 'nilegov_stack.interfaces.frappe.api.insights.get_command_centre_filters',
            callback: function(r) {
                var filters = resolve_message(r);
                var services = Array.isArray(filters.services) ? filters.services : [];
                var statuses = Array.isArray(filters.statuses) ? filters.statuses : [];
                var locations = Array.isArray(filters.locations) ? filters.locations : [];

                populate_select('#filter-service', 'All Services', services);
                populate_select('#filter-status', 'All Statuses', statuses);
                populate_select('#filter-location', 'All Locations', locations);

                force_populate_service_select(services);

                console.log('[NileGov Command Centre V3] filter hydration completed');
                wire_filter_events();
            },
            error: function(err) {
                console.error('[NileGov Command Centre V3] filter hydration failed', err);
                show_filter_warning();
                wire_filter_events();
            }
        });
    }

    function normalize_option(item) {
        if (typeof item === 'string') {
            return {
                value: item,
                label: item
            };
        }

        if (item && typeof item === 'object') {
            var value =
                item.value ||
                item.name ||
                item.service_type ||
                item.service_code ||
                item.location ||
                item.status;

            var label =
                item.label ||
                item.service_name ||
                item.value ||
                item.name ||
                item.service_type ||
                item.service_code ||
                item.location ||
                item.status;

            if (!value) {
                return null;
            }

            return {
                value: String(value),
                label: String(label || value)
            };
        }

        return null;
    }

    function populate_select(selector, fallback_label, items) {
        var select = $(selector);

        if (!select.length) {
            console.warn('[NileGov Command Centre V3] missing select', selector);
            return 0;
        }

        var safe_items = Array.isArray(items) ? items : [];

        select.empty();
        select.append($('<option>', {
            value: '',
            text: fallback_label
        }));

        safe_items
            .map(normalize_option)
            .filter(Boolean)
            .forEach(function(option) {
                select.append($('<option>', {
                    value: option.value,
                    text: option.label
                }));
            });

        var option_count = select.find('option').length;

        return option_count;
    }

    function show_filter_warning() {
        $('#filter-warning').show();

        if ($('#filter-service option').length <= 1) {
            populate_select('#filter-service', 'All Services', []);
        }

        if ($('#filter-status option').length <= 1) {
            populate_select('#filter-status', 'All Statuses', []);
        }

        if ($('#filter-location option').length <= 1) {
            populate_select('#filter-location', 'All Locations', []);
        }
    }

    // ── Event wiring ──────────────────────────────────────────────────────────

    function wire_filter_events() {
        $('#btn-refresh').off('click').on('click', function() {
            refresh_overview_kpis();
            refresh_service_delivery();
            refresh_sla_risk();
            refresh_payments_reconciliation();
            refresh_officer_workload();
            refresh_location_performance();
            refresh_policy_me();
        });
        $('#filter-from-date, #filter-to-date').off('change').on('change', function() {
            refresh_overview_kpis();
            refresh_service_delivery();
            refresh_sla_risk();
            refresh_payments_reconciliation();
            refresh_officer_workload();
            refresh_location_performance();
            refresh_policy_me();
        });
        $('#filter-service, #filter-status, #filter-location').off('change').on('change', function() {
            refresh_overview_kpis();
            refresh_service_delivery();
            refresh_sla_risk();
            refresh_payments_reconciliation();
            refresh_officer_workload();
            refresh_location_performance();
            refresh_policy_me();
        });
    }

    // ── Filter args helper ────────────────────────────────────────────────────

    function get_filter_args() {
        return {
            filters: JSON.stringify({
                from_date:  $('#filter-from-date').val()  || null,
                to_date:    $('#filter-to-date').val()    || null,
                service:    $('#filter-service').val()    || null,
                status:     $('#filter-status').val()     || null,
                location:   $('#filter-location').val()   || null
            })
        };
    }

    // ── Chart Helper ──────────────────────────────────────────────────────────

    function render_chart(container_selector, chart_config, empty_message) {
        var $c = $(container_selector);
        if (!$c.length) return;

        $c.empty();

        try {
            new frappe.Chart(container_selector, chart_config);
        } catch (e) {
            console.error('[NileGov Command Centre V3] Chart render failed for ' + container_selector, e);
            handle_chart_error(container_selector, empty_message);
        }
    }

    function clear_chart(container_selector, empty_message) {
        var $c = $(container_selector);
        if (!$c.length) return;
        $c.html('<div class="text-muted small" style="margin-top:12px;">' + empty_message + '</div>');
    }

    function handle_chart_error(container_selector, empty_message) {
        clear_chart(container_selector, empty_message);
    }

    // ── Overview KPI refresh (Layer 3) ────────────────────────────────────────

    function refresh_overview_kpis() {
        console.log('[NileGov Command Centre V3] overview refresh started');
        frappe.call({
            method: 'nilegov_stack.interfaces.frappe.api.insights.get_command_centre_overview',
            args: get_filter_args(),
            callback: function(r) {
                if (r && r.message) {
                    render_kpis(r.message);
                    $('#kpi-error-state').hide();
                    console.log('[NileGov Command Centre V3] overview refresh completed');
                } else {
                    handle_kpi_error();
                }
            },
            error: function() {
                handle_kpi_error();
            }
        });
    }

    function render_kpis(data) {
        var fn = function(val) {
            return (val === undefined || val === null) ? '0' : val.toLocaleString();
        };
        var fm = function(val) {
            return (val === undefined || val === null) ? 'UGX 0.00' : 'UGX ' + parseFloat(val).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
        };
        $('#kpi-total').text(fn(data.total));
        $('#kpi-active-backlog').text(fn(data.active_backlog));
        $('#kpi-completed').text(fn(data.completed));
        $('#kpi-escalated').text(fn(data.escalated));
        $('#kpi-sla-compliance').text(fn(data.sla_compliance) + '%');
        $('#kpi-sla-breaches').text(fn(data.sla_breaches));
        $('#kpi-payments-collected').text(fm(data.total_payments_collected));
        $('#kpi-payments-pending').text(fn(data.pending_payments_count));
    }

    function handle_kpi_error() {
        console.log('[NileGov Command Centre V3] overview refresh failed');
        $('#kpi-error-state').show();
        $('#kpi-total, #kpi-active-backlog, #kpi-completed, #kpi-escalated, #kpi-sla-compliance, #kpi-sla-breaches, #kpi-payments-pending').text('0');
        $('#kpi-payments-collected').text('UGX 0.00');
    }

    // ── Service Delivery Analytics (Layer 4) ──────────────────────────────────

    function refresh_service_delivery() {
        console.log('[NileGov Command Centre V3] service delivery hydration started');
        var loading = '<div class="text-muted small" style="margin-top:12px;">Loading...</div>';
        $('#trend-container, #by-type-container, #by-status-container, #backlog-container').html(loading);
        $('#service-delivery-error').hide();

        frappe.call({
            method: 'nilegov_stack.interfaces.frappe.api.insights.get_service_delivery_analytics',
            args: get_filter_args(),
            callback: function(r) {
                if (r && r.message) {
                    var data = r.message;
                    render_trend(data.trend || []);
                    render_by_type(data.by_type || []);
                    render_by_status(data.by_status || []);
                    render_backlog(data.oldest_backlog || []);
                    console.log('[NileGov Command Centre V3] service delivery hydration completed');
                } else {
                    handle_service_delivery_error();
                }
            },
            error: function() {
                handle_service_delivery_error();
            }
        });
    }

    var MONTHS = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    function render_trend(rows) {
        var $c = $('#trend-container');
        if (!$c.length) return;
        if (!rows || rows.length === 0) {
            clear_chart('#trend-container', 'No service delivery data available for the selected filters.');
            return;
        }
        var labels = [];
        var values = [];
        for (var i = 0; i < rows.length; i++) {
            var r = rows[i];
            labels.push((MONTHS[r.month] || r.month) + ' ' + r.year);
            values.push(r.count || 0);
        }
        render_chart('#trend-container', {
            data: { labels: labels, datasets: [{ name: 'Requests', values: values }] },
            type: 'line',
            colors: ['#2563eb'],
            height: 200
        }, 'No service delivery data available for the selected filters.');
    }

    function render_by_type(rows) {
        var $c = $('#by-type-container');
        if (!$c.length) return;
        if (!rows || rows.length === 0) {
            clear_chart('#by-type-container', 'No service delivery data available for the selected filters.');
            return;
        }
        var labels = [];
        var values = [];
        for (var i = 0; i < rows.length; i++) {
            labels.push(rows[i].service_type || 'Unknown');
            values.push(rows[i].count || 0);
        }
        render_chart('#by-type-container', {
            data: { labels: labels, datasets: [{ name: 'Requests', values: values }] },
            type: 'bar',
            colors: ['#f59e0b'],
            height: 200
        }, 'No service delivery data available for the selected filters.');
    }

    function render_by_status(rows) {
        var $c = $('#by-status-container');
        if (!$c.length) return;
        if (!rows || rows.length === 0) {
            clear_chart('#by-status-container', 'No service delivery data available for the selected filters.');
            return;
        }
        var labels = [];
        var values = [];
        for (var i = 0; i < rows.length; i++) {
            labels.push(rows[i].internal_status || 'Unknown');
            values.push(rows[i].count || 0);
        }
        render_chart('#by-status-container', {
            data: { labels: labels, datasets: [{ name: 'Requests', values: values }] },
            type: 'bar',
            colors: ['#10b981'],
            height: 200
        }, 'No service delivery data available for the selected filters.');
    }

    function render_backlog(rows) {
        var $c = $('#backlog-container');
        if (!$c.length) return;
        if (!rows || rows.length === 0) {
            $c.html('<div class="text-muted small" style="margin-top:12px;">No open backlog items for the selected filters.</div>');
            return;
        }
        var t = '<table class="table table-sm" style="font-size:12px;"><thead><tr><th>ID</th><th>Type</th><th>Status</th><th>Created</th></tr></thead><tbody>';
        for (var i = 0; i < rows.length; i++) {
            var r = rows[i];
            t += '<tr><td style="white-space:nowrap;">' + (r.name || '-') + '</td><td>' + (r.service_type || '-') + '</td><td>' + (r.internal_status || '-') + '</td><td>' + (r.creation ? r.creation.toString().substring(0, 10) : '-') + '</td></tr>';
        }
        $c.html(t + '</tbody></table>');
    }

    function handle_service_delivery_error() {
        console.log('[NileGov Command Centre V3] service delivery hydration failed');
        $('#service-delivery-error').show();
        var msg = '<div class="text-muted small" style="margin-top:12px;">Could not load data.</div>';
        $('#trend-container, #by-type-container, #by-status-container, #backlog-container').html(msg);
    }

    // ── SLA / Risk Analytics (Layer 5) ────────────────────────────────────────

    function refresh_sla_risk() {
        console.log('[NileGov Command Centre V3] sla risk hydration started');
        var loading = '<div class="text-muted small" style="margin-top:12px;">Loading...</div>';
        $('#sla-breaches-container, #escalations-status-container, #oldest-escalations-container').html(loading);
        $('#sla-risk-error').hide();

        frappe.call({
            method: 'nilegov_stack.interfaces.frappe.api.insights.get_sla_risk_analytics',
            args: get_filter_args(),
            callback: function(r) {
                if (r && r.message) {
                    var data = r.message;
                    render_sla_breaches(data.breaches_by_service || []);
                    render_escalations_by_status(data.escalations_by_status || []);
                    render_oldest_escalations(data.oldest_escalations || []);
                    console.log('[NileGov Command Centre V3] sla risk hydration completed');
                } else {
                    handle_sla_risk_error();
                }
            },
            error: function() {
                handle_sla_risk_error();
            }
        });
    }

    function render_sla_breaches(rows) {
        var $c = $('#sla-breaches-container');
        if (!$c.length) return;
        if (!rows || rows.length === 0) {
            clear_chart('#sla-breaches-container', 'No SLA breach data available for the selected filters.');
            return;
        }
        var labels = [];
        var values = [];
        for (var i = 0; i < rows.length; i++) {
            labels.push(rows[i].service_type || 'Unknown');
            values.push(rows[i].count || 0);
        }
        render_chart('#sla-breaches-container', {
            data: { labels: labels, datasets: [{ name: 'Breaches', values: values }] },
            type: 'bar',
            colors: ['#ef4444'],
            height: 200
        }, 'No SLA breach data available for the selected filters.');
    }

    function render_escalations_by_status(rows) {
        var $c = $('#escalations-status-container');
        if (!$c.length) return;
        if (!rows || rows.length === 0) {
            clear_chart('#escalations-status-container', 'No escalation status data available for the selected filters.');
            return;
        }
        var labels = [];
        var values = [];
        for (var i = 0; i < rows.length; i++) {
            labels.push(rows[i].escalation_status || 'Unknown');
            values.push(rows[i].count || 0);
        }
        render_chart('#escalations-status-container', {
            data: { labels: labels, datasets: [{ name: 'Count', values: values }] },
            type: 'bar',
            colors: ['#8b5cf6'],
            height: 200
        }, 'No escalation status data available for the selected filters.');
    }

    function render_oldest_escalations(rows) {
        var $c = $('#oldest-escalations-container');
        if (!$c.length) return;
        if (!rows || rows.length === 0) {
            $c.html('<div class="text-muted small" style="margin-top:12px;">No unresolved escalations for the selected filters.</div>');
            return;
        }
        var t = '<table class="table table-sm" style="font-size:12px;"><thead><tr><th>ID</th><th>Type</th><th>Escalation Status</th><th>Escalated At</th><th>Officer</th></tr></thead><tbody>';
        for (var i = 0; i < rows.length; i++) {
            var r = rows[i];
            t += '<tr>' +
                    '<td style="white-space:nowrap;">' + (r.name || '-') + '</td>' +
                    '<td>' + (r.service_type || '-') + '</td>' +
                    '<td>' + (r.escalation_status || '-') + '</td>' +
                    '<td>' + (r.escalated_at ? r.escalated_at.toString().substring(0, 10) : '-') + '</td>' +
                    '<td>' + (r.assigned_officer || '-') + '</td>' +
                 '</tr>';
        }
        $c.html(t + '</tbody></table>');
    }

    function handle_sla_risk_error() {
        console.log('[NileGov Command Centre V3] sla risk hydration failed');
        $('#sla-risk-error').show();
        var msg = '<div class="text-muted small" style="margin-top:12px;">Could not load data.</div>';
        $('#sla-breaches-container, #escalations-status-container, #oldest-escalations-container').html(msg);
    }

    // ── Payments & Reconciliation Analytics (Layer 6) ─────────────────────────

    function refresh_payments_reconciliation() {
        console.log('[NileGov Command Centre V3] payment reconciliation hydration started');
        var loading = '<div class="text-muted small" style="margin-top:12px;">Loading...</div>';
        $('#payment-status-container, #failed-payments-container, #pending-payments-container').html(loading);
        $('#payments-error').hide();

        frappe.call({
            method: 'nilegov_stack.interfaces.frappe.api.insights.get_payment_reconciliation_analytics',
            args: get_filter_args(),
            callback: function(r) {
                if (r && r.message) {
                    var data = r.message;
                    render_payment_status(data.payment_status_summary || []);
                    render_failed_payments(data.failed_payments || []);
                    render_pending_payments(data.pending_payments || []);
                    console.log('[NileGov Command Centre V3] payment reconciliation hydration completed');
                } else {
                    handle_payments_error();
                }
            },
            error: function() {
                handle_payments_error();
            }
        });
    }

    function render_payment_status(rows) {
        var $c = $('#payment-status-container');
        if (!$c.length) return;
        if (!rows || rows.length === 0) {
            clear_chart('#payment-status-container', 'No payment summary data available for the selected filters.');
            return;
        }
        var labels = [];
        var values = [];
        for (var i = 0; i < rows.length; i++) {
            labels.push(rows[i].status || 'Unknown');
            values.push(rows[i].count || 0);
        }
        render_chart('#payment-status-container', {
            data: { labels: labels, datasets: [{ name: 'Payments', values: values }] },
            type: 'percentage',
            colors: ['#14b8a6', '#f97316', '#ef4444', '#8b5cf6'],
            height: 200
        }, 'No payment summary data available for the selected filters.');
    }

    function render_failed_payments(rows) {
        var $c = $('#failed-payments-container');
        if (!$c.length) return;
        if (!rows || rows.length === 0) {
            $c.html('<div class="text-muted small" style="margin-top:12px;">No failed payments for the selected filters.</div>');
            return;
        }
        var t = '<table class="table table-sm" style="font-size:12px;"><thead><tr><th>ID</th><th>Type</th><th>Failed At</th></tr></thead><tbody>';
        for (var i = 0; i < rows.length; i++) {
            var r = rows[i];
            t += '<tr><td style="white-space:nowrap;">' + (r.name || '-') + '</td><td>' + (r.service_type || '-') + '</td><td>' + (r.failed_at ? r.failed_at.toString().substring(0, 10) : '-') + '</td></tr>';
        }
        $c.html(t + '</tbody></table>');
    }

    function render_pending_payments(rows) {
        var $c = $('#pending-payments-container');
        if (!$c.length) return;
        if (!rows || rows.length === 0) {
            $c.html('<div class="text-muted small" style="margin-top:12px;">No pending payments for the selected filters.</div>');
            return;
        }
        var t = '<table class="table table-sm" style="font-size:12px;"><thead><tr><th>ID</th><th>Type</th><th>Created</th></tr></thead><tbody>';
        for (var i = 0; i < rows.length; i++) {
            var r = rows[i];
            t += '<tr><td style="white-space:nowrap;">' + (r.name || '-') + '</td><td>' + (r.service_type || '-') + '</td><td>' + (r.creation ? r.creation.toString().substring(0, 10) : '-') + '</td></tr>';
        }
        $c.html(t + '</tbody></table>');
    }

    function handle_payments_error() {
        console.log('[NileGov Command Centre V3] payment reconciliation hydration failed');
        $('#payments-error').show();
        var msg = '<div class="text-muted small" style="margin-top:12px;">Could not load data.</div>';
        $('#payment-status-container, #failed-payments-container, #pending-payments-container').html(msg);
    }

    // ── Officer Workload Analytics (Layer 7) ──────────────────────────────────

    function refresh_officer_workload() {
        console.log('[NileGov Command Centre V3] officer workload hydration started');
        var loading = '<div class="text-muted small" style="margin-top:12px;">Loading...</div>';
        $('#officer-workload-container').html(loading);
        $('#officer-workload-error').hide();

        frappe.call({
            method: 'nilegov_stack.interfaces.frappe.api.insights.get_officer_workload_analytics',
            args: get_filter_args(),
            callback: function(r) {
                if (r && r.message) {
                    var data = r.message;
                    render_officer_workload(data.officer_workload || []);
                    console.log('[NileGov Command Centre V3] officer workload hydration completed');
                } else {
                    handle_officer_workload_error();
                }
            },
            error: function() {
                handle_officer_workload_error();
            }
        });
    }

    function render_officer_workload(rows) {
        var $c = $('#officer-workload-container');
        if (!$c.length) return;
        if (!rows || rows.length === 0) {
            clear_chart('#officer-workload-container', 'No officer workload data available for the selected filters.');
            return;
        }
        var labels = [];
        var values = [];
        for (var i = 0; i < rows.length; i++) {
            labels.push(rows[i].assigned_officer || 'Unassigned');
            values.push(rows[i].active_cases || 0);
        }
        render_chart('#officer-workload-container', {
            data: { labels: labels, datasets: [{ name: 'Active Cases', values: values }] },
            type: 'bar',
            colors: ['#3b82f6'],
            height: 200
        }, 'No officer workload data available for the selected filters.');
    }

    function handle_officer_workload_error() {
        console.log('[NileGov Command Centre V3] officer workload hydration failed');
        $('#officer-workload-error').show();
        var msg = '<div class="text-muted small" style="margin-top:12px;">Could not load data.</div>';
        $('#officer-workload-container').html(msg);
    }

    // ── Location Performance (Layer 8) ─────────────────────────────────────────

    function refresh_location_performance() {
        console.log('[NileGov Command Centre V3] location performance hydration started');
        var loading = '<div class="text-muted small" style="margin-top:12px;">Loading...</div>';
        $('#location-performance-container').html(loading);
        $('#location-performance-error').hide();

        frappe.call({
            method: 'nilegov_stack.interfaces.frappe.api.insights.get_location_performance_analytics',
            args: get_filter_args(),
            callback: function(r) {
                if (r && r.message) {
                    var data = r.message;
                    render_location_performance(data.location_performance || []);
                    console.log('[NileGov Command Centre V3] location performance hydration completed');
                } else {
                    handle_location_performance_error();
                }
            },
            error: function() {
                handle_location_performance_error();
            }
        });
    }

    function render_location_performance(rows) {
        var $c = $('#location-performance-container');
        if (!$c.length) return;
        if (!rows || rows.length === 0) {
            clear_chart('#location-performance-container', 'No location analytics data available for the selected filters.');
            return;
        }
        var labels = [];
        var values = [];
        for (var i = 0; i < rows.length; i++) {
            labels.push(rows[i].location || 'Unknown Location');
            values.push(rows[i].total_requests || 0);
        }
        render_chart('#location-performance-container', {
            data: { labels: labels, datasets: [{ name: 'Total Requests', values: values }] },
            type: 'bar',
            colors: ['#6366f1'],
            height: 200
        }, 'No location analytics data available for the selected filters.');
    }

    function handle_location_performance_error() {
        console.log('[NileGov Command Centre V3] location performance hydration failed');
        $('#location-performance-error').show();
        var msg = '<div class="text-muted small" style="margin-top:12px;">Could not load data.</div>';
        $('#location-performance-container').html(msg);
    }

    // ── Policy & M&E Analytics (Layer 9) ──────────────────────────────────────

    function refresh_policy_me() {
        console.log('[NileGov Command Centre V3] policy & m&e hydration started');
        var loading = '<div class="text-muted small" style="margin-top:12px;">Loading...</div>';
        $('#policy-me-container').html(loading);
        $('#policy-me-error').hide();

        frappe.call({
            method: 'nilegov_stack.interfaces.frappe.api.insights.get_policy_me_summary',
            args: get_filter_args(),
            callback: function(r) {
                if (r && r.message) {
                    var data = r.message;
                    render_policy_me(data.policy_performance || []);
                    console.log('[NileGov Command Centre V3] policy & m&e hydration completed');
                } else {
                    handle_policy_me_error();
                }
            },
            error: function() {
                handle_policy_me_error();
            }
        });
    }

    function render_policy_me(rows) {
        var $c = $('#policy-me-container');
        if (!$c.length) return;
        if (!rows || rows.length === 0) {
            $c.html('<div class="text-muted small" style="margin-top:12px;">No Policy &amp; M&amp;E analytics data available for the selected filters.</div>');
            return;
        }
        var t = '<table class="table table-sm" style="font-size:13px;"><thead><tr><th>Policy Name</th><th>Adherence Rate</th><th>Violations</th></tr></thead><tbody>';
        for (var i = 0; i < rows.length; i++) {
            var r = rows[i];
            t += '<tr><td>' + (r.policy_name || 'Unknown Policy') + '</td><td>' + (r.adherence_rate || 0) + '%</td><td>' + (r.violations || 0) + '</td></tr>';
        }
        $c.html(t + '</tbody></table>');
    }

    function handle_policy_me_error() {
        console.log('[NileGov Command Centre V3] policy & m&e hydration failed');
        $('#policy-me-error').show();
        var msg = '<div class="text-muted small" style="margin-top:12px;">Could not load data.</div>';
        $('#policy-me-container').html(msg);
    }
};
