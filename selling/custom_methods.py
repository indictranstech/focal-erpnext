
from __future__ import unicode_literals
import frappe
from frappe import _, throw
from frappe.utils import flt, cint, cstr ,add_days
import json
from erpnext.accounts.doctype.pricing_rule.pricing_rule import get_pricing_rule_for_item
from erpnext.setup.utils import get_exchange_rate
from frappe.model.delete_doc import check_if_doc_is_linked
from frappe.model.delete_doc import check_if_doc_is_dynamically_linked
from frappe.model.delete_doc import delete_doc




def get_so_price_list(args, item_doc, out): #Rohit_sw
	if args.predoc=='Multiple Qty':
		parent=frappe.db.get_value('Item Price',{'item_code':args.item_code,'price_list':args.price_list},'name')
		return frappe.db.get_value('Singular Price List',{'parent':parent,'customer_code':args.customer,'quantity':out.qty},'rate') or 0.0
	else:
		import json
		if isinstance(args.qty_label, unicode):
			range_list=json.loads(args.qty_label)
		else:
			range_list=(args.qty_label)
		if range_list:
			for s in range_list:
				if '-' in range_list[s]:
					val=range_list[s].split('-')
					if cint(out.qty) in range(cint(val[0]),cint(val[1])+1):
						p_rate=frappe.db.sql("""select a.rate from `tabPrice List Quantity` as a
							,`tabItem Price` as b where a.parent=b.name 
							and b.price_list='%s' and b.item_code='%s' 
							and a.customer_code ='%s' and quantity='%s' and a.range_qty='%s'"""
							%(args.price_list,args.item_code,args.customer,out.qty,range_list[s]),as_list=1)
						if p_rate:
							return p_rate[0][0]
				else:
					value=range_list[s].split('>')
					if cint(out.qty) >= cint(value[1]):
						p_rate=frappe.db.sql("""select a.rate from `tabPrice List Quantity` as a
							,`tabItem Price` as b where a.parent=b.name and b.price_list='%s' 
							and b.item_code='%s' and a.customer_code ='%s' and a.range_qty='%s'"""
							%(args.price_list,args.item_code,args.customer,range_list[s]),as_list=1)
						if p_rate:
							return p_rate[0][0]
		else:
			return 0.0

@frappe.whitelist()
def get_stock_uom(quantity,item_code):
	quantity=cint(quantity)
	if quantity > 1 and item_code:
		uom_for_many=frappe.db.get_value('Item',item_code,'uom_for_many')
		if uom_for_many:
			return uom_for_many
		else:
			return frappe.db.get_value('Item',item_code,'stock_uom')		
	if quantity == 1 and item_code:
		return frappe.db.get_value('Item',item_code,'stock_uom')


def create_address(doc,method):
	for addr in doc.get('customer_address'):
		if not frappe.db.exists('Address',addr.address_name):
			c = frappe.new_doc('Address')
			c.address_title = addr.address_title
			c.address_type = addr.address_type
			c.address_line1 = addr.address_line_1 or ''
 			c.address_line2 = addr.address_line_2 or ''
			c.city = addr.city or ''
			c.state = addr.state or ''
			c.pincode = addr.pincode or ''
			c.country = addr.country or  '' 
			c.phone = addr.phone  or ''
			c.preferred_billing_address = addr.preferred_billing_address
			c.preferred_shipping_address = addr.preferred_shipping_address	
			c.save()
			addr.address_name = c.name
			frappe.db.commit()
		if  frappe.db.exists('Address',addr.address_name) and addr.address_name:
			new_addr = frappe.get_doc('Address',addr.address_name)	
			new_addr.address_title = addr.address_title
			new_addr.address_type = addr.address_type
			new_addr.address_line1 = addr.address_line_1 or ''
 			new_addr.address_line2 = addr.address_line_2 or ''
			new_addr.city = addr.city or ''
			new_addr.state = addr.state or ''
			new_addr.pincode = addr.pincode or ''
			new_addr.country = addr.country or  '' 
			new_addr.phone = addr.phone  or ''
			new_addr.preferred_billing_address = addr.preferred_billing_address
			new_addr.preferred_shipping_address = addr.preferred_shipping_address
			new_addr.save()
			frappe.db.commit()






def update_customer_name(doc,method):
	for addr in doc.get('customer_address'):
		if addr.address_name:
			frappe.db.sql(""" update `tabAddress` set customer='%s' where name='%s' """%(doc.name,addr.address_name))



def delete_address(doc,method):
	if doc.address_list:
		address_list = cstr(doc.address_list).split()
		for d in address_list:
			frappe.delete_doc('Address',d)
		doc.address_list = ''	



def check_link(doc,method):
	if doc.address_list:
		address_list = cstr(doc.address_list).split()
		for d in address_list:
			if frappe.db.exists('Address',d):
				doc = frappe.get_doc('Address',d)
				check_if_doc_is_linked(doc)
				check_if_doc_is_dynamically_linked(doc)	

	


