"""Parchea ficheros (mismo tamaño) dentro de una pista MODE1/2352 y recalcula EDC/ECC."""
import struct

# --- EDC/ECC (algoritmo estándar CD-ROM, como en ECM de Neill Corlett) ---
ecc_f=[0]*256; ecc_b=[0]*256; edc_lut=[0]*256
for i in range(256):
    j=(i<<1)^(0x11D if i&0x80 else 0)
    ecc_f[i]=j&0xff; ecc_b[i^j&0xff]=i
    edc=i
    for _ in range(8): edc=(edc>>1)^(0xD8018001 if edc&1 else 0)
    edc_lut[i]=edc
def edc_calc(data):
    edc=0
    for x in data: edc=(edc>>8)^edc_lut[(edc^x)&0xff]
    return edc
def ecc_compute(sector, major_count, minor_count, major_mult, minor_inc, dest_off):
    size=major_count*minor_count
    for major in range(major_count):
        index=(major>>1)*major_mult+(major&1)
        a=0;b=0
        for minor in range(minor_count):
            t=sector[0xC+index]
            index+=minor_inc
            if index>=size: index-=size
            a^=t; b^=t; a=ecc_f[a]
        a=ecc_b[ecc_f[a]^b]
        sector[dest_off+major]=a
        sector[dest_off+major+major_count]=a^b
def fix_mode1(sector):
    sector=bytearray(sector)
    e=edc_calc(sector[0:0x810])
    sector[0x810:0x814]=struct.pack('<I',e)
    sector[0x814:0x81C]=b'\0'*8
    ecc_compute(sector,86,24,2,86,0x81C)   # P
    ecc_compute(sector,52,43,86,88,0x8C8)  # Q
    return bytes(sector)

def patch_track(src_bin, dst_bin, iso_index, replacements):
    """iso_index: {nombre: (lba, tamaño)}; replacements: {nombre: bytes}"""
    data=bytearray(open(src_bin,'rb').read())
    for name,new in replacements.items():
        lba,size=iso_index[name]
        assert len(new)==size, (name,len(new),size)
        for k in range(0,size,2048):
            s=(lba+k//2048)*2352
            sec=bytearray(data[s:s+2352])
            chunk=new[k:k+2048]
            sec[16:16+len(chunk)]=chunk
            data[s:s+2352]=fix_mode1(sec)
    open(dst_bin,'wb').write(data)

def iso_index_from(iso_path):
    import pycdlib
    i=pycdlib.PyCdlib(); i.open(iso_path); idx={}
    for root,dirs,files in i.walk(iso_path='/'):
        for f in files:
            r=i.get_record(iso_path='/'+f)
            idx[f.split(';')[0]]=(r.extent_location(), r.data_length)
    i.close(); return idx
