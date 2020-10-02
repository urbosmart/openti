from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _

class CommissionsInvoiceClearence(models.Model):
    _name = 'commissions.invoice.clearence'

    TipoMovim = fields.Selection([
        ('C','Comisiones'),
        ('O','Otros')
        ],
        string="Tipo de Movimiento"
    )
    Glosa = fields.Char(string="Glosa")
    TasaComision = fields.Integer(string="Tasa de Comision")
    ValComNeto = fields.Integer(string="Valor Neto de Comision")
    ValComExe = fields.Integer(string="Valor de Comsiones Exentas")
    ValComIVA = fields.Integer(string="Valor de Comisiones Afectas")
