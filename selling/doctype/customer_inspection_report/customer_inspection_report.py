# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import msgprint, throw, _
from frappe.utils import cstr, flt, getdate, comma_and,cint

class CustomerInspectionReport(Document):
	def get_details(self):
		jo=frappe.get_doc('Job Order',self.job_no)
		self.customer_code=jo.customer_code
		self.part_name=jo.part_name
		self.part_no=jo.part_no
		self.drawing_no=jo.drawing_no
		self.quantity=jo.qty
		self.po_no=jo.po_no
		self.batch_no=jo.batch_no
		self.add_child_toheat(jo.qty)
		return self.quantity

	def on_update(self):
		pass
		#self.validate_measurements()
			
	def validate_measurements(self):
		for d in self.get('measurements'):
			if not d.actual_mesurement:
				frappe.msgprint(_("Please add Measurements for Row {0}").format(d.idx))

	def get_concat_det(self):
		inspector=frappe.db.sql("""select first_name,last_name from `tabUser` where name='%s'"""%(self.inspected_by),as_list=1)
		if inspector:
			self.inspector_name=inspector[0][0] + " " + inspector[0][1]


	def add_child_toheat(self,qty):
		if qty:
			self.set('heat_no_details', [])
			for i in range(0,cint(qty)):
				h = self.append('heat_no_details', {})
				h.idx=i+1

