from openerp import api, models
from openerp.report import report_sxw
# Student Status Report (students on probation)

class report_consulta(models.AbstractModel):
	_name = 'report.hotel_folio.report_folio'
	@api.multi
	def render_html(self,data=None):
		report_obj = self.env['report']
		report = report_obj._get_report_from_name('hotel_folio.report_folio')
		docargs = {
			'doc_ids': self._ids,
			'doc_model': report.model,
			'docs': self,
		}
		return report_obj.render('hotel_folio.report_folio', docargs)
