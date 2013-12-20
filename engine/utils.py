from datetime import date
from django.core.files.uploadedfile import UploadedFile
import os
import csv
from django.conf import settings
import magic


def handle_uploads(request, files):
    saved = []
    upload_dir = date.today().strftime(settings.UPLOAD_PATH)
    upload_full_path = os.path.join(settings.MEDIA_ROOT, upload_dir)
    print "DEPRECATED!"
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


def document_validator(filepath, ex_col, ex_row):
    try:
        with open(os.path.join(settings.MEDIA_ROOT, filepath), 'r') as f:
            file = UploadedFile(f)
            dialect = csv.Sniffer().sniff(file.readline(), delimiters=[';', ',', '\t'])
            mimetype = magic.from_buffer(file.readline(), mime=True)
            file.seek(0)

            reader = csv.reader(file, dialect)

            temp_list = []
            for line in iter(reader):
                if reader.line_num == 1:
                    print line
                    # save first row
                    temp_list.append(line)
            # save last row
            temp_list.append(line)

        # check char in first row and first col
        if not ex_row and not temp_list[0][-1].isdigit():
            raise ValueError
        if not ex_col and not temp_list[-1][0].isdigit():
            raise ValueError

        ncol = (len(temp_list[0]) - 1) if ex_row else len(temp_list[0])
        nrow = (reader.line_num - 1) if ex_col else reader.line_num
        is_cubic = True if (ncol == nrow) else False
        return_value = {'is_valid': True, 'nrow': nrow, 'ncol': ncol, 'separator': dialect.delimiter,
                        'mimetype': mimetype, 'is_cubic': is_cubic}
    except csv.Error:
        return_value = {'is_valid': False}
        file = None
    except Exception:
        return_value = {'is_valid': False}
        file = None
    except ValueError:
        return_value = {'is_valid': False}
        file = None

    return return_value, file


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
    tomanyfile = False

    idx = 0
    for f in files:
        try:
            if idx == 3:
                tomanyfile = True
                break

            pathabs = os.path.join(settings.MEDIA_ROOT, f)

            with open(pathabs, 'rb') as csvfile:
                reader = csv.reader(csvfile, delimiter='\t')
                rowdata = []
                tomanyrow = False
                tomanycol = False
                for row in reader:
                    if reader.line_num == 10:
                        tomanyrow = True
                        break
                    if len(row) > 7:
                        tomanycol = True
                        rowdata.append(row[:9])
                    else:
                        rowdata.append(row)
                print rowdata
            result.append({
                'tomanyrow': tomanyrow,
                'tomanycol': tomanycol,
                'rowdata': rowdata
            })
        except Exception, e:
            return False

    return result, tomanyfile