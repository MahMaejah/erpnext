from __future__ import unicode_literals

from frappe import _


def get_data():
	return {
		#'heatmap': True,
		#'heatmap_message': _('This is based on transactions against this Customer. See timeline below for details'),
		'fieldname': 'school_department',
		'non_standard_fieldnames': {
			'School Items': 'school_department'
		},
		'transactions': [
			{
				'label': _('School Items'),
				'items': ['School Item']
			}
		]
	}
