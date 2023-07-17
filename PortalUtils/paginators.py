import discord


class PaginatorButton(discord.ui.Button):
    def __init__(self, f, **kwargs):
        super().__init__(**kwargs)
        self.f = f

    async def callback(self, interaction: discord.Interaction):
        return await getattr(self.view.paginator, f"show_{self.f}_page")()


class PaginatorButtons(discord.ui.View):
    def __init__(self, paginator, **kwargs):
        self.paginator = paginator
        super().__init__(**kwargs)
        mapping = [
            ("⏮", "first", 1),
            ("◀", "previous", self.paginator.current_page - 1),
            ("▶", "next", self.current_page + 1),
            ("⏭", "last", self.paginator.num_pages),
        ]
        for e, f, p in mapping:
            self.add_item(PaginatorButton(f, label=p, emoji=e, style=discord.ButtonStyle.blurple))
        self._children.insert(
            2,
            discord.ui.Button(
                label=f"{self.paginator.current_page}/{len(self.paginator.pages)}",
                style=discord.ButtonStyle.blurple,
                disabled=True,
            ),
        )


class PaginatorButtonsGoTo(PaginatorButtons):
    def __init__(self, paginator, **kwargs):
        super().__init__(paginator, **kwargs)
        self.add_item(self.GoTo(self.paginator))

    class GoTo(discord.ui.Select):
        def __init__(self, paginator, **kwargs):
            self.paginator = paginator
            options = [discord.SelectOption(label=str(i), value=i) for i in range(1, self.paginator.num_pages + 1)]
            super().__init__(placeholder="Go to page...", options=options, **kwargs)

        async def callback(self, interaction: discord.Interaction):
            await self.paginator.show_page(self.values[0])


class Paginator:
    def __init__(
        self,
        num_lines: int,
        *,
        delimiter: str = "\n",
        max_len: int = 2000,
        timeout: float = 180.0,
    ):
        self.current_page = 1
        self.max_len = max_len
        self.delimiter = delimiter
        self.message: discord.Message
        self.pages = [[]]
        self.is_embed: bool = False

    def add_line(self, line):
        if sum(map(len, self.pages)) + len(line) > self.max_len:
            self.pages.append([line])
        else:
            self.pages[-1].append(line)

    async def show_page(self, page):
        self.current_page = page
        k = "embed" if self.is_embed else "content"
        await self.message.edit(**{k: self.pages[self.current_page - 1]})

    async def show_next_page(self):
        await self.show_page(self.current_page + 1)

    async def show_previous_page(self):
        await self.show_page(self.current_page - 1)

    async def show_first_page(self):
        await self.show_page(1)

    async def show_last_page(self):
        await self.show_page(len(self.pages))

    async def send_to(self, channel: discord.TextChannel):
        self.pages = [self.delimiter.join(page) for page in self.pages]
        self.message = await channel.send(content=self.delimiter.join(self.pages[0]), view=PaginatorButtons(self))
        return self.message


class EmbedPaginator(Paginator):
    def __init__(
        self,
        num_lines: int,
        *,
        delimiter: str = "\n",
        max_len: int = 4096,
        timeout: float = 180.0,
        embed_cls: discord.Embed = discord.Embed,
        embed_kwargs: dict = None,
    ):
        super().__init__(num_lines, delimiter=delimiter, max_len=max_len, timeout=timeout)
        self.is_embed = True
        self.embed_cls = embed_cls
        self.embed_kwargs = embed_kwargs or {}

    async def send_to(self, channel: discord.TextChannel):
        self.pages = [self.embed_cls(description=self.delimiter.join(page), **self.embed_kwargs) for page in self.pages]
        self.message = await channel.send(embed=self.pages[0])
        return self.message
