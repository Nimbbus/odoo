from odoo import api, fields, models

class ResUsers(models.Model):
    _inherit = "res.users"
    _description = "Inherit res.users to add relation with estate.property"

    property_ids = fields.One2many(
        "estate.property",
        "seller_id",
        string="Real Estate Properties"
    )

    
    def _get_property(self):
        for record in self:
            record.property2_ids = self.env["estate.property"].search([("seller_id", "=", record.id),("state", "not in", ['sold', 'cancelled'])])