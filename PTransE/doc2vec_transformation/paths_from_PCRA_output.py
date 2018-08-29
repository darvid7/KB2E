import os
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-p", "--path")
parser = parser.parse_args()

print(os.getcwd())
# PCRA_OUTPUT_PATH = "../data/train_pra_sample_1000_lines.txt"

paths = []

with open(parser.path, "r") as fh:
    header_toggle = True
    for line in fh:
        line = line.split()
        if header_toggle:
            entity_1_mid, entity_2_mid, relation_id_as_str = line
            header_toggle = False
        else:
            num_relation_paths = int(line[0])
            cur_index = 1
            for i in range(num_relation_paths):
                # For each relation count, relation path, confidence level.
                relation_count = int(line[cur_index])
                relations_on_path = []

                cur_index += 1
                for r in range(relation_count):
                    # relations_on_path_count = int(line[cur_index])
                    # cur_index += 1
                    # for j in range(relations_on_path_count):
                    relations_on_path.append(line[cur_index])
                    cur_index += 1
                # Skip over confidence.
                cur_index += 1
                if relation_count == 1:
                    path = "%s %s %s"
                    paths.append(path % (entity_1_mid, relations_on_path[0], entity_2_mid))
                elif relation_count == 2:  # Relation count == 2, shouldn't be any other options.
                    path = "%s %s missing_intermediate_entity %s %s"
                    paths.append(path % (entity_1_mid, relations_on_path[0], relations_on_path[1], entity_2_mid))
                else:
                    print("WTF")

            header_toggle = True
for path in paths:
    print(path)


