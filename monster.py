import xml.etree.ElementTree as ET
from helpers import *
from pprint import pprint
import textwrap
import re


class XMLMonster:
    def __init__(self, fp: str):
        self.tree = ET.parse(fp)
        self.root = self.tree.getroot()
        self.dispatcher = DispatchTable({
            'flags': self.parse_basic_ints,
            'attacks': self.parse_full_node,
            'defenses': self.parse_full_node,
            'elements': self.parse_basic_ints,
            'immunities': self.parse_basic_ints,
            'summons': self.parse_full_node,
            'voices': self.parse_full_node,
            'loot': self.parse_full_node,
            'script': self.parse_full_node
        })

        self.parsed = self.parse()

    def parse(self) -> dict:
        parsed = {'generics': dict_int_values(self.root.attrib)}

        for node in self.root.findall('*'):
            if children := list(node):
                parsed[node.tag] = self.dispatcher.dispatch(
                                       node.tag,
                                       (node.tag, node, children)
                                      )
                continue

            parsed['generics'][node.tag] = dict_int_values(node.attrib)

        return parsed

    def parse_basic_ints(self, name: str,
                         node: ET.Element, children: list) -> dict:
        """
        Parses the child node's attributes, converting any numerics to ints
        """
        return {key: int(val)
                for element in node
                for key, val in element.attrib.items()}

    def parse_full_node(self, name: str,
                        node: ET.Element, children: list) -> dict:
        """
        Parses the root node's attributes + all top-level children, along with
        any child nodes belonging to top-level children
        """
        ret = {**dict_int_values(node.attrib),
               'children': []}

        for element in node:
            parsed_node = dict_int_values(element.attrib)
            if children := list(element):
                parsed_node['children'] = []
                for child in children:
                    parsed_node['children'].append(
                        dict_int_values(child.attrib)
                    )
            ret['children'].append(parsed_node)

        return ret

    def get_flags(self):
        return self.parsed['flags']


class LuaMonster:
    # TODO: allow nested attrs to have different conversions
    # if converter has nested attrs, but 1 converter, use the converter for all
    # ex: applying int() to <health now="8200" max="8200" />
    # TODO: process <script> tag
    # TODO: handle condition immunities in generate_immunities_lua

    generator_order = [
        'generics',
        'flags',
        'attacks',
        'defenses',
        'elements',
        'immunities',
        'summons',
        'voices',
        'loot',
        'script'
    ]

    def __init__(self, xml_monster, lua_var):
        self.xml_monster = xml_monster
        self.lua_var = lua_var
        self.processor = DispatchTable({
            'generics': self.process_generics,
            'flags': self.process_flags,
            'attacks': self.process_attacks,
            'defenses': self.process_defenses,
            'immunities': self.process_immunities,
            'voices': self.process_voices
        })
        self.generator = DispatchTable({
            'generics': self.generate_generics_lua,
            'flags': self.generate_flag_lua,
            'attacks': self.generate_attacks_lua,
            'defenses': self.generate_defenses_lua,
            'elements': self.generate_elements_lua,
            'immunities': self.generate_immunities_lua,
            'summons': self.generate_summons_lua,
            'voices': self.generate_voices_lua,
            'script': self.generate_creaturescript_lua
        })

    def generate_script(self):
        processed = {}
        script = ''

        # Process XML -> Lua values used for script generation
        for node_type, values in self.xml_monster.parsed.items():
            try:
                processed[node_type] = self.processor.dispatch(node_type,
                                                               (values,))
            except NotImplementedError:
                processed[node_type] = values  # processing is not needed

        # Generate pieces of script in order
        for node_type in LuaMonster.generator_order:
            processed_values = processed.get(node_type)
            if not processed_values:
                continue
            try:
                script += self.generator.dispatch(node_type,
                                                  (processed_values,))
            except NotImplementedError:
                pass

        return script

    def process_generics(self, generics: dict) -> dict:
        ret = {k: v
               for k, v in generics.items()
               if k not in ('health', 'look', 'nameDescription')}
        
        if health := generics.get('health'):
            ret['health'] = health['now']
            ret['maxHealth'] = health['max']

        if outfit := generics.get('look'):
            if typeex := outfit.get('typeex'):
                ret['outfit'] = {'lookTypeEx': typeex}
            elif looktype := outfit.get('type'):
                ret['outfit'] = {'lookType': looktype}
            
            if corpse := outfit.get('corpse'):
                ret['corpse'] = corpse

        if desc := generics.get('nameDescription'):
            ret['description'] = desc

        return ret

    def process_flags(self, flags: list) -> dict:
        conversion = {
            'attackable': bool,
            'canpushcreatures': bool,
            'canpushitems': bool,
            'hostile': bool,
            'pushable': bool,
            'convinceable': bool,
            'illusionable': bool,
            'runonhealth': bool,
            'summonable': bool,
            'canwalkonenergy': bool,
            'canwalkonfire': bool,
            'canwalkonpoison': bool,
            'hidehealth': bool,
            'isboss': bool
        }

        return {flag: conversion[flag](val)
                if conversion.get(flag) else val
                for flag, val in flags.items()}

    def process_attacks(self, attacks: list) -> list:
        converted = []

        for attack in attacks['children']:
            node = {k: v for k, v in attack.items() if k != 'children'}

            if children := attack.get('children'):
                for child in children:
                    # Convert XML child keys to Lua equivalent
                    key = child['key'] if child['key'] != 'areaEffect' else 'effect'
                    node[key] = child['value']

            converted.append(node)

        return converted

    def process_defenses(self, defenses: list) -> list:
        converted = []

        for defense in defenses['children']:
            node = {k: v for k, v in defense.items() if k != 'children'}

            if children := defense.get('children'):
                for child in children:
                    # Convert XML child keys to Lua equivalent
                    key = child['key'] if child['key'] != 'areaEffect' else 'effect'
                    node[key] = child['value']

            converted.append(node)

        return converted

    def process_immunities(self, immunities: dict) -> dict:
        return [{'element': key,
                 'combat': True}
                for key, val in immunities.items()]

    def process_voices(self, voices: dict) -> dict:
        children = []

        for voice in voices['children']:
            d = {
                'text': voice.get('sentence'),
                'yell': bool(voice.get('yell'))
            }
            children.append(d)

        voices['children'] = children

        return voices

    def generate_generics_lua(self, processed: dict) -> str:
        order = [
            'description',
            'experience',
            'outfit',
            'health',
            'maxHealth',
            'race',
            'corpse',
            'speed'
        ]

        script = f'''
                local mType = Game.createMonster("{processed["name"]}")
                local {self.lua_var} = {{}}
                '''
        script = textwrap.dedent(script)[1:]  # 1: removes initial newline

        for key in order:
            if val := processed.get(key):
                if isinstance(val, dict):
                    script += f'{self.lua_var}.{key} = {lua_table(val)}\n'
                else:
                    script += f'{self.lua_var}.{key} = {repr(val)}\n'

        return script

    def generate_flag_lua(self, processed: dict) -> str:
        script = f'{self.lua_var}.flags = {lua_table(processed)}'
        return script

    def generate_attacks_lua(self, processed: list) -> str:
        script = f'\n{self.lua_var}.attacks = {{\n'

        for i, spell in enumerate(processed):
            comma = ',' if i < len(processed)-1 else ''
            script += f'{lua_table(spell, indent=1)}{comma}\n'
        script += '}'

        return script

    def generate_defenses_lua(self, processed: list) -> str:
        script = f'\n{self.lua_var}.defenses = {{\n'

        for i, spell in enumerate(processed):
            comma = ',' if i < len(processed) - 1 else ''
            script += f'{lua_table(spell, indent=1)}{comma}\n'
        script += '}'

        return script

    def generate_elements_lua(self, processed: dict) -> str:
        script = f'\n{self.lua_var}.elements = {{\n'
        i = 0

        for element, value in processed.items():
            comma = ',' if i < len(processed.keys()) - 1 else ''
            script += f'\t{{type = {repr(element)}, percent = {value}}}' \
                      f'{comma}\n'
            i += 1

        script += '}'
        return script

    def generate_immunities_lua(self, processed: list) -> str:
        script = f'\n{self.lua_var}.immunities = {lua_table(processed)}'
        return script

    def generate_summons_lua(self, processed: dict) -> str:
        script = f'\n{self.lua_var}.summons = {{\n'

        for summon in processed['children']:
            script += lua_table(summon, 1)

        script += '\n}'

        if max_summons := processed.get('maxSummons'):
            script += f'\n{self.lua_var}.maxSummons = {max_summons}'

        return script

    def generate_voices_lua(self, processed: dict) -> str:
        script = f'\n{self.lua_var}.voices = {{\n'

        if interval := processed.get('interval'):
            script += f'\tinterval = {interval},\n'

        if chance := processed.get('chance'):
            script += f'\tchance = {chance},\n'

        for i, voice in enumerate(processed['children']):
            comma = ',' if i < len(processed['children']) - 1 else ''
            script += f'{lua_table(voice, indent=1)}{comma}\n'

        script += '}'
        return script

    def generate_creaturescript_lua(self, processed: list) -> str:
        script = '\n' + '\n'.join(f'{self.lua_var}:registerEvent({repr(event["name"])})'
                           for event in processed['children'])
        return script