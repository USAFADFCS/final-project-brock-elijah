from tests.test_search import test_search
from tests.test_fetch import test_fetch
from tests.test_cite import test_apa, test_mla
from tests.test_api_functs import test_api_functs

TESTS_TO_DO = {
    "search" : False,
    "fetch" : True,
    "mla" : False,
    "apa" : False,
    "api" : False
}


def do_all_tests():
    if TESTS_TO_DO["search"]:
        test_search()
    if TESTS_TO_DO["fetch"]:
        test_fetch()
    if TESTS_TO_DO["mla"]:
        test_mla()
    if TESTS_TO_DO["apa"]:
        test_apa()
    if TESTS_TO_DO["api"]:
        test_api_functs()

