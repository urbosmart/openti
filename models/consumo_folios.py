# -*- coding: utf-8 -*-
from odoo import fields, models, api, tools
from odoo.tools.translate import _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
import logging
from lxml import etree
from lxml.etree import Element, SubElement
import pytz
import logging
_logger = logging.getLogger(__name__)
try:
    from facturacion_electronica import facturacion_electronica as fe
    from facturacion_electronica.consumo_folios import ConsumoFolios as CF
except Exception as e:
    _logger.warning("Problema al cargar Facturación electrónica: %s" % str(e))


class ConsumoFoliosInherit(models.Model):
    _inherit = "account.move.consumo_folios"

    def _get_resumenes(self):
        grupos = {}
        recs = self._get_moves()
        for r in recs:
            grupos.setdefault(r.document_class_id.sii_code, [])
            grupos[r.document_class_id.sii_code].append(r.with_context(tax_detail=True)._dte())
        for r in self.anulaciones:
            grupos.setdefault(r.document_class_id.sii_code, [])
            for i in range(r.rango_inicio, r.rango_final+1):
                grupos[r.document_class_id.sii_code].append({
                    "Encabezado": {
                        "IdDoc": {
                            "Folio": i,
                            "FechaEmis": r.fecha_inicio,
                            "Anulado": True,
                        }
                    }
                })
        datos = {
            "resumen": False,
            "FchInicio": self.fecha_inicio,
            "FchFinal": self.fecha_final,
            "SecEnvio": self.sec_envio,
            "Correlativo": self.correlativo,
            "Documento": [{'TipoDTE': k, 'documentos': v} for k, v in grupos.items()]
        }
        import pdb; pdb.set_trace()
        resumenes = CF(datos)._get_resumenes()
        return resumenes


    def _get_moves(self):
        recs = super(ConsumoFolios, self)._get_moves()
        current = self.fecha_inicio.strftime(DTF) #+ ' 00:00:00'
        tz = pytz.timezone('America/Santiago')
        tz_current = tz.localize(datetime.strptime(current, DTF)).astimezone(pytz.utc)
        current = tz_current.strftime(DTF)
        next_day = (self.fecha_inicio + relativedelta.relativedelta(days=1)).strftime(DTF)
        orders_array = self.env['pos.order'].search(
            [
             ('invoice_id' , '=', False),
             ('sii_document_number', 'not in', [False, '0']),
             ('document_class_id.sii_code', 'in', [39, 41, 61]),
             ('date_order','>=', current),
             ('date_order','<', next_day),
            ]
        ).with_context(lang='es_CL')
        for order in orders_array:
            recs.append(order)
        return recs
