from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Real Estate Property Tag"
    _order = "name"

    color = fields.Integer(string="Color Index")
    
    name = fields.Char(required=True, string="Name")

    _check_name_unique = models.Constraint(
        'UNIQUE(name)', 
        'Tag Name must be unique'
    )