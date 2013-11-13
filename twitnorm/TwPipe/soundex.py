# http://wwwhomes.uni-bielefeld.de/gibbon/Forms/Python/SEARCH/soundex.html
import re
def soundex(name):
#Render as upper case
    name = name.upper()

    # Separate
    first = name[0]
    rest = name[1:]
    #Remove punctuation

    rest = rest.upper()
    rest = re.sub("[.,:;-]",'',rest)

    #1. Perform numerical substitutions for consonants
    # ***(h, w, y missing in Bird NLTK version)***
    rest = re.sub('[AEIOUHWY]','',rest)
    rest = re.sub("'",'',rest)
    rest = re.sub('[BFPV]','1',rest)
    rest = re.sub('[CGJKQSXZ]','2',rest)
    rest = re.sub('[DT]','3',rest)
    rest = re.sub('[L]','4',rest)
    rest = re.sub('[MN]','5',rest)
    rest = re.sub('[R]','6',rest)

    #2. Collapse adjacent identical digits
    rest = rest+'_'
    newstring = ''
    for n in range(len(rest)-1):
        if rest[n] != rest[n+1]:
            newstring = newstring+rest[n]
    rest = newstring
    #3. Remove non-digits
    rest = re.sub('\D','',rest)

    #4. Right-pad with zeroes, keep 1st 3 digits
    rest = rest+"000"
    rest = rest[:3]

    # Restore first letter
    soundexresult = first+rest
    return soundexresult
