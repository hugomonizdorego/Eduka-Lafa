"""Resource-limited Poppler conversion; private input/output paths supplied by LAFA."""
import os
import resource
import shutil
import sys

def main():
    if len(sys.argv)!=3:return 2
    executable=shutil.which('pdftotext')
    if not executable:return 2
    resource.setrlimit(resource.RLIMIT_CPU,(10,10))
    resource.setrlimit(resource.RLIMIT_FSIZE,(1_000_000,1_000_000))
    resource.setrlimit(resource.RLIMIT_AS,(768_000_000,768_000_000))
    os.execv(executable,[executable,'-f','1','-l','30','-enc','UTF-8',sys.argv[1],sys.argv[2]])
    return 2

if __name__=='__main__':raise SystemExit(main())
