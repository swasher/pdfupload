# coding: utf-8


from django.conf import settings

from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import StyleSheet1
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT


def StyleSheet():

    _baseFont = 'Arial'
    _baseFontName = _baseFont
    _baseFontNameI = _baseFont + '-Italic'
    _baseFontNameB = _baseFont + '-Bold'
    _baseFontNameBI = _baseFont + '-Bold-Italic'

    # Register Fonts
    pdfmetrics.registerFont(TTFont('Arial', settings.STATIC_ROOT + 'fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', settings.STATIC_ROOT + 'fonts/arialbd.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Italic', settings.STATIC_ROOT + 'fonts/ariali.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold-Italic', settings.STATIC_ROOT + 'fonts/arialbi.ttf'))

    """Returns a stylesheet object"""
    stylesheet = StyleSheet1()

    stylesheet.add(ParagraphStyle(name='Normal',
                                  fontName = _baseFontName,
                                  fontSize=10,
                                  leading=12)
                   )

    stylesheet.add(ParagraphStyle(name='Normal-Right',
                                  fontName = _baseFontName,
                                  fontSize=10,
                                  alignment=TA_RIGHT,
                                  leading=12)
                   )

    stylesheet.add(ParagraphStyle(name='BodyText',
                                  parent=stylesheet['Normal'],
                                  spaceBefore=6)
                   )
    stylesheet.add(ParagraphStyle(name='Italic',
                                  parent=stylesheet['BodyText'],
                                  fontName = _baseFontNameI)
                   )

    stylesheet.add(ParagraphStyle(name='Heading1',
                                  parent=stylesheet['Normal'],
                                  fontName = _baseFontNameB,
                                  fontSize=18,
                                  leading=22,
                                  spaceAfter=6),
                   alias='h1')

    stylesheet.add(ParagraphStyle(name='Title',
                                  parent=stylesheet['Normal'],
                                  fontName = _baseFontNameB,
                                  fontSize=18,
                                  leading=22,
                                  alignment=TA_CENTER,
                                  spaceAfter=6),
                   alias='title')

    stylesheet.add(ParagraphStyle(name='Heading2',
                                  parent=stylesheet['Normal'],
                                  fontName = _baseFontNameB,
                                  fontSize=14,
                                  leading=18,
                                  spaceBefore=12,
                                  spaceAfter=6),
                   alias='h2')

    stylesheet.add(ParagraphStyle(name='Heading3',
                                  parent=stylesheet['Normal'],
                                  fontName = _baseFontNameBI,
                                  fontSize=12,
                                  leading=14,
                                  spaceBefore=12,
                                  spaceAfter=6),
                   alias='h3')

    stylesheet.add(ParagraphStyle(name='Heading4',
                                  parent=stylesheet['Normal'],
                                  fontName = _baseFontNameBI,
                                  fontSize=10,
                                  leading=12,
                                  spaceBefore=10,
                                  spaceAfter=4),
                   alias='h4')

    stylesheet.add(ParagraphStyle(name='Heading5',
                                  parent=stylesheet['Normal'],
                                  fontName = _baseFontNameB,
                                  fontSize=9,
                                  leading=10.8,
                                  spaceBefore=8,
                                  spaceAfter=4),
                   alias='h5')

    stylesheet.add(ParagraphStyle(name='Heading6',
                                  parent=stylesheet['Normal'],
                                  fontName = _baseFontNameB,
                                  fontSize=7,
                                  leading=8.4,
                                  spaceBefore=6,
                                  spaceAfter=2),
                   alias='h6')

    stylesheet.add(ParagraphStyle(name='Bullet',
                                  parent=stylesheet['Normal'],
                                  firstLineIndent=0,
                                  spaceBefore=3),
                   alias='bu')

    stylesheet.add(ParagraphStyle(name='Definition',
                                  parent=stylesheet['Normal'],
                                  firstLineIndent=0,
                                  leftIndent=36,
                                  bulletIndent=0,
                                  spaceBefore=6,
                                  bulletFontName=_baseFontNameBI),
                   alias='df')

    stylesheet.add(ParagraphStyle(name='Code',
                                  parent=stylesheet['Normal'],
                                  fontName='Courier',
                                  fontSize=8,
                                  leading=8.8,
                                  firstLineIndent=0,
                                  leftIndent=36))

    return stylesheet
