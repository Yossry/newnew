# -*- coding: utf-8 -*-


from . import models

def pre_init_check(cr):
	from odoo.service import common
	from odoo.exceptions import Warning
	versionInfo = common.exp_version()
	serverSerie =versionInfo.get('server_serie')
	if serverSerie!='14.0':
		raise Warning(
		'Module support Odoo series 14.0, found {}.'.format(serverSerie))
	return True
