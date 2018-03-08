#!/usr/bin/python
# -*- coding: utf-8 -*-
# 本类是通过ac算法实现字符串的多模匹配
# author: jingwu

class AcismNode:
    def __init__(self, data):
        self.data = data            # 结点值
        self.fail = None            # Fail指针
        self.tail = 0               # 尾标志：标志为 i 表示第 i 个模式串串尾
        self.childs = []            # 子结点
        self.nodevalues = []        # 子结点的值

class Acism:
    def __init__(self, keywords):
        self.__keywords = keywords
        self.root = AcismNode("")
        self.count = 0
        self.__makeTrie(keywords)

    # 第一步：模式串建树
    def __makeTrieForKeyword(self, keyword):
        self.count += 1
        node = self.root
        for i in keyword:
            if i not in node.nodevalues:
                child = AcismNode(i)
                node.childs.append(child)
                node.nodevalues.append(i)
                node = child
            else:
                node = node.childs[node.nodevalues.index(i)]
        node.tail = self.count

    # 第二步：修改Fail指针
    def __correctFail(self):
        queuelist = [self.root]                     # 用列表代替队列
        while len(queuelist):                       # BFS遍历字典树
            temp = queuelist[0]
            queuelist.remove(temp)
            for i in temp.childs:
                if temp == self.root:
                    i.fail = self.root
                else:
                    node = temp.fail
                    while node:
                        if i.data in node.nodevalues:    # 若结点值在该结点的子结点中，则将Fail指向该结点的对应子结点
                            i.fail = node.childs[node.nodevalues.index(i.data)]
                            break
                        node = node.fail
                    if not node:
                        i.fail = self.root
                queuelist.append(i)

    def __makeTrie(self, keywords):
        for keyword in keywords:
            self.__makeTrieForKeyword(keyword)
        self.__correctFail()

    # 第三步：模式匹配
    def scan(self, content):
        node = self.root
        matches = {}
        for i in content:
            while i not in node.nodevalues and node is not self.root:
                node = node.fail
            if i in node.nodevalues:
                node = node.childs[node.nodevalues.index(i)]
            else:
                node = self.root
            nodetmp = node 
            while nodetmp is not self.root:
               if nodetmp.tail:
                   if nodetmp.tail not in matches:
                       matches.setdefault(nodetmp.tail)
                       matches[nodetmp.tail] = 1
                   else:
                       matches[nodetmp.tail] += 1
               nodetmp = nodetmp.fail
        results = {}
        for key,value in matches.items():
            results[self.__keywords[key-1]] = value
        return results

# keywords = []
# for keyword in open(KEYWORDS_FILE, 'r').readlines():
#    keywords.append(keyword.strip())
# acism = Acism(keywords)
#
# content = open('ifeng.html', 'r').read()
# keywords = []
# for keyword in open('keyword.txt', 'r').readlines():
#    keywords.append(keyword.strip())
# print(acism(keywords).scan(content))

