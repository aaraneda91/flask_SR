from app import db
from .queries import REPORT_STATUS_INSTITUTIONS
import datetime
from io import BytesIO
import pandas as pd
from flask import send_file
import numpy as np

def get_report_states_institutions(period):
	list = []
	sql = REPORT_STATUS_INSTITUTIONS
	
	if period is None:
		now = datetime.datetime.now()
		period = str(now.year)

	institutions = db.engine.execute(sql,(period))

	for d in institutions:
		list.append({
			"inst_name": str(d.inst_name),
			"inst_address": str(d.inst_address),
			"comn_name": str(d.comn_name),
			"status": str(d.status) if d.status is not None else '',
			"etapa": str(d.etapa) if d.etapa is not None else '',
			"change_status_date": str(d.change_status_date),
			"change_status_user": str(d.change_status_user) if d.etapa == ('terminados') else '',
			"client_name": str(d.client_name),
			"status_camp": str(d.status_camp),
			"director": str(d.director) if d.director is not None else '',
			"lc_name": str(d.lc_name) if d.lc_name is not None else '',
			"lc_phone": str(d.lc_phone) if d.lc_phone is not None else ''
		})
	return list

def get_report_states_institutions_xlsx(period):

	data = []
	sql = REPORT_STATUS_INSTITUTIONS

	now = datetime.datetime.now()

	if period is None:
		period = str(now.year)

	columns = ["cliente","establecimiento", "dirección", "comuna", "estado", "etapa", "cambio estado (fecha)", "cambio estado (usuario)", "estado campaña", "D. Servicios","contacto local (nombre)", "contacto local (teléfono)"]

	institutions = db.engine.execute(sql,(period))

	for d in institutions:
		data.append([
			str(d.client_name),
			str(d.inst_name),
			str(d.inst_address),
			str(d.comn_name),
			str(d.status) if d.status is not None else '',
			str(d.etapa) if d.etapa is not None else '',
			str(d.change_status_date),
			str(d.change_status_user) if d.etapa == ('terminados') else '',
			str(d.status_camp),
			str(d.director) if d.director is not None else '',
			str(d.lc_name) if d.lc_name is not None else '',
			str(d.lc_phone) if d.lc_phone is not None else ''])

	output = BytesIO()

	# Create a Pandas dataframe from some data.
	df = pd.DataFrame(np.array(data), columns=columns)

	pd.set_option('display.width', 100)

	writer = pd.ExcelWriter(output, engine='xlsxwriter')

	df.to_excel(writer, sheet_name='Reporte Establecimientoss', startrow=1, header=False, index=False)
	
	# Get the xlsxwriter workbook and worksheet objects.
	workbook = writer.book
	worksheet = writer.sheets['Reporte Establecimientoss']

	# Get the dimensions of the dataframe.
	(max_row, max_col) = df.shape

	# Create a list of column headers, to use in add_table().
	column_settings = [{'header': column,'header_row': False} for column in df.columns]

	# Add the Excel table structure. Pandas will add the data.
	worksheet.add_table(0, 0, max_row, max_col-1, {'columns': column_settings})

	worksheet.set_column(1, 0, 20)
	worksheet.set_column(2, 0, 20)
	worksheet.set_column(3, 0, 20)
	worksheet.set_column(4, 0, 20)
	worksheet.set_column(5, 0, 20)
	worksheet.set_column(6, 0, 20)
	worksheet.set_column(7, 0, 20)
	worksheet.set_column(8, 0, 20)
	worksheet.set_column(9, 0, 20)
	worksheet.set_column(10, 0, 20)
	worksheet.set_column(11, 0, 20)

	workbook.close()

	#the writer has done its job
	writer.close()

	#go back to the beginning of the stream
	output.seek(0)

	return send_file(output, attachment_filename="report_"+str(now.day)+"-"+str(now.month)+"-"+str(now.year)+".xlsx", as_attachment=True)