{
    "name": "Stock Card Report",
    "summary": "Add stock card report on Inventory Reporting.",
    "version": "17.0.1.0.0",
    "category": "Warehouse",
    "website": "https://github.com/OCA/stock-logistics-reporting",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "depends": [
        "base",
        "stock",
        "date_range",
        "report_xlsx",
        "report_xlsx_helper",
        "web"  # Add this line to ensure web dependencies are included
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/paper_format.xml",
        "data/report_data.xml",
        "reports/stock_card_report.xml",
        "wizard/stock_card_report_wizard_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "stock_card_report/static/src/css/report.css",
            # "stock_card_report/static/src/js/**/*",
            "stock_card_report/static/src/js/stock_card_report_backend.esm.js",
            # Include jQuery (if not already included)
        ]
    },
    "installable": True,
    "application": False,
}




