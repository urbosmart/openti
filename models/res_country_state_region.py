# -*- encoding: utf-8 -*-
from odoo import models, fields


class CustomResState(models.Model):
    _inherit = 'res.country.state.region'

    country_id = fields.Many2one(
            'res.country',
            string='Region',
            index=True,
        )
