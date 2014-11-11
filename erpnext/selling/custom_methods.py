
from __future__ import unicode_literals
import frappe
from frappe import _, throw
from frappe.utils import flt, cint, add_days
import json
from erpnext.accounts.doctype.pricing_rule.pricing_rule import get_pricing_rule_for_item
from erpnext.setup.utils import get_exchange_rate



def get_so_price_list(args, item_doc, out): #Rohit_sw
	# frappe.errprint(out)
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

