#!/usr/bin/python3
# -*- coding: iso-8859-15 -*-
"""
This file is part of the cintruder project, https://cintruder.03c8.net

Copyright (c) 2012/2020 psy <epsylon@riseup.net>

cintruder is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free
Software Foundation version 3 of the License.

cintruder is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along
with cintruder; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
from PIL import Image
from operator import itemgetter
import os, hashlib, time, sys, subprocess, platform
import shutil

class CIntruderOCR(object):
    """
    Class to apply OCR techniques to EasyCaptcha (http://kestas.kuliukas.com/EasyCaptcha/EasyCaptcha/easycaptcha.php)
    """
    def __init__(self, captcha, options):
        # generate words structure (+ previews for gui)
        if not os.path.exists("outputs/words/"):
            os.mkdir("outputs/words/")
        else:
            shutil.rmtree("outputs/words/")
            os.mkdir("outputs/words/")
        if not os.path.exists("core/images/previews/"):
            os.mkdir("core/images/previews/")
        else:
            shutil.rmtree("core/images/previews/")
            os.mkdir("core/images/previews/")
        if not os.path.exists("core/images/previews/ocr/"):
            os.mkdir("core/images/previews/ocr/")
        else:
            shutil.rmtree("core/images/previews/ocr/")
            os.mkdir("core/images/previews/ocr/")
        # initialize main CIntruder
        try:
            im = Image.open(captcha)
            im.save("core/images/previews/last-preview.gif")
            im2 = Image.new("P", im.size, 255)
            im = im.convert("P")
        except:
            print("[Error] Fail during OCR process!. Is that captcha supported?\n")
            return
        colourid = []
        try: # extract colour histogram
            hist = im.histogram()
        except:
            print("[Error] Something wrong extracting histogram. Aborting...\n")
            return
        values = {}
        for i in range(256):
            values[i] = hist[i]
        if options.verbose:
            print("[Info] Extracting advanced OCR info...")
            print("\n=============================")
            print("Image Histogram (order by >):")
            print("=============================")
        for j, k in sorted(list(values.items()), key=itemgetter(1), reverse=True)[:10]:
            colourid.append(j)  
            if options.verbose:
                print("Colour ID: [ "+ str(j) + " ] -> Total pixels: " +str(k))
        if options.verbose:
            print("")
        temp = {}
        for x in range(im.size[1]):
            for y in range(im.size[0]):
                pix = im.getpixel((y, x))
                temp[pix] = pix
                if options.setids:
                    colourid = int(options.setids)
                    if pix == colourid:
                        im2.putpixel((y, x), 0)
                else:
                    if pix == colourid[1]: #id numbers of colours to get (*)
                        im2.putpixel((y, x), 0)
        im2.save("outputs/last-ocr_image-processed.gif")
        inletter = False
        foundletter = False
        start = 0
        end = 0
        letters = []
        for y in range(im2.size[0]): 
            for x in range(im2.size[1]): 
                pix = im2.getpixel((y, x))
                if pix != 255:
                    inletter = True
            if foundletter == False and inletter == True:
                foundletter = True
                start = y
            if foundletter == True and inletter == False:
                foundletter = False
                end = y
                letters.append((start, end))
            inletter = False
        count = 0
        for letter in letters:
            m = hashlib.md5()
            try:
                m.update(str(letter))
            except:
                m.update(str(letter).encode('utf-8'))
            im3 = im2.crop(( letter[0], 0, letter[1], im2.size[1] ))
            im3.save("outputs/words/%s.gif"%(m.hexdigest()))
            im3.save("core/images/previews/ocr/%s.gif"%(m.hexdigest()))
            count += 1
        print("[Info] Processing captcha/image with OCR algorithms. Please wait...\n")
        print("=================")
        print("Training Results:")
        print("=================")
        print("\n[Info] Number of 'symbols' found: "+ str(count)+"\n")
        if count == 0:
            print("\nOuch!. Looks like this captcha is resisting to our OCR methods... by the moment ;-)\n")
            print("Try this...\n") 
            print("    1) Check colour's ID values and quantity of pixels of each by using verbose") 
            print("    2) Set different ID values to your OCR configration and try it again")
            print("    3) Try to apply some image filters (ex: B/W) manually with an editor (ex: GIMP) to your target")
            print("    4) Maybe this module that you are using is not working for this captcha...\n")
            print("------------\n")
        else:
            path, dirs, files = next(os.walk("outputs/words/"))
            file_count = str(len(files))
            print("[Info] Generated [ "+ file_count+ " ] OCR images here: outputs/words/\n")
            if options.verbose:
                # checking for platform to list new words added to dictionary
                os_sys = platform.system()
                if os_sys == "Windows":
                    subprocess.call("dir outputs/words/", shell=True)
                else:
                    subprocess.call("ls outputs/words/", shell=True)
                print("")
            print("Now move each (human-recognized) OCR image to the correct folder on: dictionary/\n")

if __name__ == "__main__":
    if sys.argv[1:]:
        ocr = CIntruderOCR(sys.argv[1:])
        print ("Data correctly extracted!")
    else:
        print ("You must set a captcha for learn. Ex: inputs/test1.gif")
