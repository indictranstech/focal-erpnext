# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr,cint,flt
from frappe.model.mapper import get_mapped_doc
from frappe import _,msgprint
from erpnext.controllers.selling_controller import SellingController
import json

class MultipleQty(Document):
	def validate(self):
		self.check_item_table()
		self.check_label()
		self.validate_for_items()
		self.check_rates()
		self.update_costings()
		
	def check_item_table(self):
		if not self.get('multiple_qty_item'):
			frappe.throw(_("Please enter item details"))

	def check_label(self):
		if not self.quantity_lable:
			frappe.throw(_("Please mention quantites in Range Master"))

	def validate_for_items(self):
                chk_dupl_itm = []
                for d in self.get('multiple_qty_item'):
                        if [cstr(d.item_code),cstr(d.description)] in chk_dupl_itm:
                                frappe.throw(_("Item {0} with same description entered twice").format(d.item_code))
                        else:
                                chk_dupl_itm.append([cstr(d.item_code),cstr(d.description)])
	def check_rates(self):
		for d in self.get('multiple_qty_item'):
			if 0 in [d.qty1,d.qty2,d.qty3,d.qty4,d.qty5]:
				frappe.throw(_("Please enter rates for Item {0} at row {1}").format(d.item_code,d.idx))



	def update_costings(self):
		for d in self.get('multiple_qty_item'):
			if d.raw_material_costing:
				frappe.db.set_value("Raw Material Cost Sheet", d.raw_material_costing,
				 "from_quotation",self.name)
			if d.primary_process_costing:
				frappe.db.set_value("Primary Process Costing", d.primary_process_costing,
				 "from_quotation",self.name)
			if d.secondary_process_costing:
				frappe.db.set_value("Secondary Process Costing", d.secondary_process_costing,
				 "from_quotation",self.name)
			if d.sub_machining_costing:
				frappe.db.set_value("Sub Machining Costing", d.sub_machining_costing,
				 "from_quotation",self.name)

	def set_label(self):
		label1=['qty6','qty7','qty8','qty9','qty10']
		label2=['qty11','qty12','qty13','qty14','qty15']
		label_dict={}
		label1_dict={}
		label2_dict={}
		labels=''
		i=0
		args=frappe.db.sql("select field,value from `tabSingles` where doctype='Range Master' and field in('qty1','qty2','qty3','qty4','qty5')",as_list=1)
		for s in range(0,len(args)):
			if args[s][1]:
				label_dict.setdefault(args[s][0],args[s][1])
				label1_dict.setdefault(label1[i],args[s][1])
				label2_dict.setdefault(label2[i],args[s][1])
			i+=1	
		self.quantity_lable=json.dumps(label_dict)
		self.qty_label=json.dumps(label1_dict)
		self.t_label=json.dumps(label2_dict)
		self.q1=label_dict['qty1']
		self.q2=label_dict['qty2']
		self.q3=label_dict['qty3']
		self.q4=label_dict['qty4']
		self.q5=label_dict['qty5']
		return "Done"

	def get_item_details(self,item_code):
		self.validate_customer()
		multiple_qty=eval(self.quantity_lable)
		for d in self.get('multiple_qty_item'):
			if d.item_code==item_code:
				d.item_name=frappe.db.get_value('Item',item_code,'item_name')
				d.description=frappe.db.get_value('Item',item_code,'description')
				parent=frappe.db.get_value('Item Price',{'item_code':item_code,'price_list':self.selling_price_list},'name')
				d.qty1=frappe.db.get_value('Singular Price List',{'parent':parent,'quantity':multiple_qty.get('qty1'),'customer_code':self.customer},'rate') or ''
				d.qty2=frappe.db.get_value('Singular Price List',{'parent':parent,'quantity':multiple_qty.get('qty2'),'customer_code':self.customer},'rate') or ''
				d.qty3=frappe.db.get_value('Singular Price List',{'parent':parent,'quantity':multiple_qty.get('qty3'),'customer_code':self.customer},'rate') or ''
				d.qty4=frappe.db.get_value('Singular Price List',{'parent':parent,'quantity':multiple_qty.get('qty4'),'customer_code':self.customer},'rate') or ''
				d.qty5=frappe.db.get_value('Singular Price List',{'parent':parent,'quantity':multiple_qty.get('qty5'),'customer_code':self.customer},'rate') or ''
		return "Done"

	def validate_customer(self):
		if not self.customer:
			msgprint(_("Please specify: Customer Code. It is needed to fetch Item Details. Please refresh page"),raise_exception=1)

	def on_submit(self):
		self.validate_customer()
		self.create_item_price_list()

	def create_item_price_list(self):
		for data in self.get('multiple_qty_item'):
			self.sort_quantity(data,{'qty1':data.qty1,'qty2':data.qty2,'qty3':data.qty3,'qty4':data.qty4,'qty5':data.qty5})

	def sort_quantity(self,data,rate):
		multiple_qty=eval(self.quantity_lable)
		if rate and multiple_qty:
			for qty in rate:
				self.create_price_list(multiple_qty[qty],rate[qty],data.item_code)

	def create_price_list(self,qty,rate,item_code):
		check=frappe.db.sql("""select b.name from `tabItem Price` as a,`tabSingular Price List` as b 
			where b.parent=a.name and a.price_list='%s' and a.item_code='%s' 
			and b.customer_code='%s' and b.quantity='%s'"""%(self.selling_price_list,item_code,self.customer,qty),as_list=1)
		if check:
			frappe.db.sql("update `tabSingular Price List` set rate='%s',parentfield='singular_price_list',parenttype='Item Price' where quantity='%s' and name='%s'"%(rate,qty,check[0][0]))
		else:
			parent=frappe.db.get_value('Item Price',{'item_code':item_code,'price_list':self.selling_price_list},'name')
			if not parent:
				parent=self.create_new_price_list(item_code,self.selling_price_list)
			pl=frappe.new_doc('Singular Price List')
			pl.parent=parent
			pl.customer_code=self.customer
			pl.quantity=qty
			pl.rate=cstr(rate)
			pl.parentfield='singular_price_list'
			pl.parenttype='Item Price'
			pl.save(ignore_permissions=True)

	def create_new_price_list(self,item_code,price_list):
		npl=frappe.new_doc('Item Price')
		npl.price_list=price_list
		npl.selling=1
		npl.item_code=item_code
		npl.item_name=frappe.db.get_value('Item',item_code,'item_name')
		npl.description=frappe.db.get_value('Item',item_code,'description')
		npl.save(ignore_permissions=True)
		return npl.name

	#anand	
	def get_rm_total_price(self,docname):
		for item in self.get('multiple_qty_item'):
			if item.idx==docname:
				rm_total_price=frappe.db.get_value("Raw Material Cost Sheet",item.raw_material_costing,'rm_total_price')
				spec=frappe.db.get_value("Raw Material Costing Details",{"parent":item.raw_material_costing},'spec')
				spec_type=frappe.db.get_value("Raw Material Costing Details",{"parent":item.raw_material_costing},'type')
				item.rm_total_price=rm_total_price
				item.spec=cstr(spec)+' '+cstr(spec_type)
				if rm_total_price:
					self.set_rate()
		return "Done"

	def get_pp_total_price(self,docname):
		for item in self.get('multiple_qty_item'):
			if item.idx==docname:
				pp_total_price=frappe.db.get_value("Primary Process Costing",item.primary_process_costing,'pp_total')
				item.pp_total_price=pp_total_price
				if pp_total_price:
					self.set_rate()
		return "Done"

	def get_sm_total_price(self,docname):
		for item in self.get('multiple_qty_item'):
			if item.idx==docname:
				sm_total_price=frappe.db.get_value("Sub Machining Costing",item.sub_machining_costing,'sm_total')
				item.sm_total_price=sm_total_price
				if sm_total_price:
					self.set_rate()
		return "Done"

	def get_sp_total_price(self,docname):
		for item in self.get('multiple_qty_item'):
			if item.idx==docname:
				sp_total_price=frappe.db.get_value("Secondary Process Costing",item.secondary_process_costing,'sp_total')
				item.sp_total_price=sp_total_price
				if sp_total_price:
					self.set_rate()
		return "Done"

	def set_rate(self):
		for item in self.get('multiple_qty_item'):
			item.qty6=flt(item.rm_total_price)+flt(item.pp_total_price)+flt(item.sm_total_price)+flt(item.sp_total_price)+flt(item.qty1)
			item.qty7=flt(item.rm_total_price)+flt(item.pp_total_price)+flt(item.sm_total_price)+flt(item.sp_total_price)+flt(item.qty2)
			item.qty8=flt(item.rm_total_price)+flt(item.pp_total_price)+flt(item.sm_total_price)+flt(item.sp_total_price)+flt(item.qty3)
			item.qty9=flt(item.rm_total_price)+flt(item.pp_total_price)+flt(item.sm_total_price)+flt(item.sp_total_price)+flt(item.qty4)
			item.qty10=flt(item.rm_total_price)+flt(item.pp_total_price)+flt(item.sm_total_price)+flt(item.sp_total_price)+flt(item.qty5)
		return "done"

	def get_rfq(self,args):
		for d in self.get('multiple_qty_item'):
			cost_docname=args["parent_cost"]
			cost_child=args["child_docname"]
			field_name=d.get(args["field_name"])
			rfqs=[]
			if field_name:
				cost=frappe.get_doc(cost_docname,field_name).get(cost_child)
				for c in cost:
					if c.quote_ref:
						self.update_rfq_with_quotattion_values(c,args,d)
						rfqs.append(c.quote_ref)
		return rfqs

	def update_rfq_with_quotattion_values(self,c,args,d):
		rfq=frappe.get_doc(args['rfq_doctype'],c.quote_ref)
		rfqc=rfq.append(args['rfq_child'],{})
		rfqc.quotation_no=self.name
		rfqc.mat_spec__type=d.spec
		rfqc.drawing_no=d.item_code
		rfqc.part_no=d.item_name
		if args['rfq_doctype']=='Material RFQ':
			rfqc.mat_spec_type=d.spec
			rfqc.od=cstr(c.od)+' '+cstr(c.od_uom)
			rfqc.id=cstr(c.id)+' '+cstr(c.id_uom)
			rfqc.lg=cstr(c.lg)+' '+cstr(c.lg_uom)
		elif args['rfq_doctype']=='Primary Process RFQ':
			rfqc.primary_process=c.spec
		elif args['rfq_doctype']=='Secondary Process RFQ':
			rfqc.secondary_process=c.spec
		elif args['rfq_doctype']=='Sub Machining RFQ':
			rfqc.sub_machining=c.type
		rfq.save(ignore_permissions=True)
		return "done"

@frappe.whitelist()
def make_sales_order(source_name, target_doc=None):
	return _make_sales_order(source_name, target_doc)

def _make_sales_order(source_name, target_doc=None, ignore_permissions=False):
	customer = _make_customer(source_name, ignore_permissions)

	def set_missing_values(source, target):
		if customer:
			target.customer = customer.name
			target.customer_name = customer.customer_name

		target.ignore_permissions = ignore_permissions
		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")

	doclist = get_mapped_doc("Multiple Qty", source_name, {
			"Multiple Qty": {
				"doctype": "Sales Order",
				"validation": {
					"docstatus": ["=", 1]
				}
			},
			"Multiple Qty Item": {
				"doctype": "Sales Order Item"
			},
			"Sales Taxes and Charges": {
				"doctype": "Sales Taxes and Charges",
				"add_if_empty": True
			},
			"Sales Team": {
				"doctype": "Sales Team",
				"add_if_empty": True
			}
		}, target_doc, set_missing_values, ignore_permissions=ignore_permissions)

	# postprocess: fetch shipping address, set missing values

	return doclist

def _make_customer(source_name, ignore_permissions=False):
	quotation = frappe.db.get_value("Quotation", source_name, ["lead", "order_type"])
	if quotation and quotation[0]:
		lead_name = quotation[0]
		customer_name = frappe.db.get_value("Customer", {"lead_name": lead_name},
			["name", "customer_name"], as_dict=True)
		if not customer_name:
			from erpnext.selling.doctype.lead.lead import _make_customer
			customer_doclist = _make_customer(lead_name, ignore_permissions=ignore_permissions)
			customer = frappe.get_doc(customer_doclist)
			customer.ignore_permissions = ignore_permissions
			if quotation[1] == "Shopping Cart":
				customer.customer_group = frappe.db.get_value("Shopping Cart Settings", None,
					"default_customer_group")

			try:
				customer.insert()
				return customer
			except frappe.NameError:
				if frappe.defaults.get_global_default('cust_master_name') == "Customer Name":
					customer.run_method("autoname")
					customer.name += "-" + lead_name
					customer.insert()
					return customer
				else:
					raise
			except frappe.MandatoryError:
				from frappe.utils import get_url_to_form
				frappe.throw(_("Please create Customer from Lead {0}").format(lead_name))
		else:
			return customer_name

