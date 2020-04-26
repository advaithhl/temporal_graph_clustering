from tgcd.community_detector import find_all_communities
from tgcd.converter import convert_all
from tgcd.data_splitter import split_dataset

if __name__ == '__main__':
    print('Splitting dataset with parts of 1 day each')
    split_dataset()
    print('\nCreating temporal graphs of each part and converting to static')
    convert_all()
    print('\nProceeding to find communities')
    find_all_communities()
