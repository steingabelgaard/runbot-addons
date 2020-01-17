# -*- coding: utf-8 -*-
# Copyright 2020 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class RunbotBranch(models.Model):

    _inherit = 'runbot.branch'

    branch_url = fields.Char(compute='_get_branch_url')

    @api.multi
    def _get_branch_url(self):
        _branch_urls = super(RunbotBranch, self)._get_branch_url(None, None)
        for branch in self:
            if not 'bitbucket' in branch.repo_id.base:
                branch.branch_url = _branch_urls[branch.id]
            else:
                if branch.branch_name.isdigit():
                    branch.branch_url = "https://%s/pull-requests/%s" % (
                        branch.repo_id.base, branch.branch_name)
                else:
                    branch.branch_url = ("https://%s/branch/%s?dest=%s" % (
                        branch.repo_id.base, branch.branch_name,branch.branch_name.split('-')[0]))
