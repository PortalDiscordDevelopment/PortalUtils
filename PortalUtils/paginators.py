from __future__ import annotations

from typing import Literal

from discord import ButtonStyle, Embed, Interaction, Message, SelectOption, abc, ui

PAGE_RELATION = Literal["first"] | Literal["previous"] | Literal["next"] | Literal["last"]


class PaginatorButton(ui.Button):
    """
    Move to a specific page in the paginator.
    """

    f: PAGE_RELATION

    def __init__(self, f: PAGE_RELATION, **kwargs):
        super().__init__(**kwargs)
        self.f = f

    async def callback(self, interaction: Interaction):
        return await getattr(self.view.paginator, f"show_{self.f}_page")()


class PaginatorButtons(ui.View):
    """
    A paginator view with buttons to move to the first, previous, next, and last pages.
    """

    def __init__(self, paginator: Paginator, **kwargs):
        self.paginator = paginator
        super().__init__(**kwargs)
        mapping: list[tuple[str, PAGE_RELATION, int]] = [
            ("⏮", "first", 1),
            ("◀", "previous", self.paginator.current_page - 1),
            ("▶", "next", self.current_page + 1),
            ("⏭", "last", self.paginator.num_pages),
        ]
        for e, f, p in mapping:
            self.add_item(PaginatorButton(f, label=str(p), emoji=e, style=ButtonStyle.blurple))
        self._children.insert(
            2,
            ui.Button(
                label=f"{self.paginator.current_page}/{len(self.paginator.pages)}",
                style=ButtonStyle.blurple,
                disabled=True,
            ),
        )


class PaginatorButtonsGoTo(PaginatorButtons):
    """
    A paginator view with buttons to move to the first, previous, next, and last pages, and a select menu to go to a specific page.
    """

    def __init__(self, paginator: Paginator, **kwargs):
        super().__init__(paginator, **kwargs)
        self.add_item(self.GoTo(self.paginator))

    class GoTo(ui.Select):
        def __init__(self, paginator, **kwargs):
            self.paginator = paginator
            options = [SelectOption(label=str(i), value=i) for i in range(1, self.paginator.num_pages + 1)]
            super().__init__(placeholder="Go to page...", options=options, **kwargs)

        async def callback(self, interaction: Interaction):
            await self.paginator.show_page(self.values[0])


class Paginator:
    """
    A paginator class.

    Parameters
    ----------
    num_lines: int
        The number of lines to show per page.
    delimiter: str
        The delimiter to use when joining lines.
    max_len: int
        The maximum length of the message content.
    timeout: float
        The timeout for the paginator.
    """

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
        self.message: Message
        self.page: list[list[str]] = [[]]
        self.is_embed: bool = False

    def add_line(self, line: str):
        """
        Add a line to the paginator.

        Parameters
        ----------
        line: str
            The line to add.
        """
        if sum(map(len, self.pages)) + len(line) > self.max_len:
            self.pages.append([line])
        else:
            self.pages[-1].append(line)

    async def show_page(self, page: int):
        """
        Show a specific page in the paginator.

        Parameters
        ----------
        page: int
            The page to show.
        """
        self.current_page = page
        k = "embed" if self.is_embed else "content"
        await self.message.edit(**{k: self.pages[self.current_page - 1]})

    async def show_next_page(self):
        """
        Show the next page in the paginator.
        """
        await self.show_page(self.current_page + 1)

    async def show_previous_page(self):
        """
        Show the previous page in the paginator.
        """
        await self.show_page(self.current_page - 1)

    async def show_first_page(self):
        """
        Show the first page in the paginator.
        """
        await self.show_page(1)

    async def show_last_page(self):
        """
        Show the last page in the paginator.
        """
        await self.show_page(len(self.pages))

    async def send_to(self, destination: abc.Messageable):
        """
        Send the paginator to a messageable.

        Parameters
        ----------
        destination: discord.abc.Messageable
            The channel to send the paginator to.
        """
        self.pages = [self.delimiter.join(page) for page in self.pages]
        self.message = await destination.send(content=self.delimiter.join(self.pages[0]), view=PaginatorButtons(self))
        return self.message


class EmbedPaginator(Paginator):
    """
    A paginator that sends embeds.
    """

    def __init__(
        self,
        num_lines: int,
        *,
        delimiter: str = "\n",
        max_len: int = 4096,
        timeout: float = 180.0,
        embed_cls: Embed = Embed,
        embed_kwargs: dict = None,
    ):
        super().__init__(num_lines, delimiter=delimiter, max_len=max_len, timeout=timeout)
        self.is_embed = True
        self.embed_cls = embed_cls
        self.embed_kwargs = embed_kwargs or {}

    async def send_to(self, channel: abc.Messageable):
        """
        Send the paginator to a messageable.

        Parameters
        ----------
        channel: discord.abc.Messageable
            The channel to send the paginator to.
        """
        self.pages = [self.embed_cls(description=self.delimiter.join(page), **self.embed_kwargs) for page in self.pages]
        self.message = await channel.send(embed=self.pages[0])
        return self.message
