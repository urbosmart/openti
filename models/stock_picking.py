# -*- coding: utf-8 -*-
from odoo import osv, models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import except_orm, UserError
import odoo.addons.decimal_precision as dp
from odoo.tools.float_utils import float_compare, float_round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import logging
_logger = logging.getLogger(__name__)

class StockPickingInherit(models.Model):
    _inherit = "stock.picking"

    def set_use_document(self):
        return True

    use_documents = fields.Boolean(
            string='Use Documents?',
            default=set_use_document,
        )
