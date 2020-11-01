from src import *

#Свид__АГР
def parsing_of_svid_agr(list_):
    t = ' '.join(list_)
    #print(t)
    p1 = re.compile(r'[Кк]од строительного объекта?:?[ ]?[0-9-/А-ЯA-Z]+[ ]').findall(t)
    if p1: 
        p1 = p1[0]
    else:
        p1 = None
    p2 = re.compile(r'[рР]егистрационный №?:?[ ]?[0-9-/А-ЯA-Z]+[ ]').findall(t)
    if p2: 
        p2 = p2[0]
    else:
        p2 = None
    p3 = re.compile(r'[рР]айон:?[ ]?\w+[ ]').findall(t)
    if p3: 
        p3 = p3[0]
    else:
        p3 = None
    #p4 = re.compile(r'[рР]айон:?[ ]?\w+[ ]').findall(t)
    return {'object_code': p1, 'reg_number': p2, 'district': p3}

#Разр__на_ввод
# Разр__на_ввод1pictures
def parsing_of_razr_on_vv(list_):
    t = ' '.join(list_)
    #print(t)
    p1 = re.compile(r'[Кк]ому:?[^0-9]+[\'\"][0-9-/А-ЯA-Zа-яa-z_ ]+[\'\"]').findall(t)
    if p1: 
        p1 = p1[0]
    else:
        p1 = None
    # разрешение на ввод объекта в эксплуатацию
    p2 = re.compile(r'эксплуатаци[юя]:?[ ]?№[ ]?\w[0-9-]+|объект[ауе]?:?[ ]?№[ ]?\w+').findall(t)
    if p2: 
        p2 = p2[0]
    else:
        p2 = None
    #p4 = re.compile(r'[рР]айон:?[ ]?\w+[ ]').findall(t)
    return {'to_whom': p1, 'expluatation': p2}

# БТИ
# БТИ26__ул_Шеногина__дом_3__строение_45_измpictures
def parsing_of_bti(list_):
    t = ' '.join(list_)
    #print(t)
    p1 = re.compile(r'[Кк]варт[.]?[ ]?№[ ]?\d+').findall(t)
    if p1: 
        p1 = p1[0]
    else:
        p1 = None
    # разрешение на ввод объекта в эксплуатацию
    p2 = re.compile(r'[Оо]бъем[ ]?[0-9.,]+').findall(t)
    if p2: 
        p2 = p2[0]
    else:
        p2 = None
    p3 = re.compile(r'[Вв]ладелец[ ]?\w+[\"А-Яа-я ]+').findall(t)
    if p3: 
        p3 = p3[0]
    else:
        p3 = None
    return {'quart': p1, 'square': p2, 'owner': p3}

# Разр__на_стр
def parsing_of_build_permission(list_):
    t = ' '.join(list_)
    #print(t)
    deal_number = re.compile(r'[Дд]ело[ ]*№[ ]*[0-9]*').findall(t)
    if deal_number: 
        deal_number = deal_number[0]
    else:
        deal_number = None
    doc_number = re.compile(r'[a-zA-Zа-яА-Я][0-9]+-[0-9]+').findall(t)
    if doc_number: 
        doc_number = doc_number[0]
    else:
        doc_number = None
    client = re.compile(r'[Кк]ому: \S+[ ]\S+[ ]').findall(t)
    if client: 
        client = client[0]
    else:
        client = None
    issuing_authority = re.compile(r'ПРАВИТЕЛЬСТВО [А-Я]+[ ][А-Я]+[ ][А-Я]+[ ][А-Я]+[ ][А-Я]+').findall(t)
    if issuing_authority: 
        issuing_authority = issuing_authority[0]
    else:
        issuing_authority = None
    date = re.compile(r'«[0-9]+»[ ]*[а-яА-Я]+[ ]*[0-9]{4}').findall(t)
    if date: 
        date = date[0]
    else:
        date = None

    return {'deal_number': deal_number, 
            'doc_number': doc_number, 
            'client': client, 
            'issuing_authority': issuing_authority, 
            'date': date}

# ЗУ
def parsing_of_rent_contract(list_):
    t = ' '.join(list_)
    #print(t)
    scale = re.compile(r'Масштаб [0-9][ ]*:[ ]*[0-9]*').findall(t)
    if scale: 
        scale = scale[0]
    else:
        scale = None
    cadastr = re.compile(r'[0-9]{2}[ ]*:[ ]*[0-9]{2}[ ]*:[0-9]+[ ]*:[ ]*[0-9]+').findall(t)
    if cadastr: 
        cadastr = cadastr[0]
    else:
        cadastr = None
    doc_number = re.compile(r'№ [a-zA-Zа-яА-Я]-[0-9]{2}-[0-9]+').findall(t)
    if doc_number: 
        doc_number = doc_number[0]
    else:
        doc_number = None
    area = re.compile(r'[0-9]+[.[0-9]+]? КВ.М. ПЛОЩАДЬ').findall(t)
    if area: 
        area = area[0]
    else:
        area = None
    term = re.compile(r'сроком на \S+[ ]\S+[ ]').findall(t)
    if term: 
        term = term[0]
    else:
        term = None
    account = re.compile(r'№[ ]?[0-9]{20}').findall(t)
    if account: 
        account = account[0]
    else:
        account = None

    return {'scale':scale, 
            'cadastr':cadastr, 
            'doc_number':doc_number, 
            'area':area, 
            'term':term,
            'account':account}

def get_result(PATH, show=True):

    logging.info('Start work')
    PATH1 = pdf_to_img_my_v1(PATH)
    logging.info('images in %s'%PATH1)
    print(PATH1)
    Q = docimg_to_text(path=PATH1, with_rotate=False, show=True)
    logging.info('Text extraction complete!')

    qq = ''
    flag = list(Q.keys())[0]
    for i in Q[flag]:
        q = ' '.join(Q[flag][i]).replace('95', '').lower()
        qq = qq + ' ' + q
        
    Q_all = []
    for i in Q[flag]:
        Q_all = Q_all + Q[flag][i]

    logging.info('Name: ', flag, '\n')

    res = {}
    for key in regular_dict_old:
        res.setdefault(key, 0)
        for i in regular_dict_old[key]:
            promres = re.compile(i).findall(qq)
            res[key] = res[key] + len(set(promres))
            
    RES = sorted([[i[1], i[0]] for i in list(res.items())], reverse=True)
    
    fin_dict = {'file_name': flag,
            'doc_type': RES[0][1],
            # Свид__АГР
            'object_code': None,
            'reg_number': None,
            'district': None,
            #Разр__на_ввод
            'to_whom':None,
            'expluatation': None,
            # БТИ
            'quart': None,
            'square': None,
            'owner': None,
            # ЗУ
            'scale': None, 
            'cadastr': None, 
            'doc_number': None, 
            'area': None, 
            'term': None,
            'account': None,
            # Разр__на_стр
            'deal_number': None, 
            'doc_number': None, 
            'client': None, 
            'issuing_authority': None, 
            'date': None,
            'all_text': Q_all,
            }
            
    add_dict = {}

    if RES[0][1] == 'Свид__АГР':
        add_dict = parsing_of_svid_agr(Q_all)
    elif RES[0][1] == 'Разр__на_ввод':
        add_dict = parsing_of_razr_on_vv(Q_all)
    elif RES[0][1] == 'БТИ':
        add_dict = parsing_of_bti(Q_all)
    elif RES[0][1] == 'Разр__на_стр':
        add_dict = parsing_of_build_permission(Q_all)
    elif RES[0][1] == 'ЗУ':
        add_dict = parsing_of_rent_contract(Q_all)
        
    fin_dict.update(add_dict)
    
    return fin_dict