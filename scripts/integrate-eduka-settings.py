#!/usr/bin/env python3
"""Generate a separate review copy with a native LAFA settings group.

--auto accepts one unambiguous top-level QVBoxLayout assignment in a host
constructor. Conditional layouts and early returns require manual integration.
No host source is executed or overwritten by this generator.
"""
import argparse
import ast
from pathlib import Path
import re
import shutil

BINDINGS={'PyQt5','PyQt6','PySide6'}


def scoped_nodes(node):
    yield node
    for child in ast.iter_child_nodes(node):
        if isinstance(child,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef,ast.Lambda)):continue
        yield from scoped_nodes(child)


def assignment_name(node):
    if isinstance(node,ast.Name):return node.id
    if isinstance(node,ast.Attribute) and isinstance(node.value,ast.Name) and node.value.id=='self':return 'self.'+node.attr
    return None


def direct_layouts(init):
    result=[]
    for node in init.body:
        if isinstance(node,ast.Assign) and len(node.targets)==1:value=node.value;target=node.targets[0]
        elif isinstance(node,ast.AnnAssign):value=node.value;target=node.target
        else:continue
        if not isinstance(value,ast.Call):continue
        name=value.func.id if isinstance(value.func,ast.Name) else value.func.attr if isinstance(value.func,ast.Attribute) else ''
        if name=='QVBoxLayout' and assignment_name(target):result.append(assignment_name(target))
    return result


def detect_host(source):
    tree=ast.parse(source);bindings=set();candidates=[]
    for node in tree.body:
        if isinstance(node,ast.ImportFrom) and node.module and node.module.split('.')[0] in BINDINGS:bindings.add(node.module.split('.')[0])
        if isinstance(node,ast.Import):
            bindings.update(alias.name.split('.')[0] for alias in node.names if alias.name.split('.')[0] in BINDINGS)
        if isinstance(node,ast.ClassDef):
            init=next((item for item in node.body if isinstance(item,ast.FunctionDef) and item.name=='__init__'),None)
            if init:
                for layout in direct_layouts(init):candidates.append((node.name,layout))
    if len(bindings)!=1:raise ValueError('Cannot determine one Qt binding. Use explicit host arguments.')
    if len(candidates)!=1:raise ValueError('Automatic integration needs one unambiguous QVBoxLayout. Use explicit class/layout arguments.')
    return (*candidates[0],next(iter(bindings)))


def add_hook(source,class_name,layout,binding):
    if binding not in BINDINGS:raise ValueError('Unsupported Qt binding.')
    if not isinstance(layout,str) or not re.fullmatch(r'(?:self\.)?[A-Za-z_][A-Za-z0-9_]*',layout):raise ValueError('Layout must be a local name or self.attribute.')
    tree=ast.parse(source);target=next((node for node in tree.body if isinstance(node,ast.ClassDef) and node.name==class_name),None)
    if target is None:raise ValueError('The requested settings class was not found.')
    init=next((node for node in target.body if isinstance(node,ast.FunctionDef) and node.name=='__init__'),None)
    if init is None or not init.body:raise ValueError('The settings class needs an __init__ method.')
    if 'add_lafa_group(' in source:raise ValueError('A LAFA settings hook is already present.')
    if layout not in direct_layouts(init):raise ValueError('Use a top-level QVBoxLayout assignment in the constructor, or integrate the factory manually.')
    if any(isinstance(node,ast.Return) for node in scoped_nodes(init)):raise ValueError('Early returns need a manually placed LAFA hook.')
    lines=source.splitlines(keepends=True);indent=re.match(r'[ \t]*',lines[init.body[0].lineno-1]).group()
    hook=f"\n{indent}# LAFA has its own settings group and separate Desktop application.\n{indent}from eduka_lafa_settings import add_lafa_group\n{indent}self.lafa_group = add_lafa_group({layout}, binding={binding!r})\n"
    lines.insert(init.end_lineno,hook);result=''.join(lines);compile(result,'eduka-settings-with-lafa','exec');return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path);parser.add_argument('--auto',action='store_true');parser.add_argument('--class-name');parser.add_argument('--layout');parser.add_argument('--binding',choices=sorted(BINDINGS));parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.source.resolve()==args.output.resolve():parser.error('Use a separate output path; the original source must remain unchanged.')
    if args.output.exists():parser.error('Output already exists. Choose a new review path.')
    if args.auto and any([args.class_name,args.layout,args.binding]):parser.error('Use --auto or explicit class/layout/binding arguments.')
    if not args.auto and not all([args.class_name,args.layout,args.binding]):parser.error('Specify --auto or all of --class-name, --layout and --binding.')
    try:
        source=args.source.read_text(encoding='utf-8');choice=detect_host(source) if args.auto else (args.class_name,args.layout,args.binding)
        result=add_hook(source,*choice);helper=args.output.parent/'eduka_lafa_settings.py'
        if helper.exists():parser.error('The output directory already contains the LAFA helper. Choose a fresh review directory.')
        args.output.parent.mkdir(parents=True,exist_ok=True);helper_source=Path(__file__).resolve().parents[1]/'integration/eduka_lafa_settings.py'
        # Exclusive writes protect an existing review copy from accidental reuse.
        with args.output.open('x',encoding='utf-8') as stream:stream.write(result)
        with helper.open('x',encoding='utf-8') as stream:stream.write(helper_source.read_text(encoding='utf-8'))
    except (OSError,ValueError,SyntaxError) as error:parser.error(str(error))
    print('Created a review copy. Test it before incorporating it into Eduka-Settings.')

if __name__=='__main__':main()
