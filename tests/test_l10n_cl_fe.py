# -*- coding: utf-8 -*-
from odoo.tests.common import SingleTransactionCase, tagged
import logging
import base64
import datetime
import time

_logger = logging.getLogger(__name__)

@tagged("tecnopti")
class Test_l10n_cl_fe(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(Test_l10n_cl_fe, cls).setUpClass()
        cls.number = {
            'boleta':101,
            'factura_electronica':188,
            'guia_despacho':93,
        }
        # Creacion de firma electronica
        file_string = open("/home/abiezer/Documentos/jsanhueza.p12", "rb").read()
        cls.firma = cls.env['sii.firma'].create({
            'name': 'jsanhueza.p12',
            'file_content': base64.encodestring(file_string),
            'password': '72918346'
        })
        # Validate signature
        cls.firma.action_process()
        cls.firma.write({
            'subject_serial_number': '14372265-1',
            'user_ids': [(6, 0, [
                cls.env.ref('base.user_admin').id,
                cls.env.ref('base.user_root').id,
            ])],
            'company_ids': [(6, 0, [
                cls.env.ref('base.main_company').id,
            ])]
        })
        cls.firma.action_process()

        #Creacion de Producto
        cls.product = cls.env['product.product'].create({
            'name': 'puerta',
            'default_code': 'puerta',
            'taxes_id': [
                cls.env.ref('l10n_cl_chart_of_account.1_IVAV_19').id,
            ],
            'lst_price': 10000,
            'standard_price':8000
        })

        # Creation of mail
        cls.mail = cls.env['mail.alias'].create({
            'alias_name':'contacto',
            'alias_model_id':cls.env['ir.model'].search([('model','=','mail.message.dte')]).id,
            'alias_contact':'everyone',
        })

        # Modificacion de Compañia
        cls.company = cls.env['res.company'].search([('id', '=', 1)])
        cls.glosa = cls.env['sii.activity.description'].create({
            'name': 'EMPRESA DE SERVICIOS INTEGRALES DE INFORMATICA',
            'vat_affected': 'SI',
            'active': True,
        })
        cls.company.write({
            'name': 'Comercializacion Y Servicios Informaticos Sanhueza & Mujica Spa',
            'street': 'OHIGGINS #241 DEPTO. #821',
            'city': 'Concepción',
            'city_id': cls.env.ref('l10n_cl_fe.CL08101').id,
            'country_id': cls.env.ref('base.cl').id,
            'state_id': cls.env['res.country.state'].search([('code', '=', 'CL08100')]).id,
            'zip': '4030000',
            'dte_service_provider': 'SIICERT',
            'dte_resolution_number': '0',
            'dte_resolution_date': datetime.date(2016, 2, 11),
            'sii_regional_office_id': cls.env.ref('l10n_cl_fe.ur_Cop').id,
            'phone': '+56412227164',
            'email': 'contacto@openti.cl',
            'document_type_id': cls.env.ref('l10n_cl_fe.dt_RUT'),
            'document_number': '76.323.752-4',
            'responsability_id': cls.env.ref('l10n_cl_fe.res_IVARI'),
            'start_date': datetime.date(2014, 1, 24),
            'company_activities_ids': [(6, 0, [
                cls.env.ref('l10n_cl_fe.eco_acti_611090').id,
                cls.env.ref('l10n_cl_fe.eco_acti_620200').id,
                cls.env.ref('l10n_cl_fe.eco_acti_951100').id,
            ])],
            'activity_description': cls.glosa.id,
            'currency_id': cls.env.ref('base.CLP').id,
            'vat': 'CL763237524',
            'tax_calculation_rounding_method':'round_globally',
            'dte_email_id':cls.mail.id,
        })
        #Creating Journal 33
        cls.sequence = cls.env['ir.sequence'].create({
            'name': 'Factura Electronica(Tests)',
            'implementation': 'no_gap',
            'sii_document_class_id': cls.env['sii.document_class'].search([('name', '=', 'Factura Electrónica')]).id,
            'is_dte': True,
            'forced_by_caf':True,
            'number_next_actual':cls.number['factura_electronica'],
        })

        file_string = open(
            "/home/abiezer/Documentos/Folios/FacturaElectronica/179-188/FoliosSII763237523317920207291220.xml",
            "rb").read()

        cls.dte = cls.env['dte.caf'].create({
            'company_id':cls.company.id,
            'caf_file': base64.encodestring(file_string),
            'sequence_id': cls.sequence.id
        })

        # Write and Create Journal
        cls.journal = cls.env['account.journal'].search([('name', '=', 'Facturas de cliente')])

        cls.document_class = cls.env['account.journal.sii_document_class'].create({
            'journal_id': cls.journal.id,
            'sii_document_class_id': cls.env['sii.document_class'].search(
                [('name', '=', 'Factura Electrónica')]).id,
            'sequence_id': cls.sequence.id
        })
        cls.journal.write({
            'journal_activities_ids': [(6, 0, [
                cls.env.ref('l10n_cl_fe.eco_acti_611090').id,
                cls.env.ref('l10n_cl_fe.eco_acti_620200').id,
                cls.env.ref('l10n_cl_fe.eco_acti_951100').id,
            ])],
            'journal_document_class_ids': [(6, 0, [
                cls.document_class.id
            ])],
        })

        # Create Customer
        cls.customer = cls.env['res.partner'].create({
            'name': 'Abiezer',
            'street': 'Tucapel 50',
            'city': 'Concepción',
            'city_id': cls.env.ref('l10n_cl_fe.CL08101').id,
            'customer':True,
            'country_id': cls.env.ref('base.cl').id,
            'state_id': cls.env['res.country.state'].search([('code', '=', 'CL08100')]).id,
            'document_type_id': cls.env.ref('l10n_cl_fe.dt_RUT').id,
            'document_number': '26.361.396-1',
            'responsability_id': cls.env.ref('l10n_cl_fe.res_IVARI').id,
            'activity_description': cls.env['sii.activity.description'].search([
                ('name', 'ilike', 'EMPRESA DE SERVICIOS INTEGRALES DE INFORMATICA')
            ]).id,
            'acteco_ids': [(6,0,[
                cls.env.ref('l10n_cl_fe.eco_acti_722000').id,
            ])],
            'email': 'jsifontes@openti.cl',
            'phone': '954968318',
            'vat': 'CL263613961',
        })

        ####################################################################################################################
        ####################################################################################################################
        ####################################################################################################################
        ####################################################################################################################
        ####################################################################################################################
        cls.sequence_boleta = cls.env['ir.sequence'].create({
            'name': 'Boleta Electronica(Tests)',
            'implementation': 'no_gap',
            'sii_document_class_id': cls.env['sii.document_class'].search([('name','ilike','Boleta Electrónica')]).id,
            'is_dte': True,
            'forced_by_caf': True,
            'active':True,
            'number_next_actual': cls.number['boleta'],
            'number_increment':1,
            'dte_caf_ids':[(0,0,{
                'company_id': cls.company.id,
                'caf_file': base64.encodestring(
                    open(
                        "/home/abiezer/Documentos/Folios/BoletaElectronica/101-150/FoliosSII76323752391012020871546.xml",
                        "rb").read()
                ),
            })]
        })

        # cls.dte_boleta = cls.env['dte.caf'].create({
        #     'company_id': cls.company.id,
        #     'caf_file': base64.encodestring(
        #         open(
        #             "/home/abiezer/Documentos/Folios/BoletaElectronica/101-150/FoliosSII76323752391012020871546.xml",
        #             "rb").read()
        #     ),
        #     'sequence_id': cls.sequence_boleta.id
        # })

        # Write and Create Journal
        cls.journal_boleta = cls.env['account.journal'].search([('name', '=', 'POS Sale Journal')])

        cls.document_class_boleta = cls.env['account.journal.sii_document_class'].create({
            'journal_id': cls.journal_boleta.id,
            'sii_document_class_id': cls.env['sii.document_class'].search(
                [('name', '=', 'Boleta Electrónica')]).id,
            'sequence_id': cls.sequence.id
        })
        cls.journal_boleta.write({
            'journal_activities_ids': [(6, 0, [
                cls.env.ref('l10n_cl_fe.eco_acti_611090').id,
                cls.env.ref('l10n_cl_fe.eco_acti_620200').id,
                cls.env.ref('l10n_cl_fe.eco_acti_951100').id,
            ])],
            'journal_document_class_ids': [(6, 0, [
                cls.document_class_boleta.id
            ])],
        })
        # Edit POS Config
        cls.pos_config = cls.env.ref('point_of_sale.pos_config_main')
        cls.env.ref('product.list0').write({
            'currency_id': cls.env.ref('base.CLP').id,
        })

        cls.pos_config.write({
            'ticket':True,
            'journal_id': cls.env['account.journal'].search([('name', '=', 'POS Sale Journal')]).id,
            'secuencia_boleta':cls.sequence_boleta.id,
            'marcar':'boleta',
            'journal_ids': [(6,0,[
                cls.env['account.journal'].search([('name','=','Efectivo')]).id,
            ])],
        })
        cls.sequence_guia = cls.env['ir.sequence'].create({
            'name': 'Guia de Despacho (certificacion)',
             'implementation': 'no_gap',
            'is_dte': True,
            'forced_by_caf': True,
            'active': True,
            'number_next_actual': cls.number['guia_despacho'],
            'number_increment': 1,
            'dte_caf_ids': [(0, 0, {
                'company_id': cls.company.id,
                'caf_file': base64.encodestring(
                    open(
                        "/home/abiezer/Documentos/Folios/GuiaDespacho/FoliosSII76323752528120208281838.xml",
                        "rb").read()
                ),
            })],
        })
        cls.pos_config.stock_location_id.write({
            'sii_document_class_id':cls.env['sii.document_class'].search([('sii_code','=',52)]),
            'sequence_id':cls.sequence_guia.id,
        })
        _logger.warning("###########################################################################")
        _logger.warning("###########################################################################")
        _logger.warning(cls.pos_config.stock_location_id.sii_document_class_id)
        _logger.warning(cls.pos_config.stock_location_id.name)
        _logger.warning(cls.pos_config.stock_location_id.usage)
        _logger.warning(cls.pos_config.stock_location_id.sequence_id)
        _logger.warning(cls.pos_config.picking_type_id)
        _logger.warning("###########################################################################")
        _logger.warning("###########################################################################")

        cls.pos_config.open_session_cb()

        cls.pos_config.current_session_id.write({'journal_ids': [(6, 0, [cls.journal_boleta.id])]})

        account_type_rcv = cls.env['account.account.type'].create({'name': 'RCV type', 'type': 'receivable'})

        cls.account = cls.env['account.account'].create({'name': 'Receivable', 'code': 'RCV00' , 'user_type_id': account_type_rcv.id, 'reconcile': True})

        cls.pos_statement = cls.env['account.bank.statement'].create({
            'balance_start': 0.0,
            'balance_end_real': 0.0,
            'date': time.strftime('%Y-%m-%d'),
            'journal_id': cls.journal_boleta.id,
            'company_id': cls.company.id,
            'name': 'pos session test',
        })

        cls.pos_config.current_session_id.write({'statement_ids': [(6, 0, [cls.pos_statement.id])]})

        # cls.pos_session = cls.env['pos.session'].create({
        #     'user_id':cls.env.ref('base.user_admin').id,
        #     'config_id': cls.pos_config.id,
        #     'secuencia_boleta':cls.sequence_boleta.id,
        # })

        # Create POS Order
        cls.pos_order_0 = cls.order = cls.env['pos.order'].create({
            'company_id':cls.company.id,
            'partner_id':cls.customer.id,
            'name':'Boleta Electronica/0001',
            'amount_tax':4750,
            'amount_total':29750,
            'amount_paid': 0,
            'amount_return':0,
            'pricelist_id':cls.env.ref('product.list0').id,
            'session_id':cls.pos_config.current_session_id.id,
            'sequence_id':cls.sequence_boleta.id,
            'lines':[(0,0,{
                'name':"OL/0001",
                'product_id': cls.product.id,
                'qty':5,
                'price_unit':cls.product.lst_price,
                'tax_ids_after_fiscal_position': [(6, 0, [
                    cls.env.ref('l10n_cl_chart_of_account.1_IVAV_19').id
                ])],
                'price_subtotal':25000,
                'price_subtotal_incl': 29750,
            })],
        })

        # I make a payment to fully pay the order
        context_make_payment = {"active_ids": [cls.pos_order_0.id], "active_id": cls.pos_order_0.id}
        cls.pos_make_payment_0 = cls.env['pos.make.payment'].with_context(context_make_payment).create({
            'amount': 29750.0,
            'journal_id': cls.journal_boleta.id,
        })

        # I click on the validate button to register the payment.
        context_payment = {'active_id': cls.pos_order_0.id}
        cls.pos_make_payment_0.with_context(context_payment).check()

        # cls.env['pos.order.line'].create({
        #     'product_id': cls.product.id,
        #     'qty':5,
        #     'price_unit':cls.product.lst_price,
        #     'tax_ids_after_fiscal_position': [(6, 0, [
        #         cls.env.ref('l10n_cl_chart_of_account.1_IVAV_19').id
        #     ])],
        #     'order_id': cls.order.id,
        #     'price_subtotal':25000,
        #     'price_subtotal_incl': 29750,
        # })
        # cls.order.do_validate()
        # cls.order.do_dte_send_order()
        # cls.order.action_pos_order_paid()
        # cls.order.action_pos_order_done()




        # I close the current session to generate the journal entries
        cls.pos_config.current_session_id.action_pos_session_close()
        #####################################################################################################################
        #####################################################################################################################
        #####################################################################################################################
        #####################################################################################################################

        # Create Invoice
        cls.invoice = cls.env['account.invoice'].create({
            'journal_document_class_id': cls.document_class.id,
            'partner_id': cls.env['res.partner'].search([('name', 'ilike', 'Abiezer')]).id,
            'account_id': cls.env.ref('l10n_cl_chart_of_account.1_410201').id,
        })

        # Create Invoice Lines
        cls.line = cls.env['account.invoice.line'].create({
            'name': cls.product.name,
            'product_id': cls.product.id,
            'quantity': 5,
            'uom_id': cls.env.ref('uom.product_uom_unit').id,
            'account_id': cls.env.ref('l10n_cl_chart_of_account.1_410201').id,
            'price_unit': cls.product.lst_price,
            'invoice_id': cls.invoice.id,
            'invoice_line_tax_ids': [(6, 0, [cls.env.ref('l10n_cl_chart_of_account.1_IVAV_19').id])],
            'price_subtotal':50000,
        })

        # cls.setUpInvoice39()

        #Envio 39
        # cls.invoice_boleta.action_invoice_open()
        # cls.invoice_boleta.do_dte_send_invoice()
        # Envio 39
        # cls.invoice.action_invoice_open()
        # cls.invoice.do_dte_send_invoice()

        # while cls.env['sii.cola_envio'].search([]):
        #     cls.env['sii.cola_envio']._cron_procesar_cola()
        #Envio

    # def test_invoice_state(self):
    #     self.assertEqual(self.invoice.state,'paid')


    def test_validate_signature2(self):
        self.assertEqual(self.firma.state, 'valid')

    # @classmethod
    # def setUpSequence39(cls):


        # Close
        # cls.pos_session.action_pos_session_closing_control()
    # @classmethod
    # def setUpInvoice39(cls):
        # Create Invoice
        # cls.invoice_boleta = cls.env['account.invoice'].create({
        #     'journal_document_class_id': cls.document_class_boleta.id,
        #     'partner_id': cls.customer.id,
        #     'account_id': cls.env.ref('l10n_cl_chart_of_account.1_410201').id,
        # })
        #
        # # Create Invoice Lines
        # cls.line_boleta = cls.env['account.invoice.line'].create({
        #     'name': cls.product.name,
        #     'product_id': cls.product.id,
        #     'quantity': 5,
        #     'uom_id': cls.env.ref('uom.product_uom_unit').id,
        #     'account_id': cls.env.ref('l10n_cl_chart_of_account.1_410201').id,
        #     'price_unit': cls.product.lst_price,
        #     'invoice_id': cls.invoice_boleta.id,
        #     'invoice_line_tax_ids': [(6, 0, [cls.env.ref('l10n_cl_chart_of_account.1_IVAV_19').id])],
        #     'price_subtotal': 50000,
        # })

    # @classmethod
    # def setUpPosOrder(cls):
    #     cls.pos_config = cls.env['pos.config'].search([('id', '=', 1)])
        # cls.pos_config.write({
        #     'ticket':True,
        #     'journal_id': cls.env['account.journal'].search([('name', '=', 'POS Sale Journal')]).id,
        # })
