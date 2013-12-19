from datetime import date
import os
import csv
from django.conf import settings
import numpy as np
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def handle_uploads(request, files):
    saved = []
    upload_dir = date.today().strftime(settings.UPLOAD_PATH)
    upload_full_path = os.path.join(settings.MEDIA_ROOT, upload_dir)

    if not os.path.exists(upload_full_path):
        os.makedirs(upload_full_path)

    for file in files:
        if file:
            upload = file
            while os.path.exists(os.path.join(upload_full_path, upload.name)):
                upload.name = '_' + upload.name
            dest = open(os.path.join(upload_full_path, upload.name), 'wb')
            for chunk in upload.chunks():
                dest.write(chunk)
            dest.close()
            saved.append((file, os.path.join(upload_dir, upload.name)))
    return saved


def handle_upload(request, file):
    upload_dir = date.today().strftime(settings.UPLOAD_PATH)
    upload_full_path = os.path.join(settings.MEDIA_ROOT, upload_dir)
    saved = ""
    if not os.path.exists(upload_full_path):
        os.makedirs(upload_full_path)

    if file:
        upload = file
        while os.path.exists(os.path.join(upload_full_path, upload.name)):
            upload.name = '_' + upload.name
        dest = open(os.path.join(upload_full_path, upload.name), 'wb')
        for chunk in upload.chunks():
            dest.write(chunk)
        dest.close()
        saved = os.path.join(upload_dir, upload.name)
    return saved


def document_validator(document, ex_col, ex_row):
    try:
        dialect = csv.Sniffer().sniff(document.read(4096), delimiters=[';', ',', '\t'])
        document.seek(0, 0)
        reader = csv.reader(document.read().splitlines(), dialect)
        temp_list = list(reader)

        # check char in first row and first col
        if not ex_row and not temp_list[0][-1].isdigit():
            raise ValueError
        if not ex_col and not temp_list[-1][0].isdigit():
            raise ValueError

        ncol = (len(temp_list[0]) - 1) if ex_row else len(temp_list[0])
        nrow = (len(temp_list) - 1) if ex_col else len(temp_list)
        is_cubic = True if (ncol == nrow) else False
        return_value = {'is_valid': True, 'nrow': nrow, 'ncol': ncol, 'separator': dialect.delimiter, 'is_cubic': is_cubic}
    except csv.Error:
        return_value = {'is_valid': False}
    except Exception:
        return_value = {'is_valid': False}
    except ValueError:
        return_value = {'is_valid': False}

    return return_value


def get_bootsrap_badge(status):
    if status == 'SUCCESS':
        badge = 'label-success'
    elif status == 'STARTED' or status == 'RUNNING':
        badge = 'label-primary'
    elif status == 'RETRY':
        badge = 'label-default'
    elif status == 'FAILURE':
        badge = 'label-danger'
    elif status == 'PENDING':
        badge = 'label-default'
    else:
        badge = 'label-default'

    return badge


def read_csv_results(files):
    result = []
    for f in files:
        pathabs = os.path.join(settings.MEDIA_ROOT, f)

        with open(pathabs, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')
            rowdata = []
            for row in reader:
                rowdata.append(row)
        result.append(rowdata)
        csvfile.close()

    return result