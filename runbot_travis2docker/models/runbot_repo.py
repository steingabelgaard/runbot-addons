# coding: utf-8
# © 2015 Vauxoo
#   Coded by: moylop260@vauxoo.com
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import requests

from openerp import _, fields, models, api
from openerp.exceptions import ValidationError, Warning as UserError
from openerp.tools.misc import scan_languages


class RunbotRepo(models.Model):
    _inherit = "runbot.repo"

    is_travis2docker_build = fields.Boolean('Travis to docker build')
    travis2docker_test_disable = fields.Boolean('Test Disable?')
    travis2docker_image = fields.Char(
        default=lambda s: s._default_travis2docker_image(),
    )
    weblate_url = fields.Char(default="https://weblate.odoo-community.org/api")
    weblate_ssh = fields.Char(
        default="ssh://user@webpage.com")
    weblate_token = fields.Char()
    weblate_languages = fields.Char(help="List of code iso of languages E.g."
                                    " en_US,es_ES")

    @api.model
    def _default_travis2docker_image(self):
        return 'vauxoo/odoo-80-image-shippable-auto'

    @api.multi
    @api.constrains('weblate_languages')
    def _check_weblate_languages(self):
        supported_langs = [item[0] for item in scan_languages()]
        supported_langs.extend(set([lang.split('_')[0] for lang in
                                    supported_langs]))
        for record in self.filtered('weblate_languages'):
            langs = record.weblate_languages.split(',')
            for lang in langs:
                lang = lang.strip()
                if lang not in supported_langs:
                    raise ValidationError(_("The language '%s' is not"
                                            "supported" % lang))

    @api.multi
    def weblate_validation(self):
        for record in self:
            if not record.weblate_url or not record.weblate_token:
                return
            session = requests.Session()
            session.headers.update({
                'Accept': 'application/json',
                'User-Agent': 'mqt',
                'Authorization': 'Token %s' % record.weblate_token})
            response = session.get(record.weblate_url)
            response.raise_for_status()
            json = response.json()
            if 'projects' not in json:
                raise ValidationError(_('Response json bad formated'))
            raise UserError(_('Connection with weblate successful'))

    @api.multi
    def cron_weblate(self):
        self.ensure_one()
        if not self.weblate_url or not self.weblate_token:
            return
        branch_ids = self.env['runbot.branch'].search([
            ['repo_id', '=', self.id], ['uses_weblate', '=', True]])
        for branch in branch_ids:
            branch.cron_weblate()
            
    def adm_notify(self, url, payload=None, ignore_errors=False):
        """Return a http request to be sent to adm.steingabelgaard.dk"""
        pass
#         for repo in self:
#             try:
#                 match_object = re.search('([^/]+)/([^/]+)/([^/.]+(.git)?)', repo.base)
#                 if match_object:
#                     url = url.replace(':owner', match_object.group(2))
#                     url = url.replace(':repo', match_object.group(3))
#                     url = url.replace(':type', 'github' if 'github' in repo.base else 'bitbucket')
#                     session = requests.Session()
#                     session.auth = (repo.token,'x-oauth-basic')
#                     session.headers.update({'Accept': 'application/vnd.github.she-hulk-preview+json'})
#                     if payload:
#                         response = session.post(url, data=simplejson.dumps(payload))
#                     else:
#                         response = session.get(url)
#                     response.raise_for_status()
#                     return True
