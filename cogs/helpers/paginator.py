from __future__ import annotations

from typing import TYPE_CHECKING, overload

from discord import ButtonStyle
from discord.ui import View, button

if TYPE_CHECKING:
    from typing import NotRequired, TypedDict

    from discord import Embed, Interaction, Message
    from discord.ext import commands
    from discord.ui import Button

    from bot import Bot

    class PaginatorStartKwargs(TypedDict):
        ephemeral: bool
        content: NotRequired[str]
        embeds: NotRequired[list[Embed]]

    class PaginatorEditKwargs(TypedDict):
        content: str | None
        embeds: list[Embed]

else:
    PaginatorStartKwargs = dict
    PaginatorEditKwargs = dict

__all__ = (
    "Page",
    "Paginator",
)


class Page:
    __slots__ = (
        "content",
        "embeds",
    )

    if TYPE_CHECKING:
        content: str | None
        embeds: list[Embed]

    @overload
    def __init__(self, *, content: str) -> None: ...
    @overload
    def __init__(self, *, embed: Embed) -> None: ...
    @overload
    def __init__(self, *, embeds: list[Embed]) -> None: ...
    @overload
    def __init__(self, *, content: str, embed: Embed) -> None: ...
    @overload
    def __init__(self, *, content: str, embeds: list[Embed]) -> None: ...
    def __init__(
        self,
        *,
        content: str | None = None,
        embed: Embed | None = None,
        embeds: list[Embed] | None = None,
    ) -> None:
        if not content and embed is None and not embeds:
            raise ValueError("Empty page is invalid.")

        if embed is not None and embeds is not None:
            raise ValueError("Cannot specify both embed and embeds.")

        self.content = content
        self.embeds = [embed] if embed is not None else embeds or []


class Paginator(View):
    if TYPE_CHECKING:
        message: Message | None
        context: commands.Context[Bot]
        pages: list[Page]
        current_page: int
        compact: bool

    def __init__(
        self,
        *,
        pages: list[Page],
        context: commands.Context[Bot],
        timeout: float | None = None,
        current_page: int = 0,
        compact: bool = False,
    ) -> None:
        super().__init__(timeout=timeout)
        self.pages = pages
        self.context = context
        self.message = None
        self.current_page = current_page
        self.compact = compact

        self.clear_items()
        self.fill_items()
        self.update_buttons()

    def fill_items(self) -> None:
        if self.compact:
            btns = [self.goto_prev, self.goto_next]
        else:
            btns = [
                self.goto_first,
                self.goto_prev,
                self.indicator,
                self.goto_next,
                self.goto_last,
            ]

        for btn in btns:
            self.add_item(btn)

    def update_buttons(self) -> None:
        is_first = self.current_page <= 0
        is_last = self.current_page >= self.page_count - 1
        self.indicator.label = f"{self.current_page + 1}/{self.page_count}"

        for btn in [
            self.goto_first,
            self.goto_prev,
            self.goto_next,
            self.goto_last,
        ]:
            btn.disabled = False

        if is_first:
            self.goto_first.disabled = True
            self.goto_prev.disabled = True

        elif is_last:
            self.goto_next.disabled = True
            self.goto_last.disabled = True

    @property
    def page_count(self) -> int:
        return len(self.pages)

    async def start(self, ephemeral: bool = False) -> None:
        initial_page = self.pages[self.current_page]
        kwargs: PaginatorStartKwargs = {"ephemeral": ephemeral}

        if initial_page.content:
            kwargs["content"] = initial_page.content

        if initial_page.embeds:
            kwargs["embeds"] = initial_page.embeds

        self.message = await self.context.send(**kwargs, view=self)

    async def goto_page(self, interaction: Interaction, page_number: int) -> None:
        page = self.pages[page_number]
        kwargs: PaginatorEditKwargs = {"content": page.content, "embeds": page.embeds}

        self.current_page = page_number
        self.update_buttons()

        if interaction.response.is_done():
            if self.message:
                self.message = await self.message.edit(**kwargs, view=self)
        else:
            await interaction.response.edit_message(**kwargs, view=self)

    async def on_timeout(self) -> None:
        if self.message:
            await self.message.edit(view=None)

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user and interaction.user.id in (
            self.context.author.id,
            self.context.bot.owner_id,
        ):
            return True
        await interaction.response.send_message(
            "このページは作成者のみが操作できます.", ephemeral=True
        )
        return False

    @button(label="<<", custom_id="Paginator_first_button", style=ButtonStyle.blurple)
    async def goto_first(self, interaction: Interaction, _: Button) -> None:
        await self.goto_page(interaction, 0)

    @button(label="<", custom_id="Paginator_prev_button", style=ButtonStyle.red)
    async def goto_prev(self, interaction: Interaction, _: Button) -> None:
        await self.goto_page(interaction, self.current_page - 1)

    @button(custom_id="Paginator_indicator", style=ButtonStyle.gray, disabled=True)
    async def indicator(self, interaction: Interaction, _: Button) -> None:
        return

    @button(label=">", custom_id="Paginator_next_button", style=ButtonStyle.green)
    async def goto_next(self, interaction: Interaction, _: Button) -> None:
        await self.goto_page(interaction, self.current_page + 1)

    @button(label=">>", custom_id="Paginator_last_button", style=ButtonStyle.green)
    async def goto_last(self, interaction: Interaction, _: Button) -> None:
        await self.goto_page(interaction, self.page_count - 1)
