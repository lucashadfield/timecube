# flash any files that have changed to microcontroller
# md5sums and script config are stored in flash_conf.yaml
# uses rshell to flash files
# --force to reflash all files
# --clean to remove all files on microcontroller and exit
# --repl to go into interactive repl after flashing

import hashlib
import os
import sys
from pathlib import Path

import yaml

CONF_FILE = '_flash_conf.yaml'
DIR = Path(os.path.realpath(__file__)).parent


def read_config() -> dict:
    flash_conf_file = Path(CONF_FILE)
    with open((DIR / flash_conf_file).resolve(), 'r') as f:
        return yaml.safe_load(f)


def write_config(flash_conf: dict) -> None:
    flash_conf_file = Path(CONF_FILE)
    with open((DIR / flash_conf_file).resolve(), 'w') as f:
        yaml.safe_dump(flash_conf, f)


def get_args() -> dict:
    return {
        'clean': '--clean' in sys.argv,  # rm all files from microcontroller
        'force': '--force' in sys.argv,  # flash all files, not just changed ones
        'repl': '--repl' in sys.argv,  # jump into repl instead of rebooting
    }


def main() -> None:
    flash_conf = read_config()
    args = get_args()

    # rm all files from microcontroller
    if args['clean']:
        os.system(f'rshell --quiet rm {flash_conf["target_dir"]}/*')
        return

    # flash changed files
    local_path = (DIR / Path(flash_conf['source_dir'])).resolve()
    local_files = os.listdir(local_path)
    updated = False
    for filename in local_files:
        md5 = hashlib.md5(open(local_path / filename, 'rb').read()).hexdigest()
        if filename not in flash_conf['md5sum'] or flash_conf['md5sum'][filename] != md5 or args['force']:
            exit_status = os.system(f'rshell --quiet cp {local_path / filename} {flash_conf["target_dir"]}/.')
            if exit_status != 0:
                sys.exit()
            updated = True

        flash_conf['md5sum'][filename] = md5

    if updated:
        write_config(flash_conf)

        if not args['repl']:
            # `sudo apt-get install moreutils` to get `ts`
            os.system('rshell --quiet repl \~ import machine~machine.soft_reset\(\)~ | ts "%H:%M:%S"')
            # os.system('rshell --quiet repl \~ import machine~machine.soft_reset\(\)~ | ts -i "%s"')

    if args['repl']:
        # `sudo apt-get install moreutils` to get `ts`
        os.system('rshell --quiet repl | ts "%H:%M:%.S"')
        # os.system('rshell --quiet repl | ts -i "%.s"')


if __name__ == '__main__':
    main()
