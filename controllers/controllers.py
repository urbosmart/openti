# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.payment_webpay.controllers.main import WebpayController

_logger = logging.getLogger(__name__)

class CustomWebsiteSale(WebsiteSale):

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True)
    def payment_confirmation(self, **post):
        response = super(CustomWebsiteSale,self).payment_confirmation(**post)
        order = response.qcontext['order']

        for payment in order.transaction_ids:
            if payment.state == 'done':
                payment._post_process_after_done()

        return request.redirect(order.access_url)
