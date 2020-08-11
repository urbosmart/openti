# -*- coding: utf-8 -*-
from odoo.tests.common import SingleTransactionCase, tagged
import logging
import base64
import datetime
from odoo.addons.openti.tests.test_l10n_cl_fe import Test_l10n_cl_fe
_logger = logging.getLogger(__name__)

@tagged("tecnopti")
class Test_Ticket_l10n_cl_fe(Test_l10n_cl_fe):
    def setUpClass(cls):
        super(Test_Ticket_l10n_cl_fe, cls).setUpClass()
        cls.setUpSequence39()
        _logger.warning("###########################################################")
        _logger.warning("###########################################################")
        _logger.warning(cls.sequence39)
        _logger.warning("###########################################################")
        _logger.warning("###########################################################")
