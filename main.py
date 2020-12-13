import os
import struct


# The main file is composed of a list of records.
# Each record has a list of subrecords.
# Each subrecord has a unique structure.

# TODO:
#  * For the fixed-length fields, verify their length and print a warning if necessary.
#  * Make functions for read_long, read_float, etc.
#  * Some strings are null-terminated (e.g. HEDR->Description); handle that.

def read_string(f, size):
    s = f.read(size).decode()
    return s.replace('\x00','')
    
def read_int(f, size=4):
    return int.from_bytes(f.read(size), 'little')

# TODO This require rounding to be exact, but I don't know exactly how, depending on the size
# https://bugs.python.org/issue4114
def read_float(f, size=4):
    return struct.unpack('<f', f.read(size))[0]

# TODO Are subrecords with the same name but different parents still the same format?
def read_subrecord(f):
    name = f.read(4).decode()
    size = read_int(f)
    subr = dict(Name=name, Size=size)
    if name == 'HEDR': # 300 bytes
        subr['Version'] = read_float(f)
        subr['Unknown'] = read_int(f)
        subr['CompanyName'] = read_string(f, 32)
        subr['Description'] = read_string(f, 256)
        subr['NumRecords'] = read_int(f)
    elif name == 'MAST': # Variable length
        subr['Content'] = read_string(f, size)
    elif name == 'DATA': # 8 bytes
        subr['Content'] = read_int(f, 8)
    elif name == 'NAME':
        subr['Content'] = read_string(f, size)
    elif name == 'FLTV':
        subr['Content'] = read_float(f, size=size)
    else:
        subr['Content'] = f.read(size)
    return subr


def read_record(f):
    rec = {}
    rec['Name'] = read_string(f, 4)
    rec['Size'] = int.from_bytes(f.read(4), 'little')
    rec['Header1'] = f.read(4)
    rec['Flags'] = f.read(4)
    # sub
    sub_records = []
    bytes_read = 0
    while bytes_read < rec['Size']:
        subr = read_subrecord(f)
        sub_records.append(subr)
        bytes_read += 8 + subr['Size']
    rec['SubRecords'] = sub_records
    return rec


if __name__ == '__main__':
    known_records = ['TES3', 'GLOB']
    with open('quiksave.ess', 'rb') as f:
        all_records = []
        record = read_record(f)
        while record['Name'] in known_records:
            all_records.append(record)
            record = read_record(f)

    # Inspect TES3
    main_rec = all_records[0]
    sub_recs = main_rec['SubRecords']
    assert sum(x['Size'] for x in sub_recs) + 8 * len(sub_recs) == main_rec['Size']
    #for subr in sub_recs:
    #    if subr['Name'] != 'SCRS':
    #        print(subr)
    print(all_records[1])
