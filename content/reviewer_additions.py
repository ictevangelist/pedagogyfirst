# -*- coding: utf-8 -*-
"""
Additions written in response to the people who endorsed the original guide.

Each block answers something a named reviewer asked of the guide and which the
site did not yet do. Their words are in the guide's praise pages; these are the
gaps between what they valued and what the site delivered.
"""

# Zoë Elder called the guide "an elegant set of evidence-informed design
# principles". The site had 144 strategies and never said what holds them
# together, so the principles were left to be inferred.
PRINCIPLES = {
    "standfirst": "Six guides, one argument.",
    "intro": (
        "Any of these 144 strategies will work on its own. They hang together because "
        "the same handful of ideas keeps turning up underneath them, whichever chapter "
        "you're in. If you only take five things from the whole thing, take these."
    ),
    "items": [
        {
            "title": "Thinking is the thing being managed",
            "body": "Working memory is narrow and attention is finite. Nearly every strategy here "
                    "is doing one of two jobs: making room for thinking, or making sure the thinking "
                    "lands on what you want learned.",
            "seen_in": [("explanations-and-modelling", "Cognitive load"), ("retrieval-practice", "Desirable difficulties")],
        },
        {
            "title": "Effort in the right place beats comfort",
            "body": "Retrieval feels worse than rereading and works better. Feedback that asks a "
                    "question is harder than feedback that corrects, and it teaches more. When a "
                    "strategy feels inefficient in the lesson, that's often the point.",
            "seen_in": [("retrieval-practice", "The testing effect"), ("feedback", "Closing the gap")],
        },
        {
            "title": "The work belongs to the learner",
            "body": "If you supply the answer, the missing evidence, or the improved sentence, you "
                    "have done the thinking. Every chapter has a version of this: the effort has to "
                    "stay where the learning is meant to happen.",
            "seen_in": [("feedback", "Feedback and the learner"), ("metacognition-and-self-regulation", "Strategy knowledge and use")],
        },
        {
            "title": "You cannot teach what you haven't checked",
            "body": "Listening isn't learning, a nod isn't understanding, and the students who signal "
                    "confusion aren't the ones you most need to hear from. Every strategy that works "
                    "assumes you know where the class actually is.",
            "seen_in": [("formative-assessment", "Eliciting evidence"), ("questioning-and-discussion", "Participation and equity")],
        },
        {
            "title": "Scaffolds are meant to come down",
            "body": "Support that never fades produces students who can do it with you and not without "
                    "you. Plan the withdrawal at the same time as you plan the help.",
            "seen_in": [("explanations-and-modelling", "Modelling and worked examples"), ("metacognition-and-self-regulation", "Forethought and planning")],
        },
    ],
}

# Al Kingsley asked for technology that "has to genuinely add value that can be
# measured". The site told people what to do and never how they would know it
# had worked, which is the question a trust asks before it commits.
HOW_WOULD_YOU_KNOW = {
    "retrieval-practice": {
        "signal": "Performance on delayed tests, not on the lesson itself.",
        "body": "Retrieval practice makes lessons look worse and later assessments look better, so "
                "measuring it on the day tells you nothing useful. Compare a topic taught with "
                "spaced retrieval against one taught without, on a test at least two weeks later. "
                "Watch the gap between how confident students feel and how much they actually recall: "
                "if that gap is narrowing, calibration is improving too.",
    },
    "formative-assessment": {
        "signal": "How often teaching changed direction because of what came back.",
        "body": "The measure isn't how much evidence you gathered, it's how much of it altered the "
                "next five minutes. Ask a department to log, for a fortnight, every time a hinge "
                "question or a whiteboard round made them reteach rather than move on. If that number "
                "is near zero, the assessment is happening and the formative part isn't.",
    },
    "feedback": {
        "signal": "What students do next, not what you wrote.",
        "body": "Look at the work after the feedback, not the feedback itself. Sample a set and count "
                "how many pieces show a specific response to a specific comment. Time is the other "
                "measure worth having: marking hours per class per week, before and after moving to "
                "whole-class feedback, alongside whether the response rate held up.",
    },
    "questioning-and-discussion": {
        "signal": "Who speaks, and for how long.",
        "body": "This one is genuinely countable. Tally who gets asked over a fortnight and the type "
                "of question each student receives. Time a few student answers: if mean response "
                "length is rising, wait time is doing its work. A colleague with a tally sheet at the "
                "back will tell you more in twenty minutes than a term of self-report.",
    },
    "explanations-and-modelling": {
        "signal": "Whether students can do it without you, sooner.",
        "body": "Measure how many worked examples a class needs before independent practice holds up, "
                "and whether that number falls across a unit. Slide audits are the cheap version: "
                "count elements per slide before and after, and see whether check-for-understanding "
                "results improve as the count comes down.",
    },
    "metacognition-and-self-regulation": {
        "signal": "The size of the gap between predicted and actual marks.",
        "body": "Calibration is the most measurable thing in this chapter. Have students predict a "
                "mark before every assessment and log both. A narrowing gap over a term is real "
                "evidence that self-monitoring is improving, and it's a better indicator than any "
                "self-report questionnaire about how reflective students feel.",
    },
}

# Tom Sale said he would use the guide "to support staff development", and Jacqui
# Hughes that the strategies are "practical and usable straight away" as her college
# embeds digital across the curriculum. Neither had anything to run a session from.
WITH_YOUR_TEAM = {
    "standfirst": "Using this with your team",
    "intro": (
        "If you're taking this to a team rather than reading it on your own, here's how I'd "
        "actually run it, whether you've got twenty minutes in a briefing or a full INSET day."
    ),
    "sessions": [
        {
            "length": "20 minutes, department meeting",
            "title": "One chapter, one strategy each",
            "steps": [
                "Pick the chapter closest to your department's current priority.",
                "Everyone reads the infographic for five minutes and picks one strategy they don't already do.",
                "Round the table: which one, and what would you have to change to run it?",
                "Agree to try it twice before the next meeting. Nothing else.",
                "Open the next meeting by asking what happened, including what didn't work.",
            ],
        },
        {
            "length": "An hour, twilight",
            "title": "The thinking, not just the tips",
            "steps": [
                "Read the chapter's opening section together, the part on why these strategies.",
                "Discuss the idea underneath rather than the list: why does effortful retrieval beat rereading?",
                "In pairs, find two strategies in the chapter that share that mechanism.",
                "Each pair plans one into a specific lesson next week, with the checking built in.",
                "Set a date to look at what came back. Without that, nothing happens.",
            ],
        },
        {
            "length": "A day, INSET",
            "title": "Across the six",
            "steps": [
                "Morning: the five principles that run through all six guides, with staff finding examples of each in their own practice.",
                "Split into six groups, one chapter each, thirty minutes to become the department expert.",
                "Each group teaches their chapter back in ten minutes, using their own subject's examples.",
                "Afternoon: everyone commits to one strategy and one way of knowing whether it worked.",
                "Collect the commitments. Revisit them in six weeks, in public.",
            ],
        },
    ],
    "note": (
        "Everything on this site is free to use and share under Creative Commons for "
        "anything other than commercial use, so put the infographics in your slides, print "
        "them for the staffroom wall, put the chapters in your CPD library. No sign-up, no "
        "gate, no need to ask."
    ),
}
