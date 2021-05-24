#!/usr/bin/env python
from monster import XMLMonster, LuaMonster
from pprint import pprint
import os
import argparse


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage='%(prog)s directory [-f file] [-n varname]',
        description='XML to revscriptsys Lua converter for TFS'
    )
    parser.add_argument('directory')
    parser.add_argument('-f', '--file', help='single file to convert')
    parser.add_argument('-n', '--name', help='Lua variable name')
    return parser


def convert_file(directory, name, failed, lua_var):
    lua_var = 'monster' if lua_var is None else lua_var
    lua_file = f'dump/{name[:-4]}.lua'
    try:
        print(f'> Writing {lua_file}')
        xml_monster = XMLMonster(os.path.join(directory, name))
        lua_monster = LuaMonster(xml_monster=xml_monster,
                                 lua_var=lua_var)
        with open(lua_file, 'w') as f:
            f.write(lua_monster.generate_script())
    except Exception as e:
        message = f'Exception occurred while writing {lua_file}:\n' \
                f'{type(e).__name__}: {e}'
        failed.append((name, message))


def main():
    parser = init_argparse()
    args = parser.parse_args()
    failed = []

    if not os.path.exists('dump/'):
        os.mkdir('dump/')

    # Only convert single file, defined by -f or --file
    if args.file:
        convert_file(args.directory, args.file,
                     lua_var=args.name,
                     failed=failed)

    # Convert entire directory
    else:
        for root, dirs, files in os.walk(args.directory):
            for name in files:
                convert_file(args.directory, name,
                             lua_var=args.name,
                             failed=failed)

    print('\n'.join(f'{message}'
          for name, message in failed))


if __name__ == '__main__':
    main()
