"""
Script to extract images from a pdf file
"""

import os
import sys
import argparse
import pickle
import csv
import io


#from PyPDF2 import PdfFileReader, PdfFileWriter
import traceback
import PyPDF2
import easyocr
#import PIL
from PIL import Image
import cv2 as cv
import pandas as pd

import pytesseract as ts

# -------------------------------------------------------------
img_modes = {'/DeviceRGB': 'RGB', '/DefaultRGB': 'RGB',
             '/DeviceCMYK': 'CMYK', '/DefaultCMYK': 'CMYK',
             '/DeviceGray': 'L', '/DefaultGray': 'L',
             '/Indexed': 'P'}
# -------------------------------------------------------------

def readpdf(pdf_file):

   PDFfile = open(pdf_file, 'rb')
   pdfobj = PyPDF2.PdfFileReader(PDFfile)
   print(f"{PyPDF2.__version__=}   {PyPDF2.__package__=}")
   print(pdfobj.numPages)

   txt1 = pdfobj.getDocumentInfo() 

   print(txt1)

   for page in range(0, pdfobj.numPages):
       pageObj = pdfobj.getPage(page)
    
       print ("------- Page:"+str(page)+" --------------")
       print(pageObj.extractText())
       print ("----------Meta Data------------------------------")
       print(pageObj.getXmpMetadata())
       print ("----------Page Attr------------------------------")
       for d in pdfobj.resolvedObjects:
           print(d, " : ", pdfobj.resolvedObjects[d])
   PDFfile.close()
   
   
   

def readimg(jpg_file, model_file):

   if (os.path.isfile(model_file)):   
       with open(model_file, 'rb') as fileh:
         reader = pickle.load(fileh)
   else:
      reader = easyocr.Reader(['en'], gpu=True) 
      #with open(model_file, 'wb') as fileh:
      #   pickle.dump(reader, fileh)
      
   #img = PIL.Image.open(jpg_file)
   img = cv.imread(jpg_file)
   #img2 = cv.blur(img,(5,5))
   img2 = cv.cvtColor(img,cv.COLOR_BGR2RGB)
   
   ret, img2 = cv.threshold(img, 127, 255, cv.THRESH_BINARY_INV)
   bounds = reader.readtext(img2,contrast_ths=0.5)
   
   #bounds = reader.readtext(jpg_file)
   y_prev = 0
   line =''
   for w in bounds:
       cord = w[0][3]
       y = cord[1]
       if abs(y_prev - y) < 5:
          line = line +": "+w[1]
       else:
          print(line)
          line=w[1]
          y_prev = y
   print("----------------------------------------------")
   for w in bounds:          
       print(w)
       
def readpdf_tess(pdf_file):
    
    
    input1 = PyPDF2.PdfFileReader(open(pdf_file, "rb"))
    nPages = input1.getNumPages()
    print(f"{nPages=} {PyPDF2.__version__=}   {PyPDF2.__package__=} {PyPDF2._version=} \
          {PyPDF2.__file__=}  {PyPDF2.__doc__=}")
    #aa = fitz.open (pdf_file)         
    
    for i in range(nPages) :
        print (f"Page Number = {i}")
        page0 = input1.getPage(i)
        try :
            xObject = page0['/Resources']['/XObject'].getObject()
        except : xObject = []
    
        for obj in xObject:
            if xObject[obj]['/Subtype'] == '/Image':
                size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                data = xObject[obj].getData()
                try :
                    
                    #color_space = xObject[obj]['/ColorSpace']
                    print (f"XOBJECT OBJ \n {xObject[obj]}")
                    #mode = img_modes.get(color_space[0])
                    if xObject[obj]['/ColorSpace'] == '/DeviceRGB':
                        mode = "RGB"
                    elif xObject[obj]['/ColorSpace'] == '/DeviceCMYK':
                        mode = "CMYK"
                        # will cause errors when saving
                    else:
                        mode = "P"
    
                    fn = 'p%03d-%s' % (i + 1, obj[1:])
                    
                    print (f"File Name = {fn},  {mode=}, {size=}")
                    
                    if '/FlateDecode' in xObject[obj]['/Filter'] :
                        img = Image.frombytes(mode, size, data)
                        img.save(fn + ".png")
                    elif '/DCTDecode' in xObject[obj]['/Filter']:
                        img = open(fn + ".jpg", "wb")
                        img.write(data)
                        img.close()
                    elif '/JPXDecode' in xObject[obj]['/Filter'] :
                        img = open(fn + ".jp2", "wb")
                        img.write(data)
                        img.close()
                    elif '/LZWDecode' in xObject[obj]['/Filter'] :
                        img = Image.frombytes(mode, size, bytes(data, "utf-8"))
                        img.save(fn + ".tif")
                        
                        #img = open(fn + ".jpg", "wb")
                        #img.write(bytes(data, "utf-8"))
                        #img.write(data)
                        #img.close()
                        #im = Image.open(f"{fn}.tif")
                        #im.save(f"{fn}.jpeg")
                    else :
                        print ('Unknown format:', xObject[obj]['/Filter'])
                except :
                    traceback.print_exc()
                
def readimg_tess(jpg_file, model_file):
    
   if (os.path.isfile(model_file)):   
       with open(model_file, 'rb') as fileh:
         reader = pickle.load(fileh)
   else:
      reader = easyocr.Reader(['en'], gpu=False) 
      #with open(model_file, 'wb') as fileh:
      #   pickle.dump(reader, fileh)
      
   img = cv.imread(jpg_file)
   #img2 = cv.blur(img,(5,5))
   img2 = cv.cvtColor(img,cv.COLOR_BGR2RGB)      

   results = ts.image_to_data(img2)
   
   print("---------------Tesseract Output-------------------------")
   rows = []
   for row in results.split("\n"):
       rows.append(list(row.split("\t")))
       
#   for row1 in rows:
#       print(row1)
   
   y_prev = 0
   x_prev = 0
   line = ""
   i = -1

   #df = pd.DataFrame(rows)
   str_data = io.StringIO(results)
   df = pd.read_csv(str_data, sep="\t")
   df = df.sort_values(["top","left"]) 
   df.to_csv("img_data.csv", sep=",",quotechar='"')
   
   l = 1
   df['line'] = 999
   
   for idx, row1 in df.iterrows():
       x = int(row1[6])  #left
       y = int(row1[7])  #top
       
       if abs(y - y_prev) > 4 : 
          l = l + 1
          y_prev = y   
          
       df.loc[idx, 'line'] = l
          
       
       
   df = df.sort_values(["line","left"]) 
   df.to_csv("img_data.csv", sep=",",quotechar='"')
   
   y_prev = 0
   x_prev = 0
   l_prev = 0
   
   for idx, row1 in df.iterrows():
#       i = i + 1
#       print (f"{i}. Row={row1} :")
#       if i == 0 or len(row1) < 11:
#           continue

       x = int(row1[6])  #left
       y = int(row1[7])  #top
       txt = row1[11]
       conf = float(row1[10])
       l = int(row1[12])

       print(f"STR: {i}.  Y: {y}  X: {x} Txt: {txt} ")
       if conf == -1 :
           continue
       
       if l_prev <= l and x_prev <= x: 
          line = line +": "+txt
       else:
          line = line + f"\n*{l}-{y}-{x}* " + txt
          #line=txt
          
       l_prev = l
       x_prev = x
          
          
   print(line)
if __name__=='__main__':
    
    print("---------------------------------------------------")
    sys.path.append(r'C:\Users\Anit\Documents\dev-soft\tesseract')
    #print("PATH: ",sys.path )
    ts.pytesseract.tesseract_cmd = "C:\\Users\\Anit\\Documents\\dev-soft\\tesseract\\tesseract.exe"
    
    pdf_file = "C:/Users/Anit/Documents/work/python/davis-invoice-test.pdf"
    readpdf_tess(pdf_file)
    #readpdf(pdf_file)
    
    jpg_file = "C:/Users/Anit/Documents/work/python/davis-invoice-image.jpg"
    model_file = "C:/Users/Anit/Documents/work/python/ocr_model.pkl"
    #readimg(jpg_file, model_file)
    #readimg_tess(jpg_file, model_file)