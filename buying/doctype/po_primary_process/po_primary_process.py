# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class POPrimaryProcess(Document):
	def get_details(self):
		jo=frappe.get_doc('Job Order',self.job_order)
		joc=jo.get('primary_process_costing')
		for j in joc:
			c_obj=self.append('primary_process_details',{})
			c_obj.job_order=self.job_order
			c_obj.part_name=jo.part_name
			c_obj.drawing_no=jo.drawing_no
			c_obj.qty=jo.qty
			c_obj.po_number=jo.po_no
			c_obj.batch_no=jo.batch_no
			c_obj.type=j.type
			c_obj.vendor=j.vendor
			c_obj.currency=j.currency
			c_obj.mark_percent=j.mark_percent
			c_obj.price_with_markup=j.price_with_markup
			c_obj.quote_ref=j.quote_ref
			c_obj.spec=j.spec
			c_obj.unit_cost=j.unit_cost

		return "Done"

@frappe.whitelist()
def make_purchase_order(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.ignore_pricing_rule = 1
		target.run_method("set_missing_values")
		target.run_method("get_schedule_dates")
		target.run_method("calculate_taxes_and_totals")

	def update_item(obj, target, source_parent):
		target.conversion_factor = 1

	doclist = get_mapped_doc("PO Primary Process", source_name,		{
		"PO Primary Process": {
			"doctype": "Purchase Order",
			"field_map": [
				["supplier", "supplier"],
			],
			"validation": {
				"docstatus": ["=", 1],
			}
		},
		"PM Costing Details": {
			"doctype": "Purchase Order Item",
			"field_map": [
				["drawing_no", "item_code"],
				["part_name", "item_name"],
				["qty", "qty"],
				["uom", "uom"],
			],
			"postprocess": update_item
		},
		"Purchase Taxes and Charges": {
			"doctype": "Purchase Taxes and Charges",
			"add_if_empty": True
		},
	}, target_doc, set_missing_values)

	return doclist

def get_job_order(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql(""" select distinct(parent) from `tabJO Primary Process Details` where parenttype='Job Order' """)


