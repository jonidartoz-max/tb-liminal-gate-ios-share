# runtime
Optional portable Python 3.11 for running the server without installing
anything. The launcher (`run_common.bat`) checks this folder FIRST, then
falls back to any system Python.

To fill it (one of):
- Download the "Windows embeddable package (64-bit)" for Python 3.11 from
  https://www.python.org/downloads/ and extract its contents here
  (python.exe must sit directly in this folder), or
- install Python normally and let the launcher find it on PATH.

Nothing else in this repo requires pip install — the server is stdlib-only.
