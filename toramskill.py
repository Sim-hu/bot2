import discord
from discord import app_commands
from discord.ext import commands
import json
import asyncio
import os
from dotenv import load_dotenv

# 環境変数のロード
load_dotenv()

SKILLS_FILE = os.getenv('SKILLS_FILE', 'skills.json')

def load_skills():
    try:
        with open(SKILLS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content:
                return {"ブレードスキル": {}, "シュートスキル": {}, "マーシャルスキル": {}, "スプライトスキル": {}, "マジックスキル": {}, "ハルバードスキル": {}, "モノノフスキル": {}, "ベアハンドスキル": {}, "クラッシャースキル":{}}
            return json.loads(content)
    except FileNotFoundError:
        return {"ブレードスキル": {}, "シュートスキル": {}, "マーシャルスキル": {}, "スプライトスキル": {}, "マジックスキル": {}, "ハルバードスキル": {}, "モノノフスキル": {}, "ベアハンドスキル": {}, "クラッシャースキル":{}}
    except json.JSONDecodeError:
        print(f"Warning: {SKILLS_FILE} contains invalid JSON. Starting with empty skills.")
        return {"ブレードスキル": {}, "シュートスキル": {}, "マーシャルスキル": {}, "スプライトスキル": {}, "マジックスキル": {}, "ハルバードスキル": {}, "モノノフスキル": {}, "ベアハンドスキル": {}, "クラッシャースキル":{}}

class ToramSkillCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.skills = load_skills()
        self.auto_bump_tasks = {}
        self.skill_types = {
            "ブレード": "ブレードスキル",
            "シュート": "シュートスキル",
            "マーシャル": "マーシャルスキル",
            "スプライト": "スプライトスキル",
            "マジック": "マジックスキル",
            "ハルバード": "ハルバードスキル",
            "モノノフ": "モノノフスキル",
            "ベアハンド": "ベアハンドスキル",
            "クラッシャー": "クラッシャースキル"
        }        

    async def skill_type_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=full_name, value=short_name)
            for short_name, full_name in self.skill_types.items()
            if current.lower() in short_name.lower() or current.lower() in full_name.lower()
        ][:25]

    async def skill_name_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        # 現在選択されているスキルタイプを取得
        skill_type = self.skill_types.get(interaction.namespace.スキルタイプ)
        if not skill_type or skill_type not in self.skills:
            return []
        
        # 該当するスキルタイプのスキル名をサジェスト
        return [
            app_commands.Choice(name=skill_name, value=skill_name)
            for skill_name in self.skills[skill_type].keys()
            if current.lower() in skill_name.lower()
        ][:25]    

    async def blade_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        skills = self.skills["ブレードスキル"].keys()
        return [
            app_commands.Choice(name=skill, value=skill)
            for skill in skills
            if current.lower() in skill.lower()
        ][:25]

    async def shoot_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        skills = self.skills["シュートスキル"].keys()
        return [
            app_commands.Choice(name=skill, value=skill)
            for skill in skills
            if current.lower() in skill.lower()
        ][:25]

    async def martial_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        skills = self.skills["マーシャルスキル"].keys()
        return [
            app_commands.Choice(name=skill, value=skill)
            for skill in skills
            if current.lower() in skill.lower()
        ][:25]

    async def sprite_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        skills = self.skills["スプライトスキル"].keys()
        return [
            app_commands.Choice(name=skill, value=skill)
            for skill in skills
            if current.lower() in skill.lower()
        ][:25]

    async def magic_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        skills = self.skills["マジックスキル"].keys()
        return [
            app_commands.Choice(name=skill, value=skill)
            for skill in skills
            if current.lower() in skill.lower()
        ][:25]

    async def halberd_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        skills = self.skills["ハルバードスキル"].keys()
        return [
            app_commands.Choice(name=skill, value=skill)
            for skill in skills
            if current.lower() in skill.lower()
        ][:25]

    async def mononohu_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        skills = self.skills["モノノフスキル"].keys()
        return [
            app_commands.Choice(name=skill, value=skill)
            for skill in skills
            if current.lower() in skill.lower()
        ][:25]

    async def bearhand_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        skills = self.skills["ベアハンドスキル"].keys()
        return [
            app_commands.Choice(name=skill, value=skill)
            for skill in skills
            if current.lower() in skill.lower()
        ][:25]

    async def crusher_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        skills = self.skills["クラッシャースキル"].keys()
        return [
            app_commands.Choice(name=skill, value=skill)
            for skill in skills
            if current.lower() in skill.lower()
        ][:25]        

    @commands.Cog.listener()
    async def on_ready(self):
        print("ToramSkillCog is ready.")

    @app_commands.command(name="d", description="スキル名と詳細を入力")
    async def skill_input(self, interaction: discord.Interaction):
        modal = SkillModal()
        await interaction.response.send_modal(modal)

    @app_commands.command(name="ブレードスキル", description="ブレードスキルを使用します")
    @app_commands.describe(スキル="使用するスキル名")
    @app_commands.autocomplete(スキル=blade_autocomplete)
    async def blade_skill(self, interaction: discord.Interaction, スキル: str):
        await self.send_skill_embed(interaction, "ブレードスキル", スキル, discord.Color.orange())

    @app_commands.command(name="シュートスキル", description="シュートスキルを使用します")
    @app_commands.describe(スキル="使用するスキル名")
    @app_commands.autocomplete(スキル=shoot_autocomplete)
    async def shoot_skill(self, interaction: discord.Interaction, スキル: str):
        await self.send_skill_embed(interaction, "シュートスキル", スキル, discord.Color.orange())

    @app_commands.command(name="マーシャルスキル", description="マーシャルスキルを使用します")
    @app_commands.describe(スキル="使用するスキル名")
    @app_commands.autocomplete(スキル=martial_autocomplete)
    async def martial_skill(self, interaction: discord.Interaction, スキル: str):
        await self.send_skill_embed(interaction, "マーシャルスキル", スキル, discord.Color.orange())

    @app_commands.command(name="スプライトスキル", description="スプライトスキルを使用します")
    @app_commands.describe(スキル="使用するスキル名")
    @app_commands.autocomplete(スキル=sprite_autocomplete)
    async def sprite_skill(self, interaction: discord.Interaction, スキル: str):
        await self.send_skill_embed(interaction, "スプライトスキル", スキル, discord.Color.orange())
    
    @app_commands.command(name="マジックスキル", description="マジックスキルを使用します")
    @app_commands.describe(スキル="使用するスキル名")
    @app_commands.autocomplete(スキル=magic_autocomplete)
    async def magic_skill(self, interaction: discord.Interaction, スキル: str):
        await self.send_skill_embed(interaction, "マジックスキル", スキル, discord.Color.orange())

    @app_commands.command(name="ハルバードスキル", description="ハルバードスキルを使用します")
    @app_commands.describe(スキル="使用するスキル名")
    @app_commands.autocomplete(スキル=halberd_autocomplete)
    async def halberd_skill(self, interaction: discord.Interaction, スキル: str):
        await self.send_skill_embed(interaction, "ハルバードスキル", スキル, discord.Color.orange())

    @app_commands.command(name="モノノフスキル", description="モノノフスキルを使用します")
    @app_commands.describe(スキル="使用するスキル名")
    @app_commands.autocomplete(スキル=mononohu_autocomplete)
    async def mononohu_skill(self, interaction: discord.Interaction, スキル: str):
        await self.send_skill_embed(interaction, "モノノフスキル", スキル, discord.Color.orange())

    @app_commands.command(name="ベアハンドスキル", description="ベアハンドスキルを使用します")
    @app_commands.describe(スキル="使用するスキル名")
    @app_commands.autocomplete(スキル=bearhand_autocomplete)
    async def bearhand_skill(self, interaction: discord.Interaction, スキル: str):
        await self.send_skill_embed(interaction, "ベアハンドスキル", スキル, discord.Color.orange())

    @app_commands.command(name="クラッシャースキル", description="クラッシャースキルを使用します")
    @app_commands.describe(スキル="使用するスキル名")
    @app_commands.autocomplete(スキル=crusher_autocomplete)
    async def crusher_skill(self, interaction: discord.Interaction, スキル: str):
        await self.send_skill_embed(interaction, "クラッシャースキル", スキル, discord.Color.orange())

    async def send_skill_embed(self, interaction: discord.Interaction, skill_type: str, skill_name: str, color: discord.Color):
        if skill_name in self.skills[skill_type]:
            skill_info = self.skills[skill_type][skill_name]
            embed = discord.Embed(title=f"{skill_type}: {skill_name}", description=skill_info, color=color)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"{skill_name}は登録されていません。")


    @app_commands.command(name="help_toram", description="Toramスキルコマンドのヘルプを表示します")
    @app_commands.describe(スキルタイプ="表示したいスキルタイプ（オプション）")
    @app_commands.autocomplete(スキルタイプ=skill_type_autocomplete)
    async def help_toram(self, interaction: discord.Interaction, スキルタイプ: str = None):
        if スキルタイプ:
            matched_type = self.skill_types.get(スキルタイプ)

            if matched_type and matched_type in self.skills:
                
                if matched_type == "ブレードスキル":
                    embed = discord.Embed(
                        title=f"{matched_type}一覧",
                        description="ブレードスキルツリー:",
                        color=discord.Color.blue()
                    )
                    embed.set_image(url="https://cdn.discordapp.com/attachments/982324760350441552/1320326085765759028/FireShot_Capture_156_-_-_Google_-_docs.google.com.png?ex=676930fd&is=6767df7d&hm=c3a96e504c954fe0d8d1419b8f1338b1bf18adf86f71e8f2f8a34c41cac036d4&")
                
                elif matched_type == "シュートスキル":
                    embed = discord.Embed(
                        title=f"{matched_type}一覧",
                        description="シュートスキルツリー:",
                        color=discord.Color.blue()
                    )
                    embed.set_image(url="https://cdn.discordapp.com/attachments/982324760350441552/1320326086164348999/FireShot_Capture_157_-_-_Google_-_docs.google.com.png?ex=676930fd&is=6767df7d&hm=059648d9d77feca23cda700d4e2093df6f4780bc7daec0dd7ab6681bf43b4376&")

                elif matched_type == "マジックスキル":
                    embed = discord.Embed(
                        title=f"{matched_type}一覧",
                        description="マジックスキルツリー:",
                        color=discord.Color.blue()
                    )
                    embed.set_image(url="https://cdn.discordapp.com/attachments/982324760350441552/1320541046593294396/FireShot_Capture_159_-_-_Google_-_docs.google.com.png?ex=6769f92f&is=6768a7af&hm=a802108bf6059783d0b797b415b4a6cc4e8e13fbc68f0a32811332bc8148f294&")

                elif matched_type == "マーシャルスキル":
                    embed = discord.Embed(
                        title=f"{matched_type}一覧",
                        description="マーシャルスキルツリー:",
                        color=discord.Color.blue()
                    )
                    embed.set_image(url="https://cdn.discordapp.com/attachments/982324760350441552/1321653589168488599/FireShot_Capture_161_-_-_Google_-_docs.google.com.png?ex=676e0552&is=676cb3d2&hm=f50e7e9d5e276e36ac9cc941273546020dfca1929ab1e5e763efdf476e83c909&")

                elif matched_type == "ハルバードスキル":
                    embed = discord.Embed(
                        title=f"{matched_type}一覧",
                        description="ハルバードスキルツリー:",
                        color=discord.Color.blue()
                    )
                    embed.set_image(url="https://cdn.discordapp.com/attachments/1298463953193537566/1322186939696283668/FireShot_Capture_164_-_-_Google_-_docs.google.com.png?ex=676ff60b&is=676ea48b&hm=b198dc2a784a0eb660fcff5219762808d8ca50459f8b98278e60030e469a1f07&")

                elif matched_type == "モノノフスキル":
                    embed = discord.Embed(
                        title=f"{matched_type}一覧",
                        description="モノノフスキルツリー:",
                        color=discord.Color.blue()
                    )
                    embed.set_image(url="https://cdn.discordapp.com/attachments/1298463953193537566/1322788995092189235/FireShot_Capture_169_-_-_Google_-_docs.google.com.png?ex=677226c0&is=6770d540&hm=bc318566f7b87014a231caf49ea6a190d01fc1828a313ed2ab86236ccbf73662&")

                elif matched_type == "スプライトスキル":
                    embed = discord.Embed(
                        title=f"{matched_type}一覧",
                        description="スプライトスキルツリー:",
                        color=discord.Color.blue()
                    )
                    embed.set_image(url="https://cdn.discordapp.com/attachments/1298463953193537566/1322783294986649671/FireShot_Capture_168_-_-_Google_-_docs.google.com.png?ex=67722171&is=6770cff1&hm=2103f2db7254c3a6f2eb386e1c359c57ea74abf69b91fc1d0f939c9c385b9b9f&")     

                elif matched_type == "クラッシャースキル":
                    embed = discord.Embed(
                        title=f"{matched_type}一覧",
                        description="クラッシャースキルツリー:",
                        color=discord.Color.blue()
                    )
                    embed.set_image(url="https://cdn.discordapp.com/attachments/1298463953193537566/1330486413535481907/FireShot_Capture_184_-_-_Google_-_docs.google.com.png?ex=679b5688&is=679a0508&hm=552b21c51ec484ac3a48a58ce29d0d39988268a5e7341cbbacff1c3f2978bbb5&")     

                elif matched_type == "ベアハンドスキル":
                    embed = discord.Embed(
                        title=f"{matched_type}一覧",
                        description="ベアハンドスキルツリー:",
                        color=discord.Color.blue()
                    )
                    embed.set_image(url="https://cdn.discordapp.com/attachments/1298463953193537566/1331743990835576872/FireShot_Capture_205_-_-_Google_-_docs.google.com.png?ex=679b4c7e&is=6799fafe&hm=d105d3c3f93621e7020a3432c42ee20ed9390502d48966ec9e3147ddba063abb&")     

                else:
                    # 他のスキルタイプは従来通りのリスト表示
                    skill_list = list(self.skills[matched_type].keys())
                    if skill_list:
                        embed = discord.Embed(
                            title=f"{matched_type}一覧",
                            description="登録されているスキル:",
                            color=discord.Color.blue()
                        )
                        # スキルを20個ずつのグループに分けて表示
                        for i in range(0, len(skill_list), 20):
                            chunk = skill_list[i:i + 20]
                            embed.add_field(
                                name=f"スキル {i+1}-{i+len(chunk)}",
                                value="\n".join(chunk) if chunk else "なし",
                                inline=False
                            )
                    else:
                        embed = discord.Embed(
                            title=f"{matched_type}一覧",
                            description="登録されているスキルはありません。",
                            color=discord.Color.blue()
                        )                    

            else:
                embed = discord.Embed(
                    title="エラー",
                    description="指定されたスキルタイプが見つかりません。",
                    color=discord.Color.red()
                )
        else:
            # 通常のヘルプメッセージを表示
            embed = discord.Embed(
                title="Toramスキルコマンドヘルプ",
                description="利用可能なToramスキルコマンド:",
                color=discord.Color.purple()
            )
            embed.add_field(name="/help_toram [スキルタイプ]", value="スキルタイプを指定すると、登録されているスキルの一覧を表示します\n例: /help_toram ブレード", inline=False)
            embed.add_field(name="/ブレードスキル スキル名", value="指定したブレードスキルの情報を表示します", inline=False)
            embed.add_field(name="/シュートスキル スキル名", value="指定したシュートスキルの情報を表示します", inline=False)
            embed.add_field(name="/マーシャルスキル スキル名", value="指定したマーシャルスキルの情報を表示します", inline=False)
            embed.add_field(name="/スプライトスキル スキル名", value="指定したスプライトスキルの情報を表示します", inline=False)
            embed.add_field(name="/マジックスキル スキル名", value="指定したマジックスキルの情報を表示します", inline=False)
            embed.add_field(name="/ハルバードスキル スキル名", value="指定したハルバードスキルの情報を表示します", inline=False)
            embed.add_field(name="/モノノフスキル スキル名", value="指定したモノノフスキルの情報を表示します", inline=False)
            embed.add_field(name="/ベアハンドスキル スキル名", value="指定したベアハンドスキルの情報を表示します", inline=False)
            embed.add_field(name="/クラッシャースキル スキル名", value="指定したクラッシャースキルの情報を表示します", inline=False)
    
        await interaction.response.send_message(embed=embed)

class SkillModal(discord.ui.Modal, title='スキル情報入力'):
    skill_name = discord.ui.TextInput(label='スキル名')
    details = discord.ui.TextInput(label='詳細', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        formatted_details = f"{self.skill_name.value}\n{self.details.value}"
        formatted_details = formatted_details.replace('\n', '\\n')
        
        response = f'    "{self.skill_name.value}": "\\n{formatted_details}",'
        
        await interaction.response.send_message(f"```json\n{response}\n```")

async def setup(bot):
    await bot.add_cog(ToramSkillCog(bot))