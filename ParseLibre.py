
def ReadFile(file_name):

    with open(file_name) as f:
        lines = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    lines = [x.strip() for x in lines] 
    
    memory = bytearray()
    reading_mem = False
    for line in lines:
        if "# Memory content:" in line:
            reading_mem = True
            continue
            
        if not reading_mem:
            continue
        #print (line)
        #print (line[7:30])
        bytes = bytearray.fromhex(line[7:30])
        #print(bytes.hex())
        memory.extend(bytes)
        if line.startswith('[F3]'):
            return memory
        


def PrintBytesAsHex(bytearray, text_file):
    i = 0
    for byte in bytearray:
        # print leading line number
        if not i % 8:
            print( format(i, '0002x'), ': ',end='', sep='', file=text_file)
        print(format(byte, '02x'), end='', file=text_file)
        i+=1
        # move line or space as needed
        if i % 8:
            print(' ',end='', file=text_file)
        else:
            print('', file=text_file)
    if i % 8:
        print('', file=text_file)


def xor_func(var, key):
    return bytes(a ^ b for a, b in zip(var, key))

        
file1_mem = ReadFile(r"C:\Users\Nirit\Downloads\5_NFCScans_with_LibreReaderShots_same_time\DA-CF-06-03-00-A0-07-E0_2018-11-02 08-58-37_taginfo_scan.txt")
print('file1_mem')
print (PrintBytesAsHex(file1_mem, None ))

file2_mem = ReadFile(r"C:\Users\Nirit\Downloads\5_NFCScans_with_LibreReaderShots_same_time\DA-CF-06-03-00-A0-07-E0_2018-11-02 09-00-26_taginfo_scan.txt")
print('file2_mem')
print (PrintBytesAsHex(file2_mem, None ))

file3_mem = ReadFile(r"C:\Users\Nirit\Downloads\5_NFCScans_with_LibreReaderShots_same_time\DA-CF-06-03-00-A0-07-E0_2018-11-02 09-03-58_taginfo_scan.txt")
print('file3_mem')
print (PrintBytesAsHex(file1_mem, None ))

file4_mem = ReadFile(r"C:\Users\Nirit\Downloads\5_NFCScans_with_LibreReaderShots_same_time\DA-CF-06-03-00-A0-07-E0_2018-11-02 09-07-00_taginfo_scan.txt")
print('file4_mem')
print (PrintBytesAsHex(file1_mem, None ))

xored = xor_func(file1_mem, file2_mem)
print('xor of file1, file2')
print (PrintBytesAsHex(xored, None ))

xored = xor_func(file3_mem, file4_mem)
print('xor of file1, file3')
print (PrintBytesAsHex(xored, None ))
    
