from openerp import http
import requests
import json
from openerp.http import Response
import logging
_logger = logging.getLogger(__name__)


class Home(http.Controller):
    @http.route('/test', type='http', auth="none", csrf=False)
    def test(self, **kwargs):
        print kwargs
        _logger.info(kwargs)
        return Response("TEST",content_type='text/html;charset=utf-8',status=500)
