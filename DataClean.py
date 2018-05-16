########################################################### Email cleaning
def check_if_correct(mail):
    splits = mail.split('@')
    if len(splits) != 2:
        return False
    elif len(splits[0]) == 0:
        return False
    else:
        return True


def correct_mail(mail):
    mail = mail.replace('(at)', '@').replace('-at-', '@').replace('[at]', '@')
    mail = mail.replace(' ', '').replace('@@', '@')
    splits = mail.split('@')
    if 'kraftanlagen' in mail:
        mail = 'contact@kraftanlagen.com'
    elif 'infoverlagshaus' in mail:
        mail = 'info@verlagshaus.de'
    elif 'pruskil' in mail:
        mail = 'info' + mail
    elif 'fcm' in mail:
        mail = 'sales' + mail
    elif ('Kontaktformular' in mail) or ('kontaktfomular' in mail):
        mail = 'not available'
    elif 'http' in mail:
        mail = 'not available'
    elif len(splits) == 1:
        mail = mail.replace('(at)', '@').replace(
            '-at-', '@').replace('[at]', '@')
        mail = mail.replace(' ', '').replace('@@', '@')
        return mail
    elif len(splits[0]) == 0:
        return mail
    return mail


def clear_email(mail):
    if mail != 'not available':
        if not check_if_correct(mail):
            mail = correct_mail(mail)
            if not check_if_correct(mail):
                mail = 'not available'

    return mail


########################################################### First Name and Last Name
suffix_list = ['jun.', 'sen.', 'jr.']
# preffix_list = ['Dipl.-Ing.', 'Dipl. - Kfm.','Dipl.', 'Dr.', 'Prof.']
preffix_list = ['Prof. Dr.', 'Prof. Dipl.', 'Prof.', 'Dr.', 'Dipl.']
engineer_tag = 'Ing.'
tags = ['Math.', 'Phys.', 'Ing.', 'Kfm.']
# preffix_list = ['Dr.']

sufi_preff_replace_list = ['M.A.', '(Univ.)', '(Univ)']

special_surr = [' von', ' van']


def get_the_name(line):
    suffix = 'nan'
    preffix = 'nan'
    line = line.replace('Management', '')
    line = line.replace('Sales / marketing:', '')
    for item in suffix_list:
        if item in line:
            line = line.replace(item, '')
            suffix = item
    for item in preffix_list:
        if item in line:
            preffix = item
            for tag in tags:
                if tag in line:
                    preffix = preffix + '-' + tag
#             if item == 'Dipl.':
#                 print(preffix, line)
            line = line.replace(item, '')
            break
    for item in sufi_preff_replace_list:
        if item in line:
            line = line.replace(item, '')
    if 'HOFER' in line:
        line = line.replace('HOFER', 'Hofer')
    new_word = line.split()
    for j in range(len(new_word)):
        if '(Mr' in new_word[j]:
            name = new_word[j-2:j+1]
            for item in special_surr:
                if item in line:
                    name = [new_word[0], ' '.join(new_word[1:j]), new_word[j]]
                    if 'Ingo' in name[1]:
                        name[0] = name[0] + ' Ingo'
                        name[1] = name[1].replace('Ingo ', '')
                    if name[1] == 'Stechow von':
                        name[1] = 'von Stechow'
                    if name[1] == 'van de pas':
                        name[0] = 'Thomas'
                        name[1] = 'van de Pas'
#                 else:
#                     name = new_word[j-2:j+1]
#             print(name)
            name.append(suffix)
            name.append(preffix)

            return name


def separate_contact(word):
    if word == 'not available':
        return [word, word, word, 'nan', 'nan']
    if 'Management' in word:
        splits = word.split(':')
        for i in range(len(splits)):
            if 'Management' in splits[i]:
                name = get_the_name(splits[i+1])
                return name
    else:
        name = get_the_name(word)
        return name


#         We sort the names that do not have sufficient data!!
nan = 'not available'


def sort_unsufficient(word):
    if len(word) < 10:
        name = [nan, nan, nan, 'nan', 'nan']
    else:
        splits = word.split()
        if len(splits) == 2:
            name = [nan, splits[0], splits[1], 'nan', 'nan']
        elif len(splits) > 2:
            name = [splits[-3], splits[-2], splits[-1], 'nan', 'nan']
        else:
            name = [nan, nan, nan, 'nan', 'nan']
    return name


def clear_sex(sex):
    sex_cor = sex.replace('(', '').replace(')', '').replace('.', '')
    return sex_cor


def clean_name(contact):
    if isinstance(contact, float):
        return [nan, nan, nan]
    name = separate_contact(contact)
    if len(name) != 5:
        word = contact.replace('Management: ', '')
        name = sort_unsufficient(word)
    if name[3] != 'nan':
        name[1] = name[1] + ' ' + name[3]
    if name[4] != 'nan':
        name[1] = name[4] + ' ' + name[1]
    return [name[0], name[1], clear_sex(name[2])]


########################################################### Phone and Fax number cleaning
def number_clean(number):
    clean = number
    if clean[0] == 'b':
        clean = clean[2:-1]
    if clean[:2] == '49':
        clean = '+' + clean
    if clean[:4] == '0049':
        clean = ('+49 ' + clean[4:])
    if '.' in clean:
        if 'bzw' not in clean:
            clean = clean.replace('.', ' ')
    clean = clean.replace('-', '')
    clean = clean.replace('  ', ' ')
    clean = clean.replace('(0)', '')
    clean = clean.replace('(', '')
    clean = clean.replace(')', '')
    clean = clean.replace('/', '')
    clean = clean.replace('  ', ' ')
    clean = clean.replace('+ 49', '+49')
    clean = clean.replace('+49', '+49 ')
    clean = clean.replace('  ', ' ')
    clean = clean.replace('++', '+')
    clean = clean.replace('+0', '+')
#     if clean[:1] != '+':
    if clean[:1] == '0':
        if clean != 'not available':
            clean = ('+49 ' + clean[1:]).replace('  ', ' ')
    elif clean[:1] != '+':
        clean = clean.replace(clean[:1], '')
        if clean[0] != '+':
            clean = '+' + clean
    if clean[:2] == '+0':
        clean = ('+49 ' + clean[2:])
    return clean


def format_number(number):
    value = number.replace(' ', '').replace('+49', '+49 ').replace('+43', '+43 ').replace(
        '+48', '+48 ').replace('+41', '+41 ').replace('+86', '+86 ').replace('+7', '+7 ').replace('+0', '+49 ')
    parts = value.split(' ')
    try:
        value = parts[0] + ' ' + parts[1][:4] + ' ' + parts[1][4:]
    except:
        print(parts)
    return value


def clean_number(number):
    number = str(number)
    if len(number) < 8:
        clean = "not available"
    elif number == 'not available':
        clean = "not available"
#     elif len(number) < 8:
#         clean = "not available"
    elif len(number) > 24:
        number = number.replace('oder', '/').replace('bzw.', '/')
        if '/' not in number:
            number = number.replace(' +49', ' / +49')
        splits = number.split('/')
        if len(splits) > 1:
            splits[1] = splits[1].replace(
                'kostenfrei', '').replace('  ', '')
        for j in range(len(splits)):
            splits[j] = number_clean(splits[j])
            splits[j] = format_number(splits[j])
        clean = ' / '.join(splits)
    else:
        clean = number_clean(number)
        clean = format_number(clean)
    return clean


########################################################### Combine Address
def combine_address(street, town):
    output = street + ', ' + town + ', ' + 'Deutschland'
    return output

########################################################### Clear County


def clear_county(county, regierungsbezirk, regierungsbezirk_eng):
    output = county.replace(
        ' / ', '').replace(regierungsbezirk, '').replace(regierungsbezirk_eng, '')
    output = output.replace('Town', 'Stadt').replace(
        'Federal State Capital', 'Landeshauptstadt')
    return output

########################################################### Create dictionary line


def create_dict_line(row_list):
    line_dict = {
        'First Name': row_list[0],
        'Last Name': row_list[1],
        'Sex': row_list[2],
        'Email Address': row_list[3],
        'Address': row_list[4],
        'Landkreis': row_list[5],
        'Regierungsbezirk': row_list[6],
        'Phone Number': row_list[7],
        'Fax Number': row_list[8],
        'Company Name': row_list[9],
        'Homepage': row_list[10]
    }
    return line_dict


def DataClean(row, regierungsbezirk, regierungsbezirk_eng):
    contact_details = clean_name(row['Contact person'])
    contact_details.append(clear_email(row['Email']))
    contact_details.append(combine_address(row['Street'], row['PC/City']))
    contact_details.append(clear_county(
        row['County'], regierungsbezirk, regierungsbezirk_eng))
    contact_details.append(regierungsbezirk)

    contact_details.append(clean_number(row['Phone']))
    contact_details.append(clean_number(row['Fax']))
    contact_details.append(row['Company'])
    contact_details.append(row['Homepage'])
    dict_line = create_dict_line(contact_details)
    return dict_line
