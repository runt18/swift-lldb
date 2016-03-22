import lldb

def disassemble(debugger, command, result, dict):
    if lldb.frame.function:
        instructions = lldb.frame.function.instructions
        start_addr = lldb.frame.function.addr.load_addr
        name = lldb.frame.function.name
    elif lldb.frame.symbol:
        instructions = lldb.frame.symbol.instructions
        start_addr = lldb.frame.symbol.addr.load_addr
        name = lldb.frame.symbol.name
    
    for inst in instructions:
        inst_addr = inst.addr.load_addr
        inst_offset = inst_addr - start_addr
        comment = inst.comment
        if comment:
            print "<{0!s} + {1:<4d}> 0x{2:x} {3:8!s}  {4!s} ; {5!s}".format(name, inst_offset, inst_addr, inst.mnemonic, inst.operands, comment)
        else:
            print "<{0!s} + {1:<4d}> 0x{2:x} {3:8!s}  {4!s}".format(name, inst_offset, inst_addr, inst.mnemonic, inst.operands)
            
# Install the command when the module gets imported
lldb.debugger.HandleCommand('command script add -f gdb_disassemble.disassemble gdb-disassemble')
print 'Installed "gdb-disassemble" command for disassembly'