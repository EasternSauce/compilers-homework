from __future__ import print_function
import os
import sys
import re
import codecs
from datetime import datetime

month_lengths = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
date_separators = [r'\.', r'/', r'-']


def generate_date_regex():
    regex = ''
    for separator in date_separators:
        month = 1
        for month_length in month_lengths:
            day_regex = r'(?:{1}[0-{2}]|[0-{0}][0-9]|[0-9])'.format(month_length / 10 - 1, month_length / 10,
                                                                    month_length % 10)
            if month < 10:
                month_regex = r'(?:0{0}|{0})'.format(month)
            else:
                month_regex = r'{0}'.format(month)

            if month == 1:
                print(month_regex, '\n')

            to_add = r'(?:(?:{0}{2}{1}{2}[0-9][0-9][0-9][0-9])|(?:[0-9][0-9][0-9][0-9]{2}{0}{2}{1}))'.format(day_regex,
                                                                                                month_regex, separator)
            regex += to_add
            regex += r'|'
            month += 1
    regex = regex[0:len(regex) - 1]  # remove last character which is unnecesasary |
    return r'\b{0}\b'.format(regex)


date_regex = generate_date_regex()  # really long regex, needs a generator


def string_to_date(string):  # string date converted to date object
    for separator in date_separators:
        if re.compile(r'[0-9][0-9]{0}|[0-9]{0}'.format(separator)).match(string):
            if separator == r'\.':
                return datetime.strptime(string, r'%d.%m.%Y')
            else:
                return datetime.strptime(string, r'%d{0}%m{0}%Y'.format(separator))
        elif re.compile(r'[0-9][0-9][0-9][0-9]{0}'.format(separator)).match(string):
            if separator == r'\.':
                return datetime.strptime(string, r'%Y.%d.%m')
            else:
                return datetime.strptime(string, r'%Y{0}%d{0}%m'.format(separator))


def process_file(filepath):
    fp = codecs.open(filepath, 'rU', 'iso-8859-2')

    content = fp.read()

    # ''.join(list) converts list of strings to a single string
    meta_content = '\n'.join(re.compile(r'<META NAME=.*?>').findall(content))
    body_content = '\n'.join(re.compile(r'<P[\s\S]*?(?=<META)').findall(content))

    author = re.compile(r'<META NAME="AUTOR" CONTENT="(.*?)">').findall(meta_content)
    category = re.compile(r'<META NAME="DZIAL" CONTENT="gazeta/(.*?)">').findall(meta_content)
    keywords = re.compile(r'<META NAME="KLUCZOWE_\d" CONTENT="([\w\s]+?)">').findall(meta_content)

    ended_sentences = r'[A-Za-z]{4,}[\.|\?|!]+'
    unended_sentences = r'[A-Za-z]\n|[A-Za-z]<.*?>'
    sentences = re.compile(r'({0})|({1})'.format(ended_sentences, unended_sentences)).findall(body_content)

    shortcuts = re.compile(r'\b[A-Za-z]{1,3}\.').findall(body_content)  # three letter at maximum word ending with a dot
    shortcuts_set = set(shortcuts)

    positive_int = r'[0-9]|[1-9][0-9]|[1-9][0-9][0-9]|[1-9][0-9][0-9][0-9]|[1-2][0-9][0-9][0-9][0-9]' \
                   + r'|3[0-1][0-9][0-9][0-9]|32[0-6][[0-9][0-9]|327[0-5][0-9]|3276[0-7]'
    negative_int = r'-32768|-({0})'.format(positive_int)
    integers = re.compile(r'\b(({0})|({1}))\b'.format(positive_int, negative_int)).findall(body_content)
    integers_set = set(integers)

    floating = re.compile(r'\b-?([0-9]+\.[0-9]+[Ee]+[+-][0-9]+|[0-9]+\.[0-9]+|[0-9]+\.|\.[0-9]+)\b').findall(
        body_content)
    floating_set = set(floating)

    dates = re.compile(date_regex).findall(body_content)
    dates_set = set()
    for date in dates:
        dates_set.add(string_to_date(date))

    emails = re.compile(r'\b\w+@\w+(\.\w+)+\b').findall(body_content)
    emails_set = set(emails)

    fp.close()
    print("nazwa pliku:", filepath)
    print("autor:", ''.join(author))
    print("dzial:", ''.join(category))
    print("slowa kluczowe:", ', '.join(keywords))
    print("liczba zdan:", len(sentences))
    print("liczba skrotow:", len(shortcuts_set))
    print("liczba liczb calkowitych z zakresu int:", len(integers_set))
    print("liczba liczb zmiennoprzecinkowych:", len(floating_set))
    print("liczba dat:", len(dates_set))
    print("liczba adresow email:", len(emails_set))
    print("\n")


try:
    path = sys.argv[1]
except IndexError:
    print("Brak podanej nazwy katalogu")
    sys.exit(0)

tree = os.walk(path)

for root, dirs, files in tree:
    for f in files:
        if f.endswith(".html"):
            filepath_ = os.path.join(root, f)
            process_file(filepath_)
