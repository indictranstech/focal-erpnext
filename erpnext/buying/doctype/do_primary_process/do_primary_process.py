# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class DOPrimaryProcess(Document):
	pass
	
@frappe.whitelist()
def get_po(source_name, target_doc=None):
	return _get_po(source_name, target_doc)

def _get_po(source_name, target_doc=None, ignore_permissions=False):
	
	doclist = get_mapped_doc("PO Primary Process", source_name, {
			"PO Primary Process": {
				"doctype": "DO Primary Process",
			},
            "PM Costing Details": {
                "doctype": "PM Costing Details"                    
            }
			
	}, target_doc,ignore_permissions=ignore_permissions)

	return doclist