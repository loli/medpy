# Simple script that serves to extract the results separated by apical, mid and basal slices

# code
def main():
    filename = "/home/omaier/Experiments/GraphCut/Miccai12/14Cut2DTime/11evaluation/_ImageResults.txt"
    
    time_offset = 20
    ctype_searched = 'i'
    
    ed_found = False
    es_found = False
    ed_slice_counter = 0
    es_slice_counter = 0
    current_patient = False
    
    ed_base = {'dm': [], 'hd': []}
    ed_mid = {'dm': [], 'hd': []}
    ed_apex = {'dm': [], 'hd': []}
    
    es_base = {'dm': [], 'hd': []}
    es_mid = {'dm': [], 'hd': []}
    es_apex = {'dm': [], 'hd': []}
    
    with open(filename, 'r') as f:
        for line in f.readlines():
            name, dm, hd = line.strip().split(' ')
            patient, slice_no, ctype = name.split('-')
            slice_no = int(slice_no)
            
            if not ctype == ctype_searched:
                continue
            
            if not patient == current_patient:
                sorting = read_patient_file(patient[1:], ctype_searched, time_offset)
                current_patient = patient
                
            if slice_no in sorting[0][0]:
                ed_base['dm'].append(float(dm))
                ed_base['hd'].append(float(hd))
            elif slice_no in sorting[0][1]:
                ed_mid['dm'].append(float(dm))
                ed_mid['hd'].append(float(hd))
            elif slice_no in sorting[0][2]:
                ed_apex['dm'].append(float(dm))
                ed_apex['hd'].append(float(hd))
            elif slice_no in sorting[1][0]:
                es_base['dm'].append(float(dm))
                es_base['hd'].append(float(hd))
            elif slice_no in sorting[1][1]:
                es_mid['dm'].append(float(dm))
                es_mid['hd'].append(float(hd))
            elif slice_no in sorting[1][2]:
                es_apex['dm'].append(float(dm))
                es_apex['hd'].append(float(hd))
            else:
                print(sorting)
                raise Exception('Failed on line {}.'.format(line))
            
    # padd all lists
    max_length = max(len(ed_base['dm']),
                     len(ed_base['hd']),
                     len(ed_mid['dm']),
                     len(ed_mid['hd']),
                     len(ed_apex['dm']),
                     len(ed_apex['hd']),
                     len(es_base['dm']),
                     len(es_base['hd']),
                     len(es_mid['dm']),
                     len(es_mid['hd']),
                     len(es_apex['dm']),
                     len(es_apex['hd']))
    ed_base['dm'] = ed_base['dm'] + [''] *  (max_length - len(ed_base['dm']))
    ed_base['hd'] = ed_base['hd'] + [''] *  (max_length - len(ed_base['hd']))
    ed_mid['dm'] = ed_mid['dm'] + [''] *  (max_length - len(ed_mid['dm']))
    ed_mid['hd'] = ed_mid['hd'] + [''] *  (max_length - len(ed_mid['hd']))
    ed_apex['dm'] = ed_apex['dm'] + [''] *  (max_length - len(ed_apex['dm']))
    ed_apex['hd'] = ed_apex['hd'] + [''] *  (max_length - len(ed_apex['hd']))
    es_base['dm'] = es_base['dm'] + [''] *  (max_length - len(es_base['dm']))
    es_base['hd'] = es_base['hd'] + [''] *  (max_length - len(es_base['hd']))
    es_mid['dm'] = es_mid['dm'] + [''] *  (max_length - len(es_mid['dm']))
    es_mid['hd'] = es_mid['hd'] + [''] *  (max_length - len(es_mid['hd']))
    es_apex['dm'] = es_apex['dm'] + [''] *  (max_length - len(es_apex['dm']))
    es_apex['hd'] = es_apex['hd'] + [''] *  (max_length - len(es_apex['hd']))
    
    # iterate and print
    print()
    print('ED;;;;;;ES')
    print('base;;mid;;apex;;base;;mid;;apex')
    print('DM;HM;DM;HM;DM;HM;DM;HM;DM;HM;DM;HM')
    for idx in range(max_length):
        print('{};{};{};{};{};{};{};{};{};{};{};{}'.format(
                        ed_base['dm'][idx],
                        ed_base['hd'][idx],
                        ed_mid['dm'][idx],
                        ed_mid['hd'][idx],
                        ed_apex['dm'][idx],
                        ed_apex['hd'][idx],
                        es_base['dm'][idx],
                        es_base['hd'][idx],
                        es_mid['dm'][idx],
                        es_mid['hd'][idx],
                        es_apex['dm'][idx],
                        es_apex['hd'][idx]))
    
def read_patient_file(patient, ctype_searched, time_offset):
    
    pf = '/home/omaier/Experiments/GraphCut/Miccai12/14Cut2DTime/50reference/patient{}/P{}list.txt'.format(patient, patient)
    
    collection = {'ed': [], 'es': []}
    ed_slice_counter = False
    
    # collect slices
    with open(pf, 'r') as f:
        for line in f.readlines():
            _, _, slice_no, ctypename, _ = line.split('-')
            slice_no = int(slice_no)
            
            if not ctypename[0] == ctype_searched: continue
            
            if not ed_slice_counter:
                ed_slice_counter = slice_no
                collection['ed'].append(slice_no)
                continue
            
            if slice_no == ed_slice_counter + time_offset:
                ed_slice_counter = slice_no
                collection['ed'].append(slice_no)
                continue
            
            # else
            collection['es'].append(slice_no)
    
    # padd es list from the left
    offset = collection['es'][0] - collection['ed'][0]
    for slice_no in collection['ed']:
        if slice_no + offset not in collection['es']:
            collection['es'] = [False] + collection['es']
            
    # padd es list from the right
    collection['es'] = collection['es'] + [False] * (len(collection['ed']) - len(collection['es']))
    
    # split according to base (3), mid(?) and appex(3) and return
    ed = (collection['ed'][:3], collection['ed'][3:-3], collection['ed'][-3:])
    es = (collection['es'][:3], collection['es'][3:-3], collection['es'][-3:])
    
    #print 'Patient {} mid count = {}.'.format(patient, len(ed[1]))
    print(len(ed[1]), ';', end=' ') 
    return ed, es 
    
if __name__ == "__main__":
    main()