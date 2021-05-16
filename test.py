from monster import XMLMonster, LuaMonster
from pprint import pprint

demon = XMLMonster('../forgottenserver/data/monster/monsters/demon.xml')
demon_lua = LuaMonster(xml_monster=demon, lua_var='monster')
script = demon_lua.generate_script()
with open('demon.lua', 'w') as f:
    f.write(script)
