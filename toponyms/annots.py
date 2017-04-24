#-*- coding: UTF-8 -*-

class Annotation(object):
    def __init__(self, name, left, right, exactness = 'strict'):
        self.name = name
        self.left = left
        self.right = right
        self.exactness = exactness

    def __eq__(self, other):
        if self.exactness == 'strict':
            return (self.name == other.name and self.left == other.left and self.right == other.right)
        elif self.exactness == 'left':
            return self.name == other.name and self.left == other.left
        else:
            return (self.name == other.name) and \
                   ((other.left >= self.left and other.left <= self.right) or (self.left >= other.left and self.left <= other.right))

    def __repr__(self):
            return str([self.name, self.left, self.right])

    def __hash__(self):
        return hash(self.__repr__())

    def setoffsets(self, l ,r):
        self.left, self.right = l, r

    def setleftoffset(self, l):
        self.left = l

    def setrightoffset(self, r):
        self.right = r

class AnnotationSet(set):

    def __add__(self, other):
        for ann in other:
            self.add(ann)

    def __init__(self, seq = ()):
        super(set, self).__init__()
        self += seq

    def intersection(self, other):
        return filter ( lambda ann: filter(lambda x: x == ann, other), self)

def setlabels(words, annotations):
    labels = []
    for annotation in annotations:
         labels.append(' '.join(words[i] for i in xrange(annotation.left, annotation.right + 1)))#.encode('utf-8'))
    return labels

def setAnnotations(y,  CLASSES, exactness = 'strict'):
    annotations = AnnotationSet()
    length = len(y)
    for i in xrange(len(y)):
        if y[i] % 2 == 0 or y[i] not in CLASSES.keys(): #(zero class or not first element of entity)
            pass
        else:
            left = i
            name = CLASSES[y[i]]
            while i < length and (y[i] == y[left] + 1 or y[i] == y[left]):
                i += 1
            i -= 1
            right = i
            annotations.add(Annotation(name, left, right, exactness = exactness))
    return annotations