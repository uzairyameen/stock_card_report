/** @odoo-module **/

import { Component, useState, xml } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

class StockCardReportComponent extends Component {
    static template = xml/* xml */ `
        <div>
            <!-- Print and Export buttons -->
            <button t-on-click="print" class="o_stock_card_reports_print">Print</button>
            <button t-on-click="export" class="o_stock_card_reports_export">Export</button>
            <div class="o_content" t-raw="state.html"></div>
        </div>
    `;

    constructor() {
        super(...arguments);

        this.state = useState({ html: "" });
        this.context = this.props.context || {};

        // Initialize the services (rpc and actionService)
        this.rpc = null;
        this.actionService = null;
    }

    async willStart() {
        // Initialize the rpc and actionService using the useService hook
        try {
            // Ensure services are initialized here before fetching the HTML content
            this.rpc = useService("rpc");
            this.actionService = useService("action");

            // Log services to check if they are initialized correctly
            console.log("RPC service initialized:", this.rpc);
            console.log("Action service initialized:", this.actionService);

            // Check if services are properly initialized before fetching the HTML content
            if (!this.rpc || !this.actionService) {
                console.error("RPC or Action service not initialized.");
                return;
            }

            // Fetch the HTML content for the report
            this.state.html = await this.fetchHtml();
        } catch (error) {
            console.error("Error in willStart:", error);
        }
    }

    async fetchHtml() {
        // Fetch the HTML content for the report
        try {
            if (this.rpc) {
                const result = await this.rpc({
                    model: this.context.model,
                    method: "get_html",
                    args: [this.context],
                    context: this.context,
                });
                return result.html || "";
            } else {
                console.error("RPC service is not available to fetch HTML.");
                return "";
            }
        } catch (error) {
            console.error("Error fetching HTML:", error);
            return "";
        }
    }

    async print() {
        // Ensure that rpc and actionService are available before proceeding
        if (this.rpc && this.actionService) {
            try {
                const result = await this.rpc({
                    model: this.context.model,
                    method: "print_report",
                    args: [this.context.active_id, "qweb-pdf"], // Request PDF format
                    context: this.context,
                });
                this.actionService.doAction(result); // Trigger the action for printing
            } catch (error) {
                console.error("Error during Print:", error);
            }
        } else {
            console.error("RPC or Action service is not initialized during print action.");
        }
    }

    async export() {
        // Ensure that rpc and actionService are available before proceeding
        if (this.rpc && this.actionService) {
            try {
                const result = await this.rpc({
                    model: this.context.model,
                    method: "print_report",
                    args: [this.context.active_id, "xlsx"], // Request XLSX format
                    context: this.context,
                });
                this.actionService.doAction(result); // Trigger the action for export
            } catch (error) {
                console.error("Error during Export:", error);
            }
        } else {
            console.error("RPC or Action service is not initialized during export action.");
        }
    }
}

// Register the component in the Odoo registry
registry.category("actions").add("stock_card_report_backend", StockCardReportComponent);


