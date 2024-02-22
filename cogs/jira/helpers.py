from jira import JIRA
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv('JIRA_EMAIL')
TOKEN = os.getenv('JIRA_TOKEN')
SERVER = os.getenv('JIRA_SERVER')
PROJECT = os.getenv('JIRA_PROJECT')
auth_jira = JIRA(basic_auth=(EMAIL, TOKEN), options={'server': SERVER})

def get_all_issues(max_results=50):
    return auth_jira.search_issues(f'project={PROJECT}', maxResults=max_results)