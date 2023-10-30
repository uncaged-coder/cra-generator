#!/usr/bin/python

from unidecode import unidecode
from email import utils
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from string import Template
import sys
import datetime
import locale
import io
from PyPDF3 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from pdb import set_trace as bp

# position of the month written at the top of document
POS_DATE_X = 470
POS_DATE_Y = 501

# position of date for signature case at bottom
POS_DATE_SIGN_X = 300
POS_DATE_SIGN_Y = 110

#
POS_TOTAL_WORKED_X = 245
POS_TOTAL_WORKED_Y = 218

# position of the 1st working day
POS_FIRST_DAY_X = 190
POS_FIRST_DAY_Y = 328
WORK_DAY_WIDTH = 56
WORK_DAY_HEIGHT = 27
DAYS_PER_LINE = 9

holidays = [# 2022 french holidays. 11-11 is holidays but I worked
            '2022-08-15', '2022-11-01', '2022-12-25',
            # 2022 vacation
            '2022-08-30', '2022-08-31',
            # 2022 mandatory holidays
            "2022-12-26", "2022-12-27", "2022-12-28", "2022-12-29",
            "2022-12-30",
            #2023 french holidays
            '2023-01-01', '2023-04-10', '2023-05-01', '2023-05-08',
            '2023-05-18', '2023-07-14', '2023-08-15', '2023-11-01',
            '2023-11-11', '2023-12-25',
            # 2023 vacation
            '2023-04-28', '2023-05-15', '2023-05-16', '2023-05-17',
            '2023-05-19',
            #2024 french holidays
            '2024-01-01']

def add_current_date(can):
    now = datetime.datetime.now()
    curr_date_sign = now.strftime("%d/%m/%Y")
    can.drawString(POS_DATE_SIGN_X, POS_DATE_SIGN_Y, curr_date_sign)

def get_cra_date(previous_month=False):
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
    cra_date = datetime.datetime.now()
    if previous_month == True:
        cra_end_date = cra_date
        cra_date = cra_date - datetime.timedelta(days=28)
    else:
        cra_end_date = cra_date + datetime.timedelta(days=28)

    return cra_date, cra_end_date

def check_case(can, day):
    day -= 1
    day_x = day % DAYS_PER_LINE
    day_y = int(day / DAYS_PER_LINE)
    day_x = POS_FIRST_DAY_X + day_x * WORK_DAY_WIDTH
    day_y = POS_FIRST_DAY_Y - day_y * WORK_DAY_HEIGHT
    can.drawString(day_x, day_y, "X")

def add_worked_day(can, previous_month=False):

    # Print current worked month at the top of the page
    worked_month = cra_date.strftime("%B %Y")
    can.drawString(POS_DATE_X, POS_DATE_Y, worked_month)

    start = datetime.date(cra_date.year, cra_date.month, 1)
    end = datetime.date(cra_end_date.year, cra_end_date.month, 1)

    all_days = [start + datetime.timedelta(x) for x in range((end - start).days)]
    week_days = [d for d in all_days if d.weekday() < 5 ]
    holidays_date = [datetime.datetime.strptime(h, "%Y-%m-%d").date() for h in holidays]
    worked_days = [d for d in week_days if d not in holidays_date]

    for d in worked_days:
        check_case(can, d.day)
    
    total_worked_days = len(worked_days)
    can.drawString(POS_TOTAL_WORKED_X, POS_TOTAL_WORKED_Y, str(total_worked_days))

    return total_worked_days

def generate_cra(cra_date, cra_end_date):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=landscape(A4))
    can.setFillColorRGB(0, 0, 1)
    add_current_date(can)
    total_worked_days = add_worked_day(can)
    can.save()

    #move to the beginning of the StringIO buffer
    packet.seek(0)

    # create a new PDF with Reportlab
    new_pdf = PdfFileReader(packet)
    # read your existing PDF
    existing_pdf = PdfFileReader(open("cra_model.pdf", "rb"))
    output = PdfFileWriter()
    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)
    # finally, write "output" to a real file
    cra_file_name = "cra_{}_{:02d}.pdf".format(cra_date.year, cra_date.month)
    outputStream = open(cra_file_name, "wb")
    output.write(outputStream)
    outputStream.close()

    return total_worked_days, cra_file_name


def generate_email(cra_date, total_worked_days, cra_file_name):
    # email content fields
    fields = {
        'date_email': utils.formatdate(localtime=True),
        'year': cra_date.year,
        'month': cra_date.strftime("%B"),
        'month_no_accents': unidecode(cra_date.strftime("%B")),
        'nb_worked_days': total_worked_days,
        'attach_filename': cra_file_name
    }
    with open('snd_template', 'r') as f:
        src = Template(f.read())
        email_content = src.substitute(fields)
        print(email_content)

    # write to Snd.0 file
    with open('Snd.0', 'w',  encoding='utf-8') as f:
        f.write(email_content)

    print('Email saved to Snd.0 file.')

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == "--previous-month":
        print("generating CRA for previous month")
        prev_month = True
    else:
        prev_month = False

    cra_date, cra_end_date = get_cra_date(prev_month)
    total_worked_days, cra_file_name = generate_cra(cra_date, cra_end_date)
    generate_email(cra_date, total_worked_days, cra_file_name)


