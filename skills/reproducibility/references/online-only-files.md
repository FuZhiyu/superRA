# Online-Only Files

Load when a file a step reads or writes is online-only on this machine (Dropbox, Google Drive, Box, OneDrive, iCloud), or before downloading one. macOS only.

## Recognize One

- **File Provider** (folders under `~/Library/CloudStorage/`, including Dropbox on File Provider): `ls -lO <file>` shows `dataless`; in Python, `os.lstat(p).st_flags & 0x40000000`. Size and mtime are real; reading the content downloads it.
- **Legacy Dropbox** (`~/Dropbox` as a real folder): a zero-byte file whose `xattr <file>` lists `com.dropbox.placeholder`. A read returns empty bytes: never hash or use one.
- **Directories:** a `stat` inside an online-only directory can download its listing. Check the directory's own flag before walking it.

## Ask First

**Downloading is the researcher's call.** Report the files and their total size, then wait for the go-ahead.

- **Sizes:** `stat -f %z <file>`; `du` counts an online-only file as 0.
- **Free space:** `df -h <dir>`. Under disk pressure, macOS may make other files online-only again.

## Download

- **File Provider, by hand:** Finder → right-click → Download Now. Make Available Offline (Dropbox) or Keep Downloaded (iCloud) also prevents later eviction.
- **File Provider, from a script:** a coordinated read requests the whole file.

  ```bash
  uv run --no-project --with pyobjc-framework-Cocoa python - <file>... <<'EOF'
  import os, sys
  import Foundation
  for p in sys.argv[1:]:
      c = Foundation.NSFileCoordinator.alloc().initWithFilePresenter_(None)
      url = Foundation.NSURL.fileURLWithPath_(os.path.abspath(p))
      err = c.coordinateReadingItemAtURL_options_error_byAccessor_(url, 0, None, lambda u: None)
      print(p, err or ('local' if not os.lstat(p).st_flags & 0x40000000 else 'still online-only'))
  EOF
  ```

  A plain full read (`cat <file> > /dev/null`) also triggers a download but may leave the file partial. `fileproviderctl materialize` and `brctl download` no longer exist.
- **Legacy Dropbox:** no command-line route. Use Dropbox's Make available offline, or move that machine to Dropbox on File Provider.

## Confirm

`ls -lO` no longer shows `dataless`; for legacy Dropbox, the size is no longer 0 and the placeholder xattr is gone. Then rerun `superra repro status`.

- **A read failing with `ETIMEDOUT` or `EDEADLK`:** the file did not download, usually because the provider's sync service is unhealthy. Report it rather than retrying in a loop.
