"""Synthetic pediatric in-basket for the Jev triage demo. Every patient, message and chart value is FABRICATED.
Seed labels (urgency, category, owner, snippets, flags) are the author's reference answers, not clinician-adjudicated."""

PRACTICE = "Proctor Pediatrics (fictional primary care practice, 6 physicians, 1 NP, RN triage pool, scheduling pool, referrals & forms desk, billing office)"

URGENCY = {
    "high":   "Needs a human today, within hours: symptoms that could be worsening or dangerous, a child out of a critical medication within 24-48 hours, or any safety concern",
    "medium": "Should be handled within 1 business day: new but stable symptoms, a clinical question that affects care this week, results the family is worried about, a medication running out within a week",
    "low":    "Routine, 2-3 business days is fine: scheduling changes, forms, records, billing, thank-you notes, general questions with no active symptoms",
}

CATEGORIES = {
    "rx_refill":         "Asking for a refill, renewal, or prior authorization of an existing medication",
    "medication_question": "Question about dosing, side effects, stopping, or safety of a medication or vaccine",
    "new_symptom":       "A new illness, injury, or symptom the family wants advice about",
    "chronic_followup":  "An update or question about a known chronic condition (asthma, diabetes, ADHD, depression, etc.)",
    "test_results":      "Question about a lab, imaging, or test result, or whether a result is back",
    "scheduling":        "Book, move, or cancel an appointment",
    "forms_paperwork":   "School, sports, camp, daycare, work, or medical-clearance forms and letters",
    "referral":          "Status or request for a specialist referral",
    "billing_insurance": "Bills, charges, coverage, or insurance questions",
    "records_request":   "Send or release medical or immunization records",
    "general_admin":     "Thank-you notes, general practice questions, confidential-care access questions, anything else",
}

OWNERS = {
    "nursing":     "RN triage pool: symptom triage, protocol refills, dosing questions, results that are back and normal, prior authorizations",
    "physician":   "The child's PCP: clinical decisions, abnormal results, controlled substances, mental health, anything needing medical judgment beyond a nursing protocol",
    "scheduling":  "Scheduling pool: booking, moving, and cancelling visits",
    "forms_desk":  "Referrals & forms desk: forms, letters, records release, referral status",
    "billing":     "Billing office: charges, statements, insurance coverage",
}

# The mini-prompt library. Epic-style drafting has moved from one monolithic prompt to small snippets
# assembled per message; Jev decides which ones to load.
SNIPPETS = {
    "med_list":            "Active medication list with doses and last-fill dates",
    "allergies":           "Allergy and adverse-reaction list",
    "recent_labs":         "Resulted labs from the last 12 months with reference ranges",
    "pending_results":     "Ordered tests that have not resulted yet",
    "problem_list":        "Active problem list / chronic diagnoses",
    "last_visit":          "Summary and plan from the most recent visit",
    "upcoming_appts":      "Upcoming scheduled appointments",
    "scheduling_rules":    "Practice visit types, open-slot rules, same-day sick policy",
    "immunizations":       "Immunization record and what is due",
    "forms_status":        "Last well visit date and which forms are on file / can be completed without a visit",
    "weight_dosing":       "Most recent weight and weight-based acetaminophen/ibuprofen dosing table",
    "refill_protocol":     "Nursing refill protocol: which meds RNs may renew, controlled-substance rules, visit-required rules",
    "referral_status":     "Open referrals and where each is in the process",
    "insurance_billing":   "Coverage, copays, preventive-vs-sick billing rules, prior-auth process",
    "triage_protocol":     "Pediatric telephone triage red flags (call 911 / ED now / same-day) for the symptom mentioned",
    "confidentiality":     "Adolescent confidential-care rules: what proxies can see, confidential reply routing, state minor-consent rules",
}

PRACTICE_SNIPPETS = {
    "scheduling_rules": "Visit types: well child (30 min, book up to 3 mo out), sick visit (15 min, same-day slots open 8am daily), follow-up (15-20 min), telehealth (15 min, weekday evenings). Same-day sick slots are held for symptoms triaged by RN. Rescheduling is fine without a reason; no fee for changes >24h out.",
    "refill_protocol": "RNs may renew per protocol, up to 90 days, if the patient was seen for that condition in the last 12 months: inhaled steroids, albuterol, montelukast, topical steroids, allergy meds, insulin and diabetic supplies, iron, vitamins. NOT per protocol (route to PCP): controlled substances (stimulants, benzodiazepines), antidepressants in patients under 18 with a change in mood, any new medication, anything with a missed follow-up. Prior authorizations are started by the RN pool with the PA form; typical turnaround 3-5 business days.",
    "insurance_billing": "Preventive visits and routine vaccines are covered at 100% for most plans when billed as preventive; if a sick problem is also addressed at a well visit, a separate office-visit charge may apply. Billing office reviews disputed charges within 10 business days. Confidential services for adolescents (reproductive health, STI testing) can be billed to the confidential-services fund so no Explanation of Benefits goes to the policyholder. Prior auth: RN pool submits, pharmacy notified on approval.",
    "triage_protocol": "RED (call 911 / ED now): trouble breathing, blue or gray lips, infant <3 mo with fever >=100.4F, head injury with repeated vomiting / unusual sleepiness / confusion, suicidal thoughts with plan or intent, seizure, signs of anaphylaxis, severe dehydration. ORANGE (same-day, RN calls within 1 hour): wheezing not relieved by albuterol, fever >3 days, ear pain with fever, new widespread rash on an antibiotic without breathing symptoms, glucose >300 with ketones, suicidal thoughts without a plan. YELLOW (visit within 24-48 h or telehealth): cough >2 weeks, persistent constipation, stable rash. Never advise over the portal for RED; phone the family and document.",
    "confidentiality": "Patients 12-17 have a confidential MyChart account. Parent/guardian proxies cannot see messages the adolescent sends, or notes about sexual health, mental health or substance use. Replies to a teen's confidential message must go only to the teen's account. PA law lets minors consent to STI testing and treatment, contraception, and outpatient mental health care at 14+. Safety exception: imminent risk of harm is shared with the guardian and emergency services as needed.",
}

def P(name, age, sex, wt, problems=(), meds=(), allergies=("NKDA",), labs=(), pending=(), last_visit="", appts=(), imms="Up to date for age.", forms="", referrals=()):
    return dict(name=name, age=age, sex=sex, weight_kg=wt, problems=list(problems), meds=list(meds), allergies=list(allergies), labs=list(labs),
                pending=list(pending), last_visit=last_visit, appts=list(appts), imms=imms, forms=forms, referrals=list(referrals))

PATIENTS = {
 "liam":   P("Liam Okafor", "9 y", "M", 29.5, ["Persistent asthma, moderate"], ["Fluticasone HFA 110 mcg 2 puffs BID (last fill 2026-06-30, 30-day supply)", "Albuterol HFA 90 mcg 2 puffs q4h PRN"],
             last_visit="2026-07-15 asthma follow-up: well controlled on fluticasone, continue, recheck in 3 months.", appts=["2026-10-14 asthma follow-up, Dr. Patel"], forms="Last well visit 2026-02-10. School asthma action plan on file."),
 "maya":   P("Maya Chen", "4 mo", "F", 6.4, ["Born at 36 weeks, otherwise healthy"], [], last_visit="2026-08-20 4-month well visit: normal exam, growing well.", imms="2-month and 4-month vaccines given."),
 "ava":    P("Ava Romano", "13 y", "F", 46.0, [], [], last_visit="2026-03-12 well visit (sports physical completed, cleared for all sports).", imms="Tdap, MenACWY, HPV #1 given 2026-03-12. HPV #2 due.",
             forms="Last well visit 2026-03-12 (within 12 months). PIAA sports form can be completed from this visit without a new appointment."),
 "noah":   P("Noah Williams", "7 y", "M", 23.0, [], [], appts=["2026-09-24 3:00 pm follow-up (ear recheck), Dr. Lee"], last_visit="2026-09-10 sick visit: left otitis media, amoxicillin x10 days."),
 "ethan":  P("Ethan Brooks", "2 y", "M", 12.8, ["Iron deficiency (resolved)"], [], labs=["2026-09-15 Blood lead (venous) 6 mcg/dL (reference <3.5; CDC reference value 3.5)", "2026-09-15 Hemoglobin 11.9 g/dL (ref 11.0-14.0)"],
             last_visit="2026-09-12 2-year well visit: routine lead screen ordered; family recently moved to a rowhouse built in 1920.", appts=[]),
 "jordan": P("Jordan Diaz", "16 y", "NB", 58.0, ["Major depressive disorder, moderate", "Generalized anxiety"], ["Sertraline 50 mg daily (started 2026-08-25)"],
             last_visit="2026-08-25 behavioral health visit (confidential): PHQ-9 16, no SI at that time, started sertraline, safety plan reviewed, follow-up 4 weeks.", appts=["2026-09-29 follow-up, Dr. Patel"]),
 "chloe":  P("Chloe Martin", "6 y", "F", 20.5, [], [], last_visit="2026-09-02 sick visit plus flu vaccine given same visit.", imms="Influenza 2026-09-02."),
 "sophia": P("Sophia Nguyen", "5 y", "F", 18.2, [], [], allergies=["Penicillin (hives, 2023)"], last_visit="2026-05-01 well visit, healthy."),
 "leo":    P("Leo Garcia", "2 y", "M", 12.7, [], [], last_visit="2026-09-05 2-year well visit, healthy."),
 "olivia": P("Olivia Park", "10 y", "F", 32.0, ["ADHD, combined type"], ["Dexmethylphenidate XR (Focalin XR) 10 mg every morning (last fill 2026-08-24)"],
             last_visit="2026-06-02 ADHD follow-up: good response, appetite mildly down, weight stable. Next check 3 months.", forms="School medication administration form last signed 2025-09-01 (expired).", appts=[]),
 "zara":   P("Zara Ahmed", "11 y", "F", 36.0, ["Chronic abdominal pain, suspected celiac"], [], labs=["2026-08-01 tTG-IgA 48 U/mL (ref <15)"],
             referrals=["Pediatric GI, placed 2026-08-14; status: awaiting prior authorization from insurer since 2026-08-20; family not yet contacted"], last_visit="2026-08-14: elevated tTG, referred to GI."),
 "mia":    P("Mia Johnson", "3 y", "F", 14.5, [], [], imms="Up to date: DTaP x4, IPV x3, MMR #1, Varicella #1, HepA x2, HepB x3, Hib x4, PCV x4, influenza 2025.", forms="Immunization certificate can be released to daycare with a signed parent release on file (release signed 2026-01-05)."),
 "jack":   P("Jack Rivera", "8 y", "M", 26.0, [], [], last_visit="2026-09-14 sick visit with Dr. Patel: influenza A, supportive care."),
 "mateo":  P("Mateo Hernandez", "4 y", "M", 16.8, ["Reactive airway disease (2 prior wheezing episodes)"], ["Albuterol HFA 90 mcg PRN (last fill 2025-11-02)"],
             last_visit="2025-11-02 sick visit: wheezing with viral illness, albuterol given.", appts=[]),
 "zoe":    P("Zoe Thompson", "3 y", "F", 14.0, [], ["Amoxicillin 90 mg/kg/day divided BID x10 days (started 2026-09-18)"], last_visit="2026-09-18 sick visit: right acute otitis media, amoxicillin started."),
 "sam":    P("Sam Patel", "14 y", "M", 50.0, [], [], last_visit="2026-04-10 well visit."),
 "aiden":  P("Aiden Kowalski", "12 y", "M", 40.0, ["Moderate-to-severe atopic dermatitis"], ["Dupilumab 300 mg SC every 4 weeks (last dose 2026-08-27; prior auth expires 2026-09-30)"],
             last_visit="2026-07-20 dermatology co-management visit: skin clear, continue dupilumab.", appts=[]),
 "riley":  P("Riley Evans", "17 y", "F", 60.0, [], [], last_visit="2026-01-15 well visit (confidential portion documented separately).", imms="Up to date."),
 "carter": P("Carter Lewis", "11 y", "M", 38.0, ["Type 1 diabetes (dx 2024)"], ["Insulin glargine 14 units nightly", "Insulin lispro per carb ratio 1:12, correction 1 unit per 50 over 150", "Ketone strips"],
             labs=["2026-07-02 HbA1c 8.4%"], last_visit="2026-07-02 diabetes visit with endocrine co-management; sick-day rules reviewed.", appts=["2026-10-02 endocrinology"]),
 "harper": P("Harper Scott", "3 y 11 mo", "F", 16.0, [], [], last_visit="2025-10-01 3-year well visit.", imms="Due at 4 years: DTaP #5, IPV #4, MMR #2, Varicella #2. Influenza due.", forms="Pre-K health form requires a well visit within 12 months (last one 2025-10-01, expiring)."),
 "ella":   P("Ella Wright", "8 y", "F", 25.0, [], [], labs=["2026-09-19 Rapid strep negative"], pending=["2026-09-19 Throat culture (ordered, expected 48-72 h)"], last_visit="2026-09-19 sick visit: sore throat, rapid strep negative, culture sent."),
 "eli":    P("Eli Morgan", "3 y", "M", 15.0, ["Recurrent otitis media (6 episodes in 12 months)"], [], referrals=["ENT: seen 2026-08-28, tympanostomy tubes scheduled 2026-10-06; ENT requests pre-op clearance letter from PCP (received 2026-09-02)"],
             last_visit="2026-08-15 sick visit: otitis media.", forms="Pre-op clearance requires PCP review; no visit needed if seen in last 30 days (last visit 2026-08-15 is 38 days ago)."),
 "grace":  P("Grace Kim", "5 y", "F", 18.5, [], [], last_visit="2026-09-21 telehealth sick visit: viral gastroenteritis, home care."),
 "owen":   P("Owen Baker", "5 y", "M", 19.0, [], [], last_visit="2026-05-20 well visit, healthy.", appts=[]),
 "lucas":  P("Lucas Hill", "6 y", "M", 21.0, [], [], last_visit="2026-02-02 well visit."),
 "isla":   P("Isla Adams", "18 mo", "F", 10.8, ["Iron deficiency anemia"], ["Ferrous sulfate 15 mg elemental iron daily (started 2026-06-10, planned 3 months)"],
             labs=["2026-06-08 Hemoglobin 9.6 g/dL (ref 10.5-13.5)", "2026-09-16 Hemoglobin 11.8 g/dL (ref 10.5-13.5)", "2026-09-16 Ferritin 14 ng/mL (ref 12-150)"],
             last_visit="2026-06-10: iron deficiency anemia, iron x3 months then recheck; plan to continue 1-2 months after Hb normalizes to replete stores."),
 "ruby":   P("Ruby Collins", "12 mo", "F", 9.5, [], [], imms="MMR #1 and Varicella #1 due now (12-month vaccines).", last_visit="2026-06-20 9-month well visit. Household: brother (6 y) on chemotherapy for ALL.", appts=["2026-09-30 12-month well visit"]),
 "bao":    P("Bao Tran", "6 y", "M", 20.0, [], [], last_visit="2026-04-02 well visit, healthy.", appts=[]),
 "henry":  P("Henry Price", "9 y", "M", 30.0, ["Persistent asthma, moderate"], ["Budesonide-formoterol 80/4.5 2 puffs BID (started 2026-07-01)", "Albuterol HFA PRN"],
             last_visit="2026-07-01: step-up to budesonide-formoterol, follow-up in 3 months to consider step-down.", appts=["2026-10-08 asthma follow-up, Dr. Nguyen"]),
}

def M(id, pt, sender, text, urg, cat, owner, snippets, **flags):
    f = dict(safety=False, multi_issue=False, confidential=False, frustrated=False, non_english=False, evisit=False, needs_reply=True); f.update(flags)
    return dict(id=id, patient=pt, sender=sender, text=text, seed=dict(urgency=urg, category=cat, owner=owner, snippets=sorted(snippets), **f))

PARENT, TEEN = "Parent/guardian (proxy account)", "Patient (adolescent's own confidential account)"

MESSAGES = [
 M("M01", "liam", PARENT, "Hi, can you send a refill for Liam's Flovent? He only has a couple puffs left and we leave for my mom's on Friday. CVS on Main St. Thanks!",
   "medium", "rx_refill", "nursing", ["med_list", "refill_protocol", "last_visit", "problem_list"]),
 M("M02", "maya", PARENT, "Maya has been breathing really fast since this morning and it looks like her ribs are sucking in. When she coughs her lips look a little blue. She's 4 months. Is this something to worry about or should we wait for our appointment?",
   "high", "new_symptom", "nursing", ["triage_protocol", "problem_list"], safety=True),
 M("M03", "ava", PARENT, "Hello, Ava needs the PIAA sports form signed for soccer tryouts on Oct 15. She had her physical with you in March. Can I drop the form off or do you need to see her again?",
   "low", "forms_paperwork", "forms_desk", ["forms_status", "immunizations"]),
 M("M04", "noah", PARENT, "Can we move Noah's Thursday 3pm appointment to sometime next week? Anytime after 3:30 works since he has school.",
   "low", "scheduling", "scheduling", ["upcoming_appts", "scheduling_rules"]),
 M("M05", "ethan", PARENT, "I saw Ethan's lead test came back in MyChart as 6. It has a little flag next to it. Is that bad?? What are we supposed to do? We just moved into an old house.",
   "medium", "test_results", "physician", ["recent_labs", "last_visit", "problem_list"]),
 M("M06", "jordan", TEEN, "honestly i dont really see the point anymore. the new med isnt helping and ive been thinking it would be easier for everyone if i just wasnt here. please dont tell my mom",
   "high", "chronic_followup", "physician", ["med_list", "problem_list", "last_visit", "triage_protocol", "confidentiality"], safety=True, confidential=True),
 M("M07", "chloe", PARENT, "We got a bill for $240 from the Sept 2 visit. I thought the flu shot was free with our insurance?? Can someone please look at this.",
   "low", "billing_insurance", "billing", ["insurance_billing", "immunizations", "last_visit"]),
 M("M08", "sophia", PARENT, "Sophia has had a fever up to 102.5 for 3 days now. Motrin brings it down and she's drinking OK but today she says her ear really hurts. Should we bring her in?",
   "high", "new_symptom", "nursing", ["triage_protocol", "allergies", "weight_dosing", "scheduling_rules"]),
 M("M09", "leo", PARENT, "How much children's Tylenol can I give Leo? He just turned 2 and weighs about 28 lbs. The box says to ask a doctor for under 2 so I wasn't sure.",
   "low", "medication_question", "nursing", ["weight_dosing", "allergies", "med_list"]),
 M("M10", "olivia", PARENT, "Three things: 1) Olivia needs her Focalin XR 10 refilled, she's out next week. 2) School says they need a new medication form for the nurse's office. 3) She's been getting headaches most afternoons, could that be from the medicine?",
   "medium", "rx_refill", "physician", ["med_list", "refill_protocol", "forms_status", "last_visit", "problem_list"], multi_issue=True),
 M("M11", "zara", PARENT, "Any update on the GI referral? It's been 5 weeks and nobody has called us. Zara is still having stomach pain almost every day.",
   "medium", "referral", "forms_desk", ["referral_status", "insurance_billing", "recent_labs"], frustrated=True),
 M("M12", "mia", PARENT, "Please send Mia's shot records to her new daycare, Little Acorns. Their fax is 215-555-0142. Thank you!",
   "low", "records_request", "forms_desk", ["immunizations", "forms_status"]),
 M("M13", "jack", PARENT, "Just wanted to say thank you to Dr. Patel for taking such good care of Jack last week. He's back to school and feeling great!",
   "low", "general_admin", "physician", ["last_visit"], needs_reply=False),
 M("M14", "mateo", PARENT, "Hola, mi hijo Mateo tiene tos desde hace dos semanas y ahora le silba el pecho en la noche. Usamos el inhalador pero ya casi no tiene. ¿El doctor lo puede ver esta semana?",
   "medium", "new_symptom", "nursing", ["triage_protocol", "problem_list", "med_list", "scheduling_rules", "refill_protocol"], non_english=True, multi_issue=True),
 M("M15", "zoe", PARENT, "Zoe started the amoxicillin 4 days ago for her ear and now she has a red blotchy rash all over her belly and back. She's breathing fine and acting normal. Should we stop the medicine?",
   "high", "medication_question", "nursing", ["med_list", "allergies", "triage_protocol", "last_visit"]),
 M("M16", "sam", PARENT, "Hi, just checking about the thing we talked about at the last appointment. Should we still go ahead with it?",
   "low", "general_admin", "physician", ["last_visit"]),
 M("M17", "aiden", PARENT, "The pharmacy says insurance needs a new prior authorization for Aiden's Dupixent. His next shot is due in 5 days and they won't fill it without it.",
   "medium", "rx_refill", "nursing", ["med_list", "insurance_billing", "refill_protocol", "problem_list"]),
 M("M18", "riley", TEEN, "Can I get tested for STDs without my parents finding out? Would it show up on their insurance?",
   "medium", "general_admin", "nursing", ["confidentiality", "insurance_billing", "scheduling_rules"], confidential=True),
 M("M19", "carter", PARENT, "Carter's sugars have been 280-350 all weekend even with correction doses. Ketones are small this morning. He says he feels fine. What should we do?",
   "high", "chronic_followup", "nursing", ["med_list", "problem_list", "triage_protocol", "recent_labs", "weight_dosing"]),
 M("M20", "harper", PARENT, "Need to book Harper's 4 year checkup. She also needs her shots and the health form for pre-K.",
   "low", "scheduling", "scheduling", ["scheduling_rules", "immunizations", "forms_status", "upcoming_appts"]),
 M("M21", "ella", PARENT, "Did Ella's strep culture come back yet? They said 48 hours and it's been 3 days.",
   "low", "test_results", "nursing", ["pending_results", "recent_labs"]),
 M("M22", "eli", PARENT, "This is the THIRD message I've sent. Nobody has called me back about Eli's clearance letter for his ear tube surgery on Oct 6. If this isn't done the surgery gets cancelled. I'm about ready to switch practices.",
   "medium", "forms_paperwork", "physician", ["referral_status", "forms_status", "last_visit", "problem_list"], frustrated=True),
 M("M23", "grace", PARENT, "I need a note for my job saying I was home with Grace Monday and Tuesday because she was sick. You saw her on video Monday.",
   "low", "forms_paperwork", "forms_desk", ["last_visit"]),
 M("M24", "owen", PARENT, "Owen has been constipated for about 2 weeks. He only goes every 4 or 5 days and it's hard and it hurts him. We tried more water and prune juice. What else can we try?",
   "low", "new_symptom", "physician", ["weight_dosing", "allergies", "med_list", "problem_list", "triage_protocol"], evisit=True),
 M("M25", "lucas", PARENT, "Lucas fell off the monkey bars about an hour ago and hit his head. He threw up twice and now he's really sleepy. Is it OK to let him nap?",
   "high", "new_symptom", "nursing", ["triage_protocol"], safety=True),
 M("M26", "isla", PARENT, "Isla's follow-up blood test was normal! Does that mean we can stop the iron drops now?",
   "low", "medication_question", "physician", ["recent_labs", "med_list", "last_visit"]),
 M("M27", "ruby", PARENT, "Ruby has her 1 year shots next week. Is it safe for her to get the MMR when her brother is on chemo? I don't want to make him sick.",
   "low", "medication_question", "physician", ["immunizations", "last_visit", "upcoming_appts"]),
 M("M28", "henry", PARENT, "Since starting the Symbicort Henry has been doing so much better, only needed albuterol once this month! Do we still need the follow-up in October?",
   "low", "chronic_followup", "physician", ["med_list", "upcoming_appts", "last_visit", "problem_list"]),
 M("M29", "bao", PARENT, "Chào bác sĩ, con tôi Bảo bị sốt 38,9 độ từ tối hôm qua và ho nhẹ. Bé vẫn ăn uống và chơi bình thường. Tôi có thể cho bé uống bao nhiêu Tylenol? Bé nặng khoảng 20 kg. Có cần đưa bé đến khám không?",
   "medium", "new_symptom", "nursing", ["weight_dosing", "allergies", "triage_protocol", "med_list", "scheduling_rules"], non_english=True, multi_issue=True),
]

FLAGS = {
    "safety":       ("The message describes a possible emergency or safety risk that needs a phone call or 911/ED advice now, not a portal reply (breathing difficulty, blue lips, head injury with vomiting or sleepiness, suicidal thoughts, anaphylaxis, seizure).",
                     "No emergency or safety risk is described; the situation can wait for a normal portal or phone reply."),
    "multi_issue":  ("The message contains two or more distinct requests that would normally be handled by different people or workflows (for example a refill plus a form plus a new symptom).",
                     "The message is about one request or one closely related problem."),
    "confidential": ("The message involves adolescent confidential care (sexual/reproductive health, mental health, substance use) or explicitly asks that a parent not be told.",
                     "Nothing in the message involves confidential adolescent care."),
    "frustrated":   ("The sender expresses frustration, anger, a complaint about the practice, repeated unanswered messages, or a threat to leave.",
                     "The tone is neutral, polite, or appreciative."),
    "non_english":  ("The message is written mostly in a language other than English.", "The message is written in English."),
    "evisit":       ("The family is asking for new clinical evaluation and treatment advice for a non-urgent problem that a clinician could manage through the portal without a visit (a billable e-visit).",
                     "The message is administrative, an emergency, a simple result/refill/dosing question, or needs an in-person exam."),
    "needs_reply":  ("The sender is asking a question or requesting an action that requires a response.", "The message is informational only (thanks, an FYI update) and needs no action."),
}
