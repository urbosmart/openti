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
            'boleta':123,
            'factura_electronica':197,
            'guia_despacho':97,
        }
        # Creacion de firma electronica
        cls.folios = {
            '39':{
                'file': 'FoliosSII7632375239101202010291227.xml',
                'location':'FacFiles/Folios/BoletaElectronica/101-150/'
            },
            '33': {
                'file': 'FoliosSII763237523319720201121333.xml',
                'location': 'FacFiles/Folios/FacturaElectronica/197-209/'
            },
            '52': {
                'file': 'FoliosSII763237525281202010291230.xml',
                'location': 'FacFiles/Folios/GuiaDespacho/81-130/'
            }
        }
        file_string = open("FacFiles/jsanhueza.p12", "rb").read()
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
            'dte_resolution_date': datetime.date(2016, 2, 11).strftime('%Y-%m-%d'),
            'sii_regional_office_id': cls.env.ref('l10n_cl_fe.ur_Cop').id,
            'phone': '+56412227164',
            'email': 'contacto@openti.cl',
            'document_type_id': cls.env.ref('l10n_cl_fe.dt_RUT').id,
            'document_number': '76.323.752-4',
            'responsability_id': cls.env.ref('l10n_cl_fe.res_IVARI').id,
            'start_date': datetime.date(2014, 1, 24).strftime('%Y-%m-%d'),
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
            'active':True,
            'name': 'Factura Electronica(Tests)',
            'implementation': 'no_gap',
            'sii_document_class_id': cls.env['sii.document_class'].search([('sii_code', '=', '33')]).id,
            'is_dte': True,
            'forced_by_caf':True,
            'number_next_actual':cls.number['factura_electronica'],
            'dte_caf_ids': [(0, 0, {
                'company_id':cls.company.id,
                'caf_file': base64.encodestring(open(
                     cls.folios['33']['location'] + cls.folios['33']['file']
                    ,"rb").read()),
                'filename': cls.folios['33']['file'],
            })]
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
            'dte_caf_ids': [(0, 0, {
                'company_id': cls.company.id,
                'caf_file': base64.encodestring(
                    open(
                        cls.folios['39']['location'] + cls.folios['39']['file'],
                        "rb").read()
                ),
                'filename': cls.folios['39']['file'],
            })],
        })
        cls.sequence_boleta.dte_caf_ids[0].load_caf()

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
        cls.env.ref('product.list0').write({
            'currency_id': cls.env.ref('base.CLP').id,
        })


        cls.guia_document = cls.env['sii.document_class'].search([('sii_code', '=', 52)])
        cls.sequence_guia = cls.env['ir.sequence'].create({
            'name': 'Guia de Despacho (certificacion)',
            'sii_document_class_id': cls.guia_document.id,
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
                         cls.folios['52']['location'] + cls.folios['52']['file'],
                        "rb").read()
                ),
                'filename':cls.folios['52']['file'],
            })],
        })

        cls.sequence_guia.dte_caf_ids[0].load_caf()

        cls.stock_location = cls.env['stock.location'].create({
            'name':'Certificacion',
            'usage':'internal',
            'location_id':cls.env.ref('stock.warehouse0').id,
            'sii_document_class_id':cls.guia_document.id,
            'sequence_id':cls.sequence_guia.id,
            'partner_id':cls.env['res.partner'].search([('name', '=', 'Comercializacion Y Servicios Informaticos Sanhueza & Mujica Spa')]).id,
            'company_id':cls.company.id,
            'acteco_ids': [(6, 0, [
                cls.env.ref('l10n_cl_fe.eco_acti_722000').id,
            ])]
        })

        cls.picking_type =  cls.env['stock.picking.type'].create({
            'name':'Pedidos TPV',
            'sequence_id': cls.sequence_guia.id,
            'default_location_src_id':cls.stock_location.id,
            'code':'outgoing',
        })

        cls.pos_config = cls.env.ref('point_of_sale.pos_config_main').copy({
            # 'restore_mode':True,
            'ticket': True,
            'journal_id': cls.env['account.journal'].search([('name', '=', 'POS Sale Journal')]).id,
            'secuencia_boleta': cls.sequence_boleta.id,
            'marcar': 'boleta',
            'journal_ids': [(6, 0, [
                cls.env['account.journal'].search([('name', '=', 'Efectivo')]).id,
                cls.env['account.journal'].search([('name', '=', 'Banco')]).id,
            ])],
            'available_pricelist_ids': [(6, 0, [cls.env.ref('product.list0').id])],
            'pricelist_id': cls.env.ref('product.list0').id,
            # 'pricelist_ids':[cls.env.ref('product.list0').id]
            'picking_type_id': cls.picking_type.id,
            'stock_location_id':cls.stock_location.id,
            'dte_picking':True,
        })

        cls.cash_journal = cls.env['account.journal'].search([('name', '=', 'Efectivo')]).write({
            'default_debit_account_id':cls.env['account.account'].search([('name','=','Efectivo')]).id,
            'default_credit_account_id':cls.env['account.account'].search([('name','=','Efectivo')]).id,
            'loss_account_id':cls.env['account.account'].search([('name','=','Pérdida por Venta Activo')]).id,
            'profit_account_id':cls.env['account.account'].search([('name','=','Ventas de Productos')]).id,
        })

        account_type_rcv = cls.env['account.account.type'].create({'name': 'RCV type', 'type': 'receivable'})

        cls.account = cls.env['account.account'].create({
            'name': 'Receivable',
            'code': 'RCV00' ,
            'user_type_id': account_type_rcv.id,
            'reconcile': True
        })

        cls.pos_statement = cls.env['account.bank.statement'].create({
            'balance_start': 0.0,
            'balance_end_real': 0.0,
            'date': time.strftime('%Y-%m-%d'),
            'journal_id': cls.env['account.journal'].search([('name','=','Efectivo')]).id,
            'company_id': cls.company.id,
            'name': 'pos session test',
        })

        cls.pos_config.open_session_cb()

        cls.pos_config.current_session_id.write({
            'statement_ids': [(6, 0, [cls.pos_statement.id])],
            'secuencia_boleta': cls.sequence_boleta.id,
        })

        # Create POS Order
        cls.pos_order_0 = cls.env['pos.order'].create({
            'sii_document_number': cls.sequence_boleta.number_next_actual,
            'document_class_id':cls.env['sii.document_class'].search([('sii_code', '=', 39)]).id,
            'company_id':cls.company.id,
            'partner_id':cls.customer.id,
            'name':'Boleta Electronica/0001',
            'amount_tax':9500,
            'amount_total':50000,
            'amount_paid': 0,
            'amount_return':0,
            'pricelist_id':cls.env.ref('product.list0').id,
            'session_id':cls.pos_config.current_session_id.id,
            'sequence_id':cls.sequence_boleta.id,
            'lines':[(0,0,{
                'name':"OL/0002",
                'product_id': cls.product.id,
                'qty':5,
                'price_unit':cls.product.lst_price,
                'tax_ids': [(6, 0, [
                    cls.env.ref('l10n_cl_chart_of_account.1_IVAV_19').id,
                ])],
                'tax_ids_after_fiscal_position': [(6, 0, [
                    cls.env.ref('l10n_cl_chart_of_account.1_IVAV_19').id,
                ])],
                'price_subtotal':50000,
                'price_subtotal_incl': 50000,
            })],
        })

        # I make a payment to fully pay the order
        context_make_payment = {"active_ids": [cls.pos_order_0.id], "active_id": cls.pos_order_0.id}
        cls.pos_make_payment_0 = cls.env['pos.make.payment'].with_context(context_make_payment).create({
            'amount': 50000,
            'journal_id': cls.env['account.journal'].search([('name','=','Efectivo')]).id,
        })

        cls.sequence_boleta.dte_caf_ids[0].load_caf()
        cls.sequence_guia.dte_caf_ids[0].load_caf()

        if not cls.sequence_guia.dte_caf_ids[0].caf_string:
            cls.sequence_guia.dte_caf_ids[0].caf_string = base64.b64decode(cls.sequence_guia.dte_caf_ids[0].caf_file).decode("ISO-8859-1")

        # I click on the validate button to register the payment.


        #####################################################################################################################
        #####################################################################################################################
        #####################################################################################################################
        #####################################################################################################################

        # Create Invoice
        # cls.invoice = cls.env['account.invoice'].create({
        #     'journal_document_class_id': cls.document_class.id,
        #     'partner_id': cls.env['res.partner'].search([('name', 'ilike', 'Abiezer')]).id,
        #     'account_id': cls.env.ref('l10n_cl_chart_of_account.1_410201').id,
        #     'document_class_id': cls.env['sii.document_class'].search([('sii_code', '=', 33)]).id,
        #     'forma_pago':'1',
        #     'date_invoice':datetime.date.today().strftime('%Y-%m-%d'),
        #     'date_due':datetime.date.today().strftime('%Y-%m-%d'),
        # })
        #
        # # Create Invoice Lines
        # cls.line = cls.env['account.invoice.line'].create({
        #     'name': cls.product.name,
        #     'product_id': cls.product.id,
        #     'quantity': 5,
        #     'uom_id': cls.env.ref('uom.product_uom_unit').id,
        #     'account_id': cls.env.ref('l10n_cl_chart_of_account.1_410201').id,
        #     'price_unit': cls.product.lst_price,
        #     'invoice_id': cls.invoice.id,
        #     'invoice_line_tax_ids': [(6, 0, [cls.env.ref('l10n_cl_chart_of_account.1_IVAV_19').id])],
        #     'price_subtotal':50000,
        # })

        # Envio 33
        # cls.sequence.get_caf_files(cls.number['factura_electronica'])
        # cls.sequence.dte_caf_ids[0].load_caf()
        # cls.invoice.action_invoice_open()
        # cls.invoice.do_dte_send_invoice()

        # while cls.env['sii.cola_envio'].search([]):
        #     _logger.warning("Enviando ...")
        #     for elem in cls.env['sii.cola_envio'].search([]):
        #         _logger.warning(elem.model)
        #         ident = cls.env['{}'.format(elem.model)].search([('id','in',[elem.doc_ids.replace('[','').replace(']','')])])
        #         _logger.warning(ident.name)
        #         _logger.warning(ident.sii_result)
        #     _logger.warning("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4")
        #     _logger.warning("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~4")
        #     cls.env['sii.cola_envio']._cron_procesar_cola()
        #Envio


    # def test_validate_signature2(self):
    #     self.assertEqual(self.firma.state, 'valid')

    def test_enviar_boleta(self):
        self.pos_order_0.do_dte_send()
        # self.pos_order_0.picking_id.do_dte_send()

        context_payment = {'active_ids':[self.pos_config.id],'active_id': self.pos_order_0.id}
        self.pos_make_payment_0.with_context(context_payment).check()

        # I close the current session to generate the journal entries
        self.pos_config.current_session_id.action_pos_session_close()