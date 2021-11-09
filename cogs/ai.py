import random

import aiosqlite
import discord
from discord import errors
from discord.ext import commands
from transformers import PreTrainedTokenizerFast, GPT2LMHeadModel
import torch

class ai(commands.Cog):
    def __init__(self, bot:commands.Bot):
        super().__init__()
        self.bot = bot
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.tokenizer = PreTrainedTokenizerFast.from_pretrained('byeongal/Ko-DialoGPT')
        self.model = GPT2LMHeadModel.from_pretrained('byeongal/Ko-DialoGPT').to(self.device)
        self.past_user_inputs = {}
        self.generated_responses = {}


    def chat(self,message:discord.Message):
        database = await aiosqlite.connect("db/db.sqlite")
        user_input = message.content[4:]
        text_idx = self.tokenizer.encode(user_input + self.tokenizer.eos_token, return_tensors='pt')
        try:
            for i in range(len(self.generated_responses[message.author.id]) - 1,
                           len(self.generated_responses[message.author.id]) - 3, -1):
                if i < 0:
                    break
                encoded_vector = self.tokenizer.encode(
                    self.generated_responses[message.author.id][i] + self.tokenizer.eos_token, return_tensors='pt')
                if text_idx.shape[-1] + encoded_vector.shape[-1] < 1000:
                    text_idx = torch.cat([encoded_vector, text_idx], dim=-1)
                else:
                    break
                encoded_vector = self.tokenizer.encode(
                    self.past_user_inputs[message.author.id][i] + self.tokenizer.eos_token, return_tensors='pt')
                if text_idx.shape[-1] + encoded_vector.shape[-1] < 1000:
                    text_idx = torch.cat([encoded_vector, text_idx], dim=-1)
                else:
                    break
        except KeyError:
            text_idx = text_idx.to(self.device)
            inference_output = self.model.generate(
                text_idx,
                max_length=1000,
                num_beams=5,
                top_k=100,
                no_repeat_ngram_size=4,
                length_penalty=0.65,
                repetition_penalty=2.0,
            )
            inference_output = inference_output.tolist()
            bot_response = self.tokenizer.decode(inference_output[0][text_idx.shape[-1]:], skip_special_tokens=True)
            # print(f"Bot: {bot_response}")
            past_input = self.past_user_inputs[message.author.id] = []
            past_input.append(user_input)
            generated_responses = self.generated_responses[message.author.id] = []
            generated_responses.append(bot_response)
            point = random.randint(1, 4)
            cur = await database.execute("SELECT * FROM ai WHERE user = ?", (message.author.id,))
            if await cur.fetchone() == None:
                await database.execute("INSERT INTO ai(user,point) VALUES (?,?)", (message.author.id, point))
                await database.commit()
            else:
                await database.execute("UPDATE ai SET point = point + ? WHERE user = ?", (point, message.author.id))
                await database.commit()
            self.bot.get_channel(901116598977462312).send(
                f"{message.author}({message.author.id}) - `{user_input}`\nresponse: {bot_response}")
            return message.reply(bot_response+ f"\n`💕호감도 +{point}`")
        text_idx = text_idx.to(self.device)
        inference_output = self.model.generate(
            text_idx,
            max_length=1000,
            num_beams=5,
            top_k=30,
            no_repeat_ngram_size=4,
            length_penalty=0.65,
            repetition_penalty=2.0,
        )
        inference_output = inference_output.tolist()
        bot_response = self.tokenizer.decode(inference_output[0][text_idx.shape[-1]:], skip_special_tokens=True)
        # print(f"Bot: {bot_response}")
        past_input: list = self.past_user_inputs[message.author.id]
        past_input.append(user_input)
        generated_responses: list = self.generated_responses[message.author.id]
        generated_responses.append(bot_response)
        point = random.randint(1, 4)
        cur = await database.execute("SELECT * FROM ai WHERE user = ?", (message.author.id,))
        if await cur.fetchone() == None:
            await database.execute("INSERT INTO ai(user,point) VALUES (?,?)", (message.author.id, point))
            await database.commit()
        else:
            await database.execute("UPDATE ai SET point = point + ? WHERE user = ?", (point, message.author.id))
            await database.commit()
        self.bot.get_channel(901116598977462312).send(
            f"{message.author}({message.author.id}) - `{user_input}`\nresponse: {bot_response}")
        return message.reply(bot_response+ f"\n`💕호감도 +{point}`")


    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        if message.content.startswith("하린아 "):
            database = await aiosqlite.connect("db/db.sqlite")
            cur = await database.execute("SELECT * FROM blacklist WHERE user = ?", (message.author.id,))
            if await cur.fetchone() != None:
                return await message.reply("블랙리스트 유저로 등록되어있어 ai채팅을 사용할 수 없어요.")
            user_input = message.content[4:]
            if user_input == '하린아 bye' or user_input == '하린아 잘가':
                del self.past_user_inputs[message.author.id]
                del self.generated_responses[message.author.id]
                await message.channel.send(content="안녕히 계세요!")
            async with message.channel.typing():
                await self.bot.loop.create_task(self.chat(message=message))
                #self.past_user_inputs[message.author.id].append(user_input)
                #self.generated_responses[message.author.id].append(bot_response)




def setup(bot):
    bot.add_cog(ai(bot))
