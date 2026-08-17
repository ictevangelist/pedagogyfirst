# -*- coding: utf-8 -*-
"""
The privacy notice.

Written to be true of this site as it actually is, not as a template imagines
it. Every claim in here was checked against the build: the fonts are vendored
so nothing is fetched from Google, there is no sign-up form, there are no
cookies at all unless analytics is switched on and agreed to, and GitHub's own
documentation confirms it logs visitor IP addresses for GitHub Pages sites.

Where a section stops being true, change it here rather than leaving it. A
privacy notice that has drifted from the site is worse than none, because it
looks like a promise.
"""

PRIVACY = {
    "kicker": "Legal",
    "title": "Privacy and cookies",
    "standfirst": "What this site collects, which is very little, and what it does with it.",
    "intro": [
        "The short version: there are no cookies on this site unless you agree to analytics, "
        "there's no sign-up, no form, no newsletter, and nothing you do here is sent to anyone "
        "else. You can read all 144 strategies and download everything without telling me who "
        "you are.",
        "The longer version is below, because a site about doing things properly should say "
        "plainly what it's up to.",
    ],
    "sections": [
        {
            "id": "the-site",
            "heading": "The site itself",
            "paras": [
                "These pages are plain static files. No trackers, no advertising, no profiling, "
                "no social media widgets, no embedded video, no comment system, no chat bubble.",
                "There are no requests to any other company either. The fonts are served from "
                "this site rather than from Google Fonts, and the images and infographics are "
                "all hosted here. Open your browser's network tab and the only domain you'll see "
                "is this one. That's deliberate, because a font request is still a request, and "
                "it still carries your IP address to somebody else.",
            ],
        },
        {
            "id": "cookies",
            "heading": "Cookies",
            "paras": [
                "By default, none. Not one. Nothing is written to your device when you arrive.",
                "If analytics is switched on and you agree to it, Google Analytics will then set "
                "cookies in your browser. That's the only circumstance in which this site sets a "
                "cookie, and it can't happen before you've said yes.",
            ],
            "note": "Two things are stored in your browser's local storage, which isn't a cookie "
                    "and isn't sent anywhere. Your reading preferences from the accessibility "
                    "controls, so text size and contrast survive between pages, and your answer "
                    "to the analytics question, so you aren't asked again on every visit. Both "
                    "live on your device only. Clearing your browser data removes them.",
        },
        {
            "id": "analytics",
            "heading": "Analytics, and only if you say yes",
            "paras": [
                "I'd like to know which of the six guides get read and whether the download "
                "actually gets taken, because that tells me what to write next. Google Analytics "
                "is how I'd measure that.",
                "It doesn't run by default. Nothing is requested from Google, and no cookie is "
                "set, until you've been asked and said yes. Saying no thanks changes nothing "
                "about what you can read or download, and the answer sticks so you're not "
                "nagged. With JavaScript switched off, analytics never loads at all.",
                "If you do agree, what I see is aggregated: page views, visit counts, rough "
                "location, device type, which links got clicked, and what people typed into the "
                "search box. I can't identify you from any of it. Google Analytics 4 doesn't log "
                "or store visitors' IP addresses. Advertising cookies and personalisation stay "
                "switched off whatever you choose, because this site doesn't advertise anything.",
            ],
        },
        {
            "id": "search",
            "heading": "The search box",
            "paras": [
                "Searching runs entirely in your browser. All 144 strategies are already on the "
                "page, and typing filters what's shown. Nothing is sent to a server, because "
                "there isn't one doing any thinking.",
                "If you've agreed to analytics, the search term is recorded so I can see what "
                "people are looking for and can't find. That's honestly the single most useful "
                "thing this site could tell me. If you haven't agreed, it isn't recorded.",
            ],
        },
        {
            "id": "hosting",
            "heading": "Hosting, and the one thing I can't switch off",
            "paras": [
                "This site is hosted on GitHub Pages. GitHub's own documentation is explicit "
                "about this: when a GitHub Pages site is visited, the visitor's IP address is "
                "logged and stored for security purposes, whether or not the visitor has a "
                "GitHub account.",
                "That happens at the server, before any of my code runs, so consent doesn't come "
                "into it and I can't turn it off. I don't see those logs and I can't get at them. "
                "It's the same arrangement as almost any hosted website, but it's worth saying "
                "out loud rather than implying nothing at all is recorded.",
            ],
        },
        {
            "id": "downloads",
            "heading": "Downloads",
            "paras": [
                "The guide and the six infographics are free, and there's no gate, no form and "
                "no email address to hand over. Click and it downloads.",
                "If you've agreed to analytics I count that the download happened and which file "
                "it was. Not who took it.",
            ],
        },
        {
            "id": "children",
            "heading": "Children",
            "paras": [
                "This site is written for teachers and school leaders, not for pupils. It "
                "doesn't knowingly collect anything from children, and there's nothing here that "
                "asks anyone of any age for personal information.",
                "If you're sharing these pages with pupils, everything above applies to them "
                "exactly as it applies to you, and you can decline analytics on their behalf on "
                "a shared device.",
            ],
        },
        {
            "id": "rights",
            "heading": "Your rights, and how to complain",
            "paras": [
                "I don't hold a list, a database or a record with your name on it from this "
                "site, so in practice there's usually nothing for me to give you a copy of or "
                "delete. If you think I've got something of yours, ask and I'll deal with it.",
                "You can change your analytics answer at any time using the control below, or by "
                "clearing this site's data in your browser.",
                "For anything about this notice, get in touch through ictevangelist.com. If "
                "you're not happy with how I've handled your information, you can complain to "
                "the Information Commissioner's Office at ico.org.uk.",
            ],
        },
    ],
    "controller": {
        "heading": "Who's responsible",
        "rows": [
            ("Controller", "Mark Anderson, trading as ICT Evangelist."),
            ("What's collected", "Nothing that identifies you, unless you agree to analytics, "
                                 "and then only aggregated usage data."),
            ("Lawful basis for analytics", "Consent, given by choosing yes on the banner, and "
                                           "withdrawable at any time."),
            ("Processors", "Google (Google Analytics), only after consent. GitHub (hosting), "
                           "which logs visitor IP addresses for security."),
            ("Retention", "Analytics data is kept for the shortest period Google Analytics "
                          "allows. Nothing else is kept, because nothing else is collected."),
            ("Contact", "Via ictevangelist.com."),
        ],
    },
    "closing": "This notice covers this website and nothing else. It'll be updated whenever "
               "what's collected, or how it's handled, changes, and the date at the bottom of "
               "every page tells you when the site was last reviewed.",
}
