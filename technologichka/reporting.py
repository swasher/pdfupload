# coding: utf-8

#
# Report Lab related functions
#

from django.http import HttpResponse
from django.conf import settings
from .models import Order

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.units import inch


from reportlab.lib.enums import TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


from reportlab.lib.pagesizes import letter, A4

class MyPrint:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
        self.width, self.height = self.pagesize


def printpdf(self):

    buffer = self.buffer

    # Register Fonts
    pdfmetrics.registerFont(TTFont('Arial', settings.STATIC_ROOT + 'fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', settings.STATIC_ROOT + 'fonts/arialbd.ttf'))

    # A large collection of style sheets pre-made for us
    styles = getSampleStyleSheet()
    # Our Custom Style
    styles.add(ParagraphStyle(name='RightAlign', fontName='Arial', align=TA_RIGHT))


    # # Create the HttpResponse object with the appropriate PDF headers.
    # response = HttpResponse(content_type='application/pdf')
    # # скачать
    # #response['Content-Disposition'] = 'attachment; filename=somefilename.pdf'
    # # показать
    # response['Content-Disposition'] = 'filename="somefilename.pdf"'

    doc = SimpleDocTemplate(buffer, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72, pagesize=A4)

    # Our container for 'Flowable' objects
    elements = []

    users = ['Masha', 'Petya', 'Vanya']


    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    elements.append(Paragraph('My User Names', styles['Heading1']))
    for i, user in enumerate(users):
        elements.append(Paragraph(user, styles['Normal']))

    doc.build(elements)

    # Get the value of the BytesIO buffer and write it to the response.
    pdf = buffer.getvalue()
    buffer.close()

    return pdf


