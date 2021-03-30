# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date
from lxml import etree
from odoo.tools.translate import _
from odoo.addons.l10n_cl_fe.models.bigint import BigInt
import pytz
import logging
_logger = logging.getLogger(__name__)

from six import string_types

try:
    from facturacion_electronica import facturacion_electronica as fe
except Exception as e:
    _logger.warning("Problema al cargar Facturación electrónica: %s" % str(e))
try:
    from io import BytesIO
except:
    _logger.warning("no se ha cargado io")

try:
    from suds.client import Client
except:
    pass
try:
    import pdf417gen
except ImportError:
    _logger.warning('Cannot import pdf417gen library')
try:
    import base64
except ImportError:
    _logger.warning('Cannot import base64 library')
try:
    from PIL import Image, ImageDraw, ImageFont
except:
    _logger.warning("no se ha cargado PIL")

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    commissions = fields.Many2many(
        'commissions.invoice.clearence',
        string="Comisiones"
    )

    @api.multi
    def _get_printed_report_name(self):
        self.ensure_one()
        report_string = "%s %s" % (self.document_class_id.name, self.sii_document_number)
        return report_string

    def _dte(self, n_atencion=None):
        dte = {}
        invoice_lines = self._invoice_lines()
        dte['Encabezado'] = self._encabezado(
            invoice_lines['MntExe'],
            invoice_lines['no_product'],
            invoice_lines['tax_include']
        )
        lin_ref = 1
        ref_lines = []
        if self.company_id.dte_service_provider == 'SIICERT' and isinstance(n_atencion, string_types) and n_atencion != '' and not self._es_boleta():
            ref_line = {}
            ref_line['NroLinRef'] = lin_ref
            ref_line['TpoDocRef'] = "SET"
            ref_line['FolioRef'] = self.get_folio()
            ref_line['FchRef'] = datetime.strftime(datetime.now(), '%Y-%m-%d')
            ref_line['RazonRef'] = "CASO "+n_atencion+"-" + str(self.sii_batch_number)
            lin_ref = 2
            ref_lines.append(ref_line)
        if self.referencias:
            for ref in self.referencias:
                ref_line = {}
                ref_line['NroLinRef'] = lin_ref
                if not self._es_boleta():
                    if  ref.sii_referencia_TpoDocRef:
                        ref_line['TpoDocRef'] = self._acortar_str(ref.sii_referencia_TpoDocRef.doc_code_prefix, 3) if ref.sii_referencia_TpoDocRef.use_prefix else ref.sii_referencia_TpoDocRef.sii_code
                        ref_line['FolioRef'] = ref.origen
                    ref_line['FchRef'] = ref.fecha_documento or datetime.strftime(datetime.now(), '%Y-%m-%d')
                if ref.sii_referencia_CodRef not in ['','none', False]:
                    ref_line['CodRef'] = ref.sii_referencia_CodRef
                ref_line['RazonRef'] = ref.motivo
                if self._es_boleta():
                    ref_line['CodVndor'] = self.seler_id.id
                    ref_lines['CodCaja'] = self.journal_id.point_of_sale_id.name
                ref_lines.append(ref_line)
                lin_ref += 1
        dte['Detalle'] = invoice_lines['Detalle']
        dte['Comisiones'] = self._get_commissions()
        dte['DscRcgGlobal'] = self._gdr()
        dte['Referencia'] = ref_lines
        dte['CodIVANoRec'] = self.no_rec_code
        dte['IVAUsoComun'] = self.iva_uso_comun
        return dte

    def _get_commissions(self):
        Commissions = {}
        Commissions['TipoMovim'] = self.commissions.TipoMovim
        Commissions['Glosa'] = self.commissions.Glosa
        Commissions['TasaComision'] = self.commissions.TasaComision
        Commissions['ValComNeto'] = self.commissions.ValComNeto
        Commissions['ValComExe'] = self.commissions.ValComExe
        Commissions['ValComIVA'] = self.commissions.ValComIVA

        return Commissions
