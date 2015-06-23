from datetime import datetime, timedelta
import difflib
import os, os.path
import pickle
import string

from context import Context
from model import Subject
from scraper import Scraper
from util import character_whitelist, makedirs


class Store:
    def __init__(self, context=None, enable_http=True,
                 log_http=False, force_refresh=False):

        if context is None:
            context = Context()

        self.__context = context
        self.__enable_http = enable_http
        self.__log_http = log_http
        self.__private_scrapers = {}

        self.__public_scraper = Scraper(
            context=context,
            enable_http=enable_http,
            log_http=log_http,
        )

        self.__journal = Journal(
            context=context,
            force_refresh=force_refresh,
        )

    def add_private_scraper(self, username, password):
        self.__private_scrapers[username] = Scraper(
            context=self.__context,
            enable_http=self.__enable_http,
            log_http=self.__log_http,
            username=username,
            password=password,
        )

    def get_scraper(self, username=None):
        if username is not None:
            if username in self.__private_scrapers:
                return self.__private_scrapers[username]
        else:
            return self.__public_scraper

    def get_terms(self):
        """
        :return: A list of Terms, sorted by chronology in reverse.
        """

        terms = self.__get_terms()

        if terms is not None:
            return terms.list

    def __get_terms(self):

        def scrape():
            source = self.get_scraper().get_terms()
            if source is not None:
                return Terms(source)

        journal = self.__journal.child('terms')

        return journal.get(Terms,
                           shelf_life=timedelta(days=1),
                           alternative=scrape)

    def __get_term_id(self, term=None):
        terms = self.__get_terms()
        if terms is None:
            return None
        if term is None:
            term = terms.list[0]
        return terms.dict[term]

    def get_subjects(self, term=None):
        """
        :return: A list of Subjects, sorted by name.
        """

        subjects = self.__get_subjects(term)

        if subjects is not None:
            return subjects.list

    def __get_subjects(self, term=None):

        term_id = self.__get_term_id(term)

        if term_id is None:
            return None

        def scrape():
            source = self.get_scraper().get_subjects(term_id=term_id)
            if source is not None:
                return Subjects(source)

        journal = self.__journal.child('terms', term_id, 'subjects')

        return journal.get(Subjects,
                           shelf_life=timedelta(days=1),
                           alternative=scrape)

    def find_subject(self, s, term=None):

        subjects = self.__get_subjects(term)

        if subjects is not None:
            return subjects.find(s)

    def __subject_id(self, s, term=None):
        if not isinstance(s, Subject):
            s = self.find_subject(s, term)
        if s is not None:
            return s.get_id()

    def get_courses(self, subject, term=None):

        courses = self.__get_courses(subject, term)

        if courses is not None:
            return courses.source

    def __get_courses(self, subject, term=None):

        term_id = self.__get_term_id(term)

        if term_id is None:
            return None

        subject_id = self.__subject_id(subject)

        if subject_id is None:
            return None

        def scrape():
            source = self.get_scraper().get_courses(
                subject_id=subject_id,
                term_id=term_id,
            )
            if source is not None:
                return Courses(source)

        journal = self.__journal.child('terms', term_id,
                                       'subject', subject_id, 'courses')

        return journal.get(Courses,
                           shelf_life=timedelta(hours=6),
                           alternative=scrape)

    def get_sections(self, course, term=None):

        return list([
            {
                'name': section['name'],
                'crn': section['crn'],
            }
            for section in self.__get_sections(
                subject=course.get_subject(),
                term=term,
            ).source
            if section['course'] == course.get_number()
        ])

    def __get_sections(self, subject, term=None):

        term_id = self.__get_term_id(term)

        if term_id is None:
            return None

        subject_id = self.__subject_id(subject)

        if subject_id is None:
            return None

        def scrape():
            source = self.get_scraper().get_sections(
                subject_id=subject_id,
                term_id=term_id,
            )
            if source is not None:
                return Sections(source)

        journal = self.__journal.child('terms', term_id,
                                       'subject', subject_id, 'sections')

        return journal.get(Sections,
                           shelf_life=timedelta(hours=6),
                           alternative=scrape)

    def get_crn(self, course, section, term=None):

        term_id = self.__get_term_id(term)

        if term_id is None:
            return None

        sections = self.get_sections(course, term)
        matches = list([s['crn'] for s in sections
                        if s['name'].upper() == section.upper()])

        if len(matches) == 1:
            return matches[0]

    def get_section(self, crn, term=None):

        section = self.__get_section(crn, term)

        if section is not None:
            return section.source

    def __get_section(self, crn, term=None):

        term_id = self.__get_term_id(term)

        if term_id is None:
            return None

        def scrape():
            source = self.get_scraper().get_section(
                crn=crn,
                term_id=term_id,
            )
            if source is not None:
                return Section(source)

        journal = self.__journal.child('terms', term_id, 'crn', crn)

        return journal.get(Section,
                           shelf_life=timedelta(minutes=10),
                           alternative=scrape)


_timestamp_format = '%Y-%m-%d-%H-%M-%S-%f'


class Terms:
    def __init__(self, source):
        self.source = source
        self.list = list([t[0] for t in source])
        self.list.sort(reverse=True)
        self.dict = dict(source)

    def dump(self, fp):
        pickle.dump(self.source, fp)

    @staticmethod
    def load(fp):
        return Terms(pickle.load(fp))


class Subjects:
    def __init__(self, source):
        self.source = source
        self.list = list(source)
        self.list.sort(key=lambda x: x.get_name())

    def dump(self, fp):
        pickle.dump(self.source, fp)

    @staticmethod
    def load(fp):
        return Subjects(pickle.load(fp))

    def find(self, s):
        s = s.upper()

        for subject in self.list:
            if s == subject.get_id():
                return subject

        subject_names = list([subject.get_name().upper()
                              for subject in self.list])
        matches = difflib.get_close_matches(s, subject_names, n=1)

        if len(matches) != 0:
            subject_name = matches[0]
            for subject in self.list:
                if subject_name == subject.get_name().upper():
                    return subject


class Courses:
    def __init__(self, source):
        self.source = source

    def dump(self, fp):
        pickle.dump(self.source, fp)

    @staticmethod
    def load(fp):
        return Courses(pickle.load(fp))


class Sections:
    def __init__(self, source):
        self.source = source

    def dump(self, fp):
        pickle.dump(self.source, fp)

    @staticmethod
    def load(fp):
        return Sections(pickle.load(fp))


class Section:
    def __init__(self, source):
        self.source = source

    def dump(self, fp):
        pickle.dump(self.source, fp)

    @staticmethod
    def load(fp):
        return Section(pickle.load(fp))


def _safe_str(x):
    return character_whitelist(
        str(x),
        string.ascii_letters + string.digits + '_-'
    )


class Journal:
    def __init__(self, context, force_refresh, path=None):
        self.__context = context
        self.__force_refresh = force_refresh
        self.__path = path or []
        self.__children = {}
        self.__known = False
        self.__data = None

    def child(self, *path):
        if len(path) == 0:
            return self
        head = _safe_str(path[0])
        if len(head) == 0:
            raise Exception('bad path')
        if path[0] not in self.__children:
            self.__children[head] = Journal(
                context=self.__context,
                force_refresh=self.__force_refresh,
                path=self.__path + [head],
            )
        return self.__children[path[0]].child(*path[1:])

    def dir(self):
        d = os.path.join(
            self.__context.get_config_dir(),
            'cache',
            os.path.join(*self.__path)
        )
        makedirs(d)
        return d

    def __filename(self):

        def is_file(f):
            full_filename = os.path.join(self.dir(), f)
            return os.path.isfile(full_filename)

        # List the files in this Journal's directory.
        files = filter(is_file, os.listdir(self.dir()))

        # The most recent file has the highest lexicographical name.
        if len(files) != 0:
            return max(files)

    def __know(self, data):
        self.__data = data
        self.__known = True

    def put(self, data):

        self.__know(data)
        now = datetime.utcnow()
        filename = os.path.join(self.dir(), now.strftime(_timestamp_format))

        self.__context.get_logger().info('Dump\n%s' % filename)

        fp = open(filename, 'w')
        try:
            data.dump(fp)
        finally:
            fp.close()

    def get(self, type_, shelf_life, alternative):

        # If data is cached in memory, always use that. Store objects
        # are intended to be used ephemerally, so we do not anticipate
        # any need to look up the same information more than once.
        if self.__known:
            return self.__data

        # Memoize the alternative function; we might call it twice.
        alternative = Memo(alternative)

        # If refresh is forced, immediately attempt to use the alternate.
        if self.__force_refresh:
            a = alternative()
            if a is not None:
                self.put(a)
                return a

        # Look in the directory to find a sufficiently recent file.
        filename = self.__filename()

        def fresh_file_exists():
            if filename is None:
                return False
            then = datetime.strptime(filename, _timestamp_format)
            age = datetime.utcnow() - then
            return age < shelf_life

        # If a recent file does not exist, attempt to use the alternate.
        if not fresh_file_exists():
            a = alternative()
            if a is not None:
                self.put(a)
                return a

        # If some file exists, use it.
        if filename is not None:
            full_filename = os.path.join(self.dir(), filename)
            self.__context.get_logger().info('Load\n%s' % full_filename)
            fp = open(full_filename, 'r')
            try:
                data = type_.load(fp)
            finally:
                fp.close()
            self.__know(data)
            return data

        # Alternate and file approaches have both failed.
        self.__know(None)


class Memo:
    """
    Memoizes a value function.
    """

    def __init__(self, fn):
        self.__fn = fn
        self.__value = None
        self.__executed = False

    def __call__(self):
        if self.__executed:
            return self.__value

        value = self.__fn()
        self.__fn = None
        self.__value = value
        self.__executed = True
        return value
