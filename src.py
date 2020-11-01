import os
from pdf2image import convert_from_path
import time
import logging
import sys
import numpy as np
import re
from PIL import Image as IM
import cv2
import pytesseract as pt

regular_dict_old = {'Свид__АГР': ['КОМИТЕТ \w{2,4} АРХИТЕКТУР\w \w{1,2} ГРАДОСТРОИТЕЛЬСТВ\w'.lower(),
                                  'свидетельств\w \w{1,4} утверждени\w'],
    'Разр__на_стр': ['КОМИТЕТ ГОСУДАРСТВЕННОГО СТРОИТЕЛЬНОГО НАДЗОРА'.lower(),
                     'РАЗРЕШЕНИ\w на строительство'.lower(),
                     'строительство объекта'],
    'Разр__на_ввод': ['КОМИТЕТ СТРОИТЕЛЬНОГО НАДЗОРА'.lower(),
                      'разрешени[ею] \w+ ввод объект\w{0,1} \w+ эксплуатацию'],
    'ЗУ': ['земельн[ыо][гйм][о]{0,1} комитет',
            'земельн[ыо][гйм][о]{0,1} участ[ко][ак]',
            'договор[у]{0,1} \w+ предоставлении участк[ао][м]{0,1}',
            'безвозмездного пользования дополнительное соглашение аренд[аы]'],
    'БТИ': ['ТЕХНИЧЕСКИЙ ПАСПОРТ'.lower(),
            'ЭКСПЛИКАЦИ[яю]'.lower()]
                   }
                   

def pdf_to_img_my_v1(file_pdf_path, show=True):
    # storage.goai.ru
    PUNCT = ['.', ',', ':', ';', ' ']
    dir_, filename = os.path.split(file_pdf_path)
    for sign in PUNCT:
        filename = filename.replace(sign, '_')
    if '_pdf' in filename:
        ind = filename.index('_pdf')
    elif '_pdf'.upper() in filename:
        ind = filename.index('_pdf'.upper())
    else:
        logging.info('Cannot remade %s'%filename)
        return None
    new_dir_name = dir_ + filename[:ind] + '_pictures'
    os.popen(r'mkdir %s'%new_dir_name).read()
    if show:
        logging.info(new_dir_name)
    pages = convert_from_path(file_pdf_path,
                            200,
                            output_folder=new_dir_name,)
    cnt = 1
    for page in pages:
        pic_name = os.path.join(new_dir_name, 'out_%s.png'%str(cnt))
        page.save(pic_name, 'JPEG')
        cnt = cnt + 1
    for file in os.listdir(new_dir_name):
        if '.png' in file:
            continue
        os.popen(r'rm %s'%os.path.join(new_dir_name, file)).read()
    return new_dir_name
        
        
def rotate(image, center=None, scale=1.0, show=True):
    angle = 360 - int(re.search('(?<=Rotate: )\d+', pt.image_to_osd(image)).group(0))
    if angle == 0 or angle == 360:
        return np.asarray(image)
    (h, w) = np.asarray(image).shape[:2]

    if center is None:
        center = (w / 2, h / 2)

    # Perform the rotation
    M = cv2.getRotationMatrix2D(center, angle, scale)
    rotated = cv2.warpAffine(np.asarray(image), M, (w, h))
    if show:
        logging.info('Rotated on %s angle'%str(angle))
    return rotated
    

# img analyse

def ImToText2(img_):
    img_2 = IM.fromarray(img_)
    q = pt.image_to_string(img_2, lang='rus')#--psm 12 --oem 3
    q = [i.strip() for i in q.split('\n') if i.strip()]
    q1 = [i.replace('\t', ' ') for i in q]
    return q1
    
    
# main var img
def ImToText1(img_, bd=200):
    #img_ = np.asarray(img.open(img_))
    #img_1 = copy.deepcopy(img_)
    #img_1[img_1<bd]=0
    #img_2 = img.fromarray(img_1)
    img_2 = IM.fromarray(img_)
    q = pt.image_to_data(img_2, lang='rus')#--psm 12 --oem 3
    q = [i.strip() for i in q.split('\n') if i.strip()]
    q0 = [i.split('\t') for i in q]
    # Теперь когда есть информация о положении слов на картинке а именно их абсцисса и ординада, можно их упорядочить по строкам и внутри строк
    te = {}
    no_list = ['*', '-', '-1', '—', '|', '/', '\\', '.', ','] # Если строка состоит лишь из этих символов(обычно это рудименты меток и графических элементов)
    picture_rudiments = ['‘', ]
    # такую строку не учитываем
    for i in q0:
        text = i[-1]
        I = i[-5] # ордината
        J = i[-6] # абсцисса
        if text in no_list or (not I.isnumeric()): continue
        for i in picture_rudiments:
            text = text.replace(i, '')
        if int(I) in te: te[int(I)] = te[int(I)]  + [[int(J), text]] # Составим словарь опираясь на ординату
        else: te[int(I)] = [[int(J), text]]
    ll = sorted(te) # Упорядочим по ординате
    ld = [te[i] for i in sorted(te)]
    LL = []
    for i in ll:
        if ll.index(i)==0:
            LL = LL + [i]
            continue
        else:
            if i in range(LL[-1], LL[-1]+6+1): # также ввиду неточности анализа некоторые фрагменты одной строки могут иметь немного отличающиеся ординаты(введем допуск)
                LL = LL + [LL[-1]]
            else:
                LL = LL + [i]
    fdin = {} # сформируем окончательный словарь и упорядочим слова(фрагменты) внутри строки            
    for i in range(len(LL)):
        if LL[i] in fdin:
            fdin[LL[i]] = fdin[LL[i]]  + ld[i]
        else:
            fdin[LL[i]] = ld[i]
    finlist = [' '.join([j[1] for j in sorted(fdin[i])]) for i in sorted(fdin)]
    finlist = [i for i in finlist if '@' not in i]
    return finlist
    
    
def docimg_to_text(path, with_rotate=False, show=False):
    
    dict_image_text = {}

    cnt = 1
    dict_image_text.setdefault(os.path.split(path)[-1], {})
    for pic in os.listdir(path): # на данный момент работаем только с первым изображением(лицевым)
        pic_path = os.path.join(path, pic)
        print(pic)
        try:
            im = np.asarray(IM.open(str(pic_path)))
        except:
            print('There is no file!')
            print(sys.exc_info()[1])
            continue
        try:
            if with_rotate:
                im1 = rotate(im)
            else:
                im1 = im
            im2 = im1.mean(axis=-1).astype('uint8')
            (h, w) = im2.shape[:2]
        except:
            print('Problem with rotation!')
            print(sys.exc_info()[1])
            continue
        try:
            im3 = cv2.fastNlMeansDenoising(im2, None, 20, 7)
        except:
            print('Problem with denoising!')
            print(sys.exc_info()[1])
            continue
        try:
            #if (h>100) and (w>100):
            #    hh = h//100*(h//100 % 2 == 1) + (h//100 + 1)*(h//100 % 2 == 1)
            #    ww = w//100*(w//100 % 2 == 1) + (w//100 + 1)*(w//100 % 2 == 1)
            #    im4 = cv2.adaptiveThreshold(im3, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            #                        cv2.THRESH_BINARY, hh, ww)
            #else:
            im4 = im3
            #if show:
            #    plt.figure(figsize=[30, 20])
            #    plt.imshow(im4)
            #    plt.show()
        except:
            print('Problem with thresholding image!')
            print(sys.exc_info()[1])
            continue
        text_ = ImToText1(im4)
        dict_image_text[os.path.split(path)[-1]].update({pic: text_})


    #pickle.dump(dict_image_text,
    #                    open(r'D:\Competitions_Tasks\Hackaton2020OCR_docs\Dataset\%s.pkl'%out_name, 'wb'))
    return dict_image_text

