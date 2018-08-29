""" A faithful but readable translation of PRCA.py """
import os, sys
import math
import random
import time


def add_connected_entities_to_dict(d, entity_path, relation_id_as_str, value):
    """
    Call using: add_connected_entities_to_dict(h_e_p, e1 + ' ' + e2, str(rel1), 1.0 / len(e2_set))
    The value is 1/how many other entities e1 is connected to.
    So the more connected entities the weaker the connection from e1 to e2 is.

    Adds to a dict so it contains

    { 'entity1 entity2':
        { 'relation_id': value, 'other_relation': value}
    }

    So it can tell me given two entities what relation best connects them.
    I think this only considers immediate relations so no notion of a path yet.
    """
    if entity_path not in d:
        d[entity_path] = {}
    if relation_id_as_str not in d[entity_path]:
        d[entity_path][relation_id_as_str] = 0.0  # Strength of this connection starts off low?
    d[entity_path][relation_id_as_str] += value  # Increment strength.


def add_to_dict_and_increment(d, key):  # Same behaviour as you can get using collections.defaultdict(int).
    if key not in d:
        d[key] = 0
    d[key] += 1

relation_to_id = {}
id_to_relation = {}
relation_num = 0

with open("data/relation2id.txt", "r") as relation2id_fh:
    """ Format of a single relation is
    /people/appointed_role/appointment./people/appointment/appointed_by	0
    """
    for line in relation2id_fh:
        relation, relation_id = line.strip().split()
        relation_to_id[relation] = int(relation_id)
        id_to_relation[int(relation_id)] = relation
        relation_num += 1

    # This code never executes?
    # Looks like it adds in the reverse relation.
    # with reverse relation id = id + num_relations as an offset.
    # word rep of reverse relations prefixed with ~.
    for line in relation2id_fh:
        # It adds in the reverse relation?
        seg = line.strip().split()
        id_to_relation[int(seg[1]) + relation_num] = "~" + seg[0]


ok = {}  # Are these paths?
# I think they are all relations that join e1 and e2.
"""
dict of {
  'e1 e2': { rel_id: 1, real_id2: 1}, 
  'e2 e1': { rel_id_reversed: 1, rel_id_reverse2: 1 },
  'ex ey': {} # if know they are connected but not by which relation.
 }
"""

all_entities = {}  # Not sure what these are?
"""
dict of {
    'e1': { 'relation_id': { 'e2': 1, 'e3': 1},  # if e1 is connected to e2 and e3 via the same relation.
    }
}
"""
num = 0
step = 0


with open("data/train.txt", "r") as train_fh:
    """ Format of a single line in train.txt is 
    /m/027rn	/m/06cx9	/location/country/form_of_government
    
    contains triples (head, tail, relation).
    """
    for line in train_fh:
        seg = line.strip().split()
        e1 = seg[0]
        e2 = seg[1]
        rel = seg[2]

        forwards_path = "%s %s" % (e1, e2)
        backwards_path = "%s %s" % (e2, e1)
        relation_id = relation_to_id[rel]
        reverse_relation_id = relation_id + relation_num

        if forwards_path not in ok:
            ok[forwards_path] = {}

        ok[forwards_path][relation_id] = 1

        if backwards_path not in ok:
            ok[backwards_path] = {}

        ok[backwards_path][reverse_relation_id] = 1

        if e1 not in all_entities:  # Add unseen entity (head) to dict.
            all_entities[e1] = {}

        if relation_id not in all_entities[e1]:  # This relation is an out going edge of e1.
            all_entities[e1][relation_id] = {}

        all_entities[e1][relation_id][e2] = 1  # Captures the path e1 -r-> e2.

        if e2 not in all_entities:  # Adds unseen entity (tail) to dict.
            all_entities[e2] = {}

        if reverse_relation_id not in all_entities[e2]:
            # The reverse relation r' is an out going edge from e2 -r'-> e1 as e1 -r-> e2 is connected via r.
            all_entities[e2][reverse_relation_id] = {}

        all_entities[e2][reverse_relation_id][e1] = 1  # Captures path e2 -r'-> e1.


with open("data/test.txt", "r") as test_fh:
    """ Format of a single line in test.txt is
    /m/040db	/m/0148d	/base/activism/activist/area_of_activism

    contains triples (head, tail, relation).
    """
    for line in test_fh:
        seg = line.strip().split()
        e1 = seg[0]
        e2 = seg[1]

        forwards_path = "%s %s" % (e1, e2)
        backwards_path = "%s %s" % (e2, e1)

        # Looks like this captures that (e1, e2) are connected but not the relation connecting them.
        if forwards_path not in ok:
            ok[forwards_path] = {}
        # Looks like this captures that (e2, e1) are connected but not the reverse relation connecting them.
        if backwards_path not in ok:
            ok[backwards_path] = {}


"""
According to the PTransE paper, e1_e2.txt is the top 500 entites ranked by TransE then re-ranked by PTransE?
"""

with open("data/e1_e2.txt", "r") as e1_e2_fh:
    """ Format of a single line in e1_e2.txt is
    0 0
    
    I believe these are entity ids whose mapping can be found in entity2id.txt
    """
    for line in e1_e2_fh:
        seg = line.strip().split()
        e1 = seg[0]
        e2 = seg[1]

        forwards_path = "%s %s" % (e1, e2)
        backwards_path = "%s %s" % (e2, e1)

        # TODO: e1_e2.txt contains "0 0" meaning 0 is connected to itself, is this allowed?

        # Looks like this captures that (e1, e2) are connected but not the relation connecting them.
        ok[forwards_path] = {}
        # Looks like this captures that (e2, e1) are connected but not the reverse relation connecting them.
        ok[backwards_path] = {}

# Paths to train on, has resource score > 0.1.
train_path = {}

# I think this holds relation paths mapped to the count or occurrence of that path.
path_dict = {}
"""
{
    'relation_id': 1,
    'relation_id_1 relation_id_2': 1  # For relations e1 -r1-> e2 -r2-> e3
}
"""

# Contains all relation_paths->all_possible_joining_relations I think.
# I think this is used to judge the reliability of the relation path
# the example in the paper is h -friend-> e1 -profession-> t.
# the more entries in here means more tail entities (I think) which means less reliable according to the paper.
path_r_dict = {}
"""
{
    'relation_id_1->relation_id_2': 1,
    'relation_id_1 relation_id_2->joining_relation': 1 
    # key is a relation path '->' 
    # value is the count/occurrence.
}
"""

with open("data/path2.txt", "w") as path2_fh:  # I don't actually see where path2.txt is used in PTransE.
    step = 0
    start_time = time.time()
    path_num = 0

    h_e_p = {}  # head_entity_path?
    # looks like this holds head, tail, paths.
    # with no notion of intermediate entities.
    """
    { 'e1 e2': {
            'relation_id': value,
            'another_relation_id': value
        },
        'e1 e3': {
            'relation_id1 relation_id2': value
        }
    }
    """

    for e1 in all_entities:  # Loop over all head entities.
        step += 1
        print step

        # Paths of length 2 entities.
        for relation_id in all_entities[e1]:  # Loop over all outgoing relations from head entity.
            e2_set = all_entities[e1][relation_id]
            for e2 in e2_set:  # Loop over all entities connected via this outgoing relation.

                # Increment the count of this relation id being used.
                add_to_dict_and_increment(path_dict, str(relation_id))

                forwards_path = "%s %s" % (e1, e2)
                # Add the count of this relation id being connected to a resulting relation id.
                # TODO: A bit confused on this part.
                for joining_relation_id in ok[forwards_path]:
                    # I think this just joins "e1 e2": relation_id.
                    # and compares relation_id -> relation_id.
                    # I think it might be used for a ratio to check if relation_id is right?
                    add_to_dict_and_increment(path_r_dict, str(relation_id) + "->" + str(joining_relation_id))

                # Represent the connection between e1 and e2 via relation_id.
                add_connected_entities_to_dict(h_e_p, e1 + ' ' + e2, str(relation_id), 1.0 / len(e2_set))

        # Paths of length 3 entities?
        for relation_id in all_entities[e1]:   # Loop over all outgoing relations from head entity.
            e2_set = all_entities[e1][relation_id]
            for e2 in e2_set:  # Loop over all entities connected via this outgoing relation.
                # up to here.
                if e2 in all_entities:  # e2 should be in here.
                    for relation_id_2 in all_entities[e2]:
                        # Path e1 -r1-> e2 -r2->e3.
                        e3_set = all_entities[e2][relation_id_2]
                        for e3 in e3_set:
                            add_to_dict_and_increment(path_dict, str(relation_id) + " " + str(relation_id_2))
                            # I think this is where they construct new triples?
                            e1_e3 = e1 + " " + e3
                            if e1_e3 in ok:  # If there is a link from e1 and e3 with no intermediate entity.
                                for joining_relation in ok[e1 + ' ' + e3]:
                                    add_to_dict_and_increment(path_r_dict, str(relation_id) + " " + str(relation_id_2) + "->" + str(joining_relation))
                            if e1_e3 in ok:  # and h_e_p[e1+' '+e2][str(rel1)]*1.0/len(e3_set)>0.01):
                                # Adds 'e1 e3' as a key mapping to 'relation_id_1 relation_id_2' mapping to
                                # h_e_p['e1 e2']['relation_id'] value / len(e3_set)
                                # I think the value is the 'network flow' of resource from e1 to e3.
                                add_connected_entities_to_dict(
                                    d=h_e_p,
                                    entity_path=e1_e3,
                                    relation_id_as_str=str(relation_id) + ' ' + str(relation_id_2),
                                    value=h_e_p[e1 + ' ' + e2][str(relation_id)] * 1.0 / len(e3_set)
                                )
        for e2 in all_entities:
            e_1 = e1
            e_2 = e2
            e1_e2 = "%s %s" % (e1, e2)
            if e1_e2 in h_e_p:
                # h_e_p['head tail'] should map to a bunch of relations (either 1 step or 2 step) that join head and
                # tail. So the number of paths between the two is the len(h_e_p['head tail]) as reach relation
                # joining them are a unique path.
                path_num += len(h_e_p[e1_e2])
                # TODO: What even are these dicts?
                bb = {}  # contains a dict of relation paths to resource allocation value.
                aa = {}  # contains bb but only paths that meet the threshold.
                # Writes: "head tail\n"
                # eg: /m/06rf7 /m/0g7pm
                path2_fh.write(e1_e2 + "\n")

                sum = 0.0  # Sum all resource values across all joining relations.

                # Note: rel_path should be '0' or '0 1' which are ids of relations either singular or multiple.
                for rel_path in h_e_p[e1_e2]:  # For each unique relation joining e1 and e2.
                    bb[rel_path] = h_e_p[e1_e2][rel_path]
                    # h_e_p[e1_e2][rel_path] should lead to a value representing the resource allocation.
                    sum += bb[rel_path]
                for rel_path in bb:
                    # Divide the value of resource for this joining relation path by sum giving a % value of
                    # resource flow.
                    bb[rel_path] /= sum

                    if bb[rel_path] > 0.01:  # If resource > 0.01 we keep this.
                        # Adds the relation path joining e1_e2 and resource allocation value to aa.
                        aa[rel_path] = bb[rel_path]
                """ The next part writes out the following in a single line after writing out e1_e2.
                23 # number of relation paths.
                2 2608 1804 0.0150940056675  # num of relations in this relation path (2), actual rel path, score.
                1 1340 0.211316079345        # num of relations in this relation path (1), actual rel path, score.
                2 143 1340 0.0528290198361   # num of relations in this relation path (2), actual rel path, score.
                """
                path2_fh.write(str(len(aa)))  # Total num of relation paths connecting e1_e2.
                for rel_path in aa:  # For each relation path we care about.
                    train_path[rel_path] = 1  # We train on this relation path I guess.
                    # number of relations, relation ids, value of resource flow
                    info = " %s %s %s" % (len(rel_path.split()), rel_path, aa[rel_path])
                    path2_fh.write(info)
                path2_fh.write("\n")
        print path_num, time.time() - start_time
        sys.stdout.flush()

print
"DAVID HERE: relation_num" + str(relation_num)

# TODO: Since the reverse relations are never captured, relation_num will be in the 1000s, this might effect below
# as we iterate through all relation nums

with open("data/confidence.txt", "w") as confidence_fh:
    for rel_path in train_path:
        out = []
        for relation_id in range(0, relation_num):
            # If either 'relation_id' or 'relation_id_1 relation_id_2' in path_dict.
            # I think path dict holds relation path counts.
            # I guess rel_path->rel_id is an assurance of the path?

            if rel_path in path_dict and rel_path + "->" + str(relation_id) in path_r_dict:
                # I think this is a ratio of value of this path divided by the total number of paths.
                # TODO: I actually have no idea.
                resource_flow = path_r_dict[rel_path + "->" + relation_id] * 1.0 / path_dict[rel_path]
                write_this = " %s %s" % (relation_id, resource_flow)
                out.append(write_this)

        """ The following section writes out something like 
        2 372 1717  # length of the relation path followed by actual relation ids.
        # count of relation id, confidence (3) followed by 'relation_id confidence' pairs.
        3 548 0.339449541284 910 0.0642201834862 1274 0.348623853211  
        """
        if len(out) > 0:
            # count of relations on the path, actual relation path.
            rel_path_info = "%s %s\n" % (len(rel_path.split()), rel_path)
            confidence_fh.write(rel_path_info)  # Writes: 2 372 1717
            confidence_fh.write(str(len(out)))  # Writes out number of entries.
            for i in range(len(out)):
                confidence_fh.write(out[i])  # Writes out 'relation_id confidence_level'
            confidence_fh.write("\n")


# Processes the test/train set and writes out data/test{or train}_pra.txt
def work(test_or_train):
    data_set_fh = open("data/" + test_or_train + ".txt", "r")
    # Contains triples:
    # /m/01qscs	/m/02x8n1n	/award/award_nominee/award_nominations./award/award_nomination/award

    write_out_pra_fh = open("data/" + test_or_train + "_pra.txt", "w")

    for line in data_set_fh:
        seg = line.strip().split()
        e1 = seg[0]
        e2 = seg[1]
        relation_id = relation_to_id[seg[2]]

        pra_heading = "%s %s %s\n" % (e1, e2, relation_id)  # Writes out a line like: /m/027rn /m/06cx9 352
        write_out_pra_fh.write(pra_heading)

        b = {}  # contains a dict of relation paths to resource allocation value.
        a = {}  # contains bb but only paths that meet the threshold.

        forwards_path = "%s %s" % (e1, e2)
        if forwards_path in h_e_p:
            sum = 0.0
            for rel_path in h_e_p[forwards_path]:
                b[rel_path] = h_e_p[forwards_path][rel_path]  # Resource flow value.
                sum += b[rel_path]
            for rel_path in b:
                b[rel_path] /= sum  # Gives a % out of 100 for the relevance of this path.
                if b[rel_path] > 0.01:  # Take paths that meet the threshold.
                    a[rel_path] = b[rel_path]
        write_out_pra_fh.write(str(len(a)))  # Writes out the number of relation paths we care about.
        for rel_path in a:
            write_out_pra_fh.write(" " + str(len(rel_path.split())) + " " + rel_path + " " + str(a[rel_path]))
        write_out_pra_fh.write("\n")

        # This does the exact same as above but writes out the reverse relation path.
        write_out_pra_fh.write(str(e2) + " " + str(e1) + ' ' + str(relation_id + relation_num) + "\n")
        # Note: e1 and e2 have been flipped.
        e1 = seg[1]
        e2 = seg[0]
        b = {}  # contains a dict of relation paths to resource allocation value.
        a = {}  # contains bb but only paths that meet the threshold.
        if (e1 + ' ' + e2 in h_e_p):
            sum = 0.0
            for rel_path in h_e_p[e1 + ' ' + e2]:
                b[rel_path] = h_e_p[e1 + ' ' + e2][rel_path]
                sum += b[rel_path]
            for rel_path in b:
                b[rel_path] /= sum
                if b[rel_path] > 0.01:
                    a[rel_path] = b[rel_path]
        write_out_pra_fh.write(str(len(a)))
        for rel_path in a:
            write_out_pra_fh.write(" " + str(len(rel_path.split())) + " " + rel_path + " " + str(a[rel_path]))
        write_out_pra_fh.write("\n")
    data_set_fh.close()
    write_out_pra_fh.close()


work("train")
work("test")
