# My cleaning script
def number_clean(number):
    if len(number) < 1:
        clean = "not available"
    elif len(number) < 8:
        clean = "not available"
#         print(number)
    else:
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
    if clean[:1] != '+':
        if clean != 'not available':
            clean = ('+49 ' + clean[1:]).replace('  ', ' ')
    if clean[:2] == '+0':
        clean = ('+49 ' + clean[2:])
    return clean


def format_number(number):
    value = number.replace(' ', '').replace('+49', '+49 ').replace('+43', '+43 ').replace(
        '+48', '+48 ').replace('+86', '+86 ').replace('+7', '+7 ').replace('+0', '+49 ')
    parts = value.split(' ')
    value = parts[0] + ' ' + parts[1][:4] + ' ' + parts[1][4:]
    return value


def email_split(mail):
    splits = mail.split('@')
    if len(splits) == 1:
        mail = mail.replace('(at)', '@').replace(
            '-at-', '@').replace(' ', '').replace('info', 'info@')
        return mail
    elif len(splits[0]) == 0:
        if 'pruskil' in mail:
            mail = 'info' + mail
        elif 'fcm' in mail:
            mail = 'sales' + mail
        return mail


def DataClean(df):
    # Cleaning the phone and fax numbers (and formating them)
    string_to_clean = ["Phone", "Fax"]
    for item in string_to_clean:
        for i in range(len(df[item])):
            item_clean = number_clean(str(df[item][i]))
            df[item][i] = item_clean
            value = df[item][i]
            if value != "not available":
                if len(value) > 22:
                    value = value.replace('oder', '/').replace('bzw.', '/')
                    if '/' not in value:
                        value = value.replace(' +49', ' / +49')
                splits = value.split('/')
                if len(splits) > 1:
                    splits[1] = splits[1].replace(
                        'kostenfrei', '').replace('  ', '')
                for j in range(len(splits)):
                    splits[j] = number_clean(splits[j])
                    splits[j] = format_number(splits[j])
                df[item][i] = ' / '.join(splits)


    for i in range(len(df["Contact person"])):
        if isinstance(df["Contact person"][i], float):
            df["Contact person"][i] = "not available"

    for item in df:
        for i in range(len(df[item])):
            if isinstance(df[item][i], str):
                if len(df[item][i]) < 2:
                    df[item][i] = "not available"
            else:
                df[item][i] = df[item][i].decode("latin-1")

            # TAKE CARE OF THISS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            
    # for i in range(len(df['Email'])):
    #     if df['Email'][i] != 'not available':
    #         df['Email'][i] = email_split(df['Email'][i])
    #         if mail:
    #             mail = email_split(mail)
    #             if mail:
    #                 mail = 'not available'
    return df
