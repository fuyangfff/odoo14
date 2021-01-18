# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models,_
from odoo.exceptions import UserError

class Parter_Inherit(models.Model):
    _inherit = "res.partner"

    pre = fields.Many2one("account.son",string=u'预付账款')
    rec = fields.Many2one("account.son",string=u'应付账款')
    group = fields.Selection([
        ('in','内关联'),
        ('out','外关联'),
        ('none','非关联')
    ],string=u'集团分类')

class account_son(models.Model):
    _name = "account.son"

    code_num = fields.Char(string=u'代号')
    name = fields.Char(string=u'名称',default='New')
    clas = fields.Char(string=u'分类')

class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('sure', '已确认')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)


    def button_sure(self):
        self.write({'state': 'sure'})

class SaleOrderInherit(models.Model):
    _inherit = "sale.order"





    @api.onchange('requisition_id')
    def _onchange_requisit_id(self):
        if not self.requisition_id:
            return

        self = self.with_company(self.company_id)
        requisition = self.requisition_id
        if self.partner_id:
            partner = self.partner_id
        else:
            partner = requisition.vendor_id
        payment_term = partner.property_supplier_payment_term_id

        FiscalPosition = self.env['account.fiscal.position']
        fpos = FiscalPosition.with_company(self.company_id).get_fiscal_position(partner.id)

        self.partner_id = partner.id
        self.fiscal_position_id = fpos.id
        self.payment_term_id = payment_term.id,
        self.company_id = requisition.company_id.id
        self.currency_id = requisition.currency_id.id
        if not self.origin or requisition.name not in self.origin.split(', '):
            if self.origin:
                if requisition.name:
                    self.origin = self.origin + ', ' + requisition.name
            else:
                self.origin = requisition.name
        # self.notes = requisition.description
        self.date_order = fields.Datetime.now()

        if requisition.type_id.line_copy != 'copy':
            return

        # Create PO lines if necessary
        order_lines = []
        for line in requisition.line_ids:
            # Compute name
            product_lang = line.product_id.with_context(
                lang=partner.lang,
                partner_id=partner.id
            )
            name = product_lang.display_name
            if product_lang.description_purchase:
                name += '\n' + product_lang.description_purchase

            # Compute taxes
            taxes_ids = fpos.map_tax(
                line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id)).ids

            # Compute quantity and price_unit
            if line.product_uom_id != line.product_id.uom_po_id:
                product_qty = line.product_uom_id._compute_quantity(line.product_qty, line.product_id.uom_po_id)
                price_unit = line.product_uom_id._compute_price(line.price_unit, line.product_id.uom_po_id)
            else:
                product_qty = line.product_qty
                price_unit = line.price_unit

            if requisition.type_id.quantity_copy != 'copy':
                product_qty = 0

            # Create PO line
            order_line_values = {
                'name': name, 'product_uom_qty': product_qty, 'price_unit': price_unit,
                'tax_id': taxes_ids, 'product_id': line.product_id.id, 'product_uom': line.product_id.uom_po_id.id}
            order_lines.append((0, 0, order_line_values))
        self.order_line = order_lines

class SaleOrderLineInherit(models.Model):
    _inherit = "sale.order.line"

    customer_lead = fields.Float(
        'Lead Time', default=0.0,
        help="Number of days between the order confirmation and the shipping of the products to the customer")

