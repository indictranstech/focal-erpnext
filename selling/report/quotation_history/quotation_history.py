from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, cint
from erpnext.controllers.trends	import get_columns,get_data

def execute(filters=None):

	# if filters.get("company"):
	# 	company_condition = ' and company=%(company)s'
	if not filters: filters ={}
	data=frappe.db.sql("""select b.name,b.customer, a.item_code,b.rq1,a.r_qty1,b.rq2,a.r_qty2,b.rq3,a.r_qty3 from 
		`tabMultiple Quantity Item` as a , `tabQuotation for Mulitple Quantity` as b
		where b.docstatus=1 and a.parent=b.name
		 order by b.customer""",as_list=1)
	frappe.errprint(data)
	columns = ["Name:Link/Quotation for Mulitple Quantity","Customer Code::120", "Item Code:Data","Qty1:Data","Rate1:Currency","Qty2:Data","Rate2:Currency","Qty3:Data","Rate3:Currency"]	
	return columns, data 

