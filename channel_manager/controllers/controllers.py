from openerp import http
import requests
import json
from openerp.http import Response


class Home(http.Controller):
    @http.route('/test', type='http', auth="none")
    def test(self, **kwargs):
        print kwargs
        return Response("TEST",content_type='text/html;charset=utf-8',status=500)
