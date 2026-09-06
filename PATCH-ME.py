import zipfile, os, sys

SLOT = 26
TEMPLATE = 'TerraBattle-UNPATCHED-template.ipa'
OUT = 'TerraBattle-PATCHED.ipa'
PLACEHOLDER = b'http://00.000.000.000:8696'   # 26 chars
EXPECTED = 9

def _pause():
    try: input('\nPress Enter to exit...')
    except EOFError: pass

def _guess_ip() -> str:
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return ''

def _guess_tailscale() -> str:
    try:
        import subprocess
        out = subprocess.check_output(['tailscale', 'ip', '-4'], stderr=subprocess.DEVNULL, text=True, timeout=3)
        ip = out.strip().split()[0] if out.strip() else ''
        return ip if ip.startswith('100.') else ''
    except Exception:
        return ''

def main():
    print('=' * 62)
    print(' TERRA BATTLE IPA AUTO-PATCHER')
    print('=' * 62)
    ip_guess = _guess_ip() or '192.168.1.100'
    ts_guess = _guess_tailscale()
    print(f'\nThis PC LAN IP looks like : {ip_guess}')
    if ts_guess:
        print(f'Tailscale IP                 : {ts_guess}  (100.x, works from anywhere)')
    else:
        print('Tailscale IP                 : (not installed; get it at https://tailscale.com — login with your email)')
    print('Enter the SERVER address the game should connect to.')
    print('  - Same Wi-Fi  : the LAN IP above (just press Enter)')
    print('  - Tailscale   : paste the 100.x IP or MagicDNS name (e.g. my-pc.tailXXXX.ts.net)')
    print('                  (install Tailscale on PC + iPhone, login with SAME email)')
    print('                  or any IPv4 with NO leading zeros')
    print(f'  Total length (http:// + address + : + port) must be exactly {SLOT}.')
    print()
    raw = input('Server address [http://%s:18696]: ' % ip_guess).strip()
    if not raw:
        raw = 'http://%s:18696' % ip_guess
    if not raw.startswith('http://'):
        raw = 'http://' + raw

    port = input('Server port [18696]: ').strip() or '18696'
    if not port.isdigit():
        print('Port must be numeric.'); _pause(); sys.exit(1)
    port = str(int(port))          # normalize, drop any leading zeros
    if int(port) > 65535:
        print(f'ERROR: port {port} is invalid (max 65535).')
        _pause(); sys.exit(1)
    host = raw[len('http://'):].split(':')[0].strip()

    # FORBID leading zeros in any octet (octal interpretation hazard)
    octs = host.split('.')
    if len(octs) == 4:
        bad = [o for o in octs if o.startswith('0') and o != '0']
        if bad:
            print(f'\nERROR: "{host}" has leading-zero octet(s): {bad}')
            print('Leading-zero octets can be read as OCTAL by iOS and point')
            print('to a WRONG address. Use e.g. "%d" not "0%s".' %
                  (int(bad[0], 10), bad[0]))
            _pause(); sys.exit(1)

    addr = f'http://{host}:{port}'
    new = addr.encode()
    print(f'\nGame will connect to: {addr}')

    if len(new) > SLOT:
        print(f'\nERROR: that address is {len(new)} characters but the slot is {SLOT}.')
        print('Options:')
        print('  - Use a shorter hostname (MagicDNS names are usually short)')
        print('  - Or use a shorter port (e.g. 8696) so the total is exactly %d' % SLOT)
        print('  - Never pad the IP with zeros.')
        _pause(); sys.exit(1)
    if len(new) < SLOT:
        need = SLOT - len(new)
        print(f'Note: address is {len(new)} chars, slot is {SLOT}. Auto-padding with {need} null byte(s) (iOS safe).')
        new = new + b'\x00' * need

    print(f'\nPatching {TEMPLATE} ...')
    zin = zipfile.ZipFile(TEMPLATE)
    zout = zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED)
    count = 0
    for info in zin.infolist():
        data = zin.read(info.filename)
        if info.filename.endswith('global-metadata.dat'):
            count = data.count(PLACEHOLDER)
            data = data.replace(PLACEHOLDER, new)
        zout.writestr(info, data)
    zout.close(); zin.close()

    z = zipfile.ZipFile(OUT)
    meta = [z.read(n) for n in z.namelist() if 'global-metadata' in n][0]
    z.close()
    left = meta.count(PLACEHOLDER)
    size_ok = len(meta) == 13094052
    print('\n--- RESULT ---')
    print(f' slots patched     : {count} (expected {EXPECTED})')
    print(f' placeholders left : {left} (expected 0)')
    print(f' metadata size ok  : {size_ok}')
    print(f' output            : {OUT} ({os.path.getsize(OUT)//1024//1024} MB)')
    if count == EXPECTED and left == 0 and size_ok:
        print(f'\nSUCCESS! Install {OUT} via Sideloadly.')
        print(f'Server check: {addr}/healthz')
    else:
        print('\nWARNING: unexpected result, do NOT install.')
    _pause()

if __name__ == '__main__':
    try: main()
    except Exception as e:
        print('UNEXPECTED ERROR:', e); _pause(); sys.exit(1)
