# coding: utf-8

from django.http import HttpResponse
from .models import Order

from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from reportlab.lib.styles import getSampleStyleSheet

from reportlab.rl_config import defaultPageSize
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.units import inch


from reportlab.lib.enums import TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.conf import settings

# direct report lab
def printpdf_(request, orderid):

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    # скачать pdf
    #response['Content-Disposition'] = 'attachment; filename=somefilename.pdf'
    # показать pdf
    response['Content-Disposition'] = 'filename="somefilename.pdf"'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response, bottomup=1, pagesize=A4)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.


    # устанавливаем шрифт
    p.setFont('Helvetica', 12)

    #p.translate(mm, mm)
    # умножаем на mm - переводим пункты в миллиметры
    p.drawString(100*mm, 100*mm, "Hello world111.")

    # Устанавливаем толщину линии, в пунктах
    p.setLineWidth(1)

    # Рисуем линию - точка 0,0 слева внизу
    p.line(0, 0, 210*mm, 210*mm)

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return response

#_platypus
def printpdf__(request, orderid):


    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    # скачать
    #response['Content-Disposition'] = 'attachment; filename=somefilename.pdf'
    # показать
    response['Content-Disposition'] = 'filename="somefilename.pdf"'

    # Первый пример
    #
    # doc = SimpleDocTemplate(response)
    # styles = getSampleStyleSheet()
    # Elements = []
    # p = Paragraph("Hello World", styles['Heading1'])
    # Elements.append(p)
    # doc.build(Elements)





    # Второй пример
    #
    PAGE_HEIGHT=A4[1]
    PAGE_WIDTH=A4[0]
    styles = getSampleStyleSheet()
    Title = "Hello world"
    pageinfo = "platypus example"

    def myFirstPage(canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Bold',16)
        canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-108, Title)
        canvas.setFont('Times-Roman',9)
        canvas.drawString(inch, 0.75 * inch,"First Page / %s" % pageinfo)
        canvas.restoreState()

    def myLaterPages(canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman', 9)
        canvas.drawString(inch, 0.75 * inch,"Page %d %s" % (doc.page, pageinfo))
        canvas.restoreState()


    doc = SimpleDocTemplate(response)

    # или для создания ландскейпа
    from reportlab.lib.pagesizes import letter, landscape
    doc = SimpleDocTemplate(buffer, pagesize=landscape(self.pagesize))


    Story = [Spacer(1,2*inch)]
    style = styles["Normal"]
    for i in range(100):
        bogustext = ("Paragraph number %s. " % i) *20
        p = Paragraph(bogustext, style)
        Story.append(p)
        Story.append(Spacer(1,0.2*inch))
    doc.build(Story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)

    return response


"""
поворот изображения
"""

from reportlab.platypus.flowables import Image

class RotatedImage(Image):

    def wrap(self,availWidth,availHeight):
        h, w = Image.wrap(self,availHeight,availWidth)
        return w, h
    def draw(self):
        self.canv.rotate(90)
        Image.draw(self)

I = RotatedImage('../images/somelogo.gif')