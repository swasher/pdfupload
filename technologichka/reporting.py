# coding: utf-8

import datetime
from django.http import HttpResponse
from .models import Order, PrintSheet

#
# Report Lab related functions
#
from reportlab.pdfgen import canvas

from reportlab.platypus import BaseDocTemplate, Paragraph, Spacer, Table, TableStyle, Frame, PageTemplate, FrameBreak

from reportlab.lib.styles import getSampleStyleSheet

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.units import inch
from reportlab.lib import colors


from reporting_adds import StyleSheet


"""
# Функция для нумерации страниц.
# Работает, но я буду ставить номера в _header_footer
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        # add page info to each page (page x of y)
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        # Change the position of this to wherever you want the page number to be
        self.drawRightString(200 * mm, 7 * mm, "Page %d of %d" % (self._pageNumber, page_count))
"""


class PrintOrder(object):




    def __init__(self, buffer, orderid):
        self.buffer = buffer
        self.orderid = orderid

        self.pagesize = A4
        self.width, self.height = self.pagesize
        self.rightMargin=10*mm
        self.leftMargin=10*mm
        self.topMargin=15*mm
        self.bottomMargin=30*mm

        # PDF Properties
        self.Title = "ECS Report #1"
        self.Author = "ECS Information Systems"
        self.PageInfo = "Sample Report"


    @staticmethod
    def _header_footer(canvas, doc):

        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        styles = StyleSheet()

        # Header
        header = Paragraph('Типография ТЭС. Заказ № {}'.format('orderid'), styles['Title'])
        w, h = header.wrap(doc.width, doc.topMargin)
        #y = doc.height + doc.topMargin - h
        y = 282*mm
        header.drawOn(canvas, doc.leftMargin, y)

        # Footer
        now = datetime.datetime.now()
        footer = Paragraph('Типография ТЭС. Одесса. {} -- стр. {}'.format(now.strftime("%Y-%m-%d %H:%M"), doc.page) , styles['Normal'])
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, h)

        # Release the canvas
        canvas.restoreState()

    def printpdf(self):




        order = Order.objects.get(order=self.orderid)

        # this section contain list of all data for report:
        # order.order - номер заказа
        # order.customer - заказчик
        # order.name - наименование заказа

        buffer = self.buffer



        # A large collection of style sheets pre-made for us
        # But we overwrite it with custom styles by StyleSheet() function above
        styles = StyleSheet()


        # # Create the HttpResponse object with the appropriate PDF headers.
        # response = HttpResponse(content_type='application/pdf')
        # # скачать
        # #response['Content-Disposition'] = 'attachment; filename=somefilename.pdf'
        # # показать
        # response['Content-Disposition'] = 'filename="somefilename.pdf"'


        ##### define frames
        # Frame declaration format
        # Frame(x1, y1, width,height, leftPadding=6, bottomPadding=6, rightPadding=6, topPadding=6, id=None, showBoundary=0)
        column_gap = 10

        left_frame = Frame(
            self.leftMargin,
            self.height - 100*mm, #doc.bottomMargin,
            self.width / 2,
            70*mm, #doc.height,
            id='frame_left',
            rightPadding=column_gap / 2,
            showBoundary=1  # set to 1 for debugging
        )

        right_frame = Frame(
            self.leftMargin + self.width / 2,
            self.height - 100*mm, #doc.bottomMargin,
            self.width / 2,
            70*mm, #doc.height,
            id='frame_right',
            leftPadding=column_gap / 2,
            showBoundary=1
        )

        ##### define pageTemplates - for page in document
        mainPage = PageTemplate(frames=[left_frame, right_frame])


        ##### define BasicDocTemplate - for document
        doc = BaseDocTemplate(buffer,
                              pagesize=self.pagesize, pageTemplates=mainPage,
                              rightMargin=self.rightMargin, leftMargin=self.leftMargin, topMargin=self.topMargin, bottomMargin=self.bottomMargin,
                              title=self.Title, showBoundary=1)

        #doc = SimpleDocTemplate(buffer, rightMargin=10*mm, leftMargin=10*mm, topMargin=15*mm, bottomMargin=30*mm, pagesize=self.pagesize)



        # Our container for 'Flowable' objects
        flowables = []


        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.
        flowables.append(Paragraph(u'Заказ № {}'.format(order.order), styles['Heading2']))
        flowables.append(FrameBreak())
        flowables.append(Paragraph(u'Заказчик: {}'.format(order.customer), styles['Normal']))
        flowables.append(FrameBreak())
        flowables.append(Paragraph(u'Наименовение заказа: {}'.format(order.name), styles['Normal']))


        # example how to use color for certain text
        flowables.append(Paragraph('<font name="Arial-Bold" color="red">My</font> User Names', styles['Normal']))

        """
        # example how to add picture in paragraph
        elements.append(Paragraph('<img src="/home/vagrant/pdfupload/smiley.jpg" width="100" height="100"></img>', styles['Normal-Right']))
        """


        """
        # Example how add table to PDF
        # table_data is a place for our data
        query_data = PrintSheet.objects.filter(order=order)
        table_data = []
        for i, sheet in enumerate(query_data):
            # Add a row to the table
            table_data.append([sheet.name, sheet.printingpress, sheet.pressrun])

        # Create the table
        user_table = Table(table_data, colWidths=[doc.width/3.0]*3)
        user_table.setStyle(TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
        ]))
        elements.append(user_table)
        """

        #example big paragraph
        words = "lorem ipsum dolor sit amet consetetur sadipscing elitr sed diam nonumy eirmod tempor invidunt ut labore et".split()
        import random
        flowables.append(Paragraph(" ".join([random.choice(words) for i in range(100)]), styles['Normal']))
        flowables.append(Spacer(1, 0.2 * inch))

        flowables.append(Paragraph(" ".join([random.choice(words) for i in range(100)]), styles['Heading4']))
        flowables.append(Spacer(1, 0.2 * inch))

        flowables.append(Paragraph(" ".join([random.choice(words) for i in range(120)]), styles['Normal']))

        flowables.append(Paragraph(" ".join([random.choice(words) for i in range(100)]), styles['Heading4']))




        #doc.build(flowables, onFirstPage=self._header_footer, onLaterPages=self._header_footer) #, canvasmaker=NumberedCanvas)
        doc.build(flowables)



        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()

        return pdf