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


def convert_file(directory, name, lua_var):
    failed = []

    lua_file = f'dump/{name[:-4]}.lua'
    try:
        print(f'> Writing {lua_file}')
        xml_monster = XMLMonster(os.path.join(directory, name))
        lua_monster = LuaMonster(xml_monster=xml_monster,
                                 lua_var='monster')
    except Exception as e:
        message = f'Exception occurred while writing {lua_file}:\n' \
                f'{type(e).__name__}: {e}'
        failed.append((name, message))
    with open(lua_file, 'w') as f:
        f.write(lua_monster.generate_script())

    print('\n'.join(f'{message}'
                    for name, message in failed))


def main():
    parser = init_argparse()
    args = parser.parse_args()
    lua_var = args.name if args.name else 'monster'

    # Only convert single file, defined by -f or --file
    if args.file:
        convert_file(args.directory, args.file, lua_var)
        return

    # Convert entire directory
    for root, dirs, files in os.walk(args.directory):
        for name in files:
            convert_file(name, lua_var)


if __name__ == '__main__':
    main()
