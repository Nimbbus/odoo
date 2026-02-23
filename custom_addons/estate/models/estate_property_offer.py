from odoo import api, fields, models
from odoo.orm.environments import UserError
from datetime import timedelta

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
    _order = "price desc"

    _check_offer_price = models.Constraint(
        'CHECK(price > 0)', 
        'The offer price must be strictly positive.'
    )

    price = fields.Float(string="Price")
 
    status = fields.Selection(
        selection=[('accepted', 'Accepted'), ('refused', 'Refused')],
        copy=False,
        string="Status"
    )
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
   
    property_id = fields.Many2one("estate.property", string="Property", required=True, ondelete="cascade")

    validity = fields.Integer(string="Validity (days)", default=7)
    date_deadline = fields.Date(string="Deadline", compute="_compute_date_deadline", inverse="_inverse_date_deadline")

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            start_date = record.create_date.date() if record.create_date else fields.Date.today()
            record.date_deadline = start_date + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            start_date = record.create_date.date() if record.create_date else fields.Date.today()
            delta = record.date_deadline - start_date
            record.validity = delta.days

    def action_accept(self):
        for record in self:
            if record.property_id.offer_ids.filtered(lambda o: o.status == 'accepted'):
                raise UserError("An offer has already been accepted for this property!")

            record.status = 'accepted'
            record.property_id.buyer_id = record.partner_id
            record.property_id.selling_price = record.price
            record.property_id.state = 'offer_accepted'
        return True

    
    def action_refuse(self):
        for record in self:
            record.status = 'refused'
            record.property_id.state = 'offer_received'
            return True
        
    property_type_id = fields.Many2one("estate.property.type",
                                       string="Property Type",
                                       related="property_id.property_type_id",
                                       store=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        if 'price' in vals_list[0]:
            if vals_list[0]['price'] <= 0:
                raise UserError("The offer price must be positive.")
            price = vals_list[0]['price']
            history = self.env['estate.property.offer'].search([('property_id','=',vals_list[0]['property_id'])],
            order='price desc',limit=1)
            if history and price <= history.price:
                raise UserError("The offer price must be higher than the current best offer.")
            
            res = super(EstatePropertyOffer, self).create(vals_list)
            property = self.env['estate.property'].browse(vals_list[0]['property_id'])
            property.write({'state': 'offer_received'})
            return res