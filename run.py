import discord
from discord.ext.commands import Bot
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from discord.utils import get
from discord.ext import *
import requests
import binascii, hashlib, base58, ecdsa
import os

Client = discord.Client()
bot_prefix= "!"
client = commands.Bot(command_prefix=bot_prefix)

client.remove_command('help')

@client.event
async def on_command_error(ctx, error):
  if isinstance(error, CommandNotFound):
    if str(error)[9:][:1] == "!":
      pass
    else:
      return await ctx.send(str(error))
    
def ripemd160(x):
  d = hashlib.new('ripemd160')
  d.update(x)
  return d
    
@client.event
async def on_ready():
  activity = discord.Game(name="!luck")
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='!luck'))
  print("Name: {}".format(client.user.name))
  print("ID: {}".format(client.user.id))
  
@client.command(aliases=['btc', 'wallet'])
async def luck(ctx):
  i = 0
  wallets = {}
  while i < 11:
    i = i+1
    priv_key = os.urandom(32)
    fullkey = '80' + binascii.hexlify(priv_key).decode()
    sha256a = hashlib.sha256(binascii.unhexlify(fullkey)).hexdigest()
    sha256b = hashlib.sha256(binascii.unhexlify(sha256a)).hexdigest()
    WIF = base58.b58encode(binascii.unhexlify(fullkey+sha256b[:8]))

    sk = ecdsa.SigningKey.from_string(priv_key, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    publ_key = '04' + binascii.hexlify(vk.to_string()).decode()
    hash160 = ripemd160(hashlib.sha256(binascii.unhexlify(publ_key)).digest()).digest()
    publ_addr_a = b"\x00" + hash160
    checksum = hashlib.sha256(hashlib.sha256(publ_addr_a).digest()).digest()[:4]
    publ_addr_b = base58.b58encode(publ_addr_a + checksum)
    priv = WIF.decode()
    pub = publ_addr_b.decode()
    wallets[priv] = pub
    
  finalWallets = ""
  nr = 0
  for w in wallets:
    finalWallets = finalWallets + f"[{w}](https://www.blockchain.com/btc/address/{wallets[w]}) lol{str(nr)}\n\n"
    nr = nr+1
    
  balances = []
  for w1 in wallets:
    r = requests.get("https://www.blockchain.com/btc/address/" + wallets[w])
    if 'The current value of this address is 0.00000000 BTC ($0.00)' in r.text:
      balances.append("(Empty)")
    elif not 'The current value of this address is' in r.text:
      balances.append("(Failed to check balance)")
    else:
      balances.append("(Not Empty)")

  nr2 = 0
  for b in balances:
    finalWallets = finalWallets.replace("lol" + str(nr2), balances[nr2])
    nr2 = nr2+1
    
  finalWallets = finalWallets.replace(")0", ")")

  embed=discord.Embed(title="Random Seeds", description=finalWallets, color=0xf7941a)
  embed.set_author(name="Bitcoin", icon_url="https://bitmarket.pl/wp-content/uploads/2020/10/Bitcoin.svg_.png")
  await ctx.send(embed=embed)
  print(">> Successfully generated 10 random and valid bitcoin seeds.")
  print("")

client.run("Your bot token here")
