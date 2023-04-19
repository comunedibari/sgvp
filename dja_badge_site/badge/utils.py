# libreria di utilità 
import io
import logging
import os
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A6
from reportlab.lib.units import mm
import qrcode
from django.contrib.admin.utils import NestedObjects
from django.utils.text import capfirst
from django.utils.encoding import force_str


logger = logging.getLogger(__name__)

# generazione response con file pdf contenente qrcode di esempio
def testrendpdf(request):
     # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)
    # set page in points
    p.setPageSize((400,400))
    
    sfondo= ImageReader('https://www.google.com/images/srpr/logo11w.png')
    p.drawImage(image=sfondo,x=10,y=10,mask='auto') 

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.setFont("Helvetica",20)
    p.drawString(10, 100, "Hello world.")
    
    # generazione qrcode
    img_qrcode=genera_qrcode("1234567890123456789012345",10,4,1,'L')
    p.drawImage(image=ImageReader(img_qrcode),x=10,y=150,mask='auto') 
    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='hello.pdf')

# generazione qrcode e restituzione di immagine
def genera_qrcode(data:str,box_size:int,border:int,version:int,error_correct:str):
    error_connection_constant=qrcode.constants.ERROR_CORRECT_L
    if error_correct=='M':
        error_connection_constant=qrcode.constants.ERROR_CORRECT_M
    elif error_correct=='Q':
        error_connection_constant=qrcode.constants.ERROR_CORRECT_Q
    elif error_correct=='H':    
        error_connection_constant=qrcode.constants.ERROR_CORRECT_H
    qr = qrcode.QRCode(
    version=version,
    error_correction=error_connection_constant,
    box_size=box_size,
    border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img= img.get_image()
    return img

# parsing dell'albero degli oggitti relazionati ad un oggetto a db
def get_deleted_objects(objs): 
    collector = NestedObjects(using='default')
    collector.collect(objs)
    #
    def format_callback(obj):
        opts = obj._meta
        no_edit_link = '%s: %s' % (capfirst(opts.verbose_name),
                                   force_str(obj))
        return no_edit_link            
    #
    to_delete = collector.nested(format_callback)
    protected = [format_callback(obj) for obj in collector.protected]
    model_count = {model._meta.verbose_name_plural: len(objs) for model, objs in collector.model_objs.items()}
    #
    return to_delete, model_count, protected

from PIL import Image,ImageDraw

def build_image_w_text(text:str):
    img = Image.new('RGB', (100, 100), color = (73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((10,10), text, fill=(255,255,0))
    return img