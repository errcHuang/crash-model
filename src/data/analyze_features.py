from . import util
import argparse
import os
import json
from collections import OrderedDict
import numpy as np

DATA_FP = None


def get_bin(value, bins):
    return_val = 0
    if not value:
        return return_val
    return_val = 1
    for i, bin in enumerate(bins):
        if bin > value:
            return i + 1

    return len(bins) + 1

def analyze(years=[2016]):

    crash_file = os.path.join(DATA_FP, 'processed', 'crash_joined.json')
    with open(crash_file, "r") as f:
        items = json.load(f)

    crash_data, crashes = util.group_json_by_location(
        items,
        years=years,
        yearfield='dateOccurred')
    
    non_inter_segments = util.read_geojson(
        os.path.join(MAP_FP, 'non_inters_segments.geojson'))
    with open(os.path.join(
            DATA_FP, 'processed', 'inters_data.json'), "r") as f:
        inter_segments = json.load(f)

    # Start by just hard-coding features we want to look at
    feat_values = []
    crash_info = []
    crash_info_no_count = []
    use_feats = OrderedDict([
        # bridge has yes or null value; consider using eventually
        # ('bridge', {'values': []}),
        # junction can have value 'roundabout'; consider using eventually
        # ('junction', {'values': []}),
        ('inter', {'values': []}),
        ('lanes', {'values': []}),
        ('length', {'values': [], 'bins': [50, 100, 200]}),
        ('oneway', {'values': []}),
        ('width', {'values': []}),
        ('hwy_type', {'values': []}),
        # ('dead_end', {'values': []}),
        ('parking_tickets', {'values': [], 'bins': [100]}),
        ('signal', {'values': []}),
        ('crosswalk', {'values': []}),
        ('osm_speed', {'values': []}),
        ('intersection_segments', {'values': []}),
        ('width_per_lane', {'values': [], 'bins': [5, 10, 20]})
    ])
    # Turn inter segments into similar format to non inters
    updated_inter_segments = []
    for segment_id in list(inter_segments.keys()):
        segment = inter_segments[segment_id]
        segment[0]['id'] = segment_id
        updated_inter_segments.append(('', segment[0]))

    for segment in non_inter_segments + updated_inter_segments:
        if segment[1]['id'] in crashes:
            crash_info.append(
                crashes[segment[1]['id']]['count'])
            crash_info_no_count.append(1)
        else:
            crash_info.append(0)
            crash_info_no_count.append(0)
        for feat in use_feats:
            if feat in segment[1] and segment[1][feat]:

                # For now, the only string should be length
                if type(segment[1][feat]) == str:
                    segment[1][feat] = round(float(segment[1][feat]))

                if 'bins' in use_feats[feat]:
                    use_feats[feat]['values'].append(get_bin(
                        segment[1][feat], use_feats[feat]['bins']))
                else:
                    use_feats[feat]['values'].append(round(segment[1][feat]))
            else:
                use_feats[feat]['values'].append(0)

    m = [crash_info] + [crash_info_no_count] + [
        x['values'] for x in use_feats.values()]
    result = np.corrcoef(m)
    print(result[0])
    print(result[1])
#    import ipdb; ipdb.set_trace()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--datadir", type=str,
                        help="Can give alternate data directory")
    args = parser.parse_args()
    DATA_FP = args.datadir
    MAP_FP = os.path.join(DATA_FP, 'processed', 'maps')
    analyze()
