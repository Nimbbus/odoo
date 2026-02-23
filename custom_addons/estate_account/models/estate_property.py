from odoo import  fields, models

class estateProperty(models.Model):
    _inherit = "estate.property"
    _description = "Real Estate Property with Account Integration"

def action_sold(self):
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.buyer_id.id,
            'invoice_line_ids': [
                fields.Command.create({
                    'name': 'selling price commission',
                    'quantity': 1,
                    'price_unit': self.selling_price * 0.06,
                }),
                fields.Command.create({
                    'name': 'Administration fees',
                    'quantity': 1,
                    'price_unit': 100.00,
                }),
            ],
        }
        self.env['account.move'].create(invoice_vals)
        return super(estateProperty,self).action_sold()
