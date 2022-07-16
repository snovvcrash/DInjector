import re
import hmac
from hashlib import md5
from random import randbytes
from pathlib import Path

for dname in ('DInvoke', 'API', 'Modules', 'Utils'):
    for cs in Path(dname).rglob('*.cs'):
        with open(cs, 'r') as f:
            code = f.read().splitlines()

        rewrite = False
        for i, line in enumerate(code):
            if '{ API_HASHING' in line:
                func_name = line.split(':')[1].split()[0]

                kbytes = randbytes(4)
                func_hash = hmac.new(kbytes, func_name.lower().encode('utf-8'), digestmod=md5).hexdigest()
                key = hex(int.from_bytes(kbytes, byteorder='little'))

                next_line = code[i + 1]

                match = re.search(r'([a-fA-F\d]{32})', next_line).group(0)
                code[i + 1] = code[i + 1].replace(match, func_hash)

                match = re.search(r'0x[a-f\d]+', next_line).group(0)
                code[i + 1] = code[i + 1].replace(match, key)

                print(f'    [+] {func_name} -> ({func_hash}, {key})')
                rewrite = True

        if rewrite:
            with open(cs, 'w') as f:
                f.write('\n'.join(code))

            print(f'[*] Re-hashed function names in {cs}')