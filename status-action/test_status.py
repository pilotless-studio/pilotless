# stdlib unittest for weekly issue counts. No network: call() is replaced per test.
# Run: python3 -m unittest discover -s status-action -p 'test_*.py' -v
import contextlib, datetime, importlib.util, io, os, unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def load():
    os.environ.pop('DAYS', None)
    os.environ.pop('GH_REPO', None)
    spec = importlib.util.spec_from_file_location('pilotless_status', os.path.join(HERE, 'status.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def stamp(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def issue(n, created, updated=None, closed=None, pr=False):
    row = {
        'number': n,
        'title': 't' + str(n),
        'created_at': stamp(created),
        'updated_at': stamp(updated or created),
        'closed_at': stamp(closed) if closed else None,
        'html_url': 'https://example.test/' + str(n),
    }
    if pr:
        row['pull_request'] = {'url': 'https://api.github.com/repos/acme/widgets/pulls/' + str(n)}
    return row


class IssueCountTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load()

    def setUp(self):
        self.mod.WARN[:] = []
        self.mod.REPO = 'acme/widgets'
        self.pages = []

        def boom(*a, **k):
            raise AssertionError('unexpected API call')

        self.mod.call = boom

    def inside(self):
        return self.mod.SINCE + datetime.timedelta(hours=1)

    def route(self, pages):
        def fake(path, params=None, method='GET', body=None):
            self.assertIn('/issues', path)
            self.assertEqual(params.get('state'), 'all')
            self.assertEqual(params.get('sort'), 'updated')
            self.assertEqual(params.get('direction'), 'desc')
            self.assertEqual(params.get('per_page'), 100)
            self.assertEqual(params.get('since'), self.mod.SINCE_S)
            n = params.get('page')
            self.pages.append(n)
            if n not in pages:
                raise AssertionError('unexpected page ' + str(n))
            return pages[n]
        self.mod.call = fake

    def test_second_issues_page_is_counted(self):
        mod = self.mod
        inside = self.inside()
        before = mod.SINCE - datetime.timedelta(days=2)
        page1 = [issue(i, inside) for i in range(100)]
        page2 = [
            issue(200, inside),
            issue(201, mod.SINCE),
            issue(202, mod.END),
            issue(203, before, updated=inside, closed=mod.SINCE),
            issue(204, before, updated=mod.END, closed=mod.END),
        ]
        self.route({1: page1, 2: page2})
        text, issues, opened, closed, ok = mod.opened_closed_phrase()
        self.assertTrue(ok)
        self.assertEqual(self.pages, [1, 2])
        opened_ids = [i['number'] for i in opened]
        closed_ids = [i['number'] for i in closed]
        self.assertIn(200, opened_ids)
        self.assertIn(201, opened_ids)
        self.assertNotIn(202, opened_ids)
        self.assertEqual(closed_ids, [203])
        self.assertNotIn(204, closed_ids)
        self.assertEqual(len(opened), 102)
        self.assertEqual(text, '**1 issues closed**, 102 opened')
        self.assertEqual(len(issues), 105)

    def test_pull_requests_are_excluded(self):
        mod = self.mod
        inside = self.inside()
        before = mod.SINCE - datetime.timedelta(days=2)
        self.route({1: [
            issue(1, inside),
            issue(2, before, updated=inside, closed=inside),
            issue(3, inside, closed=inside, pr=True),
            issue(4, before, updated=inside, closed=inside, pr=True),
        ]})
        text, issues, opened, closed, ok = mod.opened_closed_phrase()
        self.assertTrue(ok)
        self.assertEqual([i['number'] for i in opened], [1])
        self.assertEqual([i['number'] for i in closed], [2])
        self.assertEqual([i['number'] for i in issues], [1, 2])
        self.assertEqual(text, '**1 issues closed**, 1 opened')

    def test_stops_early_once_updated_before_since(self):
        mod = self.mod
        inside = self.inside()
        old = mod.SINCE - datetime.timedelta(days=1)
        page2 = [issue(100 + i, inside) for i in range(99)]
        page2.append(issue(199, old, updated=old))
        self.route({
            1: [issue(i, inside) for i in range(100)],
            2: page2,
            3: [issue(300, inside)],
        })
        text, issues, opened, closed, ok = mod.opened_closed_phrase()
        self.assertTrue(ok)
        self.assertEqual(self.pages, [1, 2])
        self.assertEqual(len(opened), 199)
        self.assertNotIn(199, [i['number'] for i in opened])
        self.assertNotIn(300, [i['number'] for i in issues])
        self.assertEqual(text, '**0 issues closed**, 199 opened')

    def test_failed_page_says_issue_data_unavailable(self):
        mod = self.mod
        inside = self.inside()

        def fake(path, params=None, method='GET', body=None):
            self.pages.append(params.get('page'))
            if params.get('page') == 1:
                return [issue(i, inside) for i in range(100)]
            raise RuntimeError('rate limited')

        mod.call = fake
        text, issues, opened, closed, ok = mod.opened_closed_phrase()
        self.assertFalse(ok)
        self.assertEqual(self.pages, [1, 2])
        self.assertEqual(issues, [])
        self.assertEqual(opened, [])
        self.assertEqual(closed, [])
        self.assertIn('issue data unavailable this week', text)
        self.assertFalse(any(ch.isdigit() for ch in text))
        line = mod.summary_line(True, 4, 2, True, 1, False, text)
        self.assertEqual(
            line,
            '**4 commits** by 2 people, **1 PRs merged**, **issue data unavailable this week**.')
        self.assertNotIn('issues closed', line)
        self.assertTrue(mod.WARN)
        mod.OUT = ''
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            mod.main()
        report = buf.getvalue()
        self.assertIn('issue data unavailable this week', report)
        self.assertNotIn('issues closed', report)


if __name__ == '__main__':
    unittest.main()
