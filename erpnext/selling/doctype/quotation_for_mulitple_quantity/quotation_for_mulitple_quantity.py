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

class QuotationforMulitpleQuantity(Document):
	def validate(self):
		self.check_item_table()
		self.validate_for_items()
		self.check_rates()
		self.update_costings()#update names of quotation anand
		
	def check_item_table(self):
		if not self.get('multiple_quantity_item'):
			frappe.throw(_("Please enter item details"))

	def validate_for_items(self):
		chk_dupl_itm = []
		for d in self.get('multiple_quantity_item'):
			if [cstr(d.item_code),cstr(d.description)] in chk_dupl_itm:
				frappe.throw(_("Item {0} with same description entered twice").format(d.item_code))
			else:
				chk_dupl_itm.append([cstr(d.item_code),cstr(d.description)])

	def check_rates(self):
                for d in self.get('multiple_quantity_item'):
                        if 0 in [d.r_qty1,d.r_qty2,d.r_qty3]:
                                frappe.throw(_("Please enter rates for Item {0} at row {1}").format(d.item_code,d.idx))

	def set_label(self):
		label=['r_qty1','r_qty2','r_qty3']
		label1=['r_qty_4','r_qty_5','r_qty_6']
		label2=['r_qty_7','r_qty_8','r_qty_9']
		label_dict={}
		label1_dict={}
		label2_dict={}
		i=0	
		qty_data=frappe.db.sql("select from_quantity, to_quantity from `tabQuantity Range` where parent='Range Master' order by idx",as_dict=1)
		if qty_data:
			for qty in qty_data:
				if qty['to_quantity']:
					label_dict.setdefault(label[i],cstr(qty['from_quantity'])+'-'+cstr(qty['to_quantity']))
					label1_dict.setdefault(label1[i],cstr(qty['from_quantity'])+'-'+cstr(qty['to_quantity']))
					label2_dict.setdefault(label2[i],cstr(qty['from_quantity'])+'-'+cstr(qty['to_quantity']))
				else:
					label_dict.setdefault(label[i],'>'+cstr(qty['from_quantity']))
					label1_dict.setdefault(label1[i],'>'+cstr(qty['from_quantity']))
					label2_dict.setdefault(label2[i],'>'+cstr(qty['from_quantity']))
				i=i+1
			self.quantity_lable=json.dumps(label_dict)
			self.qty_label=json.dumps(label1_dict)
			self.t_lable=json.dumps(label2_dict)
			self.rq1='Quantity '+label_dict.get('r_qty1')
			self.rq2='Quantity '+label_dict.get('r_qty2')
			self.rq3='Quantity '+label_dict.get('r_qty3')
		return "Done"

	def get_item_details(self,item_code):
		self.validate_customer()
		multiple_qty=eval(self.quantity_lable)
		for d in self.get('multiple_quantity_item'):
			if d.item_code==item_code:
				d.item_name=frappe.db.get_value('Item',item_code,'item_name')
				d.description=frappe.db.get_value('Item',item_code,'description')
				parent=frappe.db.get_value('Item Price',{'item_code':item_code,'price_list':self.selling_price_list},'name')
				d.r_qty1=frappe.db.get_value('Price List Quantity',{'parent':parent,'range_qty':multiple_qty.get('r_qty1'),'customer_code':self.customer},'rate')
				d.r_qty2=frappe.db.get_value('Price List Quantity',{'parent':parent,'range_qty':multiple_qty.get('r_qty2'),'customer_code':self.customer},'rate')
				d.r_qty3=frappe.db.get_value('Price List Quantity',{'parent':parent,'range_qty':multiple_qty.get('r_qty3'),'customer_code':self.customer},'rate')
		return "Done"

	def validate_customer(self):
		if not self.customer:
			msgprint(_("Please specify: Customer Code. It is needed to fetch Item Details. Please refresh page"),raise_exception=1)

	def on_submit(self):
		self.validate_customer()
		self.create_item_price_list()

	def create_item_price_list(self):
		for data in self.get('multiple_quantity_item'):
			self.sort_quantity(data.item_code,{'r_qty1':data.r_qty1,'r_qty2':data.r_qty2,'r_qty3':data.r_qty3})

	def sort_quantity(self,item_code,rate):
		#rate=sorted(rate)
		if rate:
			for qty in rate:
				self.add_price(qty,rate[qty],item_code)

	 #anand
	def update_costings(self):
		for d in self.get('multiple_quantity_item'):
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


	def add_price(self,qty,rate,item_code):
		multiple_qty=eval(self.quantity_lable)
		if '-' in multiple_qty[qty]:
			value=multiple_qty[qty].split('-')
			for r in range(cint(value[0]),cint(value[1])+1):
				self.create_price_list(r,multiple_qty[qty],item_code,rate)
		else:
			value=multiple_qty[qty].split('>')
			self.create_price_list(value[1],multiple_qty[qty],item_code,rate)

	def create_price_list(self,qty,range_qty,item_code,rate):
		check=frappe.db.sql("""select b.name from `tabItem Price` as a,`tabPrice List Quantity` as b 
			where b.parent=a.name and a.price_list='%s' and a.item_code='%s' 
			and b.customer_code='%s' and quantity='%s' and range_qty='%s'"""%(self.selling_price_list,item_code,self.customer,qty,range_qty),as_list=1)
		if check:
			frappe.db.sql("update `tabPrice List Quantity` set rate='%s',parentfield='item',parenttype='Item Price' where range_qty='%s' and name='%s'"%(rate,range_qty,check[0][0]))
		else:
			parent=frappe.db.get_value('Item Price',{'item_code':item_code,'price_list':self.selling_price_list},'name')
			if not parent:
				parent=self.create_new_price_list(item_code,self.selling_price_list)
			pl=frappe.new_doc('Price List Quantity')
			pl.parent=parent
			pl.customer_code=self.customer
			pl.quantity=qty
			pl.rate=cstr(rate)
			pl.parentfield='item'
			pl.parenttype='Item Price'
			pl.range_qty=range_qty
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
		for item in self.get('multiple_quantity_item'):
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
		for item in self.get('multiple_quantity_item'):
			if item.idx==docname:
				pp_total_price=frappe.db.get_value("Primary Process Costing",item.primary_process_costing,'pp_total')
				item.pp_total_price=pp_total_price
				if pp_total_price:
					self.set_rate()
		return "Done"

	def get_sm_total_price(self,docname):
		for item in self.get('multiple_quantity_item'):
			if item.idx==docname:
				sm_total_price=frappe.db.get_value("Sub Machining Costing",item.sub_machining_costing,'sm_total')
				item.sm_total_price=sm_total_price
				if sm_total_price:
					self.set_rate()
		return "Done"

	def get_sp_total_price(self,docname):
		for item in self.get('multiple_quantity_item'):
			if item.idx==docname:
				sp_total_price=frappe.db.get_value("Secondary Process Costing",item.secondary_process_costing,'sp_total')
				item.sp_total_price=sp_total_price
				if sp_total_price:
					self.set_rate()
		return "Done"

	def set_rate(self):
		for item in self.get('multiple_quantity_item'):
			item.r_qty_4=flt(item.rm_total_price)+flt(item.pp_total_price)+flt(item.sm_total_price)+flt(item.sp_total_price)+flt(item.r_qty1)
			item.r_qty_5=flt(item.rm_total_price)+flt(item.pp_total_price)+flt(item.sm_total_price)+flt(item.sp_total_price)+flt(item.r_qty2)
			item.r_qty_6=flt(item.rm_total_price)+flt(item.pp_total_price)+flt(item.sm_total_price)+flt(item.sp_total_price)+flt(item.r_qty3)

	def get_rfq(self,args):
		for d in self.get('multiple_quantity_item'):
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

	doclist = get_mapped_doc("Quotation for Mulitple Quantity", source_name, {
			"Quotation for Mulitple Quantity": {
				"doctype": "Sales Order",
				"validation": {
					"docstatus": ["=", 1]
				}
			},
            "Multiple Quantity Item": {
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
