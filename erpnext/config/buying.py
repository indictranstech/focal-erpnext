from frappe import _

def get_data():
	return [
		{
			"label": _("Documents"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Supplier",
					"description": _("Supplier database."),
				},
				{
					"type": "doctype",
					"name": "Material Request",
					"description": _("Request for purchase."),
				},
				{
					"type": "doctype",
					"name": "Supplier Quotation",
					"description": _("Quotations received from Suppliers."),
				},
				{
					"type": "doctype",
					"name": "Purchase Order",
					"description": _("Purchase Orders given to Suppliers."),
				},
				{
					"type": "doctype",
					"name": "Contact",
					"description": _("All Contacts."),
				},
				{
					"type": "doctype",
					"name": "Address",
					"description": _("All Addresses."),
				},
				{
					"type": "doctype",
					"name": "Item",
					"description": _("All Products or Services."),
				},
			]
		},
		{
			"label": _("PO Process"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "PO Material",
					"description": _("PO Material"),
				},
				{
					"type": "doctype",
					"name": "PO Primary Process",
					"description": _("PO Primary Process"),
				},
				{
					"type": "doctype",
					"name": "PO Secondary Process",
					"description": _("PO Secondary Process"),
				},
				{
					"type": "doctype",
					"name": "PO Machining",
					"description": _("PO Machining"),
				}		]
		},
		{
			"label": _("DO Process"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "DO Material",
					"description": _("DO Material"),
				},
				{
					"type": "doctype",
					"name": "DO Primary Process",
					"description": _("DO Primary Process"),
				},
				{
					"type": "doctype",
					"name": "DO Secondary Process",
					"description": _("DO Secondary Process"),
				},
				{
					"type": "doctype",
					"name": "DO Machining",
					"description": _("DO Machining"),
				},
				# {
				# 	"type": "doctype",
				# 	"name": "Certificate Of Conformance",
				# 	"description": _("Certificate Of Conformance"),
				# }
						]
		},
		{
			"label": _("Setup"),
			"icon": "icon-cog",
			"items": [
				{
					"type": "doctype",
					"name": "Buying Settings",
					"description": _("Default settings for buying transactions.")
				},
				{
					"type": "doctype",
					"name": "Supplier Type",
					"description": _("Supplier Type master.")
				},
				{
					"type": "page",
					"name": "Sales Browser",
					"icon": "icon-sitemap",
					"label": _("Item Group Tree"),
					"link": "Sales Browser/Item Group",
					"description": _("Tree of Item Groups."),
					"doctype": "Item Group",
				},
				{
					"type": "doctype",
					"name":"Terms and Conditions",
					"label": _("Terms and Conditions Template"),
					"description": _("Template of terms or contract.")
				},
				{
					"type": "doctype",
					"name": "Purchase Taxes and Charges Master",
					"description": _("Tax template for buying transactions.")
				},
				{
					"type": "doctype",
					"name": "Price List",
					"description": _("Price List master.")
				},
				{
					"type": "doctype",
					"name": "Item Price",
					"description": _("Multiple Item prices."),
					"route": "Report/Item Price"
				},
				{
					"type": "doctype",
					"name": "Pricing Rule",
					"description": _("Rules for applying pricing and discount.")
				},
			]
		},
		{
			"label": _("Main Reports"),
			"icon": "icon-table",
			"items": [
				{
					"type": "page",
					"name": "purchase-analytics",
					"label": _("Purchase Analytics"),
					"icon": "icon-bar-chart",
				},
			]
		},
		{
			"label": _("Standard Reports"),
			"icon": "icon-list",
			"items": [
				{
					"type": "report",
					"is_query_report": True,
					"name": "Items To Be Requested",
					"doctype": "Item"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Requested Items To Be Ordered",
					"doctype": "Material Request"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Material Requests for which Supplier Quotations are not created",
					"doctype": "Material Request"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Item-wise Purchase History",
					"doctype": "Item"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Purchase Order Trends",
					"doctype": "Purchase Order"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Supplier Addresses and Contacts",
					"doctype": "Supplier"
				},
				{
					"type": "report",
					"is_query_report": True,
					"name": "Supplier-Wise Sales Analytics",
					"doctype": "Stock Ledger Entry"
				}
			]
		},
	]
