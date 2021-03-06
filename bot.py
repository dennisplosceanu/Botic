from enum import Enum
from random import randint
import os
import subprocess
import asyncio
import youtube_dl
import utils
from subprocess import STDOUT
from queue import Queue
from player import Player


class Cmd(Enum):
    HELLO    = 'hello'
    HELP     = 'help'
    FLIP     = 'flip'
    BOT_SRC  = 'botsrc'
    # SHELL    = 'shell'
    PLAY     = 'play'
    SKIP     = 'skip'

class Bot:
    MAX_COMMAND_SIZE = 20

    COMMANDS = [Cmd.HELLO, Cmd.HELP, Cmd.FLIP, Cmd.BOT_SRC, Cmd.PLAY, Cmd.SKIP]

    COMMANDS_DESCRIPTION = {
            Cmd.HELLO: 'Responds by saying hello to you.',
            Cmd.FLIP:  'Flips a coin.',
            Cmd.HELP:  'Prints this info message.',
            Cmd.BOT_SRC: 'Prints the source code of the Bot class',
            Cmd.PLAY : 'Play music from youtube',
            Cmd.SKIP : 'Skip the current song in the queue',
            # Cmd.SHELL:   'Run a shell command'
    }

    def __init__(self, client, prefix):
        self.prefix = prefix
        self.client = client
        self.players = {}

    def log(self, message):
        server  = message.server.name
        channel = message.channel.name
        content = message.content
        author = message.author.name

        path = server
        if not os.path.exists(path):
            os.makedirs(path)

        path += "/" + channel + "_log.txt"
        with open(path, 'a+', encoding = 'utf-8') as f:
            f.write(author + ": " + content + "\n")

    async def run(self, message):
        content = message.content
        server = message.server
        channel = message.channel
        author = message.author

        if author == self.client.user:
            return

        self.log(message)

        if content[0:1] != self.prefix:
            return

        args = content.split(' ')
        command = args[0][1:]

        if command == Cmd.HELP.value:
            await self.help(channel)
        elif command == Cmd.HELLO.value:
            await self.hello(channel, author)
        elif command == Cmd.FLIP.value:
            await self.flip(channel, author)
        elif command == Cmd.BOT_SRC.value:
            await self.bot_src(channel)
        elif command == Cmd.PLAY.value:
            voice_channel = author.voice.voice_channel
            if len(args) > 1:
                await self.play(server, channel, voice_channel, " ".join(args[1:]).strip())
        elif command == Cmd.SKIP.value:
            await self.skip(server, channel)
        # elif command == Cmd.SHELL.value:
            # if len(args) > 1:
                # await self.shell(channel, " ".join(args[1:]))
        else:
            await self.invalid_command(channel)

    async def hello(self, channel, author):
        msg = 'Hello {0.mention}'.format(author)

        await utils.send_message(self.client, channel, msg)

    async def flip(self, channel, author):
        if author.name == 'mihaid':
            msg = "Muie Miță! :))))))))))))))))))))"
        else:
            if randint(0, 1) == 0:
                msg = "Heads!"
            else:
                msg = "Tails!"

        await utils.send_message(self.client, channel, msg)

    async def play(self, server, channel, voice_channel, arg):
        if not voice_channel:
            await utils.send_message(self.client, channel, "You must be in a voice channel!")

        if server not in self.players:
            self.players[server] = Player(self.client, server)

        await self.players[server].add(channel, voice_channel, arg)

    async def skip(self, server, channel):
        await self.players[server].skip(channel)

    async def shell(self, channel, arg):
        try:
            msg = subprocess.check_output(arg + " &", stderr = STDOUT, shell=True, timeout = 2).decode("utf-8").strip()
        except subprocess.CalledProcessError as exc:
            msg = exc.output.decode("utf-8").strip()
        except subprocess.TimeoutExpired as exc:
            msg = "Timeout!"

        await utils.send_message(self.client, channel, msg, True)

    async def bot_src(self, channel):
        msg = open('bot.py', encoding="utf-8").read().strip().replace('`', '`\u200b')
        await utils.send_message(self.client, channel, msg, True, "python")

    async def help(self, channel):
        msg = ""
        for c in self.COMMANDS:
            msg += "{}{} - {}\n".format(self.prefix, c.value,
                                        self.COMMANDS_DESCRIPTION[c])

        await utils.send_message(self.client, channel, msg, True)

    async def invalid_command(self, channel):
        msg = "Invalid command! Use `" + self.prefix + "help` for more info."
        await utils.send_message(self.client, channel, msg)

    def ready(self):
        print('Logged in as')
        print(self.client.user.name)
        print(self.client.user.id)
        print('------')
