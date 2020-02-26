from odoo.tests.common import TransactionCase

class testPosOrderCase(TransactionCase):

    def test_register_open(self):
        """
            In order to test the Point of Sale module, I will open all cash registers through the wizard
            """
        # open all statements/cash registers
        self.env['pos.open.statement'].create({}).open_statement()
