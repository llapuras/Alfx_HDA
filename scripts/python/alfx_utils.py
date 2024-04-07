# -*- coding: utf-8 -*-
import hou

# 只执行选中节点内部的子节点
def definition_nodes():
    print("------------------Definition Node-----------------------")
    nodes = hou.selectedNodes()
    for node in nodes:
        for child in node.allSubChildren():
            if not (child.matchesCurrentDefinition()):
                print(child.path())
                child.matchCurrentDefinition()

# 快速定位到objmerge中的节点路径
def quikfind():
    nodes = hou.selectedNodes()
    if len(nodes):
        node = nodes[0]
        if node.type().name() == "object_merge":
            despath = node.parm("objpath1").eval()
            desnode = hou.node(hou.text.abspath(despath,node.path()))
            plane = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
            
            hou.clearAllSelected()
            desnode.setSelected(1)
            plane.homeToSelection()
        else:
            print("选中的节点需要是objmerge类型------")

# 快速给四个输出端口创建null节点
def quikedisplay():

    plane = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
    currentpos = plane.selectPosition()
    
    node = hou.selectedNodes()[0]
    parent = node.parent()
    
    if len(node.outputNames())>0:
        terrain = parent.createNode("null","terrain")
        mesh = parent.createNode("null","mesh")
        pt = parent.createNode("null","points")
        curve = parent.createNode("null","curves")
        # asset = parent.createNode("null","asset")
        
        terrain.setPosition(currentpos)
        terrain.setInput(0,node,0)
        terrain.setColor(hou.Color(0.71,0.518,0.004))
        
        pt.setPosition(currentpos)
        pt.move([2,0])
        pt.setInput(0,node,1)
        pt.setColor(hou.Color(0.475,0.812,0.204))
        
        mesh.setPosition(currentpos)
        mesh.move([4,0])
        mesh.setInput(0,node,2)
        mesh.setColor(hou.Color(0.29,0.565,0.886))
        
        curve.setPosition(currentpos)
        curve.move([6,0])
        curve.setInput(0,node,3)
        curve.setColor(hou.Color(0.451,0.369,0.796))
        
        # asset.setPosition(currentpos)
        # asset.move([8,0])
        # asset.setInput(0,node,4)
        # asset.setColor(hou.Color(0.306,0.306,0.306))

# 将选中节点内部的heightfield相关节点的clamo开启   
def clampmask():
    print("------------------------------------------------")

    blackList =['heightfield_maskblur','heightfield_maskbyfeature','heightfield_maskbyobject']
    for node in hou.selectedNodes():
        if node.type().name()=="heightfield_layer" :
            if (not node.parm("doclampmin").eval()) or (not node.parm("doclampmax").eval()):
                try:
                    print(node.path())
                    node.parm("doclampmin").set(1)
                    node.parm("doclampmax").set(1)
                except:
                    pass
        if node.type().name()=="heightfield_remap" :
            if (not node.parm("clampmin").eval()) or (not node.parm("clampmax").eval()):
                try:
                    print(node.path())
                    node.parm("clampmin").set(1)
                    node.parm("clampmax").set(1)
                except:
                    pass
        else:
            node.allowEditingOfContents()
            for child in node.allSubChildren():
                typename = child.type().name()
                if typename=="heightfield_layer" and (typename not in blackList):
                    if (not child.parm("doclampmin").eval()) or (not child.parm("doclampmax").eval()):
                        try:
                            child.parm("doclampmin").set(1)
                            child.parm("doclampmax").set(1)
                            print(child.path())
                        except:
                            pass
                if typename=="heightfield_remap" and (typename not in blackList):
                    if (not child.parm("clampmin").eval()) or (not child.parm("clampmax").eval()):
                        try:
                            child.parm("clampmin").set(1)
                            child.parm("clampmax").set(1)
                            print(child.path())
                        except:
                            pass            
# copy node 
def copynode():

    nodeGrp = hou.selectedNodes()
    path_info = []
    file = open("path.txt","w")
    
    for eachnode in nodeGrp:
        currentpath = eachnode.path()
        path_info.append(currentpath)
    nodepaths = path_info
    for eachpath in nodepaths:
        file.write(eachpath)
        file.write("\n")
    file.close()

# paste node
def pastenode():
    
    plane = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
    parent = plane.pwd()
    currentpos = plane.selectPosition()
    
    lineList = []
    file = open("path.txt","r")
    lineList = file.readlines()
    file.close()
            
    for num in range(len(lineList)):
    
        objmerge_name ="objmer_"+lineList[num].split("/")[-1][0:-1]
        
        objmerge = parent.createNode("object_merge",objmerge_name)

        nodepath = lineList[num][0:-1]
        inputnode = hou.node(nodepath)

        nodepath = objmerge.relativePathTo(inputnode)

        objmerge.parm("objpath1").set(nodepath)
        objmerge.parm("xformtype").set(1)
        objmerge.setPosition(currentpos)
    
        currentpos[0]+=3
        
# merge node
def mergenode():
   
    nodes = hou.selectedNodes() 
    
    if len(nodes):
    
        plane = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
        parent = plane.pwd()
        currentpos = plane.selectPosition()
        
        merge = parent.createNode('merge')
        merge.setPosition(currentpos)
        
        merge.setDisplayFlag(True)
        merge.setTemplateFlag(True)
        merge.setRenderFlag(True)
        
        for node in nodes:
            merge.setNextInput(node)  

# node count
def nodecount(detailInfo = False):
    nodes = hou.selectedNodes()

    hdalists = dict()
    for node in nodes:
        childs = node.allSubChildren()
        hdalists[node.type().name()] = len(childs)
        nodelists = dict()
        for child in childs:
            typename = child.type().name()
            if typename not in nodelists.keys():
                nodelists[typename] = 0
            else:
                nodelists[typename] += 1
        if detailInfo:
            nodelists = sorted(nodelists.items())
            for key in nodelists:
                print(key,nodelists[key])

    hdalist = sorted(hdalists.items(),key = lambda kv:(kv[1], kv[0]),reverse=True)

    for key in hdalist:
        print(key[0]," : ",key[1])

#---main-----------------
if __name__ == "__main__":
    pass