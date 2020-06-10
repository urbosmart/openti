# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request
from odoo.addons.payment_webpay.controllers.main import WebpayController

class CustomWebpayController(WebpayController):
    @http.route([
        '/payment/webpay/return/<model("payment.acquirer"):acquirer_id>',
        '/payment/webpay/test/return',
    ], type='http', auth='public', csrf=False, website=True)
    def webpay_form_feedback(self, acquirer_id=None, **post):
        resp = super(CustomWebsiteSale, self).webpay_form_feedback()
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
        return resp
