# -*- coding: utf-8 -*-
import collections
from odoo import fields, models, api, tools
from odoo.tools.translate import _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import dateutil.relativedelta as relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
import logging
from lxml import etree
from lxml.etree import Element, SubElement
import pytz
import logging
from odoo.addons.l10n_cl_dte_point_of_sale.models.consumo_folios import ConsumoFolios as cfpo
_logger = logging.getLogger(__name__)
try:
    from facturacion_electronica import facturacion_electronica as fe
    from facturacion_electronica.consumo_folios import ConsumoFolios as CF
except Exception as e:
    _logger.warning("Problema al cargar Facturación electrónica: %s" % str(e))


class ConsumoFolios(models.Model):
    _inherit = "account.move.consumo_folios"

    tipo_operacion = fields.Selection([('utilizados','Utilizados'), ('anulados','Anulados')])
    periodo_tributario = fields.Char(
            string='Periodo Tributario',
            required=True,
            readonly=True,
            states={'draft': [('readonly', False)]},
            default=lambda *a: datetime.now().strftime('%Y-%m'),
        )
    impuestos = fields.One2many(
        'account.move.consumo_folios.impuestos',
       'cf_id',
       string="Detalle Impuestos",
       readonly=True,
       states={'draft': [('readonly', False)]},)
    sec_envio = fields.Integer(
        string="Secuencia de Envío",
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    fecha_inicio = fields.Date(
        string="Fecha Inicio",
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: fields.Date.context_today(self),
    )
    total_neto = fields.Monetary(
        string="Total Neto",
        store=True,
        readonly=True,
        compute='get_totales',)
    total_iva = fields.Monetary(
        string="Total Iva",
        store=True,
        readonly=True,
        compute='get_totales',)
    total_exento = fields.Monetary(
        string="Total Exento",
        store=True,
        readonly=True,
        compute='get_totales',)
    total = fields.Monetary(
        string="Monto Total",
        store=True,
        readonly=True,
        compute='get_totales',)
    total_boletas = fields.Integer(
        string="Total Boletas",
        store=True,
        readonly=True,
        compute='get_totales',)
    detalles = fields.One2many(
        'account.move.consumo_folios.detalles',
       'cf_id',
       string="Detalle Rangos",
       readonly=True,
       states={'draft': [('readonly', False)]},)

    def _get_moves(self):
        recs = super(cfpo, self)._get_moves()
        current = self.fecha_inicio.strftime(DTF) #+ ' 00:00:00'
        tz = pytz.timezone('America/Santiago')
        tz_current = tz.localize(datetime.strptime(current, DTF)).astimezone(pytz.utc)
        # '2020-02-24 03:00:00'
        current = tz_current.strftime(DTF)
        # '2020-02-25 00:00:00'
        next_day = (self.fecha_inicio + relativedelta.relativedelta(days=1)).strftime(DTF)
        # pos.order(143, 142, 141, 140)
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
        # [pos.order(143,), pos.order(142,), pos.order(141,), pos.order(140,)]
        return recs

    def _get_resumenes(self):
        grupos = {}
        # [pos.order(143,), pos.order(142,), pos.order(141,), pos.order(140,)]
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
        resumenes = CF(datos)._get_resumenes()
        return resumenes

    @api.onchange('move_ids', 'anulaciones')
    def _resumenes(self):
        resumenes = self._get_resumenes()

        if self.impuestos and isinstance(self.id, int):
            self._cr.execute("DELETE FROM account_move_consumo_folios_impuestos WHERE cf_id=%s", (self.id,))
            self.invalidate_cache()
        if self.detalles and isinstance(self.id, int):
            self._cr.execute("DELETE FROM account_move_consumo_folios_detalles WHERE cf_id=%s", (self.id,))
            self.invalidate_cache()
        detalles = [[5,],]
        def pushItem(key_item, item, tpo_doc):
            rango = {
                'tipo_operacion': 'utilizados' if key_item == 'RangoUtilizados' else 'anulados',
                'folio_inicio': item['Inicial'],
                'folio_final': item['Final'],
                'cantidad': int(item['Final']) - int(item['Inicial']) +1,
                'tpo_doc': self.env['sii.document_class'].search([('sii_code', '=', tpo_doc)]).id,
            }
            detalles.append([0,0,rango])
        for r, value in resumenes.items():
            if '%s_folios' %str(r) in value:
                Rangos = value[ str(r)+'_folios' ]
                if 'itemUtilizados' in Rangos:
                    for rango in Rangos['itemUtilizados']:
                        pushItem('RangoUtilizados', rango, r)
                if 'itemAnulados' in Rangos:
                    for rango in Rangos['itemAnulados']:
                        pushItem('RangoAnulados', rango, r)
        self.detalles = detalles
        docs = collections.OrderedDict()
        for r, value in resumenes.items():
            if value.get('FoliosUtilizados', False):
                docs[r] = {
                       'tpo_doc': self.env['sii.document_class'].search([('sii_code','=', r)]).id,
                       'cantidad': value['FoliosUtilizados'],
                       'monto_neto': value['MntNeto'],
                       'monto_iva': value['MntIva'],
                       'monto_exento': value['MntExento'],
                       'monto_total': value['MntTotal'],
                       }
        lines = [[5,],]
        for key, i in docs.items():
            i['currency_id'] = self.env.user.company_id.currency_id.id
            lines.append([0,0, i])
        self.impuestos = lines

    @api.multi
    def validar_consumo_folios(self):
        self._validar()
        consumos = self.search([
            ('fecha_inicio', '=', self.fecha_inicio),
            ('state', 'not in', ['draft', 'Rechazado', 'Anulado']),
            ('company_id', '=', self.company_id.id),
            ('id', '!=', self.id),
            ])
        for r in consumos:
            r.state = "Anulado"
        return self.write({'state': 'NoEnviado'})

    def _validar(self):
        datos = self._get_datos_empresa(self.company_id)
        grupos = {}
        recs = self._get_moves()
        for r in recs:
            grupos.setdefault(r.document_class_id.sii_code, [])
            grupos[r.document_class_id.sii_code].append(r)
        for anulaciones in self.anulaciones:
            raise UserError("terminar código anulaciones manuales")
            grupos.setdefault(r.document_class_id.sii_code, [])
            grupos[r.document_class_id.sii_code].append(r)
        datos['ConsumoFolios'] = [{
            "FchInicio": self.fecha_inicio,
            "FchFinal": self.fecha_final,
            "SecEnvio": self.sec_envio,
            "Correlativo": self.correlativo,
            "Documento": [{'TipoDTE': k, 'documentos': v} for k, v in grupos.items()]
        }]
        datos['test'] = True
        ###################################################################
        #                                                                 #
        #######AttributeError: 'str' object has no attribute 'items'#######
        #                                                                 #
        ###################################################################
        result = fe.consumo_folios(datos)[0]
        envio_dte = result['sii_xml_request']
        doc_id = '%s_%s' % (self.tipo_operacion, self.periodo_tributario)
        self.sii_xml_request = self.env['sii.xml.envio'].create({
            'xml_envio': envio_dte,
            'name': doc_id,
            'company_id': self.company_id.id,
        }).id

    @api.onchange('fecha_inicio', 'company_id', 'fecha_final')
    def set_data(self):
        if self.fecha_inicio > fields.Date.context_today(self):
            raise UserError("No puede hacer Consumo de Folios de días futuros")
        self.name = self.fecha_inicio
        self.fecha_final = self.fecha_inicio
        self.move_ids = self.env['account.move'].search([
            ('document_class_id.sii_code', 'in', [39, 41]),
            ('sended','=', False),
            ('date', '=', self.fecha_inicio),
            ('company_id', '=', self.company_id.id),
            ]).ids
        # self.fecha_inicio = datetime.date(2020, 2, 28)
        # self.company_id.id = 1
        consumos = self.env['account.move.consumo_folios'].search_count([
            ('fecha_inicio', '=', self.fecha_inicio),
            ('state', 'not in', ['draft', 'Rechazado']),
            ('company_id', '=', self.company_id.id),
            ])
        if consumos >= 0:
            self.sec_envio = (consumos+1)
        self._resumenes()

    @api.onchange('impuestos')
    @api.depends('impuestos')
    def get_totales(self):
        for r in self:
            total_iva = 0
            total_exento = 0
            total = 0
            total_boletas = 0
            for d in r.impuestos:
                total_iva += d.monto_iva
                total_exento += d.monto_exento
                total += d.monto_total
            if r.detalles:
                _logger.warning("#########################################################################")
                _logger.warning("#########################################################################")
                _logger.warning("there are r.detalles")
                _logger.warning("#########################################################################")
                _logger.warning("#########################################################################")
                for d in r.detalles:
                    if d.tpo_doc.sii_code in [39, 41] and d.tipo_operacion == "utilizados":
                        total_boletas += d.cantidad
            else:
                _logger.warning("#########################################################################")
                _logger.warning("#########################################################################")
                _logger.warning("dont have r.detalles")
                _logger.warning("#########################################################################")
                _logger.warning("#########################################################################")
            r.total_neto = total - total_iva - total_exento
            r.total_iva = total_iva
            r.total_exento = total_exento
            r.total = total
            r.total_boletas = total_boletas



####################################################################################################
####################################################################################################
####################################################################################################
################################ Original files above ######################################
####################################################################################################
####################################################################################################
