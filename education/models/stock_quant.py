from odoo import models, fields, _


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def show_related_stock_move_lines(self):
        moves = self.env['stock.move.line'].search(
            ['|', ('location_id', '=', self.location_id.id), ('location_dest_id', '=', self.location_id.id),
             ('product_id', '=', self.product_id.id)])
        if self.lot_id:
            moves = self.env['stock.move.line'].search(
                ['|', ('location_id', '=', self.location_id.id), ('location_dest_id', '=', self.location_id.id),
                 ('product_id', '=', self.product_id.id), ('lot_id', '=', self.lot_id.id)])
        if moves:
            ctx = {}
            ctx['search_default_done'] = 1
            res = {
                'type': 'ir.actions.act_window',
                'name': _('Product Moves'),
                'view_mode': 'tree,form',
                'res_model': 'stock.move.line',
                'domain': [('id', 'in', moves.ids)],
                'target': 'current',
                'context': ctx,
            }

            return res

        return True
