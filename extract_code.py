"""Extract bundled server source. Run: python extract_code.py
Extracts project-liminal-gate-source.tar.gz into the folder of this script."""
import tarfile, os, sys, stat, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ARCHIVE = os.path.join(HERE, 'project-liminal-gate-source.tar.gz')
DEST = os.path.join(HERE, 'project-liminal-gate')

def force_rm(p):
    try:
        os.chmod(p, stat.S_IWRITE)
    except Exception:
        pass
    if os.path.isdir(p):
        shutil.rmtree(p, ignore_errors=True)
    else:
        try: os.remove(p)
        except Exception: pass

def main():
    if not os.path.exists(ARCHIVE):
        print('ERROR: project-liminal-gate-source.tar.gz not found next to this script.')
        return 1
    # if a previous partial extraction exists, remove it
    if os.path.isdir(DEST):
        print('Removing previous partial extraction...')
        force_rm(DEST)
    print('Extracting server code...')
    with tarfile.open(ARCHIVE) as t:
        t.extractall(HERE)
    ok = os.path.isdir(os.path.join(DEST, 'liminal_gate'))
    print('Extraction OK' if ok else 'Extraction failed (liminal_gate missing)')
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
