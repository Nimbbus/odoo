from odoo import fields, models


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real Estate Property Type"
    _order = "name"

    name = fields.Char(required=True, string="Name")

    sequence = fields.Integer( string="Sequence" , default=1 )

    _check_name_unique = models.Constraint(
        'UNIQUE(name)', 
        'Type Name must be unique'
    )

    property_ids = fields.One2many(
        "estate.property", 
        "property_type_id", 
        string="Properties"
    )

    offer_ids = fields.One2many(
        "estate.property.offer", 
        "property_type_id", 
        string="Offers"
    )

    offer_count = fields.Integer(
        string="Offer Count", 
        compute="_compute_offer_count"
    )

    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)

    
    def action_view_offers(self):
        self.ensure_one()
        return{
            "type": "ir.actions.act_window",
            "name": "Offers",
            "res_model": "estate.property.offer",
            "view_mode": "list,form",
            "domain": [("property_type_id", "=", self.id)],
        }