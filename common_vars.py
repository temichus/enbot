import telepot
inport os
TOKEN = os.environ['TOKEN']
bot = telepot.Bot(TOKEN)

sql_path = "/sql/my_db.sqlite"


name_key = "name"
jira_status_key = "jira_status"
