#-*- coding: UTF-8 -*-
import itertools
import re
from taiwan import *
from chinese import *
from korean import *
from nicknames import *


asian_units = taiwan_units.union(chinese_units)
asian_last_names = korean_last_names.union(taiwan_last_names.union(chinese_last_names))
nickname_set = set()
for name_group in nicknames:
    for name1 in name_group:
        for name2 in name_group:
            if name1 != name2:
                nickname_set.add((name1, name2))
                nickname_set.add((name2, name1))


def is_asian_name(last_name):
    if last_name in asian_last_names:
        return True
    else:
        return False


class Name:
    """Represent a name with its alternatives and authors.

    Attributes:
        name: a string describing the name.
            e.g., "Michael Jordan".
        first_name: a string describing the first name.
        middle_name: a string describing the middle name.
        last_name: a string describing the last name.
        alternatives: a set of all possible names.
            e.g., "Michael I. Jordan" or "M. Jordan".
        author_ids: a set of all author ids with the exact same name.
        similar_author_ids: a set of all author ids with similar names.
    """

    def get_initials(self):
        initials = ''
        elements = self.name.split(' ')
        for element in elements:
            if len(element) >= 1:
                initials += element[0]
        return initials

    def __name_process(self, name, mode=1):

        # In case of M.I. Jordan
        name = name.replace('?', '').lower().strip()
        # replace M.I. to M I.
        name = re.sub('([a-zA-Z]+)(\.)([a-zA-Z]+)', '\g<1> \g<3>', name)
        # replace M I. to M I

        # remove all  non [a-zA-Z] characters
        # eable this and try again
        name = re.sub('[^a-zA-Z ]', '', name)

        name = ' '.join(name.split())

        (first_name, middle_name, last_name) = self.__split_name(name)

        if mode == 1:
            self.first_name = first_name
            self.middle_name = middle_name
            self.last_name = last_name
            self.name = ' '.join([first_name, middle_name, last_name]).strip()
            self.name = ' '.join(self.name.split())
            return self.name
        else:
            s = ' '.join([first_name, middle_name, last_name]).strip()
            return ' '.join(s.split())


    def __init__(self, name, quick=False):
        """Initialize the instance with a name.

        Parameters:
            name: The name read from the csv file, could be noisy.
        """
        if name.find('.') >= 0:
            self.has_dot = True
        else:
            self.has_dot = False

        if name.find('-') >= 0:
            self.has_dash = True
        else:
            self.has_dash = False

        if is_asian_name(name.strip().lower().split(' ')[-1]):
            self.is_asian = True
            self.__name_process(name.replace('.', ' ').replace('-', ''), 1)
        else:
            self.is_asian = False
            self.__name_process(name.replace('.', ' ').replace('-', ' '), 1)
        if not quick:
            self.alternatives = set()
            self.author_ids = set()
            self.similar_author_ids = set()
            self.add_alternative(self.__name_process(name.replace('.', '').replace('-', ''), 2))
            self.add_alternative(self.__name_process(name.replace('.', '').replace('-', ' '), 2))
            self.add_alternative(self.__name_process(name.replace('.', '').replace('-', ' '), 2))
            self.add_alternative(self.__name_process(name.replace('.', ' ').replace('-', ' '), 2))
            self.initials = self.get_initials()

    def __split_name(self, name):
        """Split a name into first, middle and last names."""
        tokens = name.split(' ')
        suffix = ['jr', 'sr']
        suffix2 = ['i', 'ii', 'iii', 'iv', 'v', 'first', 'second', 'third']
        elements = [token for token in tokens if token not in suffix]
        if len(elements) > 0 and elements[-1] in suffix2:
            del elements[-1]
        if len(elements) > 0 and elements[-1] in suffix2:
            del elements[-1]

        if len(elements) > 0:
            first_name = elements[0].strip()
        else:
            first_name = ''

        if len(elements) > 1:
            last_name = elements[-1].strip()
        else:
            last_name = ''

        if len(elements) > 2:
            middle_name = ' '.join(elements[1:-1]).strip()
        else:
            middle_name = ''

        # Given 'jia-lu liu' or 'jia lu liu', generate 'jialu liu'
        if self.is_asian:
            if len(middle_name) > 1 and middle_name.find(' ') < 0 and not self.has_dot and not self.has_dash:
                first_name = (first_name + middle_name).replace(' ', '')
                middle_name = ''
        #     elements = first_name.split(' ')
        #     while True:
        #         pos = -1
        #         for i in xrange(len(elements) - 1):
        #             # print elements
        #             if elements[i] in asian_units:
        #                 k = i
        #                 while k + 1 < len(elements):
        #                     if elements[k + 1] in asian_units:
        #                         k = k + 1
        #                         pos = i
        #                     else:
        #                         break
        #                 new_element = elements.pop(i)
        #                 while k - i > 0:
        #                     new_element += elements.pop(i)
        #                     k -= 1
        #                 elements.insert(i, new_element)
        #                 break
        #         if pos == -1:
        #             break
        #     first_name = elements[0]
        #     if len(elements) > 1:
        #         middle_name = ' '.join(elements[1:])
        #     else:
        #         middle_name = ''
        return (first_name, middle_name, last_name)


    def __shorten_string(self, string):
        """Find initial of a string.

        Parameters:
            string: Input string to find initial.

        Returns:
            The initial character.
        """
        if not string:
            return ''
        else:
            return string[0]

    def __genearte_possible_names(self, (first_name, middle_name, last_name)):
        """Generate all possible names give the full name.

        Parameters:
            (first_name, middle_name, last_name): A tuple composed of
                first, middle and last names.
        Returns:
            A set of all possible names.
        """
        candidates = set()

        if len(first_name) == 0 and len(middle_name) == 0 and len(last_name) == 0:
            candidates.add('')
            return candidates

        #e.g., Michael Jr. Jordan
        candidates.add(' '.join([first_name, middle_name, last_name]).strip())
        #e.g., Michael Jordan
        candidates.add(' '.join([first_name, '', last_name]).strip())
        #e.g., M. Jordan
        candidates.add(' '.join([self.__shorten_string(first_name), '',
                                 last_name]).strip())
        # #e.g., M. J.
        # candidates.add(' '.join(
        #                [self.__shorten_string(first_name),
        #                '',
        #                self.__shorten_string(last_name)]
        #                ))
        # e.g., Michael J. Jordan
        candidates.add(' '.join(
                       [first_name,
                       self.__shorten_string(middle_name),
                       last_name]
                       ).strip())
        #e.g., M. J. Jordan
        candidates.add(' '.join(
                       [self.__shorten_string(first_name),
                       self.__shorten_string(middle_name),
                       last_name]
                       ).strip())

        candidates_new = set()
        for candidate in candidates:
            candidates_new.add(' '.join(candidate.split()))
        # #e.g., M. J. J.
        # candidates.add(' '.join(
        #                [self.__shorten_string(first_name),
        #                self.__shorten_string(middle_name),
        #                self.__shorten_string(last_name)]
        #                ))

        #####################################################
        # Further improvements: alternatives like Mike

        return candidates_new

    def __generate_all_possible_names(self):
        """Generate all possible names considering all possible permutations.

        Note: compared to generate_possbile_names, this function additionally
            covers the permutations of first, middle and last names.

        Returns:
            A set of all possible names.
        """
        self.alternatives.add(self.name.strip())
        if len(self.first_name) == 0 and len(self.middle_name) == 0 and len(self.last_name) == 0:
            return self.alternatives
        pool = [self.first_name, self.middle_name, self.last_name]
        self.alternatives = self.alternatives.union(self.__genearte_possible_names(pool))
        # for permutation in itertools.permutations(pool):
        #     self.alternatives = self.alternatives.union(
        #         self.__genearte_possible_names(permutation))
        # self.alternatives = self.alternatives.difference(set([self.name]))
        return self.alternatives

    def get_alternatives(self):
        """Get all possible names.

        Note: This function will call generate_all_possible_names automatically
            if self.alternatives is empty.

        Returns:
            A set of all possible names.
        """
        self.__generate_all_possible_names()
        return self.alternatives

    def add_alternative(self, alternative):
        self.alternatives.add(alternative)

    def add_author_id(self, author_id):
        """Add author_id which matches the name into set author_ids.

        Parameters:
            author_id: Id of the author.
        """
        self.author_ids.add(author_id)

    def add_similar_author_id(self, author_id):
        """Add author_id which has similar name into set similar_author_ids.

        Parameters:
            author_id: Id of the author.
        """
        self.similar_author_ids.add(author_id)
