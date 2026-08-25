from odoo import models, fields, api
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class SolidWorksSync(models.AbstractModel):
    """
    Abstract model to handle SolidWorks CAD data synchronization.
    This logic can be called from the controller.
    """
    _name = 'solidworks.sync'
    _description = 'SolidWorks Data Sync Service'

    @api.model
    def process_cad_data(self, data):
        """
        Main entry point for recursive sync.
        :param data: JSON/Dict from SolidWorks
        """
        # Ensure we are in a clean transaction
        return self._sync_item(data)

    def _sync_item(self, item):
        """
        Recursive helper function to sync a single item (Part or Assembly).
        :param item: Dictionary representing a product and its components.
        :return: product.product record
        """
        name = item.get('name')
        default_code = item.get('default_code')
        item_type = item.get('type')  # 'part' or 'assembly'
        uom_name = item.get('uom', 'Units')

        # 1. Ensure Product Exists
        product = self.env['product.product'].search([('default_code', '=', default_code)], limit=1)
        if not product:
            uom_id = self.env['uom.uom'].search([('name', '=', uom_name)], limit=1) or self.env.ref('uom.product_uom_unit')
            product = self.env['product.product'].create({
                'name': name,
                'default_code': default_code,
                'type': 'consu' if item_type == 'part' else 'product', # Standard Odoo 19 mapping
                'uom_id': uom_id.id,
                'uom_po_id': uom_id.id,
            })
            _logger.info("Created new product: %s (%s)", name, default_code)
        else:
            # Optional: Update name if changed
            product.write({'name': name})

        # 2. If Assembly, Create BOM
        if item_type == 'assembly' and 'components' in item:
            bom_lines = []
            for comp_data in item.get('components'):
                # RECURSIVE CALL: Ensure component exists (and its BOM if it's an assembly)
                comp_product = self._sync_item(comp_data)
                
                bom_lines.append((0, 0, {
                    'product_id': comp_product.id,
                    'product_qty': comp_data.get('quantity', 1),
                }))

            # Create NEW BOM with datetime reference
            new_bom = self.env['mrp.bom'].create({
                'product_tmpl_id': product.product_tmpl_id.id,
                'product_id': product.id,
                'code': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'type': 'normal',
                'bom_line_ids': bom_lines,
                'sequence': 1, # Set as priority
            })
            
            # Reset sequence of older BOMs for this product
            other_boms = self.env['mrp.bom'].search([
                ('product_tmpl_id', '=', product.product_tmpl_id.id),
                ('id', '!=', new_bom.id)
            ])
            if other_boms:
                other_boms.write({'sequence': 10})

            _logger.info("Created new BOM for assembly: %s", default_code)

        return product
