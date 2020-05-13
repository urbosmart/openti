# -*- coding: utf-8 -*-
import logging
import pprint
import werkzeug
from odoo import http, fields
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.http import request
from odoo.exceptions import UserError
from odoo.addons.payment_webpay.controllers.main import WebpayController


_logger = logging.getLogger(__name__)

try:
    import urllib3
    urllib3.disable_warnings()
    pool = urllib3.PoolManager()
except:
    _logger.warning("No Load urllib3")
    pass

class CustomWebpayController(WebpayController, http.Controller):

    @http.route([
        '/payment/webpay/final/<model("payment.acquirer"):acquirer_id>',
    ], type='http', auth='public', csrf=False, website=True)
    def final(self, acquirer_id=False, **post):
        resp = super(CustomWebpayController, self).final(acquirer_id=s_action, **post)
        """ Webpay contacts using GET, at least for accept """
        _logger.info('Webpay: entering End with post data %s', pprint.pformat(post))  # debug
        if post.get('TBK_TOKEN'):
            return self.webpay_form_feedback2(acquirer_id, **post)
        return resp

    @http.route([
        '/payment/webpay/return/<model("payment.acquirer"):acquirer_id>',
        '/payment/webpay/test/return',
    ], type='http', auth='public', csrf=False, website=True)
    def webpay_form_feedback2(self, acquirer_id=None, **post):
        """ Webpay contacts using GET, at least for accept """
        _logger.warning('Webpay: entering form_feedback with post data %s', pprint.pformat(post))  # debug
        token_ws = post.get('token_ws') or post.get('TBK_TOKEN')
        try:
            resp = request.env['payment.transaction'].getTransaction(acquirer_id, token_ws)
        except:
            resp = False
            if not post.get('TBK_TOKEN'):
                raise UserError('Ha ocurrido un error al obtener la transacción desde Webpay')
        '''
            TSY: Autenticación exitosa
            TSN: Autenticación fallida.
            TO6: Tiempo máximo excedido para autenticación.
            ABO: Autenticación abortada por tarjetahabiente.
            U3: Error interno en la autenticación.
            Puede ser vacío si la transacción no se autenticó.
        '''
        if resp:
            request.env['payment.transaction'].sudo().form_feedback(resp, 'webpay')
            if str(resp.detailOutput[0].responseCode) in ['0']:
                values = {
                            'url': resp.urlRedirection,
                            'token_ws': token_ws
                        }
                return request.render('payment_webpay.webpay_redirect', values)
            request.website.sale_reset()
        elif post.get('TBK_ORDEN_COMPRA'):
            tx = request.env['payment.transaction'].sudo().search([
                            ('reference', '=', post.get('TBK_ORDEN_COMPRA'))
                            ])
            tx.write({'state': 'error', 'state_message': 'Pago cancelado (abortado en formulario Webpay)'})
        return werkzeug.utils.redirect('/shop/confirmation')
