from aiogram.types import BotCommand

private = [
    BotCommand(command='start', description='STARTa'),
    BotCommand(command='sub', description='my subscription'),
    BotCommand(command='test', description='test')
]

# private = BotCommand(command='start', description='START')


# await ctx.setChatMenuButton(JSON.stringify({
#    type: 'web_app',
#    text: '🕹️ Open app',
#    web_app: { url: "your_game_url" }
#  }))