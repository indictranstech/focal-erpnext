# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class POMachining(Document):
	def get_details(self):
		jo=frappe.get_doc('Job Order',self.job_order)
		joc=jo.get('sub_machining_costing')
		for j in joc:
			c_obj=self.append('sub_machining_details',{})
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
			c_obj.price=j.price

		return "done"

def get_job_order(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql(""" select distinct(parent) from `tabJO Machining Details` where parenttype='Job Order' """)



