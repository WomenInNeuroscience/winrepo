import recurrence
from django import template
from django.contrib.sites.models import Site
from django.utils.http import urlquote_plus

from martor.utils import markdownify

register = template.Library()

@register.filter
def google_calendarize(occurrence):
    st = occurrence["start_date"]
    en = occurrence.get("end_date", occurrence["start_date"])
    tfmt = r"%Y%m%dT%H%M%S"

    event = occurrence["event"]

    dates = "%s%s%s" % (st.strftime(tfmt), "%2F", en.strftime(tfmt))
    title = urlquote_plus(event.title)

    description = None
    if event.description:
        description = markdownify(event.description)

    s = (
        "http://www.google.com/calendar/render?action=TEMPLATE&" +
        "text=" + title + "&" +
        "detail=" + title + "&" +
        "dates=" + dates + "&" +
        "ctz=UTC&" +
        "sprop=website:" + urlquote_plus(Site.objects.get_current().domain)
    )

    if description:
        s = s + "&details=" + urlquote_plus(description)

    if event.location:
        s = s + "&location=" + urlquote_plus(event.location)

    # TODO unclear for now how to handle recurrence with multiple rules
    if event.recurrence:
        recur = recurrence.serialize(event.recurrence)
        if recur:
            s = s + "&recur=" + urlquote_plus(recur)

    return s + "&trp=false"

google_calendarize.safe = True
