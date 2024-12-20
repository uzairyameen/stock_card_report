import pytz 
from odoo import api, fields, models

class StockCardView(models.TransientModel):
    _name = "stock.card.view"
    _description = "Stock Card View"
    _order = "date"

    date = fields.Datetime()
    product_id = fields.Many2one(comodel_name="product.product", string="Product")
    product_qty = fields.Float()
    product_uom_qty = fields.Float()
    product_uom = fields.Many2one(comodel_name="uom.uom", string="Unit of Measure")
    reference = fields.Char()
    location_id = fields.Many2one(comodel_name="stock.location", string="Source Location")
    location_dest_id = fields.Many2one(comodel_name="stock.location", string="Destination Location")
    is_initial = fields.Boolean()
    product_in = fields.Float()
    product_out = fields.Float()
    picking_id = fields.Many2one(comodel_name="stock.picking", string="Picking")

    def name_get(self):
        """Override name_get to return the product name with reference"""
        result = []
        for rec in self:
            # Ensure product_id is populated correctly
            name = rec.product_id.name if rec.product_id else "Unknown Product"
            if rec.reference:
                name += f" ({rec.reference})"
            result.append((rec.id, name))
        return result

class StockCardReport(models.TransientModel):
    _name = "report.stock.card.report"
    _description = "Stock Card Report"

    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    product_ids = fields.Many2many(comodel_name="product.product", string="Products")
    location_id = fields.Many2one(comodel_name="stock.location", string="Location")

    results = fields.Many2many(
        comodel_name="stock.card.view",
        compute="_compute_results",
        help="Computed stock card results, not stored in the database",
    )

    def _compute_results(self):
        """Compute stock card results and store them in the results field."""
        self.ensure_one()
        date_from = self.date_from or "0001-01-01"
        date_to = self.date_to or fields.Date.context_today(self)
        locations = self.env["stock.location"].search(
            [("id", "child_of", [self.location_id.id])]
        )
        self._cr.execute(
            """
            SELECT move.date, move.product_id, move.product_qty,
                move.product_uom_qty, move.product_uom, move.reference,
                move.location_id, move.location_dest_id,
                CASE WHEN move.location_dest_id IN %s THEN move.product_qty END AS product_in,
                CASE WHEN move.location_id IN %s THEN move.product_qty END AS product_out,
                CASE WHEN move.date < %s THEN True ELSE False END AS is_initial,
                move.picking_id
            FROM stock_move move
            WHERE (move.location_id IN %s OR move.location_dest_id IN %s)
                AND move.state = 'done' AND move.product_id IN %s
                AND CAST(move.date AS date) <= %s
            ORDER BY move.date, move.reference
            """,
            (
                tuple(locations.ids),
                tuple(locations.ids),
                date_from,
                tuple(locations.ids),
                tuple(locations.ids),
                tuple(self.product_ids.ids),
                date_to,
            ),
        )
        stock_card_results = self._cr.dictfetchall()
        ReportLine = self.env["stock.card.view"]
        user_timezone = pytz.timezone(self.env.user.tz)

        # Create records for the stock card results and assign them to results
        new_results = []
        for line in stock_card_results:
            line["date"] = line["date"].astimezone(user_timezone).replace(tzinfo=None)

            # Ensure that the product_id is properly linked to the product name
            product = self.env["product.product"].browse(line["product_id"])
            if product:
                line["product_id"] = product.id  # Ensure product_id is correctly set

            # Create record in stock.card.view model
            report_line = ReportLine.create(line)  # Store the record
            new_results.append(report_line.id)

        # Update the Many2many field with the new records
        self.results = [(6, 0, new_results)]  # Use Many2many format

    def _get_initial(self, product_line):
        """Compute initial balance based on product in/out quantities."""
        product_input_qty = sum(product_line.mapped("product_in"))
        product_output_qty = sum(product_line.mapped("product_out"))
        return product_input_qty - product_output_qty

    def print_report(self, report_type="qweb"):
        """Trigger the report action based on the selected report type."""
        self.ensure_one()
        action = (
            report_type == "xlsx"
            and self.env.ref("stock_card_report.action_stock_card_report_xlsx")
            or self.env.ref("stock_card_report.action_stock_card_report_pdf")
        )
        return action.report_action(self, config=False)