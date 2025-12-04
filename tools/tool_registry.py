# from tools.citation_tools import MLA_Citation_Tool, APA_Citation_Tool
from tools.site_fetcher_tool import SiteFetcherTool
from tools.google_search_tool import GoogleSearchTool
from tools.essay_reader_tool import Essay_Reader_Tool
from tools.bulk_citation_tools import Bulk_APA_Citation_Tool, Bulk_MLA_Citation_Tool
from tools.delegate import Delegate_Tool
from tools.leave_note_tool import Leave_Note_Tool

ALL_TOOLS = [
    Bulk_MLA_Citation_Tool,
    Bulk_APA_Citation_Tool,
    SiteFetcherTool,
    GoogleSearchTool,
    Essay_Reader_Tool,
    Delegate_Tool,
    Leave_Note_Tool
]