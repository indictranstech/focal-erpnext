# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class DOMaterial(Document):
	pass



@frappe.whitelist()
def get_po(source_name, target_doc=None):
	return _get_po(source_name, target_doc)

def _get_po(source_name, target_doc=None, ignore_permissions=False):
	
	doclist = get_mapped_doc("PO Material", source_name, {
			"PO Material": {
				"doctype": "DO Material",
				"field_map": {
					"": "prevdoc_detail_docname",
					"parent": "against_sales_invoice",
					"serial_no": "serial_no"
				}
			},
            "RM Costing Details": {
                "doctype": "RM Costing Details"                    
            }
			
	}, target_doc,ignore_permissions=ignore_permissions)

	return doclist

