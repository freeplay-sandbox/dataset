from collections import OrderedDict

CHILDCHILD = "childchild"
CHILDROBOT = "childrobot"


GOALORIENTED="goaloriented"
AIMLESS="aimless"
ADULTSEEKING="adultseeking"
NOPLAY="noplay"

TASKENGAGEMENT=(GOALORIENTED,
                AIMLESS,
                ADULTSEEKING,
                NOPLAY)

SOLITARY="solitary"
ONLOOKER="onlooker"
PARALLEL="parallel"
ASSOCIATIVE="associative"
COOPERATIVE="cooperative"

SOCIALENGAGEMENT=(SOLITARY,
                  ONLOOKER,
                  PARALLEL,
                  ASSOCIATIVE,
                  COOPERATIVE)

PROSOCIAL="prosocial"
ADVERSARIAL="adversarial"
ASSERTIVE="assertive"
FRUSTRATED="frustrated"
PASSIVE="passive"

SOCIALATTITUDE=(PROSOCIAL,
                ADVERSARIAL,
                ASSERTIVE,
                FRUSTRATED,
                PASSIVE)

CONSTRUCTS = (TASKENGAGEMENT, SOCIALENGAGEMENT, SOCIALATTITUDE)
CONSTRUCTS_NAMES = {TASKENGAGEMENT:"task_engagement",
                    SOCIALENGAGEMENT:"social_engagement",
                    SOCIALATTITUDE:"social_attitude"}

MISSINGDATA="missingdata"


class Timeline:

    def __init__(self, construct, annotations):

        self.construct = construct

        self.timeline=OrderedDict()
        self.start = 0
        self.end = 0

        self.prepare(annotations)

    def prepare(self, annotations):
        
        for a in annotations:
            for k,v in a.items():
                if k in self.construct:
                    self.timeline[v[0]] = (v[0], v[1], k)

                    if self.start == 0:
                        self.start = v[0]
                    self.end = v[1]



    def attime(self, t):
        for k, v in self.timeline.items():
            start, end, construct = v
            if t >= start and t < end:
                return construct
        return MISSINGDATA

    def __repr__(self):
        return "timeline from %f to %f (%d sec), %s" % (self.start, self.end, self.end-self.start, str(self.construct))

class TimelinePrinter:
    
    def __init__(self, id, construct, coder, cdt = CHILDCHILD):
        self.id = id
        self.construct = construct
        self.tp = Timeline(construct, coder["purple"])

        self.cdt = cdt

        self.start = self.tp.start
        self.end = self.tp.end


        if cdt == CHILDCHILD:
            self.ty = Timeline(construct, coder["yellow"])
            self.start = max(self.start, self.ty.start)
            self.end = min(self.end, self.ty.end)

    @staticmethod
    def csv_header():
        return ["id", "condition", "child", "construct_class", "construct", "duration"]

    def csvrows(self):
        rows = []
        for k, v in self.tp.timeline.items():
            start, end, annotation = v
            rows.append([self.id, self.cdt, "purple", CONSTRUCTS_NAMES[self.construct], annotation, end-start])

        if self.cdt == CHILDCHILD:
            for k, v in self.ty.timeline.items():
                start, end, annotation = v
                rows.append([self.id, self.cdt, "yellow", CONSTRUCTS_NAMES[self.construct], annotation, end-start])

        return rows

 
class InterraterReliability:
    
    def __init__(self, construct, coder1, coder2, cdt = CHILDCHILD):
        self.construct = construct
        self.t1p = Timeline(construct, coder1["purple"])
        self.t2p = Timeline(construct, coder2["purple"])

        self.cdt = cdt

        # [start, end] is the shortest overlapping interval
        # between to two coders
        self.start = max(self.t1p.start, self.t2p.start)
        self.end = min(self.t1p.end, self.t2p.end)


        if cdt == CHILDCHILD:
            self.t1y = Timeline(construct, coder1["yellow"])
            self.t2y = Timeline(construct, coder2["yellow"])
            self.start = max(self.start, self.t1y.start, self.t2y.start)
            self.end = min(self.end, self.t1y.end, self.t2y.end)

        self.total_units = 0
        self.total_units_missing_data = 0
        self.total_units_agree = 0

        self.compute()

        self.percentage_agreement = self.total_units_agree * 100. / (self.total_units - self.total_units_missing_data)

        self.alpha = self.krippendorff_alpha()

    def compute(self, window = 1.):

        t = self.start

        while t < self.end:
            c1 = self.t1p.attime(t)
            c2 = self.t2p.attime(t)

            t += window
            self.total_units += 1

            if c1 == MISSINGDATA or c2 == MISSINGDATA:
                self.total_units_missing_data += 1
                continue

            if c1 == c2:
                self.total_units_agree += 1

        if self.cdt == CHILDCHILD:
            t = self.start

            while t < self.end:
                c1 = self.t1y.attime(t)
                c2 = self.t2y.attime(t)

                t += window
                self.total_units += 1

                if c1 == MISSINGDATA or c2 == MISSINGDATA:
                    self.total_units_missing_data += 1
                    continue

                if c1 == c2:
                    self.total_units_agree += 1


    def krippendorff_alpha(self, window = 1.):
        import krippendorff
        import numpy as np

        data1 = []
        data2 = []
        t = self.start

        while t < self.end:
            c1 = self.t1p.attime(t)
            if c1 == MISSINGDATA:
                data1.append(np.nan)
            else:
                data1.append(hash(c1))

            c2 = self.t2p.attime(t)
            if c2 == MISSINGDATA:
                data2.append(np.nan)
            else:
                data2.append(hash(c2))

            t += window

        return krippendorff.alpha([data1, data2], level_of_measurement='nominal')

if __name__=="__main__":

    import yaml
    import sys

    with open(sys.argv[1], 'r') as yml:
        coder1 = yaml.load(yml)

    with open(sys.argv[2], 'r') as yml:
        coder2 = yaml.load(yml)

    for construct in CONSTRUCTS:
        irr = InterraterReliability(construct, coder1, coder2)

        print("Percentage agreement: %f%% on %s" % (irr.percentage_agreement, construct))
