# -*- encoding: utf-8 -*-
from odoo import models, fields, api


class CustomResStateRegion(models.Model):
    _inherit = 'res.country'

    state_region_ids = fields.One2many('res.country.state.region', 'country_id', string='States')

    def get_website_sale_regions(self):
        return self.sudo().state_region_ids
