# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr,cint
from frappe import _, msgprint, throw
import json

class RangeMaster(Document):
	def validate(self):
		self.validate_range()#anand
		#self.check_duplicate()

	def validate_range(self):
		range_count=0
		ranges_list=[]
		from_qty1=0 #temperory variable specifies from_quantity for 1st range
		to_qty1=0 #temperory variable specifies to_quantity for 1st range
		from_qty2=0 #temperory variable specifies from_quantity for 2nd range
		to_qty2=0 #temperory variable specifies to_quantity for 2nd range
		flag=0
		#no_of_ranges=len(self.get('range'))
		for data in self.get('range'):
			range_count=range_count+1
			Ranges=cstr(data.from_quantity)+'-'+cstr(data.to_quantity)
			frappe.errprint(flag)
			if not len(self.get('range'))==3:
				frappe.throw('Number of Quantity Ranges should be Three')	
			elif not data.from_quantity:
				frappe.throw('From Quantity cant be left blank')
			elif flag==1:
				frappe.throw('Range %s cant be added as previous To Quantity for #%s left blank'%(Ranges,range_count-1))
			elif Ranges in ranges_list:
				frappe.throw('Range %s already Specified'%(Ranges))
			elif (range_count!=1):
				if (from_qty1<= data.from_quantity <=to_qty1) or (from_qty1 <= data.to_quantity <=to_qty1) or (from_qty2<=data.to_quantity<=to_qty2) or (from_qty2 <= data.from_quantity <=to_qty2):
					frappe.throw('You selected Range %s which is within range difined in above'%(Ranges))
			elif (data.to_quantity) and (data.from_quantity >= data.to_quantity):
				frappe.throw('From Quantity must be less than and not equal TO (To Quantity)')
			elif (range_count==2 and (data.from_quantity != to_qty1+1)) or (range_count==3 and (data.from_quantity != to_qty2+1)):
				frappe.throw('Please Increment From Quantity for(#%s)'%(range_count))
			
			ranges_list.append(Ranges)
			if not data.to_quantity:
				flag=1
			elif range_count==1:
				from_qty1=data.from_quantity
				to_qty1=data.to_quantity
			elif range_count==2:
				from_qty2=data.from_quantity
				to_qty2=data.to_quantity
			
	def on_update(self):
		label=['r_qty1','r_qty2','r_qty3']
		label_dict={}
		i=0
		for d in self.get('range'):
			if not d.to_quantity:
				frappe.db.sql("update `tabDocField` set label='%s' where parent='Multiple Quantity Item' and fieldname='%s'"%('Qty >'+cstr(d.from_quantity),label[i]),debug=1)
			else:	
				frappe.db.sql("update `tabDocField` set label='%s' where parent='Multiple Quantity Item' and fieldname='%s'"%('Qty '+cstr(d.from_quantity)+'-'+cstr(d.to_quantity),label[i]),debug=1)
			i=i+1
		frappe.db.commit()
		self.change_label_for_singular()

	def change_label_for_singular(self):
		values=frappe.db.sql("select value,field from `tabSingles` where field in ('qty1','qty2','qty3','qty4','qty5') order by field",as_list=1)
		if len(values)==5:
			for qty in values:
				frappe.db.sql("update `tabDocField` set label='%s' where parent='Multiple Qty Item' and fieldname='%s'"%('QTY '+qty[0],qty[1]))

	def check_duplicate(self):
		quantity=[self.qty1,self.qty2,self.qty3,self.qty4,self.qty5]
		for qty in quantity:
			if quantity.count(qty)>1:
				frappe.throw(_("Duplicate quantities are not allowed"))
