# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, flt, getdate, comma_and,cint
from frappe.model.mapper import get_mapped_doc


class POMaterial(Document):
	def get_details(self):
		jo=frappe.get_doc('Job Order',self.job_order)
		joc=jo.get('raw_material_costing')
		for j in joc:
			c_obj=self.append('raw_material_details',{})
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
			c_obj.od=j.od
			c_obj.od_uom=j.od_uom
			c_obj.id=j.id
			c_obj.id_uom=j.id_uom
			c_obj.lg=j.lg
			c_obj.lg_uom=j.lg_uom
			c_obj.unit_cost=j.unit_cost
			c_obj.price=j.price	
		self.po_no=jo.po_no
		
		return "done"

@frappe.whitelist()
def get_address(supplier):
	supplier_address=frappe.db.get_value('Address',{"supplier":supplier,"is_primary_address":1},"*")
	if supplier_address:
		address=cstr(supplier_address["address_line1"])+'<br>'+cstr(supplier_address["address_line2"])+'<br>'+cstr(supplier_address["city"])+' '+cstr(supplier_address["state"])+'<br>'+cstr(supplier_address["phone"])+'<br>'+cstr(supplier_address["fax"])
		return address
			
@frappe.whitelist()
def make_purchase_order(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.ignore_pricing_rule = 1
		target.run_method("set_missing_values")
		target.run_method("get_schedule_dates")
		target.run_method("calculate_taxes_and_totals")

	def update_item(obj, target, source_parent):
		target.conversion_factor = 1

	doclist = get_mapped_doc("PO Material", source_name,		{
		"PO Material": {
			"doctype": "Purchase Order",
			"field_map": [
				["supplier", "supplier"],
			],
			"validation": {
				"docstatus": ["=", 1],
			}
		},
		"RM Costing Details": {
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
	return frappe.db.sql(""" select distinct(parent) from `tabJO Material Cossting Details` where parenttype='Job Order' """)



