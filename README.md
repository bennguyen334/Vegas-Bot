# Vegas-Bot

Github Link:\
https://github.com/bennguyen334/Vegas-Bot
-----
Project Members:\
Arturo Girona\
Benjamin Nguyen\
Bryan Dean\
Hala Benssimmou
-----
Video Link:\
~INSERT VIDEO HERE
-----
Project Description:\
For the group project, we created a Discord bot called VegasBot that simulates a casino experience through the eponymous chat client. To create the bot, we focused on the hikari library due to Discord.py being discontinued.\
VegasBot has three games: slots, poker, and blackjack. These games allow users to bet virtual currency for a chance to gain or lose the amount. As planned, slots is a singleplayer game and poker is multiplayer compatible. Due to time constraints and complexity of existing code, blackjack will remain a singleplayer game.
In addition, there is a command to receive a set amount of currency at a daily rate and another to check current user's balance.\
There is a help command to show all the available commands VegasBot has to offer.\
VegasBot has a database implementation through sqlite3 using setup_db.py. The database consists of three fields: userID, balance, lastcollected. The userID stores each user, the balance stores the amount of currency the user has, and lastcollected is a datetime record for daily command.
-----
A description of the problem you are trying to solve:\
Since the last status report, we encountered an issue involving the combination of code. Moreso, Bryan had a bot prepared for submission, but Benjamin did blackjack on a personal testing bot. Thanks to Arturo, he was able to change the blackjack.py file to work with Bryan's bot.
-----
Any details regarding instructions for the user interface that is beyond the obvious:\
First, invite VegasBot to a Discord server. The invitation link is below.\
insert link here\
Before launching bot.py, first launch setup_db.py for the database.\
Once bot.py launched, the user can access the help command (-help) for all the commands available to them.\
Once a game (slots, poker, blackjack) launches, it should prompt users on what to do.
-----
A list of Python libraries you are using:\
*Hikari\
*Pydealer\
*SQLite3\
*Treys\
*Emojis\
*APScheduler\
*Lib Library includes: random, asyncio, typing, time, os, datetime, logging\
These libraries are the main ones to pip install for the program to work.
-----
A list of other resources:\
Hikari Library GitHub: https://github.com/hikari-py/hikari \
Hikari Library API: https://www.hikari-py.dev/hikari/ \
Pydealer: https://pydealer.readthedocs.io/en/latest/ \
Treys: https://github.com/ihendley/treys \
Emojis: https://pypi.org/project/emoji/ \
APScheduler: https://apscheduler.readthedocs.io/en/3.x/ \

We refer to other links to get started on Hikari:\
https://neonjonn.github.io/hikari-get-started/lightbulb \
https://patchwork.systems/programming/hikari-discord-bot/index.html \
https://youtu.be/5Jz_feIOKjA 
-----
Descriptions of any extra features implemented (beyond the project proposal): 
-----
Include a description of the separation of work:\
Arturo Girona:\
Benjamin Nguyen: Main programmer of blackjack.py. Created the code and graphic user inferface for the game.\
Bryan Dean:\
Hala Benssimmou:
