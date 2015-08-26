# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr,flt
from frappe.model.mapper import get_mapped_doc
from frappe import _

from erpnext.controllers.selling_controller import SellingController

form_grid_templates = {
	"quotation_details": "templates/form_grid/item_grid.html"
}

class Quotation(SellingController):
	tname = 'Quotation Item'
	fname = 'quotation_details'

	def validate(self):
		super(Quotation, self).validate()
		self.set_status()
		self.validate_order_type()
		#self.validate_for_items()
		self.validate_uom_is_integer("stock_uom", "qty")
		self.validate_quotation_to()
		self.update_costings()#update names of quotation anand
		# self.cust_ref_no()

		
	def has_sales_order(self):
		return frappe.db.get_value("Sales Order Item", {"prevdoc_docname": self.name, "docstatus": 1})

	def validate_for_items(self):
		chk_dupl_itm = []
		for d in self.get('quotation_details'):
			if [cstr(d.item_code),cstr(d.description)] in chk_dupl_itm:
				frappe.throw(_("Item {0} with same description entered twice").format(d.item_code))
			else:
				chk_dupl_itm.append([cstr(d.item_code),cstr(d.description)])

	def validate_order_type(self):
		super(Quotation, self).validate_order_type()

		if self.order_type in ['Maintenance', 'Service']:
			for d in self.get('quotation_details'):
				is_service_item = frappe.db.sql("select is_service_item from `tabItem` where name=%s", d.item_code)
				is_service_item = is_service_item and is_service_item[0][0] or 'No'

				if is_service_item == 'No':
					frappe.throw(_("Item {0} must be Service Item").format(d.item_code))
		else:
			for d in self.get('quotation_details'):
				is_sales_item = frappe.db.sql("select is_sales_item from `tabItem` where name=%s", d.item_code)
				is_sales_item = is_sales_item and is_sales_item[0][0] or 'No'

				if is_sales_item == 'No':
					frappe.throw(_("Item {0} must be Sales Item").format(d.item_code))

	def validate_quotation_to(self):
		if self.customer:
			self.quotation_to = "Customer"
			self.lead = None
		elif self.lead:
			self.quotation_to = "Lead"

    #anand
	def update_costings(self):
		for d in self.get('quotation_details'):
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


	def update_opportunity(self):
		for opportunity in list(set([d.prevdoc_docname for d in self.get("quotation_details")])):
			if opportunity:
				frappe.get_doc("Opportunity", opportunity).set_status(update=True)

	def declare_order_lost(self, arg):
		if not self.has_sales_order():
			frappe.db.set(self, 'status', 'Lost')
			frappe.db.set(self, 'order_lost_reason', arg)
			self.update_opportunity()
		else:
			frappe.throw(_("Cannot set as Lost as Sales Order is made."))

	def check_item_table(self):
		if not self.get('quotation_details'):
			frappe.throw(_("Please enter item details"))

	def on_submit(self):
		self.check_item_table()

		# Check for Approving Authority
		frappe.get_doc('Authorization Control').validate_approving_authority(self.doctype, self.company, self.grand_total, self)

		#update enquiry status
		self.update_opportunity()

	def on_cancel(self):
		#update enquiry status
		self.set_status()
		self.update_opportunity()

	def print_other_charges(self,docname):
		print_lst = []
		for d in self.get('other_charges'):
			lst1 = []
			lst1.append(d.description)
			lst1.append(d.total)
			print_lst.append(lst1)
		return print_lst


	#anand	
	def refresh_rm_total_price(self,docname):
		for item in self.get('quotation_details'):
			if item.raw_material_costing:
				self.get_rm_total_price(item.idx)
		return "Done"

	#anand	
	def refresh_pp_total_price(self,docname):
		for item in self.get('quotation_details'):
			if item.primary_process_costing:
				self.get_pp_total_price(item.idx)
		return "Done"

	#anand	
	def refresh_sp_total_price(self,docname):
		for item in self.get('quotation_details'):
			if item.secondary_process_costing:
				self.get_sp_total_price(item.idx)
		return "Done"
	#anand	
	def refresh_sm_total_price(self,docname):
		for item in self.get('quotation_details'):
			if item.sub_machining_costing:
				self.get_sm_total_price(item.idx)
		return "Done"

	#anand	
	def get_rm_total_price(self,docname):
		frappe.errprint("updated rm")
		for item in self.get('quotation_details'):
			if item.idx==docname:
				rm_total_price=frappe.db.get_value("Raw Material Cost Sheet",item.raw_material_costing,'rm_total_price')
				spec=frappe.db.get_value("Raw Material Costing Details",{"parent":item.raw_material_costing},'spec')
				spec_type=frappe.db.get_value("Raw Material Costing Details",{"parent":item.raw_material_costing},'type')
				item.rm_total_price=rm_total_price
				item.spec=cstr(spec)+' '+cstr(spec_type)
				if rm_total_price:
					self.set_rate()
				# if not ___islocal:
				# 	self.save(ignore_permissions=True)
		return "Done"

	def get_pp_total_price(self,docname):
		frappe.errprint("updated pp")
		for item in self.get('quotation_details'):
			if item.idx==docname:
				pp_total_price=frappe.db.get_value("Primary Process Costing",item.primary_process_costing,'pp_total')
				item.pp_total_price=pp_total_price
				if pp_total_price:
					self.set_rate()
			# self.save(ignore_permissions=True)			
		return "Done"

	def get_sm_total_price(self,docname):
		frappe.errprint("updated sm")
		for item in self.get('quotation_details'):
			if item.idx==docname:
				sm_total_price=frappe.db.get_value("Sub Machining Costing",item.sub_machining_costing,'sm_total')
				item.sm_total_price=sm_total_price
				if sm_total_price:
					self.set_rate()			
		return "Done"

	def get_sp_total_price(self,docname):
		frappe.errprint("updated sp")
		for item in self.get('quotation_details'):
			if item.idx==docname:
				sp_total_price=frappe.db.get_value("Secondary Process Costing",item.secondary_process_costing,'sp_total')
				item.sp_total_price=sp_total_price
				if sp_total_price:
					self.set_rate()
		return "Done"
	#anand	
	def refresh_rm_total_price(self,docname):
		for item in self.get('quotation_details'):
			if item.raw_material_costing:
				self.get_rm_total_price(item.idx)
		return "Done"

	#anand	
	def refresh_pp_total_price(self,docname):
		for item in self.get('quotation_details'):
			if item.primary_process_costing:
				self.get_pp_total_price(item.idx)
		return "Done"

	#anand	
	def refresh_sp_total_price(self,docname):
		for item in self.get('quotation_details'):
			if item.secondary_process_costing:
				self.get_sp_total_price(item.idx)
		return "Done"
	#anand	
	def refresh_sm_total_price(self,docname):
		for item in self.get('quotation_details'):
			if item.sub_machining_costing:
				self.get_sm_total_price(item.idx)
		return "Done"


	def set_rate(self):
		for item in self.get('quotation_details'):
			item.rate=flt(item.rm_total_price)+flt(item.pp_total_price)+flt(item.sm_total_price)+flt(item.sp_total_price)+flt(item.machining_cost)
		return "done"	


	def get_rfq(self,args):
		# frappe.errprint("in the get_rfq")
		# frappe.errprint(args)
		for d in self.get('quotation_details'):
			cost_docname=args["parent_cost"]
			cost_child=args["child_docname"]
			field_name=d.get(args["field_name"])
			rfqs=[]
			if field_name:
				# frappe.errprint("in the if")
				cost=frappe.get_doc(cost_docname,field_name).get(cost_child)
				# frappe.errprint(cost.quote_ref)
				for c in cost:
					# frappe.errprint(c.quote_ref)
					if c.quote_ref:
						# frappe.errprint("in the if")
						# frappe.errprint(c.pp_spec_type)
						rfq = self.update_rfq_with_quotattion_values(c,args,d)
						if rfq:
							rfqs.append(c.quote_ref)
		return rfqs

	def update_rfq_with_quotattion_values(self,c,args,d):
		rfq=frappe.get_doc(args['rfq_doctype'],c.quote_ref)
		if rfq.docstatus == 0:
			rfqc=rfq.append(args['rfq_child'],{})
			rfqc.quotation_no=self.name
			rfqc.part_no=d.part_number
			rfqc.drawing_no=d.item_code
			rfqc.mat_spec__type=d.spec

			if args['rfq_doctype']=='Material RFQ':
				rfqc.mat_spec_type=d.spec
				rfqc.od=cstr(c.od)+' '+cstr(c.od_uom)
				rfqc.id=cstr(c.id)+' '+cstr(c.id_uom)
				rfqc.lg=cstr(c.lg)+' '+cstr(c.lg_uom)
			elif args['rfq_doctype']=='Primary Process RFQ':
				rfqc.primary_process=c.spec
				rfqc.pp_spec_type=cstr(c.spec)+' '+cstr(c.type)
			elif args['rfq_doctype']=='Secondary Process RFQ':
				rfqc.secondary_process=c.spec
				rfqc.sp_spec_type=cstr(c.spec)+' '+cstr(c.type)
			elif args['rfq_doctype']=='Sub Machining RFQ':
				rfqc.sub_machining=c.type
				rfqc.sm_type=cstr(c.type)
			rfq.save(ignore_permissions=True)
			return True
		elif rfq.docstatus == 1:
			frappe.msgprint(_("Warning: RFQ Already Submitted"))
			return False
		elif rfq.docstatus == 2:
			frappe.msgprint(_("Warning: RFQ Is in Cancelled state so can't update"))
			return False

		return "done"
#roshan
@frappe.whitelist()
def get_customer_refno(customer):
	return frappe.db.sql( """select ref_no from `tabCustomer`
	 where name='%s'"""%(customer),debug=1)

@frappe.whitelist()
def raw_material_costing_query(doctype,txt,searchfield,start,page_len,filters):
	return frappe.db.sql( """select name from `tabRaw Material Cost Sheet`
	 order by creation desc""" )	

@frappe.whitelist()
def primary_process_costing_query(doctype,txt,searchfield,start,page_len,filters):
	return frappe.db.sql( """select name from `tabPrimary Process Costing`
	 order by creation desc""" )

@frappe.whitelist()
def secondary_process_costing_query(doctype,txt,searchfield,start,page_len,filters):
	return frappe.db.sql( """select name from `tabSecondary Process Costing`
	 order by creation desc""" )

@frappe.whitelist()
def sub_machining_costing_query(doctype,txt,searchfield,start,page_len,filters):
	return frappe.db.sql( """select name from `tabSub Machining Costing`
	 order by creation desc""" )


@frappe.whitelist()	
def make_sales_order(source_name, target_doc=None):
	return _make_sales_order(source_name, target_doc)

def _make_sales_order(source_name, target_doc=None, ignore_permissions=False):
	customer = _make_customer(source_name, ignore_permissions)

	def set_missing_values(source, target):
		if customer:
			target.customer = customer.name
			target.customer_name = customer.customer_name
		target.ignore_pricing_rule = 1
		target.ignore_permissions = ignore_permissions
		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")

	doclist = get_mapped_doc("Quotation", source_name, {
			"Quotation": {
				"doctype": "Sales Order",
				"validation": {
					"docstatus": ["=", 1]
				}
			},
			"Quotation Item": {
				"doctype": "Sales Order Item",
				"field_map": {
					"parent": "prevdoc_docname"
				}
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
	quotation = frappe.db.get_value("Quotation", source_name, ["lead", "order_type", "customer"])
	if quotation and quotation[0] and not quotation[2]:
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





