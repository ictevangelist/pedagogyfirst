# -*- coding: utf-8 -*-
"""
Front and back matter taken from the definitive guide: the praise pages,
Mark's biography, and the work-with-Mark endorsements.

Kept as curated data rather than parsed at build time because the source
layout puts a lead testimonial and three or four supporting ones on each
spread, which does not survive automatic extraction cleanly.
"""

PRAISE = [
    {
        "quote": (
            "Pedagogy should always be our North Star in education. Learning remains the core "
            "business of every classroom, for every student, in every context. Anderson's guide "
            "keeps this principle firmly in view, offering a rich collection of evidence-informed, "
            "pedagogy-first strategies that can be applied across classrooms, curricula and "
            "systems. Practical, thoughtful and rooted in what matters most, this is a must-read "
            "for educators who want technology, strategy and classroom practice to truly and "
            "impactfully serve learning."
        ),
        "name": "Olly Lewis",
        "role": "Head of School, Amity International School Abu Dhabi",
        "lead": True,
    },
    {
        "quote": (
            "These guides provide an elegant set of evidence-informed design principles. They "
            "offer learning experiences that are served by technology, not driven by it. From "
            "these first principles, the guide offers a rich and full menu of evidence-informed, "
            "easily navigable ideas, all beautifully organised and codified."
        ),
        "name": "Dr Zoë Elder",
        "role": "Director of Education, Research & Innovation, ASDAN",
        "lead": True,
    },
    {
        "quote": (
            "Mark has done the hard thinking, so the rest of us don't have to. Every strategy here "
            "starts with the learning and treats technology as something that has to genuinely add "
            "value that can be measured, which is exactly the order schools keep getting wrong."
        ),
        "name": "Al Kingsley MBE",
        "role": "MAT Chair and EdTech CEO, NetSupport",
    },
    {
        "quote": (
            "This is an excellent and much needed resource for all school staff looking to use "
            "technology with care and purpose. It avoids gimmicks and trends, focusing instead on "
            "evidence-informed practice. Above all, it keeps the focus firmly where it belongs, on "
            "learners and learning."
        ),
        "name": "Emma Darcy",
        "role": "Director of Technology for Learning, Denbigh High School",
    },
    {
        "quote": (
            "This is a really strong, evidence-informed guide that keeps the focus exactly where it "
            "should be, on teaching and learning first. The strategies are practical and usable "
            "straight away, which makes it particularly helpful as we continue embedding digital "
            "across the curriculum in a purposeful and meaningful way."
        ),
        "name": "Jacqui Hughes",
        "role": "Head of Digital Innovation, Moulton College",
    },
    {
        "quote": (
            "This is another strong example of pedagogy led by purpose, grounded in cognitive "
            "science and focused on what genuinely supports learning rather than what is "
            "fashionable. It reflects a clear commitment to making thoughtful use of whatever "
            "tools are available, ensuring the right approach is chosen for the right activity at "
            "the right moment in time."
        ),
        "name": "Gemma Gwilliam",
        "role": "Head of Digital Learning, Education and Innovation, Portsmouth: The Digital City",
    },
    {
        "quote": (
            "Each guide Mark has produced is perfect for any teacher to pick and use straight away. "
            "The use of evidence-informed pedagogy and practical classroom strategies provides a "
            "clear link before any discussion of technology. I will use this guide to support staff "
            "development, inspire classroom practice and support teachers to make purposeful "
            "decisions about when technology genuinely adds value."
        ),
        "name": "Tom Sale",
        "role": "Assistant Head for Data, Reporting, EdTech and Innovation, North Gate British School, Ajman",
    },
    {
        "quote": (
            "I'm always on the lookout for resources that cut through the noise and get straight to "
            "what matters in the classroom. Mark's Pedagogy First guides are not tool or tech with "
            "learning theory bolted on; the pedagogy genuinely leads. Each guide distils a "
            "substantial body of research into strategies teachers can actually use on Monday "
            "morning. And as ever, Mark is generous with his sharing; no gatekeeping."
        ),
        "name": "Jo Fletcher-Saxon",
        "role": "Assistant Principal, Teaching & Learning, Ashton Sixth Form College",
    },
]

ABOUT = {
    "standfirst": (
        "Mark Anderson. Thirty years in education, and a leading voice on pedagogy and technology."
    ),
    "paragraphs": [
        "An award winning author, globally sought after keynote speaker, trainer and strategic "
        "consultant in education technology, AI and digital strategy. Mark works independently as "
        "ICT Evangelist and part time as Principal Education Consultant at NetSupport. He was the "
        "lead education and AI consultant on the BBC Bitesize Guide to AI.",
        "He co-authored the Amazon chart topping The EdTech Playbook with Olly Lewis, and his "
        "earlier Perfect ICT Every Lesson topped the Amazon charts too. He is a Founding Fellow of "
        "the Chartered College of Teaching, an Independent Thinking Associate, a member of the BCS "
        "Schools and Colleges committee, and an Apple Distinguished Educator, Google Certified "
        "Innovator and Microsoft Certified Educator.",
        "His blog won UK Education Blog of the Year, he co-founded the Digital Leader Network and "
        "the GESS award winning LearnLiveUAE, and he keynotes at the world's major education "
        "events, among them BETT and GESS.",
        "That reach is built on decades in the classroom and in a range of middle and senior "
        "leadership roles, from head of department to senior leader, alongside a spell as a local "
        "authority lead teacher for computing and the teaching and learning lead on Clevedon "
        "School's pioneering one-to-one rollout. One idea runs through all of it: good teaching "
        "comes first, and technology only helps once the teaching is right.",
    ],
}

WORK_WITH_MARK = {
    "standfirst": "Bring this thinking to your school or trust.",
    "body": (
        "Keynotes, INSET, workshops and strategic consultancy on pedagogy, AI and digital "
        "strategy, tailored to where your team is and built on a relationship over time."
    ),
    "quotes": [
        {
            "quote": (
                "Don't just book a one off. The magic comes from building a relationship over time "
                "where he can understand your needs and help you develop digital strategy in a "
                "sustainable way."
            ),
            "name": "Robbie McGrath",
            "role": "School Improvement Director, Nova Education Trust",
        },
        {
            "quote": (
                "Mark is a true edtech pioneer and a constant source of innovation, inspiration and "
                "support. The response from our staff was universally positive."
            ),
            "name": "Steve Bambury",
            "role": "Head of Digital Learning, JESS Dubai",
        },
        {
            "quote": (
                "Mark is an excellent communicator who delivers a clear and meaningful message. He "
                "exudes confidence and brings people with him."
            ),
            "name": "Paul Rickeard",
            "role": "CEO, DND Learning Trust",
        },
    ],
}
