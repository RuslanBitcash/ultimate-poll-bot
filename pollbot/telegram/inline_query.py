"""Inline query handler function."""
from sqlalchemy import or_
from telegram.ext import run_async
from telegram import InlineQueryResultArticle, InputTextMessageContent

from pollbot.helper.management import get_poll_management_text
from pollbot.helper.session import hidden_session_wrapper
from pollbot.helper.keyboard import get_vote_keyboard
from pollbot.models import Poll


@run_async
@hidden_session_wrapper()
def search(bot, update, session, user):
    """Handle inline queries for sticker search."""
    query = update.inline_query.query
    if query.strip() == '':
        # Just display all polls
        polls = session.query(Poll) \
            .filter(Poll.user == user) \
            .filter(Poll.finished.is_(False)) \
            .order_by(Poll.created_at.desc()) \
            .all()

    else:
        # Find polls with search paramter in name or description
        polls = session.query(Poll) \
            .filter(Poll.user == user) \
            .filter(Poll.finished.is_(False)) \
            .filter(or_(
                Poll.name.ilike(f'%{query}%'),
                Poll.description.ilike(f'%{query}%'),
            )) \
            .order_by(Poll.created_at.desc()) \
            .all()

    if len(polls) == 0:
        update.inline_query.answer([], cache_time=300, is_personal=True,
                                   switch_pm_text="Click here to create a poll first ;)",
                                   switch_pm_parameter='inline')
    else:
        results = []
        for poll in polls:
            text = get_poll_management_text(session, poll)
            content = InputTextMessageContent(text, parse_mode='markdown')
            results.append(InlineQueryResultArticle(
                poll.id,
                poll.name,
                description=poll.description,
                input_message_content=content,
                reply_markup=get_vote_keyboard(poll),
            ))

        update.inline_query.answer(results, cache_time=300, is_personal=True,
                                   switch_pm_text="Click to create a new poll.",
                                   switch_pm_parameter='inline')
