# -*- coding: utf-8 -*-

import logging
import psycopg2
from odoo import api, fields, models
from odoo.tools import mute_logger

_logger = logging.getLogger('base.partner.merge')


class MergePartnerAutomatic(models.TransientModel):
    _inherit = 'base.partner.merge.automatic.wizard'
    _description = 'Merge Partner Wizard'

    @api.model
    def _update_foreign_keys(self, src_partners, dst_partner):
        """ Update all foreign key from the src_partner to dst_partner. All many2one fields will be updated.
            :param src_partners : merge source res.partner recordset (does not include destination one)
            :param dst_partner : record of destination res.partner
        """
        _logger.debug('_update_foreign_keys for dst_partner: %s for src_partners: %s', dst_partner.id, str(src_partners.ids))

        # find the many2one relation to a partner
        Partner = self.env['res.partner']
        relations = self._get_fk_on('res_partner')

        self.flush()

        for table, column in relations:
            if 'base_partner_merge_' in table:  # ignore two tables
                continue

            # get list of columns of current table (exept the current fk column)
            query = "SELECT column_name FROM information_schema.columns WHERE table_name LIKE '%s'" % (table)
            self._cr.execute(query, ())
            columns = []
            for data in self._cr.fetchall():
                if data[0] != column:
                    columns.append(data[0])

            # do the update for the current table/column in SQL
            if len(columns) != 0:
                query_dic = {
                    'table': table,
                    'column': column,
                    'value': columns[0],
                }
                if len(columns) <= 1:
                    # unique key treated
                    query = """
                        UPDATE "%(table)s" as ___tu
                        SET "%(column)s" = %%s
                        WHERE
                            "%(column)s" = %%s AND
                            NOT EXISTS (
                                SELECT 1
                                FROM "%(table)s" as ___tw
                                WHERE
                                    "%(column)s" = %%s AND
                                    ___tu.%(value)s = ___tw.%(value)s
                            )""" % query_dic
                    for partner in src_partners:
                        self._cr.execute(query, (dst_partner.id, partner.id, dst_partner.id))
                else:
                    try:
                        with mute_logger('odoo.sql_db'), self._cr.savepoint():
                            query = 'UPDATE "%(table)s" SET "%(column)s" = %%s WHERE "%(column)s" IN %%s' % query_dic
                            self._cr.execute(query, (dst_partner.id, tuple(src_partners.ids),))

                            # handle the recursivity with parent relation
                            if column == Partner._parent_name and table == 'res_partner':
                                query = """
                                    WITH RECURSIVE cycle(id, parent_id) AS (
                                            SELECT id, parent_id FROM res_partner
                                        UNION
                                            SELECT  cycle.id, res_partner.parent_id
                                            FROM    res_partner, cycle
                                            WHERE   res_partner.id = cycle.parent_id AND
                                                    cycle.id != cycle.parent_id
                                    )
                                    SELECT id FROM cycle WHERE id = parent_id AND id = %s
                                """
                                self._cr.execute(query, (dst_partner.id,))
                                # NOTE JEM : shouldn't we fetch the data ?
                    except psycopg2.Error:
                        # updating fails, most likely due to a violated unique constraint
                        # keeping record with nonexistent partner_id is useless, better delete it
                        query = 'DELETE FROM "%(table)s" WHERE "%(column)s" IN %%s' % query_dic
                        self._cr.execute(query, (tuple(src_partners.ids),))

        self.invalidate_cache()
