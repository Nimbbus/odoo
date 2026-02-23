from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero

class estateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"
    _order = "id desc"
    
    # SQL Constraints
    _check_expected_price = models.Constraint(
        'CHECK(expected_price > 0)', 
        'The expected price must be strictly positive.'
    )
    _check_selling_price = models.Constraint(
        'CHECK(selling_price >= 0)', 
        'The selling price must be positive.'
    )
    
    # Fields
    name = fields.Char(required=True, string="Title", default="unknown")
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, 
        default=lambda self: fields.Date.today() + relativedelta(months=3))
    expected_price = fields.Float(required=True, string="Expected Price")
    selling_price = fields.Float(readonly=True, copy=False, default=0.0)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        string='Type',
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
        help="Direction the garden faces"
    )
    property_type_id = fields.Many2one(
        comodel_name='estate.property.type',
        string='Property Type'
    )
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    buyer_id = fields.Many2one(comodel_name='res.partner', string='Buyer', copy=False)
    seller_id = fields.Many2one(
        comodel_name='res.users', 
        string='Salesperson', 
        default=lambda self: self.env.user
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('cancelled', 'Cancelled'),
        ],
        string="Status",
        required=True,
        copy=False,
        default='new',
    )
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    
    # Computes
    total_area = fields.Integer(string="Total Area (sqm)", compute="_compute_total_area")
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    best_price = fields.Float(string="Best Offer", compute="_compute_best_price")
    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped("price"))
            else:
                record.best_price = 0
                
    last_seen = fields.Datetime("Last Seen", default=lambda self: fields.Datetime.now(), readonly=True)

    # Methods
    def write(self, vals):
        vals = dict(vals or {})
        vals['last_seen'] = fields.Datetime.now()
        return super(estateProperty, self).write(vals)

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    def action_sold(self):
        for record in self:
            if record.state == "cancelled":
                raise UserError("Canceled properties cannot be sold.")
            record.state = "sold"
        return True

    def action_cancel(self):
        for record in self:
            if record.state == "sold":
                raise UserError("Sold properties cannot be canceled.")
            record.state = "cancelled"
        return True

    # Python Constraints
    @api.constrains("expected_price", "selling_price")
    def _check_selling_price_limit(self):
        for record in self:
            if float_is_zero(record.selling_price, precision_digits=2):
                continue
            limit_price = record.expected_price * 0.9
            if float_compare(record.selling_price, limit_price, precision_digits=2) == -1:
                raise UserError("The selling price cannot be lower than 90% of the expected price!")

    def unlink(self):
        for record in self:
            if record.state not in ['new', 'cancelled']:
                raise UserError("Only properties in 'New' or 'Cancelled' state can be deleted.")
        return super(estateProperty, self).unlink()
