# -*- coding: utf-8 -*-
from odoo.tests.common import SingleTransactionCase, tagged
import logging
import base64
import datetime
_logger = logging.getLogger(__name__)

@tagged("tecnopti")
class Test_l10n_cl_fe(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(Test_l10n_cl_fe, cls).setUpClass()
        # Creacion de firma electronica
        file_string = open("/home/abiezer/Documentos/jsanhueza.p12", "rb").read()
        cls.firma = cls.env['sii.firma'].create({
            'name': 'jsanhueza.p12',
            'file_content': base64.encodestring(file_string),
            'password': '72918346'
        })

    def test_create_company(self):
        self.company = self.env['res.company'].search([('id','=',1)])
        self.glosa = self.env['sii.activity.description'].create({
            'name':'EMPRESA DE SERVICIOS INTEGRALES DE INFORMATICA',
            'vat_affected':'SI',
            'active':True,
        })
        self.company.write({
            'name':'Comercializacion Y Servicios Informaticos Sanhueza & Mujica Spa',
            'street':'OHIGGINS #241 DEPTO. #821',
            'city':'Concepción',
            'city_id':self.env.ref('l10n_cl_fe.CL08101').id,
            'country_id':self.env.ref('base.cl').id,
            'state_id':self.env['res.country.state'].search([('code','=','CL08100')]).id,
            'zip':'4030000',
            'dte_service_provider':'SIICERT',
            'dte_resolution_number':'0',
            'dte_resolution_date': datetime.date(2014,8,22),
            'sii_regional_office_id': self.env.ref('l10n_cl_fe.ur_Cop').id,
            'phone': '+56412227164',
            'email': '	contacto@openti.cl',
            'document_type_id': self.env.ref('l10n_cl_fe.dt_RUT'),
            'document_number': '76.323.752-4',
            'responsability_id': self.env.ref('l10n_cl_fe.res_IVARI'),
            'start_date':datetime.date(2014,1,24),
            'company_activities_ids': [(6,0,[
                self.env.ref('l10n_cl_fe.eco_acti_611090').id,
                self.env.ref('l10n_cl_fe.eco_acti_620200').id,
                self.env.ref('l10n_cl_fe.eco_acti_951100').id,
            ])],
            'activity_description':self.glosa.id,
            'currency_id': self.env.ref('base.CLP').id,
            'vat':'CL763237524',
        })

    def test_upload_signature(self):
        self.assertEqual(self.firma.state,'unverified')

    def test_validate_signature1(self):
        self.firma.action_process()
        self.assertEqual(self.firma.state,'incomplete')

    def test_validate_signature2(self):
        self.firma.write({
            'subject_serial_number': '14372265-1',
            'user_ids':[(6,0,[
                self.env.ref('base.user_admin').id,
                self.env.ref('base.user_root').id,
            ])],
            'company_ids':[(6,0,[
                self.env.ref('base.main_company').id,
            ])]
        })
        self.firma.action_process()
        self.assertEqual(self.firma.state, 'valid')

    def test_create_dte_caf(self):
        self.sequence = self.env['ir.sequence'].create({
            'name': 'Factura Electronica(Tests)',
            'implementation': 'no_gap',
            'sii_document_class_id': self.env['sii.document_class'].search([('name', '=', 'Factura Electrónica')]).id,
            'is_dte': True,
        })

    def test_create_dte_caf2(self):
        file_string = open("/home/abiezer/Documentos/Folios/FacturaElectronica/179-188/FoliosSII763237523317920207291220.xml", "rb").read()
        self.dte = self.env['dte.caf'].create({
            'caf_file':base64.encodestring(file_string),
            'sequence_id':self.env['ir.sequence'].search([('name','=','Factura Electronica(Tests)')]).id
        })

    def test_create_journal(self):
        self.journal = self.env['account.journal'].search([('name','=','Customer Invoices')])

        self.document_class = self.env['account.journal.sii_document_class'].create({
            'journal_id': self.journal.id,
            'sii_document_class_id': self.env['sii.document_class'].search(
                [('name', '=', 'Factura Electrónica')]).id,
            'sequence_id': self.env['ir.sequence'].search([('name', '=', 'Factura Electronica(Tests)')]).id
        })
        self.journal.write({
            'journal_activities_ids':[(6,0,[
                self.env.ref('l10n_cl_fe.eco_acti_611090').id,
                self.env.ref('l10n_cl_fe.eco_acti_620200').id,
                self.env.ref('l10n_cl_fe.eco_acti_951100').id,
            ])],
            'journal_document_class_ids': [(6,0,[
                self.document_class.id
            ])],
        })

    def test_create_customer(self):

        self.env['res.partner'].create({
            'name':'Abiezer',
            'street': 'Tucapel 50',
            'city': 'Concepción',
            'city_id': self.env.ref('l10n_cl_fe.CL08101').id,
            'country_id': self.env.ref('base.cl').id,
            'state_id': self.env['res.country.state'].search([('code', '=', 'CL08100')]).id,
            'document_type_id': self.env.ref('l10n_cl_fe.dt_RUT').id,
            'document_number': '26.361.396-1',
            'responsability_id': self.env.ref('l10n_cl_fe.res_IVARI').id,
            'activity_description': self.env['sii.activity.description'].search([
                ('name','ilike', 'EMPRESA DE SERVICIOS INTEGRALES DE INFORMATICA')
            ]).id,
            'acteco_ids': self.env.ref('l10n_cl_fe.eco_acti_722000'),
            'email': 'jsifontes@openti.cl',
            'phone': '954968318'
        })

    # def test_create_invoice(self):
    #     self.env['account.invoice'].create({
    #         'journal_document_class_id': self.env['account.journal.sii_document_class'].search([('name','ilike','Factura Electrónica: Factura Electronica(Tests)')]),
    #         'partner_id':
    #     })