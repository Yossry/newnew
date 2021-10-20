from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    qty_done_sign = fields.Float(string="Qty Done", compute="_compute_qty_done")

    def _compute_qty_done(self):
        for record in self:
            record['qty_done_sign'] = 0

            if record.picking_code == 'incoming':
                record['qty_done_sign'] = record.qty_done

            elif record.picking_code == 'outgoing':
                record['qty_done_sign'] = -record.qty_done

            elif record.location_id.usage == 'internal' and record.location_dest_id.usage != 'internal':
                record['qty_done_sign'] = -record.qty_done

            elif record.location_id.usage != 'internal' and record.location_dest_id.usage == 'internal':
                record['qty_done_sign'] = record.qty_done

            elif record.location_id.usage == 'internal' and record.location_dest_id.usage == 'internal':
                record['qty_done_sign'] = record.qty_done
