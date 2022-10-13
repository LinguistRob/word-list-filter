import csv
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re

def create_new_list_file(tl):
    """
    Takes a language name, runs get_unmatched_words()
    and saves the result to a new file with the name 'new_{language}_WordList.tsv'
    """
    global language
    language = tl
    unmatched_words = get_unmatched_words()
    with open(f"new_{language}_WordList.tsv", 'w') as new_file:
        tsv_writer = csv.writer(new_file, delimiter='\t')
        for word in unmatched_words:
            tsv_writer.writerow([word])


def get_word_list():
    """
    Reads the '{language}_WordList.tsv' file and returns the list of words minus the header row
    """
    word_list = []
    with open((language + '_WordList.tsv'), 'r') as wl_file:
        for row in wl_file:
            word_list.append(row.strip('\n'))
        return word_list[1:]


def get_target_item_list():
    """
    Reads a list of target items in a .tsv file named with the format:
        {language}_TargetItems.tsv      (e.g. italian_TargetItems.tsv)
    It then takes the first column of each row, adds it to a list.
    """
    target_item_list = []
    with open((language + '_TargetItems.tsv'), 'r') as ti_file:
        rd = csv.reader(ti_file, delimiter="\t", quotechar='"')
        for row in rd:
            target_item_list.append(row[0])
    target_item_list = target_item_list[1:]  # set the list equal to all rows minus the header row
    return clean_target_items(target_item_list)


def clean_target_items(ti_list):
    """
    Takes a list of target items and returns the list with the strings cleaned
    """
    clean_list = []
    if language == 'korean' or language == 'japanese':
        for item in ti_list:
            item_no_punctuation = re.sub('\W+', ' ', item)
            if item_no_punctuation != '':
                clean_list.append(item_no_punctuation)
    else:
        for item in ti_list:
            item_no_semicolon = get_str_before_semicolon(item)
            item_no_apostrophe = get_str_after_apostrophe(item_no_semicolon)
            item_no_punctuation = re.sub('\W+', ' ', item_no_apostrophe)
            item_no_stopwords_list = [word for word in word_tokenize(item_no_punctuation, language) if not is_stopword(word)]
            clean_item = ' '.join(item_no_stopwords_list)
            # print(item, "\n>> ", clean_item, "\n----------------\n")
            if clean_item != '':
                clean_list.append(clean_item)
    return clean_list


def get_str_before_semicolon(item):
    """
    If the item contains a semicolon, return only the text before the semicolon
    """
    if "; " in item:
        new_item = item.split("; ")[0]
        # print("Changed ", item, " to ", new_item)
        return new_item
    return item


def get_str_after_apostrophe(item):
    """
    Checks it the language is FR or IT and returns the string after the apostrophe,
    this is to exclude words like " l' " or " d' " in French and Italian
    """
    if "'" in item and (language == 'italian' or language == 'french'):
        new_item = item.split("'")[1]
        # print(f'Changed "{item}"  to  "{new_item}"')
        return new_item
    return item


def get_unmatched_words():
    """
    Takes a language name and returns a list of words
    from the corresponding word list that don't have matches in
    either the stopwords or of the list of target items for that language
    """
    word_list = get_word_list()
    target_item_list = get_target_item_list()
    unmatched_words = []
    removed_stopwords = []
    removed_target_items = []
    removed_proper_nouns = []

    for word in word_list:
        if language == 'korean' or language == 'japanese':
            if is_target_item(word, target_item_list):
                removed_target_items.append(word)
            else:
                unmatched_words.append(word)
        else:
            if is_stopword(word):
                removed_stopwords.append(word)
            elif is_target_item(word, target_item_list):
                removed_target_items.append(word)
            # elif is_proper_noun(word):
            #     removed_proper_nouns.append(word)
            else:
                unmatched_words.append(word)
    all_removed_words = removed_target_items + removed_stopwords + removed_proper_nouns
    print(f"-------------\n{language.upper()}\nFound {len(unmatched_words)} unmatched words in {language.title()} from the list of {len(word_list)} words")
    print(f"""
Removed {len(all_removed_words)} words from the word list
>> {len(removed_stopwords)} were stopwords:
    {removed_stopwords}
>> {len(removed_proper_nouns)} were proper nouns:
    {removed_proper_nouns}
>> {len(removed_target_items)} already exist in CAS:
    {removed_target_items}
    """)
    # print("Words matched to existing items in CAS:")
    # print(removed_target_items)
    # print("Proper nouns removed:")
    # print(removed_proper_nouns)
    return unmatched_words


def is_proper_noun(word):
    """
    Returns True if the given word is a proper noun
    """
    word_as_list = [word]
    tagged_word = nltk.pos_tag(word_as_list)
    if tagged_word[0][1] == 'NNP':
        return True
    return False


def is_stopword(word):
    """
    Checks a word against list of stopwords from the NLTK corpus
    Returns True if the word checked matches any of the stopwords
    """
    stop_words = stopwords.words(language)
    if word in stop_words:
        return True
    return False


def is_target_item(word, target_item_list):
    """
    Checks a word against the target item list and returns True if it is a target item
    """
    if word in target_item_list:
        return True
    return False


# We iterate over the languages list to run the task for each prepared document in all languages
# The files should be in the following formats:
# '{language}_WordList.tsv'   and    '{language}_TargetItems.tsv'
languages = ['italian',
             'english',
             'spanish',
             'french',
             'german',
             'russian',
             'korean',
             'japanese']

for lang in languages:
    create_new_list_file(lang)
