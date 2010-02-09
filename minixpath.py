"""
    minixpath - simple xpath expression finder for python.

    Copyright (c) 2008, Pascal Gauthier
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:
        * Redistributions of source code must retain the above copyright
          notice, this list of conditions and the following disclaimer.
        * Redistributions in binary form must reproduce the above copyright
          notice, this list of conditions and the following disclaimer in the
          documentation and/or other materials provided with the distribution.
        * Neither the name of the 'Pascal Gauthier' nor the
          names of its contributors may be used to endorse or promote products
          derived from this software without specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY PASCAL GAUTHIER ''AS IS'' AND ANY
    EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL PASCAL GAUTHIER BE LIABLE FOR ANY
    DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
    ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import xml.dom.minidom
import shlex

def compileExpr(expr) :
    pgm = []

    lex = shlex.shlex(expr)
    token = lex.get_token()
    
    while token != '' :
        if token == '/' :
            token = lex.get_token()
            pgm.append((token,))
            token = lex.get_token()
            if token == '/' :
                continue
        
        if token == '' :
            break

        if token == '[' :
            field = lex.get_token()
            if field == '@' :
                field = "@%s" % lex.get_token()
            
            op = lex.get_token()
            if op == "!" :
                if lex.get_token() == '=' :
                    op = '!='
                else :
                    raise "Parsing error on ! operator"
                
            value = lex.get_token()
            if value[0] == '"' :
                value = value[1:-1]

            if lex.get_token() != ']' :
                raise "Parsing error"

            pgm.append((field, op, value))
            token = lex.get_token()
            continue

        raise Exception, "Parsing error; unknown token %s" % token

    return pgm

def findnode(node, pgm) :
    """ Recursive node finder
    """

    searchCtx = pgm[0]
    result = []

    if searchCtx[0] == ".." :
        result.append(node.parentNode)

    elif searchCtx[0][0] == '@' :
        attrib = searchCtx[0][1:]
        value = node.getAttribute(attrib)
        if searchCtx[1] == "=" :
            if searchCtx[2] != value :
                return None
        elif searchCtx[1] == "!=" :
            if searchCtx[2] == value :
                return None
        else :
            return None

        if len(pgm) > 1 :
            found = findnode(node, pgm[1:])
            if found != None :
                result = result + found
        # result.append(i)

    else :
        for i in node.getElementsByTagName(searchCtx[0]) :
            if len(searchCtx) > 1 :
                value = getText(i)
                if searchCtx[1] == "=" :
                    if searchCtx[2] == value :
                        i = i.parentNode
                elif searchCtx[1] == "!=" :
                    if searchCtx[2] != value :
                        i = i.parentNode
                else :
                    return None

            if len(pgm) > 1 :
                found = findnode(i, pgm[1:])
                if found != None :
                    result = result + found
            else :
                result.append(i)

    return result

def evaluate(node, expr) :
    """ main entry point for minixpath. 
    """
    pgm = compileExpr(expr)
    return findnode(node, pgm)

def getText(*nodes):
    return ''.join(''.join(child.data for child in node.childNodes
                           if child.nodeType == node.TEXT_NODE)
                   for node in nodes)

if __name__ == "__main__" :
    xmltest = """
        <list>
            <item active="false"><id>1023</id><name>patate</name></item>
            <item><id>1030</id><name>courge</name></item>
            <item active="not"><id>1040</id><name>noix</name></item>
            <item active="true"><id>1050></id><name>gum</name></item>
        </list>"""

    root = xml.dom.minidom.parseString(xmltest)

    node = evaluate(root, "/list/item/id")
    assert node
    assert [u'1023', u'1030', u'1040', u'1050>'] == [getText(n) for n in node]

    node = evaluate(root, '/list/item[name="courge"]/id')
    assert node
    assert [u'1030'] == [getText(n) for n in node]
    assert u'1030' == getText(*node)

    node = evaluate(root, '/list/item[id!=1040]/name')
    assert node
    assert [u'patate', u'courge', u'gum'] == [getText(n) for n in node]
    assert u'patatecourgegum' == getText(*node)
    
    node = evaluate(root, '/list/item[@active ="true"]/name')
    assert node
    assert [u'gum'] == [getText(n) for n in node]
    assert u'gum' == getText(*node)

    node = evaluate(root, '/nonesuch')
    assert not getText(*node)
    assert '' == getText(*node)
