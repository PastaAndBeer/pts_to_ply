import re
import sys
import argparse

SUPPORTED_FORMATS = ['.pts' , '.ply']
PROGRESS_STEP = 1000

class CONVERSION_DIRECTION(object):
    PTS_TO_PLY = 0
    PLY_TO_PTS = 1


COORDS_ROW_REGEX = re.compile(
    r'(-)?(\d+\.\d+ \d+\.\d+ \d+\.\d+) (\d+ \d+ \d+ \d+)')

# PLY to PTS
REGEX_NUM_VERTICES = re.compile(r"element vertex (?P<num>\d+)")
REGEX_PLY_PROPERTY = re.compile(r"property (\w+) (?P<pname>[a-zA-z]+)")
REGEX_PLY_LIST_PROPERTY = re.compile(r"property list (\w+) (\w+) (?P<pname>[a-zA-z]+)")
DEFAULT_PTS_INTENSITY_VALUE = "100"
DEFAULT_PTS_PROPERTY_VALUE = "255"

# PTS to PLY
PLY_HEADER_TEMPLATE = """ply
format ascii 1.0
element vertex /total_vertices/
comment /optional_comment/
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
"""

def pts_to_ply(in_path, out_path, comment=None, signals=None):
    i = 0
    total_lines_num = None
    output_file = open(out_path, 'a')

    with open(in_path, 'r') as f:
        for line in f:
            if i % PROGRESS_STEP == 0:
                if signals:
                    signals.progress.emit(i)
            # First line contains number of points
            if i == 0:
                total_lines = str(line)
                print('total lines: {}\n'.format(total_lines))
                header = PLY_HEADER_TEMPLATE.replace('/total_vertices/', total_lines)
                if comment:
                    header = header.replace('/optional_comment/', comment)
                else:
                    header = header.replace('/optional_comment/',
                                            "export ply from pts "
                                            "using python (by vvz3n)")
                output_file.write(header)

                try:
                    total_lines_num = int(total_lines.strip().replace(
                        '\n', ''))
                    if signals:
                        signals.started.emit(total_lines_num)
                except ValueError:
                    if signals:
                        signals.failed.emit(
                            'Header of file does not contain total vertices number'
                        )
                    return
            else:
                if i % PROGRESS_STEP == 0:
                    # sys.stdout.write('\r{} / {}'.format(i, total_lines))
                    pass
                xyz_values = ' '.join(line.split(' ')[:3])
                rgb_values = ' '.join(line.split(' ')[4:])
                new_ply_line = '{xyz} {rgb}'.format(
                    xyz=xyz_values, rgb=rgb_values)
                output_file.write(new_ply_line)
                
            i += 1
            
        sys.stdout.write('written {} lines!\n'.format(i))
        output_file.close()
        
        
if __name__ == '__main__':
    usage = 'Usage: python3 pts_to_ply.py --pts [input_pts_path] --ply [output_ply_path]'
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument('--pts', type=str)
    parser.add_argument('--ply', type=str)
    args = parser.parse_args()
    
    try:
        pts_to_ply(args.pts, args.ply)
        print('Done')
    except TypeError:
            print(usage)

    # pts_to_ply(args.pts, args.ply)
