# -*- coding: utf-8 -*-
# Copyright (c) 2018, Facilitators and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.utils import cstr, flt, cint,add_days,format_datetime
from frappe import msgprint, _
from frappe.model.mapper import get_mapped_doc
from erpnext.controllers.buying_controller import BuyingController
from erpnext.stock.doctype.item.item import get_last_purchase_details
from erpnext.stock.stock_balance import update_bin_qty, get_ordered_qty
from frappe.desk.notifications import clear_doctype_notifications
from erpnext.buying.utils import validate_for_items, check_for_closed_status
from erpnext.stock.utils import get_bin
from datetime import datetime,date, timedelta



@frappe.whitelist()
def getData(start,end,filters=None):
	event_obj=[]
	avail_faci=False
	from frappe.desk.calendar import get_event_conditions
	conditions = get_event_conditions("Facilitator", filters)
	#frappe.msgprint(conditions)
	cond_event=''
	cond_holiday=''
	avail_faci_fil=False
	if filters:
		fil=json.loads(filters)
		for fil_cond in fil:
			#frappe.msgprint(fil_cond)
			if fil_cond[1]=="available_facilitators":
				#frappe.msgprint("yes")
				avail_faci=True

			if fil_cond[1]=="facilitator":
				cond_event=cond_event+' where ft.facilitator='+'"'+fil_cond[3]+'"'
				cond_holiday=cond_holiday+' where facilitator='+'"'+fil_cond[3]+'"'
				avail_faci_fil=True

			if fil_cond[1]=="event":
				
				if avail_faci_fil==True:
					cond_event=cond_event+' and ev.name='+'"'+fil_cond[3]+'"'
				else:
					cond_event=cond_event+' where ev.name='+'"'+fil_cond[3]+'"'
		

		#frappe.msgprint(cond_event+cond_holiday)
				
				

			

		
	#return event
	if not avail_faci==True:
		sql=''
		if not cond_event=='':
			sql='select ev.name,ev.starts_on,ev.ends_on,ev.course_family,ft.facilitator,ev.color,ev.client,ft.status from `tabEvent` as ev inner join `tabFacilitator Table` as ft on ev.name=ft.parent'+cond_event
		else:
			sql='select ev.name,ev.starts_on,ev.ends_on,ev.course_family,ft.facilitator,ev.color,ev.client,ft.status from `tabEvent` as ev inner join `tabFacilitator Table` as ft on ev.name=ft.parent'	
			
		event=frappe.db.sql(sql)

		if event:
			for row in event:
				title_temp=''
				if not row[6]==None:
					title_temp=row[4]+('\n').encode('utf8')+str(row[3])+('\n').encode('utf8')+row[6]
				else:
					title_temp=row[4]+('\n').encode('utf8')+row[3]
				if not row[7]==None:
					row_sevan=row[7]
				else:
					row_sevan='Default'
				item={}
				item["start_on"]=row[1] if not row[2]==None else add_days(row[1],0)
				item["end_on"]=row[2] if not row[2]==None else add_days(row[1],0)
				item["name"]=row[0]
				item["title"]=title_temp
				item["doctype"]="Event"
				item["color"]=getColor(row_sevan)
				event_obj.append(item)
		
		sql1=''

		if not cond_holiday=='':
			sql1='select name,start_on,end_on,facilitator from `tabFacilitator Holiday`'+cond_holiday
		else:
			sql1='select name,start_on,end_on,facilitator from `tabFacilitator Holiday`'
		#frappe.msgprint(sql1)
		leave=frappe.db.sql(sql1)
		if leave:
			for row1 in leave:
				leave_item={}
				leave_item["name"]=row1[0]
				leave_item["start_on"]=row1[1]
				leave_item["end_on"]=row1[2]
				leave_item["title"]='Holiday -'+'\n'+str(row1[3])
				leave_item["doctype"]="Facilitator Holiday"
				leave_item["color"]="#808080"
				event_obj.append(leave_item)
		return event_obj

	else:

		temp=[]
		fil1=json.loads(filters)
		check_faci_flag=False
		filter_val=''
		for fil_cond1 in fil1:
			if fil_cond1[1]=="facilitator":
				check_faci_flag=True
				filter_val=fil_cond1[3]
				break

		if check_faci_flag==True:
			available_faci=getAvailableFacilitator(start,end,event_obj,filter_val)
			if available_faci:	
				return available_faci
			else:
				return temp
		else:
			available_faci=getAvailableFacilitator(start,end,event_obj)
			if available_faci:	
				return available_faci
			else:
				return temp
			


@frappe.whitelist()
def getColor(status):
	data=frappe.db.sql("""select color from `tabFacilitator Status Color` where status=%s limit 1""",status)
	if data:
		return data[0][0]
	else:
		return '#07f2c7'





@frappe.whitelist()
def getAvailableFacilitator(start,end,event_obj,faci_cond=None):
	facilitator=frappe.db.sql("""select name,email from `tabFacilitator`""")
	start_date=add_days(format_datetime(start,'YYYY-MM-dd'),1)
	end_date=format_datetime(end,'YYYY-MM-dd')
	#return (start_date,end_date)
	faci_obj=[]
	if faci_cond==None:
		#frappe.msgprint("None")
		while start_date<end_date:
		
			#title='Available'+'\n'+'----------------'+'\n'
			flag=False
		
			for row in facilitator:
				faci_item={}
				event=frappe.db.sql("""select ev.name,ev.starts_on,ev.ends_on,ft.facilitator from `tabEvent` as ev inner join `tabFacilitator Table` as ft on ev.name=ft.parent where %s between ev.starts_on and ev.ends_on and ft.facilitator=%s""",(start_date,row[0]))
				if event:
					continue
				holiday=frappe.db.sql("""select name,start_on,end_on,facilitator from `tabFacilitator Holiday` where %s between start_on and end_on and facilitator=%s""",(start_date,row[0]))
				if holiday:
					continue
			
				flag=True
				#title+=row[0]+'\n'

			
				faci_item["name"]=row[0]
				faci_item["start_on"]=start_date
				faci_item["end_on"]=start_date
				faci_item["title"]=row[0]
				faci_item["doctype"]="Facilitator"
				faci_item["color"]="#000080"	
				event_obj.append(faci_item)
			start_date=add_days(start_date,1)
	else:
		while start_date<end_date:
		
			#title='Available'+'\n'+'----------------'+'\n'
			flag=False
		
			#for row in facilitator:
			faci_item={}
			event=frappe.db.sql("""select ev.name,ev.starts_on,ev.ends_on,ft.facilitator from `tabEvent` as ev inner join `tabFacilitator Table` as ft on ev.name=ft.parent where %s between ev.starts_on and ev.ends_on and ft.facilitator=%s""",(start_date,faci_cond))
			if event:
				start_date=add_days(start_date,1)
				continue
			holiday=frappe.db.sql("""select name,start_on,end_on,facilitator from `tabFacilitator Holiday` where %s between start_on and end_on and facilitator=%s""",(start_date,faci_cond))
			if holiday:
				start_date=add_days(start_date,1)
				continue
			
			flag=True
			#title+=row[0]+'\n'
			
			faci_item["name"]=faci_cond
			faci_item["start_on"]=start_date
			faci_item["end_on"]=start_date
			faci_item["title"]=faci_cond
			faci_item["doctype"]="Facilitator"
			faci_item["color"]="#000080"	
			event_obj.append(faci_item)
			start_date=add_days(start_date,1)
		

	return event_obj		

