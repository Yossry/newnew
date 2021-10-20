import base64
import datetime
import io
import re
import requests
import PyPDF2

from PIL import Image
from werkzeug import urls

from odoo import api, fields, models, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import Warning, UserError, AccessError
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import url_for

import requests

class Slide(models.Model):
	_inherit = "slide.slide"
	is_vimeo = fields.Boolean()

	def _find_document_data_from_url(self, url):
		url_obj = urls.url_parse(url)
		#raise UserError(url_obj.ascii_host)
		if url_obj.ascii_host == 'youtu.be':
			return ('youtube', url_obj.path[1:] if url_obj.path else False)

		elif url_obj.ascii_host in ('youtube.com', 'www.youtube.com', 'm.youtube.com'):
			v_query_value = url_obj.decode_query().get('v')
			if v_query_value:
				return ('youtube', v_query_value)

			split_path = url_obj.path.split('/')
			if len(split_path) >= 3 and split_path[1] in ('v', 'embed'):
				return ('youtube', split_path[2])

		elif url_obj.ascii_host in ('player.vimeo.com'):
			r = requests.get('https://vimeo.com/api/oembed.json?url=%s' % url)
			data = r.json()
			return ('vimeo', data)

		expr = re.compile(r'(^https:\/\/docs.google.com|^https:\/\/drive.google.com).*\/d\/([^\/]*)')
		arg = expr.match(url)
		document_id = arg and arg.group(2) or False
		if document_id:
			return ('google', document_id)

		return (None, False)

	def _parse_document_url(self, url, only_preview_fields=False):
		document_source, document_id = self._find_document_data_from_url(url)

		if document_source == 'vimeo':
			vimeo_dict = {}
			vals = {}
			vals['document_id'] = document_id['video_id']
			vals['name'] = document_id['title']
			vals['is_vimeo'] = 1
			vimeo_dict['values'] = vals
			#raise UserError(str(vimeo_dict))
			return vimeo_dict

		elif document_source and hasattr(self, '_parse_%s_document' % document_source):
			return getattr(self, '_parse_%s_document' % document_source)(document_id, only_preview_fields)

		return {'error': _('Unknown document')}

	@api.depends('document_id', 'slide_type', 'mime_type')
	def _compute_embed_code(self):
		base_url = request and request.httprequest.url_root or self.env['ir.config_parameter'].sudo().get_param('web.base.url')
		if base_url[-1] == '/':
			base_url = base_url[:-1]

		for record in self:
			if record.datas and (not record.document_id or record.slide_type in ['document', 'presentation']):
				slide_url = base_url + url_for('/slides/embed/%s?page=1' % record.id)
				record.embed_code = '<iframe src="%s" class="o_wslides_iframe_viewer" allowFullScreen="true" height="%s" width="%s" frameborder="0"></iframe>' % (slide_url, 315, 420)
			elif record.slide_type == 'video' and record.document_id:
				if not record.mime_type and not record.is_vimeo:
					record.embed_code = '<iframe src="//www.youtube.com/embed/%s?theme=light" allowFullScreen="true" frameborder="0"></iframe>' % (record.document_id) #or '<iframe src="https://player.vimeo.com/video/%s" frameborder="0" allow="autoplay; fullscreen" allowfullscreen></iframe>' % (record.document_id)

				elif not record.mime_type and record.is_vimeo:
					record.embed_code = '<iframe src="https://player.vimeo.com/video/%s" frameborder="0" allow="autoplay; fullscreen" allowfullscreen></iframe>' % (record.document_id)

				else:
					record.embed_code = '<iframe src="//drive.google.com/file/d/%s/preview" allowFullScreen="true" frameborder="0"></iframe>' % (record.document_id)
			else:
				record.embed_code = False

	@api.onchange('url')
	def _on_change_url(self):
		self.ensure_one()
		if self.url:
			self.is_vimeo = False
			res = self._parse_document_url(self.url)
			if res.get('error'):
				raise Warning(_('Could not fetch data from url. Document or access right not available:\n%s') % res['error'])

			values = res['values']
			if not values.get('document_id'):
				raise Warning(_('Please enter valid Youtube or Google Doc URL'))

			for key, value in values.items():
				self[key] = value

	def write(self, values):
		if values.get('url') and values['url'] != self.url:
			doc_data = self._parse_document_url(values['url']).get('values', dict())
			for key, value in doc_data.items():
				values.setdefault(key, value)

		if values.get('is_category'):
			values['is_preview'] = True
			values['is_published'] = True

		res = super(Slide, self).write(values)
		if values.get('is_published'):
			self.date_published = datetime.datetime.now()
			self._post_publication()
		
		if 'is_published' in values or 'active' in values:
			self.slide_partner_ids._set_completed_callback()

		return res

