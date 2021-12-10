from ru.views import *

from docx.document import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph
import docx


def get_image_with_rel(doc, rid):
    for rel in doc.part._rels:
        rel = doc.part._rels[rel]
        if rel.rId == rid:
            return rel.target_part.blob


def iter_block_items(parent):
    if isinstance(parent, Document):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        raise ValueError("something's not right")

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)


def doctable(ls, row, column):
    df = pd.DataFrame(np.array(ls).reshape(row, column))  # reshape to the table shape
    df.columns = df.loc[0, :].values
    df = df.loc[1:, :].dropna(how="all").drop_duplicates().reset_index(drop=True)
    return df


def genarate_table(table):
    ls = []
    for row in table.rows:
        for cell in row.cells:
            temp = []
            for paragraph in cell.paragraphs:
                temp.append(paragraph.text)
            ls.append('\n'.join(temp))
    return doctable(ls, len(table.rows), len(table.rows[0].cells))


class BaseDocxHandle(object):

    def __init__(self, path):
        self.path = path
        self.proper_nouns = set()
        self.document = docx.Document(self.path)

    def get_docx_structure(self):
        tmp = []
        for para in iter_block_items(self.document):
            style_name = para.style.name

            if 'docx.table.Table' in str(para):
                table = genarate_table(para)
                if len(table) < 1:
                    continue
                tmp.append({'type': 'table', 'style': style_name, 'content': table})
                continue

            if 'imagedata' in para._p.xml:
                rid = re.findall('imagedata r:id=(.*?) ', para._p.xml)[0].replace('"', '')
                tmp.append({'type': 'image', 'style': style_name, 'content': get_image_with_rel(self.document, rid)})
                continue

            doc = para.text.strip()
            if doc in ['', '\n']:
                continue
            if style_name in ['List abc double line', 'List number single line']:
                style_name = 'List Bullet'
            tmp.append({'type': 'text', 'style': style_name, 'content': doc})
        return {'name': self.document.core_properties.title, 'content': tmp}

    def get_catalog(self):
        data = self.get_docx_structure()
        prev_level = 0
        content = [0 for _ in range(0, 10)]
        count = [0 for _ in range(0, 10)]
        tmp = []
        for elm in data['content']:
            if 'Heading ' in elm['style'].strip():
                current_level = int(elm['style'].strip().split(' ')[1])

                if prev_level == current_level:
                    content[current_level - 1] = elm['content']
                    count[current_level - 1] += 1
                elif prev_level + 1 == current_level:
                    content[current_level - 1] = elm['content']
                    prev_level = current_level
                    count[current_level - 1] = 1
                elif prev_level > current_level:
                    content[current_level - 1] = elm['content']
                    prev_level = current_level
                    count[current_level - 1] += 1
                    content[current_level:] = [0 for _ in range(current_level, 10)]
                    count[current_level:] = [0 for _ in range(current_level, 10)]
                tmp.append({'chapter': '.'.join([str(v) for v in count if v != 0]), 'title': [str(v) for v in content if v != 0][-1], 'path_content':
                            ' '.join([str(v) for v in content if v != 0])})
        return {'name': self.document.core_properties.title, 'catalog': tmp}

##########################################################################################

def is_db_line(line):
    if len(line) <= 2:
        return False
    elif line[0:2] == "/*":
        return False
    return True


def clean_line(line):
    if "/*" in line:
        line = line.split('/*')[0]
    line = re.sub(' +', ' ', line.replace(" \"","\"").replace(',', ' ').replace('"', '')).strip()
    if line.split(' ')[-1] == '':
        return line.split(' ')[0:-1]
    return line.split(' ')


def parse_db_txt(path):
    with open(path, "r") as f:
        lines = f.readlines()
        result = {}
        key = ''
        value = []
        val_type = ''
        for line in lines:
            line = re.sub(' +', ' ', line.strip().replace("\n", ''))
            if is_db_line(line):
                if line[0] == '/':
                    if (key != '') & (len(value) != 0):
                        result[key] = {'type': val_type, 'value':value}
                        key = ''
                        val_type = ''
                        value = []
                    key = line.split()[0]
                    val_type = line.split()[1]
                    value.extend(clean_line(' '.join(line.split()[2:])))
                else:
                    value.extend(clean_line(line))
        if (key != '') & (len(value) != 0):
            result[key] = {'type': val_type, 'value':value}
    return result


def is_driver_container(driver_name, driver_sets):
    for db_key in driver_sets.keys():
        if driver_name+'/type' in db_key:
            if driver_sets[db_key]['value'][0] == 'DriverContainer':
                return db_key, True
    return '', False


def extract_db_by_drvier_name(driver_name, data):
    result = []
    _type = ''
    for db_key in data.keys():
        db_keys = db_key.split('/')
        com_key = ''
        if ':' in driver_name:
            com_key = driver_name.split(':')[0] + ':x'

        if (driver_name in db_keys) or ((com_key in db_keys) & (com_key != '')):
            if db_key[-5:] == '/type':
                _type = data[db_key]['value'][0]
            else:
                result.append({'name': db_key + ' ' + data[db_key]['type'] + ' ' + ' '.join(data[db_key]['value']), 'color':'#000000'})
    return {'name': _type, 'children': result}


def extract_dbs(entry_name):
    driver_sets = parse_db_txt("D:\\projects\\test\\db_tool_data\\driverSetsPrdType_1_1.txt")
    driver_drivers = parse_db_txt("D:\\projects\\test\\db_tool_data\\deviceDriversPrdType_1_1.txt")
    channels = parse_db_txt("D:\\projects\\test\\db_tool_data\\channelsPrdType_1_1.txt")

    driver_entry = entry_name
    hw_db = {'name': driver_entry, 'children': []}
    for driver in driver_sets[driver_entry]['value']:
        db_key, flag = is_driver_container(driver, driver_sets)
        if flag:
            dirvers = []
            for _dirver in driver_sets[db_key.replace("/type", "/drivers")]['value']:
                tmp = extract_db_by_drvier_name(_dirver, driver_drivers)
                if len(tmp['children']) == 0:
                    tmp = extract_db_by_drvier_name(_dirver, channels)
                else:
                    tmp['children'].extend(extract_db_by_drvier_name(_dirver, channels)['children'])
                dirvers.append(tmp)
            hw_db['children'].append({'name': driver, 'color':'#000000', 'children': dirvers})
        else:
            tmp = extract_db_by_drvier_name(driver, driver_sets)
            if len(tmp['children']) == 0:
                tmp = extract_db_by_drvier_name(driver, driver_drivers)
            else:
                tmp['children'].extend(extract_db_by_drvier_name(driver, driver_drivers)['children'])
            hw_db['children'].append({'name': driver, 'color':'#000000', 'children': tmp})
    return hw_db


def get_dbs_by_drvier_name(driver_name):
    hw_db = extract_dbs('/810/trxDrivers')
    for item in hw_db['children']:
        if item['name'] == driver_name:
            return item
    return {}