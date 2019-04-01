precode_=open("example.txt").read().split('\n')
precode=[]
for line in precode_:
    if "#" in line:
        line=line[:line.index('#')]
    line=line.replace('\t','    ').replace("\r",'')
    if line.replace("\n",'').replace(" ",'')=='':
        continue

    
    while '  'in line:
        line=line.replace('  ',' ')
    line=line.lstrip(' ').rstrip(' ')
    precode.append(line)


#CAN PROBOBLY OPTIMISE SOMETHING THANKS TO THE conditional/unconditional option in command blocks





#asm commands avalible
#goto
#jif
#jit
    
#POP_FUNCTION_STACK #pops call stack
#PUSH_RET_GOTO  
#CALL #pushes return goto onto call stack and goes to goto

#set

#add
#sub
#mul
#div
#mod
#swp  #swaps variables values
    
#eql
#gtn
#lsn



#RAW_BLOCK
#RAW_BLOCK_END

#cannot use the variable name COMPILER_TEMP



block_endings=["POP_FUNCTION_STACK","goto","jif","jit"]


code=[]
tmp_goto_counter=0
tmp_return_counter=0
for index,line in enumerate(precode):
    #MAKE PREPROCESSER TO FIX ALL goto, jif, jit, POP_FUNCTION_STACK
    sline=line.split(' ')
    pline=precode[index-1].split(' ')
    if sline[0][0]=='[':
        if not pline[0] in block_endings:
            code.append("goto "+line)
            
    if pline[0] in ["jif","jit"]:
        tmp=pline[0]=="jif"
        code.append(["jif","jit"][tmp]+" "+pline[1]+" ["+str(tmp_goto_counter)+"_jump]")
        code.append("["+str(tmp_goto_counter)+"_jump]")
        tmp_goto_counter+=1
    if sline[0]=="CALL":
        code.append("PUSH_RET_GOTO ["+str(tmp_return_counter)+"_return]")
        code.append("goto "+sline[1])
        code.append("["+str(tmp_return_counter)+"_return]")
    else:
        code.append(line)
     



grid_x_width=30



from collections import OrderedDict
blocks=OrderedDict({"BOOT_PROGRAM":[]})
current_block="BOOT_PROGRAM"
for index,line in enumerate(code):
    if line[0]=='[':#might be [index-1]
        current_block=line[1:-1]
        blocks[current_block]=[]
    else:
        blocks[current_block].append(line)


block_positions_in_grid=OrderedDict({})
for index,name in enumerate(blocks.keys()):
    block_positions_in_grid[name]=[index%grid_x_width,int(index/grid_x_width)]






def get_goto_relitive_pos(c_block,name):
        anti_depth=-len(c_block)-1
          
        anti_horizontal,anti_height=block_positions_in_grid[name]
        #pos=block_positions_in_grid[name]
        #anti_horizontal-=pos[0]
        #anti_height-=pos[1]
        return [-anti_horizontal,-anti_height,anti_depth]
        

def is_num(thing):
    try:
        int(thing)
        return True
    except:
        return False

#reset program commands
#["/scoreboard objectives remove program","/scoreboard objectives add program dummy"]
#compiler to cmd blocks
compiled_blocks=OrderedDict({})
for name in blocks:
    compiled_blocks[name]=[]
    c_block=compiled_blocks[name]#current block (referenced, not copy)
    for line in blocks[name]:
        line=line.split(" ")
        op=line[0]
        args=line[1:]
        #print(op)
        if op=="set":
            if is_num(args[1]):
                c_block.append("/scoreboard players set %s program %s"%(args[0],args[1]))
            else:
                c_block.append("/scoreboard players operation %s program = %s program"%(args[0],args[1]))

        if op=="add":
            if is_num(args[1]):
                c_block.append("/scoreboard players add %s program %s"%(args[0],args[1]))
            else:
                c_block.append("/scoreboard players operation %s program += %s program"%(args[0],args[1]))
                
        if op=="sub":
            if is_num(args[1]):
                c_block.append("/scoreboard players add %s program %s"%(args[0],str(-int(args[1]))))
            else:
                c_block.append("/scoreboard players operation %s program -= %s program"%(args[0],args[1]))
        if op=="mul":
            if is_num(args[1]):
                c_block.append("/scoreboard players set COMPILER_TEMP program %s"%(args[1]))
                c_block.append("/scoreboard players operation %s program *= COMPILER_TEMP program"%(args[0]))
            else:
                c_block.append("/scoreboard players operation %s program *= %s program"%(args[0],args[1]))
        if op=="div":
            if is_num(args[1]):
                c_block.append("/scoreboard players set COMPILER_TEMP program %s"%(args[1]))
                c_block.append("/scoreboard players operation %s program /= COMPILER_TEMP program"%(args[0]))
            else:
                c_block.append("/scoreboard players operation %s program /= %s program"%(args[0],args[1]))
        if op=="mod":
            if is_num(args[1]):
                c_block.append("/scoreboard players set COMPILER_TEMP program %s"%(args[1]))
                c_block.append("/scoreboard players operation %s program %= COMPILER_TEMP program"%(args[0]))
            else:
                c_block.append("/scoreboard players operation %s program %= %s program"%(args[0],args[1]))


        if op=="swp":
            c_block.append("/scoreboard players operation %s program >< %s program"%(args[0],args[1]))

        if op=="eql":
            c_block.append("/scoreboard players set %s program 0"%(args[0]))
            if is_num(args[1]) and is_num(args[2]):
                c_block.append("/execute if score %s program = %s program run scoreboard players set %s program 1"%(args[1],args[2],args[0]))
            elif is_num(args[1])^is_num(args[2]):
                number=[args[2],args[1]][is_num(args[1])]
                variable=[args[1],args[2]][is_num(args[1])]
                c_block.append("/scoreboard players set COMPILER_TEMP program %s"%(number))
                c_block.append("/execute if score %s program = COMPILER_TEMP program run scoreboard players set %s program 1"%(variable,args[0]))
        if op=="lsn":
            op="gtn"
            tmp=args[1]
            args[2]=args[1]
            args[1]=tmp
        if op=="gtn":
            c_block.append("/scoreboard players set %s program 0"%(args[0]))
            if is_num(args[1]) and is_num(args[2]):
                c_block.append("/execute if score %s program > %s program run scoreboard players set %s program 1"%(args[1],args[2],args[0]))
            elif is_num(args[1])^is_num(args[2]):
                number=[args[2],args[1]][is_num(args[1])]
                variable=[args[1],args[2]][is_num(args[1])]
                c_block.append("/scoreboard players set COMPILER_TEMP program %s"%(number))
                c_block.append("/execute if score %s program > COMPILER_TEMP program run scoreboard players set %s program 1"%(variable,args[0]))
        
        if op=="goto":#~ ~ ~ = horizontal, heigt, depth
            pos=get_goto_relitive_pos(c_block,name)
            c_block.append("/setblock ~0 ~0 ~%s minecraft:air"%(pos[2]))#set current position start to air block
            if args[0]=="[end]":
                print("END TAG")
                c_block.append("GOTOTOTOTO END")
                continue
            pos=get_goto_relitive_pos(c_block,name)#finds position to 0,0,0
            delta_to_add=get_goto_relitive_pos(c_block,args[0][1:-1])
            pos[0]-=delta_to_add[0]#since there opposit to what we want subtract them
            pos[1]-=delta_to_add[1]
            c_block.append("/setblock ~%s ~%s ~%s minecraft:redstone_block"%(pos[0],pos[1],pos[2]))#set new goto position start to a redstone block

        if op=="jif":
            c_block.append("/scoreboard players set COMPILER_TEMP program 0")
            pos=get_goto_relitive_pos(c_block,name)
            c_block.append("/execute if score %s program = COMPILER_TEMP program run setblock ~0 ~0 ~%s minecraft:air"%(args[0],pos[2]))
            pos=get_goto_relitive_pos(c_block,name)#finds position to 0,0,0
            delta_to_add=get_goto_relitive_pos(c_block,args[1][1:-1])
            pos[0]-=delta_to_add[0]#since there opposit to what we want subtract them
            pos[1]-=delta_to_add[1]
            c_block.append("/execute if score %s program = COMPILER_TEMP program run setblock ~%s ~%s ~%s minecraft:redstone_block"%(args[0],pos[0],pos[1],pos[2]))
        if op=="jit":
            c_block.append("/scoreboard players set COMPILER_TEMP program 1")
            pos=get_goto_relitive_pos(c_block,name)
            c_block.append("/execute if score %s program = COMPILER_TEMP program run setblock ~0 ~0 ~%s minecraft:air"%(args[0],pos[2]))
            pos=get_goto_relitive_pos(c_block,name)#finds position to 0,0,0
            delta_to_add=get_goto_relitive_pos(c_block,args[1][1:-1])
            pos[0]-=delta_to_add[0]#since there opposit to what we want subtract them
            pos[1]-=delta_to_add[1]
            c_block.append("/execute if score %s program = COMPILER_TEMP program run setblock ~%s ~%s ~%s minecraft:redstone_block"%(args[0],pos[0],pos[1],pos[2]))
        if op=="POP_FUNCTION_STACK":
            print("NOT IMPLEMENTED")
        if op=="PUSH_RET_GOTO":
            print("NOT IMPLEMENTED")









class command_block:
    def __init__(self,position,command,type="chain",facing="south"):
        self.pos=position
        self.command=command
        self.type=["chain_command_block","repeating_command_block"][type=="normal"]
        self.facing=facing
    def __repr__(self):
        return str([self.pos,self.facing,self.type,self.command])
    def make_generation_command(self,version="13"):
        auto=['',',auto:1'][self.type=="chain_command_block"]
        if version=="13":
            return '/setblock ~%s ~%s ~%s %s[facing=%s]{Command:"%s"%s}'%(self.pos[0],self.pos[1],self.pos[2],self.type,self.facing,self.command,auto)
        if version=="12":
            raise Exception("Not compatible with mc 1.12 at the moment")
            #return '/setblock ~%s ~%s ~%s %s %s replace {Command:"%s"%s}'%(self.pos[0],self.pos[1],self.pos[2],self.type,['3'][not self.facing=="south"],self.command,auto)
        
    
command_blocks=[]
for name in compiled_blocks:
    x_offset,y_offset=block_positions_in_grid[name]
    for depth,command in enumerate(compiled_blocks[name]):
        command_blocks.append(command_block([x_offset,y_offset,depth],command,["chain","normal"][depth==0]))


generation_commands=[]
for command in command_blocks:
    generation_commands.append(command.make_generation_command())
if input("save to output (y/n): ").lower() in ["yes",'y']:
    f=open("compiled_out.txt",'w')
    f.write('\n'.join(generation_commands).replace('{C','{{}C').replace('"}','"{}}').replace('1}','1{}}'))#these replacements are for autohotkey auto placer
    f.close()
    print('saved')

if True:
    input("press enter to simulate program")



#simulator
current_block="BOOT_PROGRAM"

variables=OrderedDict({})
call_stack=[]


def parse(thing):
    try:
        return int(thing)
    except:
        return variables[thing]



while True:
    in_raw_block=False
    if current_block=="end":
        break
    for line in blocks[current_block]:
        print(line)
        
        if line=="RAW_BLOCK_END" and in_raw_block:
            in_raw_block=False
            
        if in_raw_block:
            print("in raw block:",line)

        line=line.split(" ")
        if line[0]=="RAW_BLOCK":
            in_raw_block=True

        
        if line[0]=='goto':
            current_block=line[1][1:-1]

        if line[0]=='set':
            variables[line[1]]=parse(line[2])
        
        if line[0]=='jif':#jump if false
            if not parse(line[1]):
                current_block=line[2][1:-1]
        if line[0]=='jit':#jump if true
            if parse(line[1]):
                current_block=line[2][1:-1]
                
        if line[0]=='add':
            variables[line[1]]+=parse(line[2])
        if line[0]=='sub':
            variables[line[1]]-=parse(line[2])
        if line[0]=='mul':
            variables[line[1]]*=parse(line[2])
        if line[0]=='div':
            variables[line[1]]=int(parse(line[2])/variables[line[1]])
        if line[0]=='mod':
            variables[line[1]]%=parse(line[2])
            

        if line[0]=='eql':
            variables[line[1]]=parse(line[2])==parse(line[3])
        if line[0]=='gtn':
            variables[line[1]]=parse(line[2])>parse(line[3])
        if line[0]=='lsn':
            variables[line[1]]=parse(line[2])<parse(line[3])

        
            
        
        if line[0]=='POP_FUNCTION_STACK':
            current_block=call_stack[0]
            del call_stack[0]
        if line[0]=='PUSH_RET_GOTO':
            call_stack.insert(0,line[1][1:-1])
            
        
        


print(variables)



