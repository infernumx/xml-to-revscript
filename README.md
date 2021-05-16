
# xml-to-revscript

  

[The Forgotten Server](https://github.com/otland/forgottenserver) monster XML converter to revscriptsys format (Lua)

  

## Requirements

* Python 3.8+

  

## Usage

`python converter.py directory [-f file] [-n varname]`

  

- -f, --file: single file to convert [optional]

-  -n, --name: var name for the Lua file [optional]

  

## Examples

#### Convert demon.xml (with demon varname):

- `python converter.py "../forgottenserver/data/monster/monsters" --file demon.xml --name demon`

#### Convert amazon.xml (with default varname, monster)

- `python converter.py "../forgottenserver/data/monster/monsters" --file amazon.xml`

#### Convert entire directory:

- `python converter.py "../forgottenserver/data/monster/monsters"`

  

## Generator checklist

- [x] Generics (name, description, experience, health, etc)

- [x] Flags

- [x] Attacks

- [x] Defenses

- [x] Elements

- [x] Immunities (only combat immunities for the moment)

- [ ] Summons

- [ ] Voices

- [ ] Loot

  

## Confirmed fully working generators

- [x] Flags