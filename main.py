#!/usr/bin/python3

from subprocess import run
import pathlib
import os


def download_files():
    for playlist in PLAYLISTS:
        run("youtube-dl -x {} -i --download-archive video_archive.txt".format(playlist), shell=True, check=False)


def convert_files():
    run("find . -maxdepth 1 -name '*.opus' | parallel -j 4 -I% --max-args 1 {}".format("ffmpeg -y -i '%' -threads 4 -f ogg '%.ogg' 2>&1"), shell=True, check=True)


def move_raws():
    run("find . -maxdepth 1 -name '*.opus' -exec {} \;".format("mv '{}' raws/"), shell=True, check=True)


def replace_sync_conflict():
    """Remove the .sync-conflict file name"""
    run("{} -o -a 'r:\\.sync-conflict.*\\.:.' -d *".format(RENAME_SCRIPT), shell=True, check=True)


def replace_youtube_id():
    run("{} -o -a 'r:-[a-zA-Z0-9_-]{{11}}\\.({}):.\\1' -d *".format(RENAME_SCRIPT, '|'.join(VALID_FILE_TYPES)), shell=True, check=True)


def replace_dot_opus_dot():
    """Replaces <file_name>.opus.ogg with <file_name>.ogg
    Also does mp3"""
    run("{} -o -a 'r:\\.opus\\.({}):.\\1' -d *".format(RENAME_SCRIPT, '|'.join(VALID_FILE_TYPES)), shell=True, check=True)


def rename_files():
    replace_sync_conflict()
    replace_dot_opus_dot()
    replace_youtube_id()


def remove_prefer_ogg():
    """If two files have the same name but one with an extension other than .ogg and the other with .ogg, remove the not .ogg."""
    p = pathlib.Path('.')
    files = []
    for f in p.iterdir():
        if f.is_file():
            files.append(f)

    for f in files:
        if f.suffix == '.ogg':
            for suffix in VALID_FILE_TYPES:
                if suffix == 'ogg': continue
                new_f = f.with_suffix('.'+suffix)
                if new_f.exists():
                    print("Removing {}".format(new_f.name))
                    os.remove(new_f)


def remove_three_short():
    """If two files have the same name but one is missing the last N letters, delete the latter."""
    N = 3

    p = pathlib.Path('.')
    files = []
    for f in p.iterdir():
        if f.is_file():
            files.append(f)

    for f in files:
        if len(f.name) <= N: continue
        name = f.with_suffix('').name
        new_fn = f.with_name(name[0:-N])

        new_f = new_fn.with_name(new_fn.name+f.suffix)
        if new_f.exists():
            print("Removing {}".format(new_f.name))
            os.remove(new_f)


def remove_files():
    remove_prefer_ogg()
    #remove_three_short()


def main():
    global RENAME_SCRIPT, PLAYLISTS, VALID_FILE_TYPES
    RENAME_SCRIPT = "/data/source_code/projects/renamer/src/main.py"
    PLAYLISTS = ('https://youtu.be/JWp4JXc_0uY?list=PLC0KPL2roO6VbvAsy-xnXSZnHRn3ZTMi4',)
    VALID_FILE_TYPES = ('mp3', 'ogg', 'm4a')

    #download_files()
    convert_files()
    move_raws()
    rename_files()
    remove_files()

    # Rename files
    replace_sync_conflict()
    replace_dot_opus_dot()


if __name__ == '__main__':
    main()
