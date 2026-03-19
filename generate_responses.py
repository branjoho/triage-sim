#!/usr/bin/env python3
"""
Generate 25-key chat_responses for all 20 cases in cases.json.
No API calls — responses are pre-written inline.
"""
import json
import os

CASES_FILE = os.path.join(os.path.dirname(__file__), "cases.json")

new_responses = {}

# CASE 1: Apneic Infant, 3-month-old, GCS 8 -> nonverbal caregiver
new_responses[1] = {
    "vitals": "HR 180, RR 6, SpO2 52%, Temp 38.1\u00b0C, BP 70/40, cap refill 5s, GCS 8.",
    "appearance": "Limp infant with agonal gasping respirations. Central cyanosis present.",
    "respiratory": "Markedly decreased air entry bilaterally with diffuse crackles. No retractions visible due to severe muscle hypotonia. Agonal gasping at a rate of 6.",
    "neuro": "Minimally responsive. Pupils equal and sluggishly reactive. Fontanelle flat. Severe hypotonia throughout.",
    "skin": "Central cyanosis. Skin cool to touch.",
    "cardiac": "Tachycardic at 180. Capillary refill delayed at 5 seconds. Hypotensive at 70/40.",
    "abdominal": "Abdomen soft, non-distended. No hepatosplenomegaly appreciated.",
    "hpi": "He was in the waiting room and he just turned blue and stopped breathing \u2014 it was maybe 30 seconds. Then he started taking these gasping breaths. He was seen at the clinic 3 days ago for a cold.",
    "onset": "It happened in the waiting room, maybe 20 minutes ago. He was sniffly for a few days before this, but nothing like this.",
    "pmh": "He was born at 35 weeks. No other hospital stays. He's up to date on his shots.",
    "medications": "He's not on any medications.",
    "allergies": "No allergies that I know of.",
    "pain": "I don't know, I wasn't there for that part. He's not really responding to anything right now.",
    "interventions": "I don't think anyone gave him anything before the ambulance got here. We just ran to get help.",
    "hydration": "He was feeding okay earlier today \u2014 breastfeeding like normal. But since the episode he hasn't had anything.",
    "fever_history": "He felt warm to me this morning but I didn't take his temperature. The clinic said he just had a cold.",
    "behavior": "Before this he was fussier than usual, kind of sleepy. But nothing like this \u2014 he's completely limp now.",
    "feeding": "He was breastfeeding fine up until a few hours ago. Since the episode he hasn't been able to eat at all.",
    "urinary": "He had a wet diaper earlier today, I think. I'm not sure about recently.",
    "exposure": "His older sister had a runny nose last week. No one else has been really sick around him.",
    "immunization": "He's had his 2-month shots. I think he's up to date.",
    "family_history": "No family history of seizures or anything like that. His sister is healthy.",
    "caregiver_concern": "I'm terrified. He just stopped breathing. Is he going to be okay? He's never done anything like this before.",
    "review_of_systems": "He had a runny nose and a little cough for a few days. No vomiting or diarrhea. Just the cold symptoms, and then this.",
    "unknown": "I'm sorry, I'm so scared right now \u2014 I don't understand what you're asking. Can you say that differently?"
}

# CASE 2: Anaphylaxis, 4-year-old, GCS 14 -> standard caregiver (father)
new_responses[2] = {
    "vitals": "HR 168, RR 34, SpO2 90%, Temp 37.2\u00b0C, BP 72/40, cap refill 4s, GCS 14.",
    "appearance": "Child is anxious and crying. Diffuse urticaria visible on face, trunk, and extremities. Bilateral periorbital angioedema.",
    "respiratory": "Audible inspiratory stridor. Diffuse expiratory wheeze bilaterally. Intercostal retractions present. Tongue appears mildly swollen.",
    "neuro": "Alert but anxious and crying. GCS 14. Following commands.",
    "skin": "Diffuse urticaria on trunk, face, and extremities. Bilateral periorbital angioedema. Tongue mildly swollen.",
    "cardiac": "Tachycardic at 168. Hypotensive at 72/40. Capillary refill delayed at 4 seconds.",
    "abdominal": "Abdomen soft. No focal tenderness appreciated.",
    "hpi": "She ate a peanut butter cookie at a birthday party \u2014 we didn't know there were peanuts in it. Within minutes she broke out in hives everywhere and started making this wheezing sound. Her throat is swelling up. I gave her Benadryl in the car but it doesn't seem like it helped.",
    "onset": "It started about 15 minutes ago at the birthday party. She took a bite of the cookie and it happened really fast.",
    "pmh": "She has a peanut and tree nut allergy \u2014 diagnosed when she was 2. She has an EpiPen prescribed but we didn't have it with us today. She's never had a reaction this bad before. No asthma.",
    "medications": "She doesn't take any daily medications. She has an EpiPen prescribed but we left it at home.",
    "allergies": "Peanuts and tree nuts. It was diagnosed when she was 2. This is the worst reaction she's ever had.",
    "pain": "She's saying her throat feels tight and it hurts. She keeps grabbing at her neck.",
    "interventions": "I gave her one dose of children's Benadryl \u2014 12.5 milligrams \u2014 in the car on the way here. I didn't have the EpiPen.",
    "hydration": "She was drinking juice at the party right before this happened. She hasn't had anything since.",
    "fever_history": "No fever. She was perfectly fine before the cookie.",
    "behavior": "She's really scared and crying. She keeps saying she can't breathe well. Normally she's a happy, active kid.",
    "feeding": "She was eating and drinking fine at the party. She only had one bite of the cookie before we realized.",
    "urinary": "She went to the bathroom normally at the party. No problems there.",
    "exposure": "Just the peanut butter cookie. No new foods, no bee stings, no new soaps or anything else today.",
    "immunization": "She's up to date on all her shots.",
    "family_history": "I have a shellfish allergy but nothing this severe. No one in the family has had anaphylaxis before.",
    "caregiver_concern": "She's never reacted this badly. Her face is so swollen and she's making that terrible breathing sound. I should have had the EpiPen. Please help her.",
    "review_of_systems": "No vomiting or diarrhea yet. She's complaining about her throat being tight. The hives are everywhere. No belly pain that she's mentioned.",
    "unknown": "I'm sorry, I'm really panicked right now \u2014 can you ask me that a different way?"
}

# CASE 3: Submersion, 8-year-old, GCS 3 -> nonverbal caregiver
new_responses[3] = {
    "vitals": "HR 44, RR 4, SpO2 64%, Temp 34.8\u00b0C, BP 60/30, cap refill 6s, GCS 3.",
    "appearance": "Unresponsive child. Cyanotic. No purposeful movement. Agonal gasping respirations.",
    "respiratory": "Agonal gasping respirations at a rate of 4. BVM ventilation in progress on arrival by EMS.",
    "neuro": "Unresponsive to pain. GCS 3. Pupils fixed and dilated at 5mm bilaterally. No purposeful movement.",
    "skin": "Cyanotic. Cool, mottled skin. Hypothermic.",
    "cardiac": "Bradycardic at 44. Hypotensive at 60/30. Capillary refill markedly delayed at 6 seconds.",
    "abdominal": "Abdomen soft. No distension noted.",
    "hpi": "I found him face-down in the pool. I don't know how long he was in there \u2014 maybe 4 to 6 minutes. I pulled him out and started CPR right away. The paramedics took over when they got there. They said his heart started again a few minutes ago.",
    "onset": "I found him maybe 20 minutes ago. He was playing in the backyard and I went inside for just a few minutes. When I came back out he was in the pool, face-down.",
    "pmh": "He's a healthy kid. No medical problems. No medications. All his vaccinations are up to date.",
    "medications": "He doesn't take any medications.",
    "allergies": "No allergies that I know of.",
    "pain": "I don't know, I wasn't there for that part. He hasn't responded to anything since I found him.",
    "interventions": "I started CPR as soon as I pulled him out. The neighbors called 911. The paramedics continued CPR and used the bag thing to help him breathe. They said his heart restarted about 3 minutes before we got here.",
    "hydration": "He had lunch and was drinking water before he went outside. That was maybe an hour before I found him.",
    "fever_history": "No fever. He was completely fine today. Running around, playing \u2014 totally normal.",
    "behavior": "He was his normal self all day \u2014 running around, playing in the yard. I don't know how he ended up in the pool. He knows how to swim a little bit.",
    "feeding": "He ate lunch about an hour before. Normal appetite. Nothing unusual.",
    "urinary": "I don't know, I wasn't there for that part. Everything was normal earlier today.",
    "exposure": "He was just in our backyard. No chemicals or anything. Just the pool water.",
    "immunization": "He's fully vaccinated. Up to date on everything.",
    "family_history": "No family history of seizures or heart problems. Everyone in the family is healthy.",
    "caregiver_concern": "Please save my son. I found him in the pool and I don't know how long he was under. I did CPR but I don't know if I did it right. Please, is he going to make it?",
    "review_of_systems": "He was completely healthy today. No illness, no complaints. I don't know, I wasn't there for that part \u2014 I just found him in the water.",
    "unknown": "I'm sorry, I can't think straight right now. Can you ask me that again?"
}

# CASE 4: Toddler fever/petechiae, 18-month-old, GCS 14 -> standard caregiver
new_responses[4] = {
    "vitals": "HR 148, RR 32, SpO2 98%, Temp 39.8\u00b0C, BP 88/54, cap refill 3s, GCS 14.",
    "appearance": "Fussy but consolable toddler. Mildly decreased muscle tone noted.",
    "respiratory": "No respiratory distress. Lungs clear to auscultation bilaterally.",
    "neuro": "Fussy but consolable. Anterior fontanelle flat. No nuchal rigidity appreciated, though difficult to fully assess. Mildly decreased muscle tone.",
    "skin": "Non-blanching petechiae distributed across trunk and bilateral lower extremities, largest measuring 3mm. No purpuric plaques.",
    "cardiac": "Mildly tachycardic at 148. Borderline tachypneic. Capillary refill 3 seconds.",
    "abdominal": "Abdomen soft, non-tender. Mucous membranes moist.",
    "hpi": "She's had a fever since last night \u2014 it was 40.1 at home. Then about 3 hours ago we noticed these little spots on her belly and legs. They don't go away when you press on them. She's been fussier than normal and not as playful, but she does look at us and respond.",
    "onset": "The fever started about 12 hours ago. The spots showed up maybe 3 hours ago and they seem to be spreading.",
    "pmh": "She was born full-term. She's had all her vaccines on schedule. No hospitalizations, no surgeries. She's been a healthy baby.",
    "medications": "She's not on any medications. We gave her Tylenol about 6 hours ago but haven't given any more since.",
    "allergies": "No known allergies.",
    "pain": "She's been fussy and crying more than usual. She pulls away when I touch the spots but I think she's just uncomfortable from the fever.",
    "interventions": "We gave her acetaminophen about 6 hours ago. That's it. We came in as soon as we noticed the spots.",
    "hydration": "She's been drinking a little less than normal but she had some breast milk about 2 hours ago. Her lips don't look dry.",
    "fever_history": "The fever started last night. We measured 40.1 at home with a rectal thermometer. The Tylenol brought it down for a while but it came back.",
    "behavior": "She's definitely not herself. Usually she's crawling everywhere and babbling, but today she's just kind of laying on me. She does respond when I talk to her though.",
    "feeding": "She breastfed a little bit this morning but not as much as usual. She refused the sippy cup.",
    "urinary": "She's had maybe 3 wet diapers today. That's less than normal \u2014 she usually has 5 or 6 by this time.",
    "exposure": "No sick contacts that we know of. She goes to a home daycare but no one there has been sick. No recent travel.",
    "immunization": "She's up to date on everything. She had her 15-month shots about 3 months ago.",
    "family_history": "No family history of bleeding problems or immune issues. Both parents are healthy.",
    "caregiver_concern": "I'm really worried about these spots. They look like bruises but they're not \u2014 she didn't fall or anything. And with the fever, I just have a bad feeling about this.",
    "review_of_systems": "No vomiting, no diarrhea. No cough or runny nose. Just the fever and the rash. She's been fussier and less active than normal.",
    "unknown": "Sorry, I'm not sure what you mean. Can you ask me that a different way?"
}

# CASE 5: First-time seizure, 6-year-old, GCS 12 -> standard caregiver
new_responses[5] = {
    "vitals": "HR 122, RR 18, SpO2 97%, Temp 37.0\u00b0C, BP 96/58, cap refill 2s, GCS 12.",
    "appearance": "Child appears post-ictal \u2014 eyes open to voice, moaning, making non-purposeful movements.",
    "respiratory": "No respiratory distress. Lungs clear bilaterally. Breathing regular.",
    "neuro": "Post-ictal state. Eyes open to voice. Oriented to self only. Moaning but not following commands consistently. No focal neurological deficits. Pupils equal and reactive bilaterally.",
    "skin": "No rash. No cyanosis. Skin warm, dry, and well-perfused.",
    "cardiac": "Slightly tachycardic at 122. Regular rhythm. Capillary refill 2 seconds.",
    "abdominal": "Abdomen soft, non-distended. No tenderness appreciated.",
    "hpi": "He just suddenly started shaking all over \u2014 his whole body. It lasted maybe 3 minutes, then he went limp. He's never done that before. He wasn't sick, no fever, no head injury. The paramedics came and he stopped shaking before they arrived.",
    "onset": "It happened out of nowhere, maybe an hour ago. He was sitting on the couch watching TV and it just started. He was totally fine before that.",
    "pmh": "He's never had a seizure before. No brain problems or neurologic issues. Born full-term, meeting all his milestones. Healthy kid.",
    "medications": "He's not on any medications.",
    "allergies": "No known allergies.",
    "pain": "He can't really tell us right now \u2014 he's too out of it. Before the seizure he wasn't complaining about anything.",
    "interventions": "We called 911 right away. We turned him on his side like they say to do. The paramedics checked him over and brought us here. Nobody gave him any medication.",
    "hydration": "He was drinking water and juice like normal today. No concerns about that before this happened.",
    "fever_history": "No fever at all. We checked when it happened because we'd heard of fever seizures, but he was normal temperature.",
    "behavior": "He's not himself at all \u2014 usually he's running around everywhere but right now he's just really out of it. He opened his eyes when I said his name but he's not talking.",
    "feeding": "He ate breakfast and lunch normally today. Nothing unusual.",
    "urinary": "Normal. He went to the bathroom fine earlier today.",
    "exposure": "No sick contacts. No medications lying around. No chemicals. We don't think he could have gotten into anything.",
    "immunization": "He's fully up to date on all his vaccinations.",
    "family_history": "No seizures in the family. No epilepsy. My husband's cousin has migraines but that's about it.",
    "caregiver_concern": "I've never seen anything like that. The shaking was terrifying. And now he won't talk to me. Is this going to happen again? Is something wrong with his brain?",
    "review_of_systems": "No fever, no headache that he mentioned, no vomiting. He was completely normal before this. No recent illness. No rash.",
    "unknown": "I'm sorry, I'm not sure I understand what you're asking. Can you try asking it a different way?"
}

# CASE 6: Suicidal ideation, 14-year-old, GCS 15 -> patient-as-speaker
new_responses[6] = {
    "vitals": "HR 88, RR 16, SpO2 99%, Temp 36.8\u00b0C, BP 110/68, cap refill 2s, GCS 15.",
    "appearance": "Alert and oriented. Appropriate but somewhat flat affect. Makes eye contact. No signs of self-harm or acute intoxication.",
    "respiratory": "No respiratory distress. Lungs clear. Breathing unlabored.",
    "neuro": "Alert and oriented x4. Neurological exam unremarkable. No focal deficits.",
    "skin": "No visible wounds or signs of self-harm. Skin intact.",
    "cardiac": "Regular rate and rhythm. Heart sounds normal.",
    "abdominal": "Abdomen soft, non-tender. No abnormalities noted.",
    "hpi": "I've been thinking about killing myself for a couple of months now. Today I told my friend that I've been collecting my mom's sertraline \u2014 I have about 30 pills. I was planning to take them all tonight after everyone went to sleep. The school counselor found out and called my mom.",
    "onset": "The thoughts have been going on for about 2 months. But today is when I made the plan. I told my friend at lunch and then the counselor called my mom.",
    "pmh": "I was diagnosed with depression about 6 months ago. I see my regular doctor for it. No previous attempts or hospitalizations.",
    "medications": "I take sertraline 50mg every day for my depression. That's the same medication I was collecting from my mom's bottle.",
    "allergies": "I don't have any allergies.",
    "pain": "I'm not in any physical pain.",
    "interventions": "Nothing. My mom brought me straight here from school. I haven't taken any pills or done anything to hurt myself.",
    "hydration": "I've been drinking water normally. I'm fine physically.",
    "fever_history": "No fever. I'm not sick or anything.",
    "behavior": "I've been more withdrawn lately. I don't want to hang out with my friends anymore. I've been sleeping a lot. My grades have been dropping. I just feel numb most of the time.",
    "feeding": "I haven't really had much of an appetite lately. I ate a little at lunch today but I've been skipping breakfast.",
    "urinary": "Nothing unusual there.",
    "exposure": "I'm not on any drugs or alcohol. I haven't been drinking or anything like that.",
    "immunization": "I think I'm up to date. My mom would know better.",
    "family_history": "My uncle has depression. My mom is on medication for anxiety. No one in my family has attempted suicide that I know of.",
    "caregiver_concern": "I know my mom is really upset. I didn't want to worry anyone. I just feel like everything would be easier if I wasn't here.",
    "review_of_systems": "I haven't been sleeping well \u2014 I sleep a lot but I'm still tired. My appetite is down. I've been having headaches. No other physical complaints.",
    "unknown": "I'm not really sure what you're asking. Could you rephrase that?"
}

# CASE 7: Possible ingestion, 2-year-old, GCS 11 -> standard caregiver (grandmother)
new_responses[7] = {
    "vitals": "HR 68, RR 14, SpO2 95%, Temp 36.4\u00b0C, BP 86/52, cap refill 3s, GCS 11.",
    "appearance": "Drowsy toddler, rousable to sternal rub. Decreased muscle tone. Shallow respirations.",
    "respiratory": "Shallow respirations at rate of 14. No adventitious lung sounds. No retractions.",
    "neuro": "GCS 11 (E3V3M5). Pinpoint pupils bilaterally at 2mm, non-reactive to light. Decreased muscle tone throughout.",
    "skin": "Skin warm. Normal turgor. No rash, no cyanosis. Moist mucous membranes.",
    "cardiac": "Bradycardic at 68 for age. Capillary refill 3 seconds.",
    "abdominal": "Abdomen soft, non-distended. Bowel sounds present.",
    "hpi": "I found him on the living room floor about 45 minutes ago and he was really hard to wake up. He'd been playing by himself for maybe 20 minutes. I take oxycodone for my back and I'm not sure if my pill organizer is all accounted for. He threw up once at home.",
    "onset": "About 45 minutes ago. I left him playing in the living room and when I came back he was on the floor, barely awake. It was sudden \u2014 he was fine before that.",
    "pmh": "He's a healthy boy. No medical problems, no medications, nothing like this has ever happened before.",
    "medications": "He doesn't take any medications. But I take oxycodone and acetaminophen for my back, and I keep it in a weekly pill organizer on the counter.",
    "allergies": "No known allergies.",
    "pain": "He threw up once, but he can't tell me if anything hurts. He's too sleepy to respond to me.",
    "interventions": "I just tried to wake him up and called 911. I didn't give him anything. The paramedics checked him and brought us straight here.",
    "hydration": "He was drinking his sippy cup fine before this. He had juice and water earlier today.",
    "fever_history": "No fever at all. He was completely healthy today. No illness recently.",
    "behavior": "He was his normal active self \u2014 running around, playing with his trucks. And then I found him like this. It's like night and day.",
    "feeding": "He ate lunch about an hour before this happened. Good appetite. Nothing unusual in what he ate.",
    "urinary": "He had a normal wet diaper earlier. I haven't checked since I found him like this.",
    "exposure": "My oxycodone is on the kitchen counter in one of those daily pill organizers. I can't be sure it's all there. No other medications in the house that he could reach. No chemicals or cleaning products accessible.",
    "immunization": "He's up to date on his vaccines.",
    "family_history": "No family history of seizures or anything like that. Just my chronic back pain.",
    "caregiver_concern": "I think he might have gotten into my pills. I feel terrible. His eyes look so tiny and he's barely breathing. I should have put them up higher. Is he going to be okay?",
    "review_of_systems": "He was totally fine today until this. No fever, no cough, no diarrhea. Just the vomiting when I found him and now he's so sleepy. His breathing looks too slow to me.",
    "unknown": "I'm sorry, I don't understand. Can you ask me that a different way? I'm really worried about him."
}

# CASE 8: Severe asthma, 10-year-old, GCS 15 -> standard caregiver
new_responses[8] = {
    "vitals": "HR 138, RR 36, SpO2 88%, Temp 37.1\u00b0C, BP 102/62, cap refill 2s, GCS 15.",
    "appearance": "Anxious child sitting upright, tripoding. Speaking in 1-2 word phrases only. Prominent accessory muscle use.",
    "respiratory": "Audible wheeze without stethoscope. Severe intercostal and suprasternal retractions. Prolonged expiratory phase. Decreased air entry at bilateral bases.",
    "neuro": "Alert, GCS 15. Anxious but following commands. Oriented appropriately.",
    "skin": "No cyanosis currently. No rash. Skin slightly diaphoretic.",
    "cardiac": "Tachycardic at 138. Regular rhythm. Trachea midline. No pulsus paradoxus measured yet.",
    "abdominal": "Abdomen soft. Limited exam due to respiratory distress and tripod positioning.",
    "hpi": "Her asthma has been flaring up for about 4 hours. She started wheezing and couldn't catch her breath. We gave her the albuterol inhaler 3 times with the spacer but it barely helped. She can only say a word or two at a time now. She's really working hard to breathe.",
    "onset": "It started about 4 hours ago. She had a cold for the last couple days and then the wheezing kicked in this afternoon and just kept getting worse.",
    "pmh": "She has severe persistent asthma. She's been in the hospital twice this year \u2014 one of those was in the ICU and she was on a breathing machine when she was 7. She has a combination inhaler she uses every day and a rescue inhaler.",
    "medications": "She takes fluticasone-salmeterol \u2014 the combination puffer \u2014 every day, and montelukast at night. Her rescue inhaler is albuterol. She used it 3 times today.",
    "allergies": "No known drug allergies. She does have seasonal allergies.",
    "pain": "She's saying 'chest...tight' but she can't say much more than that right now.",
    "interventions": "We gave her 3 doses of albuterol through the spacer at home over the last 4 hours. It helped a tiny bit after the first one but the last two didn't seem to do anything.",
    "hydration": "She's been too breathless to drink much. She had a few sips of water but that's about it for the last couple hours.",
    "fever_history": "She had a very slight temperature \u2014 37.5 \u2014 but it's basically from the cold she's had. No real fever.",
    "behavior": "She's usually a talkative, active kid. Right now she can barely get a word out. She looks scared. She knows when her asthma is bad because it's happened before.",
    "feeding": "She ate a little lunch but since the wheezing got worse she hasn't eaten anything. She's too breathless.",
    "urinary": "Normal earlier today. No concerns.",
    "exposure": "She had a cold for 2 days \u2014 runny nose, mild cough. No known exposure to smoke, pets, or other triggers today. We think the cold triggered the asthma.",
    "immunization": "She's up to date on all her vaccines, including flu shot this year.",
    "family_history": "I have asthma too, but not as severe as hers. Her grandmother has COPD. No other lung problems in the family.",
    "caregiver_concern": "The inhalers aren't working this time. Last time it got this bad she ended up in the ICU. I'm really scared it's happening again. She can barely talk.",
    "review_of_systems": "Cold symptoms for 2 days \u2014 runny nose, cough. The wheezing got severe today. Chest tightness. No vomiting, no fever really. Just can't breathe.",
    "unknown": "I'm sorry, I'm not sure what you mean. Can you ask that differently? I'm really worried about her breathing."
}

# CASE 9: Appendicitis, 7-year-old, GCS 15 -> standard caregiver
new_responses[9] = {
    "vitals": "HR 104, RR 20, SpO2 99%, Temp 38.1\u00b0C, BP 98/60, cap refill 2s, GCS 15.",
    "appearance": "Ill-appearing but alert child. Walked in bent slightly forward, guarding abdomen.",
    "respiratory": "No respiratory distress. Lungs clear bilaterally.",
    "neuro": "Alert and oriented. Cooperative but in visible discomfort. GCS 15.",
    "skin": "No rash. Skin warm. Mild pallor.",
    "cardiac": "Mildly tachycardic at 104. Regular rhythm. Well-perfused.",
    "abdominal": "Guarding and point tenderness at McBurney's point. Positive Rovsing's sign. Psoas sign positive. Voluntary guarding on palpation. Bowel sounds diminished. No rigidity or peritoneal signs currently.",
    "hpi": "His belly started hurting around his belly button yesterday afternoon. Then overnight the pain moved down to his right side and it's been getting worse. He didn't eat dinner last night and wouldn't touch breakfast. He threw up once this morning. The pain is constant and it gets worse when he moves.",
    "onset": "It started yesterday afternoon \u2014 about 18 hours ago. First it was around his belly button, and then by this morning it was all down on his right side.",
    "pmh": "He's a healthy kid. No stomach problems before. No surgeries. No medical conditions. No medications.",
    "medications": "He doesn't take any medications. We didn't give him anything for pain because we weren't sure if we should.",
    "allergies": "No known allergies.",
    "pain": "He says it's a 6 out of 10. It's on his right side, low down. It hurts more when he walks or moves around. It's been constant since last night.",
    "interventions": "We didn't give him anything \u2014 no medicine, no food or drink this morning. We just brought him in.",
    "hydration": "He had a little water last night but hasn't had anything to drink this morning. He refused everything.",
    "fever_history": "He felt warm to us last night but we didn't take his temperature then. This morning it was 38.1. He hasn't had any fever medicine.",
    "behavior": "He's usually really active and playful but he just wants to lie on his side and not move. He's been really quiet since this morning. He walked in here hunched over.",
    "feeding": "He skipped dinner last night and refused breakfast this morning. He says he feels like he might throw up if he eats. He vomited once this morning.",
    "urinary": "He's been peeing normally. No pain with urination. No changes there.",
    "exposure": "No sick contacts. No one else in the house has a stomach bug. No recent travel. He ate the same thing as the rest of us.",
    "immunization": "He's fully up to date on all his shots.",
    "family_history": "No family history of bowel problems. His dad had his appendix out as a teenager.",
    "caregiver_concern": "I'm worried it might be his appendix. The pain moved from his belly button to the right side \u2014 that's what happened to my husband. He's really miserable and it's getting worse, not better.",
    "review_of_systems": "Belly pain that moved to the right side, not eating, threw up once, low fever. No diarrhea, no blood in his stool, no urinary problems. No rash.",
    "unknown": "Sorry, I'm not sure what you mean by that. Can you rephrase it?"
}

# CASE 10: Febrile neonate, 5-week-old, GCS 15 -> standard caregiver
new_responses[10] = {
    "vitals": "HR 168, RR 46, SpO2 99%, Temp 38.3\u00b0C, BP 72/46, cap refill 2s, GCS 15.",
    "appearance": "Alert, fussy but consolable infant. Good tone and color.",
    "respiratory": "No respiratory distress. Lungs clear. No retractions, no grunting, no nasal flaring.",
    "neuro": "Alert. Good tone. Anterior fontanelle flat and soft, not bulging. Fussy but consolable.",
    "skin": "No rash. Good color. Skin warm.",
    "cardiac": "Tachycardic at 168 for age. Regular rhythm. Capillary refill 2 seconds.",
    "abdominal": "Abdomen soft, non-tender, non-distended. No hepatosplenomegaly.",
    "hpi": "We took her temperature rectally about 2 hours ago and it was 38.2. This is the first time she's ever had a fever. She's been fussier than usual today but she's still looking at us and responding. She was born at 39 weeks, normal delivery, no problems.",
    "onset": "We noticed she felt warm about 2 hours ago and that's when we checked her temperature. The fussiness started earlier today, maybe this morning.",
    "pmh": "She was born at 39 weeks, regular vaginal delivery, no complications. She passed the newborn screening. No antibiotics since birth. No ED visits before today.",
    "medications": "She's not on any medications. Just breast milk.",
    "allergies": "No known allergies.",
    "pain": "She's fussier than normal but she does calm down when I hold her. I'm not sure if she's in pain or just uncomfortable from the fever.",
    "interventions": "We just took her temperature and came straight here. We didn't give her any medicine \u2014 we didn't know if we could give a 5-week-old anything for fever.",
    "hydration": "She's been breastfeeding okay. Maybe a little less than usual but she's still latching and eating. Her diapers have been wet.",
    "fever_history": "This is her very first fever. 38.2 rectally about 2 hours ago. No fever before today.",
    "behavior": "She's been fussier than usual today. Normally she's pretty content after feeding. Today she's been crying more and harder to settle, but she does eventually calm down.",
    "feeding": "She's breastfed. She ate about an hour and a half ago. A little shorter feed than usual but she did take it. Her normal pattern is every 2-3 hours.",
    "urinary": "She's had normal wet diapers today \u2014 I think about 4 so far. Normal-looking stools too.",
    "exposure": "No one at home has been sick that we know of. Her older brother is in preschool but he seems fine. No recent travel.",
    "immunization": "She hasn't had her 2-month vaccines yet \u2014 she's only 5 weeks old. She did get the hepatitis B shot at the hospital.",
    "family_history": "No family history of immune problems. No serious infections in the family. Both parents are healthy.",
    "caregiver_concern": "I know a fever in a baby this young can be serious. Our pediatrician always told us to come straight to the ER if she got a fever in the first 2 months. She looks okay to me but I'm worried there could be something we can't see.",
    "review_of_systems": "Just the fever and fussiness. No vomiting, no diarrhea. No cough, no congestion. No rash. She's been eating and having wet diapers. Just fussier than normal.",
    "unknown": "I'm sorry, I don't know what you're asking. Can you say that in a different way?"
}

# CASE 11: Wrist fracture, 12-year-old, GCS 15 -> patient-as-speaker
new_responses[11] = {
    "vitals": "HR 98, RR 18, SpO2 99%, Temp 36.9\u00b0C, BP 108/64, cap refill 2s, GCS 15.",
    "appearance": "Alert adolescent cradling right wrist. Obvious dorsal angulation at distal radius with mild swelling and ecchymosis.",
    "respiratory": "No respiratory distress. Lungs clear.",
    "neuro": "Alert and oriented. Sensation decreased to light touch over first webspace. Flexor and extensor strength 4/5, limited by pain.",
    "skin": "Mild swelling and ecchymosis at distal right wrist. No open wound. No laceration.",
    "cardiac": "Radial pulse 2+ and intact distally. Heart rate 98, regular.",
    "abdominal": "No abdominal complaints. Exam not indicated for this chief complaint.",
    "hpi": "I was doing a trick on my skateboard about an hour ago and I fell on my hand. My wrist is killing me \u2014 I can see it's bent weird. I can move my fingers a little but my thumb and pointer finger feel kind of numb. It's the worst pain I've ever felt.",
    "onset": "About an hour ago. I was at the skate park and I fell trying to land a kickflip. I put my hand out to catch myself.",
    "pmh": "I've never broken anything before. I'm pretty healthy. No medical problems. I don't take any medications.",
    "medications": "I don't take any medications.",
    "allergies": "I don't have any allergies.",
    "pain": "It's like a 7 out of 10. It hurts constantly and it gets way worse if I try to move it at all. It's right at my wrist where it's bent.",
    "interventions": "My mom put ice on it and wrapped it in a towel. We came here right away. I haven't taken any pain medicine.",
    "hydration": "I had a Gatorade at the skate park before I fell. I'm not thirsty.",
    "fever_history": "No fever. I feel fine other than my wrist.",
    "behavior": "I'm okay, just in a lot of pain. I'm trying not to move it.",
    "feeding": "I ate lunch before I went skating. Normal appetite. I feel fine other than the wrist.",
    "urinary": "Normal. No issues.",
    "exposure": "I fell on concrete at the skate park. No open wound. Just the impact on my hand and wrist.",
    "immunization": "I think I'm up to date. My mom handles that stuff.",
    "family_history": "Nobody in my family has bone problems or anything like that.",
    "caregiver_concern": "I'm mostly just worried about the numbness in my fingers. And it looks really crooked. Is that normal? Am I going to need surgery?",
    "review_of_systems": "Just the wrist pain and the numbness in my thumb and index finger. No other injuries. No headache, no dizziness. I didn't hit my head.",
    "unknown": "Uh, I'm not sure what you mean. Can you ask that differently?"
}

# CASE 12: Mild-moderate asthma, 9-year-old, GCS 15 -> standard caregiver
new_responses[12] = {
    "vitals": "HR 112, RR 24, SpO2 95%, Temp 37.5\u00b0C, BP 104/62, cap refill 2s, GCS 15.",
    "appearance": "Mild-to-moderate respiratory distress. Speaking in full sentences. Mildly anxious.",
    "respiratory": "Bilateral expiratory wheeze on auscultation with good air entry. Mild intercostal retractions. No accessory muscle use. No nasal flaring.",
    "neuro": "Alert and oriented. GCS 15. Cooperative, mildly anxious.",
    "skin": "No cyanosis. No rash. Skin warm and dry.",
    "cardiac": "Mildly tachycardic at 112. Regular rhythm. Well-perfused.",
    "abdominal": "Abdomen soft, non-tender. No distension.",
    "hpi": "He's been wheezing and short of breath for about 6 hours now. He had a cold for the last 2 days and then the asthma kicked in. We gave him his albuterol twice at home and it helped a little each time but didn't last. He can still talk in full sentences but he's working harder to breathe than normal.",
    "onset": "The wheezing started about 6 hours ago. He's had a runny nose and cough for 2 days before this. The cold seems to have triggered his asthma.",
    "pmh": "He has moderate persistent asthma. He was in the hospital once about 18 months ago for an asthma flare but never in the ICU. He gets worse in spring and fall usually.",
    "medications": "He takes budesonide \u2014 the inhaled steroid \u2014 every day, and albuterol as needed. He also takes montelukast. He's been using his albuterol a lot the last 2 days.",
    "allergies": "No known drug allergies. He has seasonal allergies.",
    "pain": "He says his chest feels tight. No actual chest pain \u2014 more like pressure. He rates it maybe a 3 or 4.",
    "interventions": "We gave him 2 doses of albuterol through his spacer at home. The first one helped for about an hour, the second one didn't help much at all. That's when we decided to come in.",
    "hydration": "He's been drinking water and juice. He's kept hydrated. No vomiting.",
    "fever_history": "He had a very slight temp \u2014 37.5. Just from the cold. No significant fever.",
    "behavior": "He's a little anxious about the breathing but otherwise acting like himself. He's talking normally and answering questions. Just a little more winded than usual.",
    "feeding": "He ate breakfast but skipped lunch because he said the breathing made him not want to eat. He's been drinking fluids though.",
    "urinary": "Totally normal. No issues.",
    "exposure": "He had a cold for 2 days \u2014 that's his main trigger. No smoke exposure, no new pets, no construction. We keep the house pretty clean for his asthma.",
    "immunization": "He's fully vaccinated including his flu shot this year.",
    "family_history": "I have mild asthma. His dad has seasonal allergies. No other lung problems in the family.",
    "caregiver_concern": "The albuterol isn't lasting like it usually does and I can hear the wheeze without a stethoscope. I don't want it to get worse like last time when he was hospitalized.",
    "review_of_systems": "Cold symptoms for 2 days, wheezing for 6 hours, chest tightness. No vomiting, no fever really, no rash. Still talking fine and drinking fluids.",
    "unknown": "Sorry, I'm not sure what you're asking. Could you phrase that differently?"
}

# CASE 13: SVT, 15-year-old, GCS 15 -> patient-as-speaker
new_responses[13] = {
    "vitals": "HR 214, RR 22, SpO2 98%, Temp 36.7\u00b0C, BP 94/58, cap refill 2s, GCS 15.",
    "appearance": "Alert, anxious adolescent. Mild pallor. Neck veins slightly distended. Visible neck pulsations (frog sign).",
    "respiratory": "Lungs clear bilaterally. No wheeze, no crackles. Mild tachypnea at 22.",
    "neuro": "Alert and oriented x4. Anxious but cooperative. No focal deficits.",
    "skin": "Mild pallor. Moist mucous membranes. No rash, no diaphoresis.",
    "cardiac": "Regular rapid rhythm at 214 \u2014 no pulse deficit. Neck veins slightly distended. Frog sign noted. No murmur audible, though auscultation limited by rapid rate.",
    "abdominal": "Abdomen soft, non-tender. No organomegaly.",
    "hpi": "I was just sitting on the couch watching TV and my heart suddenly started racing really fast. It's been going for about 2 hours now. My chest feels tight and I feel a little short of breath. I've never had anything like this before. I didn't pass out or get dizzy.",
    "onset": "It started about 2 hours ago. It came on super suddenly \u2014 like a switch flipped. One second I was fine and then my heart was pounding.",
    "pmh": "I don't have any heart problems. I've never had an EKG or seen a cardiologist. I'm healthy \u2014 no medical conditions.",
    "medications": "I don't take any medications or supplements. No birth control or anything.",
    "allergies": "No allergies.",
    "pain": "My chest feels tight and uncomfortable, like my heart is trying to beat out of my chest. It's not really pain exactly, more like pressure. Maybe a 4 out of 10.",
    "interventions": "I tried drinking cold water and bearing down like I read online. It didn't help. We came here after it didn't stop for over an hour.",
    "hydration": "I've been drinking water normally today. I'm not dehydrated.",
    "fever_history": "No fever. I'm not sick at all.",
    "behavior": "I'm really anxious because this won't stop. I can feel my heart pounding in my neck. I just want it to go back to normal.",
    "feeding": "I had dinner a couple hours before this started. Normal meal. I didn't have any energy drinks or extra caffeine today.",
    "urinary": "Normal. No issues.",
    "exposure": "No caffeine, no energy drinks, no drugs, no alcohol. I don't smoke or vape. I wasn't exercising when it started \u2014 I was literally sitting on the couch.",
    "immunization": "I'm up to date on everything. I had my meningococcal booster recently.",
    "family_history": "No one in my family has died suddenly or had heart problems young. My grandpa had a heart attack but he was in his 70s. No arrhythmias that I know of.",
    "caregiver_concern": "I'm scared because it won't stop. Two hours is a long time for my heart to be going this fast. I can see my neck pulsing in the mirror. Something is definitely wrong.",
    "review_of_systems": "Heart racing, chest tightness, mild shortness of breath, mild lightheadedness. No fainting, no actual dizziness, no nausea. No fever, no cough, no other symptoms.",
    "unknown": "Sorry, I don't really get what you're asking. Can you say it differently?"
}

# CASE 14: Croup, 3-year-old, GCS 15 -> standard caregiver
new_responses[14] = {
    "vitals": "HR 128, RR 30, SpO2 97%, Temp 38.2\u00b0C, BP 92/56, cap refill 2s, GCS 15.",
    "appearance": "Alert, mildly anxious toddler sitting upright in parent's lap. Moderate barky cough noted during exam.",
    "respiratory": "Audible inspiratory stridor at rest, not only with crying. Mild intercostal retractions. Good air entry bilaterally. No drooling.",
    "neuro": "Alert, interactive. Age-appropriate. Mildly anxious. GCS 15.",
    "skin": "No rash. Skin warm. Well-perfused.",
    "cardiac": "Mildly tachycardic at 128. Regular rhythm. Capillary refill 2 seconds.",
    "abdominal": "Abdomen soft, non-tender. No distension.",
    "hpi": "He's had this barky cough for 2 days \u2014 it sounds like a seal. Then tonight he woke up from sleeping and he had this loud, harsh breathing sound. You can hear it even when he's just sitting calmly. No choking, no drooling. He had a mild fever earlier.",
    "onset": "The cough started 2 days ago. The noisy breathing started tonight \u2014 he woke up from sleep with it, maybe 2 hours ago. It hasn't gone away.",
    "pmh": "This is his first time having croup. He's never had stridor or breathing problems before. No hospitalizations. No airway surgeries or problems. He's a healthy kid.",
    "medications": "He doesn't take any medications. We haven't given him anything for this yet \u2014 we came straight in.",
    "allergies": "No known allergies.",
    "pain": "He hasn't been complaining about pain. He's more scared by the breathing sound than anything. He's pointing at his throat sometimes.",
    "interventions": "We tried taking him outside into the cold night air like the internet said. It might have helped for a minute but the noisy breathing came right back. We haven't given any medicine.",
    "hydration": "He drank some water before bed. He hasn't wanted anything since he woke up with the stridor. But his mouth looks moist.",
    "fever_history": "He's had a low fever for 2 days \u2014 38.2 was the highest. No fever medicine given tonight.",
    "behavior": "He's a little clingy and anxious but he's alert and looking around. He usually chatters a lot but tonight he's quieter. He's scared by the sound he's making.",
    "feeding": "He ate okay yesterday and had some dinner tonight. Since waking up with the breathing problem he hasn't eaten anything.",
    "urinary": "Normal wet diapers today. No concerns there.",
    "exposure": "He might have caught a cold from daycare. A few kids were sick last week with coughs and runny noses. No one had anything serious.",
    "immunization": "He's up to date on all his vaccinations.",
    "family_history": "No family history of airway problems. His older sister had croup once when she was little but it wasn't this bad.",
    "caregiver_concern": "The breathing sound is really scary \u2014 you can hear it across the room. It's not going away on its own and he's having to work harder to breathe. I want to make sure it's not something worse.",
    "review_of_systems": "Barky cough for 2 days, runny nose, low fever, and now the stridor since tonight. No vomiting, no diarrhea, no rash. He's still interactive.",
    "unknown": "I'm sorry, I don't understand what you're asking. Can you rephrase that?"
}

# CASE 15: Ankle sprain, 8-year-old, GCS 15 -> standard caregiver
new_responses[15] = {
    "vitals": "HR 86, RR 16, SpO2 99%, Temp 36.8\u00b0C, BP 100/62, cap refill 2s, GCS 15.",
    "appearance": "Alert, well-appearing child in mild distress. Bearing weight with a limp.",
    "respiratory": "No respiratory distress. Lungs clear.",
    "neuro": "Alert and oriented. GCS 15. Sensation intact distally.",
    "skin": "Lateral ankle swelling with mild ecchymosis over right ankle.",
    "cardiac": "Dorsalis pedis and posterior tibial pulses intact. Capillary refill brisk.",
    "abdominal": "No abdominal complaints. Exam not pertinent.",
    "hpi": "She twisted her right ankle at soccer practice about 2 hours ago. She was able to walk off the field with a coach helping her. The outside of her ankle got swollen pretty fast. She says it hurts about a 4 out of 10. We gave her ibuprofen at home and it helped a little. She can walk on it with a limp.",
    "onset": "About 2 hours ago at soccer practice. She was running and stepped on someone's foot and her ankle rolled.",
    "pmh": "She's never hurt her ankle before. No bone problems. Healthy, active kid. No medical conditions.",
    "medications": "She doesn't take any medications regularly. We gave her 200mg of ibuprofen about an hour ago.",
    "allergies": "No known allergies.",
    "pain": "She says it's about a 4 out of 10. It hurts on the outside of her ankle. It's worse when she tries to turn her foot inward. Walking hurts but she can do it.",
    "interventions": "We gave her ibuprofen 200mg about an hour ago and put ice on it. We wrapped it in an ace bandage. The ice and ibuprofen helped some.",
    "hydration": "She's been drinking water fine. No concerns.",
    "fever_history": "No fever. She's not sick at all.",
    "behavior": "She's a little bummed about soccer but otherwise acting totally normal. She walked in here on her own with a limp.",
    "feeding": "She ate a snack before practice and has been fine. Normal appetite.",
    "urinary": "No issues. Totally normal.",
    "exposure": "Just a soccer injury. She was wearing her cleats. Nothing unusual about the field or conditions.",
    "immunization": "She's up to date on all her vaccines.",
    "family_history": "No bone or joint problems in the family.",
    "caregiver_concern": "I just want to make sure it's not broken. It swelled up fast and I can see some bruising. She can walk on it though, so hopefully that's a good sign.",
    "review_of_systems": "Just the ankle pain and swelling. No other injuries. She didn't fall or hit her head. No numbness or tingling in her toes.",
    "unknown": "I'm not sure what you mean by that. Could you ask that differently?"
}

# CASE 16: Cellulitis, 6-year-old, GCS 15 -> standard caregiver
new_responses[16] = {
    "vitals": "HR 88, RR 18, SpO2 99%, Temp 36.9\u00b0C, BP 96/58, cap refill 2s, GCS 15.",
    "appearance": "Alert, well-appearing, comfortable child.",
    "respiratory": "No respiratory distress. Lungs clear.",
    "neuro": "Alert and oriented. GCS 15. Comfortable and interactive.",
    "skin": "6x8cm area of erythema, warmth, and induration on anterior right lower leg. Non-fluctuant. No streaking or lymphangitis. Small dried abrasion at center. Wound margins well-defined.",
    "cardiac": "Regular rate and rhythm. Heart rate 88. Well-perfused.",
    "abdominal": "Abdomen soft, non-tender. No lymphadenopathy.",
    "hpi": "He scraped his knee at the playground about 4 days ago. It seemed fine at first, but 2 days ago the skin around it started getting red and swollen. I drew a line with a pen around the red area 8 hours ago and it's spread about 2 centimeters past my line. He doesn't have a fever and he's acting normally otherwise.",
    "onset": "The scrape happened 4 days ago. The redness started spreading about 2 days ago. I marked the edge with pen 8 hours ago and it's definitely bigger now.",
    "pmh": "He's never had a skin infection before. No immune problems. No diabetes. No MRSA history. No recent antibiotics. Healthy kid.",
    "medications": "He's not on any medications.",
    "allergies": "No known allergies.",
    "pain": "He says it hurts a little \u2014 maybe a 2 or 3. It's more sore and warm than really painful. He's not too bothered by it.",
    "interventions": "We've been cleaning it with soap and water and putting a bandaid on it. I marked the border with a pen this morning to watch it. We haven't given any antibiotics or anything.",
    "hydration": "He's drinking fine. No concerns about that.",
    "fever_history": "No fever at all. He's been a normal temperature the whole time. We've been checking.",
    "behavior": "He's totally himself. Running around, playing, eating normally. If you didn't look at his leg you'd never know anything was wrong.",
    "feeding": "Eating and drinking normally. Good appetite.",
    "urinary": "Completely normal.",
    "exposure": "He scraped his knee on the playground equipment. Just a normal playground \u2014 nothing unusual. No exposure to anyone with skin infections.",
    "immunization": "He's fully vaccinated and up to date.",
    "family_history": "No family history of MRSA or recurring skin infections. Everyone's healthy.",
    "caregiver_concern": "I'm mainly worried because it's spreading. I drew that line to track it and it's definitely getting bigger. But he seems fine otherwise \u2014 no fever, no sick feeling. I just want to make sure it doesn't turn into something worse.",
    "review_of_systems": "Just the red area on his leg that's spreading. No fever, no body aches, no chills, no feeling sick. He's eating and playing normally.",
    "unknown": "I'm sorry, I'm not sure what you're asking. Can you rephrase that?"
}

# CASE 17: UTI, 16-year-old, GCS 15 -> patient-as-speaker
new_responses[17] = {
    "vitals": "HR 82, RR 16, SpO2 99%, Temp 36.8\u00b0C, BP 112/68, cap refill 2s, GCS 15.",
    "appearance": "Alert, well-appearing adolescent in no acute distress.",
    "respiratory": "No respiratory distress. Lungs clear.",
    "neuro": "Alert and oriented x4. GCS 15. No abnormalities.",
    "skin": "No rash. Skin warm, dry, well-perfused.",
    "cardiac": "Regular rate and rhythm. Well-perfused.",
    "abdominal": "Mild suprapubic tenderness on palpation. No costovertebral angle tenderness. Abdomen soft, no guarding or rebound.",
    "hpi": "It's been hurting when I pee for about 2 days. I have to go really often \u2014 like every 30 minutes \u2014 and it burns. There's some pressure down low in my belly. No back pain, no fever. This is the first time this has happened to me.",
    "onset": "It started about 2 days ago. The burning came first, and then I noticed I was going to the bathroom way more often than normal.",
    "pmh": "I've never had a UTI before. No gynecologic issues. I'm sexually active. My last period was about 10 days ago. I don't think I'm pregnant.",
    "medications": "I'm not on any medications. No birth control.",
    "allergies": "No allergies.",
    "pain": "It's mostly the burning when I pee and some pressure in my lower belly. Maybe a 4 out of 10. No back pain or flank pain.",
    "interventions": "I've been trying to drink a lot of water. I took some cranberry supplements \u2014 I don't know if they help. I haven't taken any antibiotics.",
    "hydration": "I've been drinking a ton of water trying to flush it out. Probably more than usual.",
    "fever_history": "No fever at all. I've been checking.",
    "behavior": "I'm fine, just annoyed by having to pee constantly. It's disrupting school. Otherwise I feel normal.",
    "feeding": "Normal appetite. I've been eating fine.",
    "urinary": "Burning with urination, going every 30 minutes or so, feels urgent every time. No blood that I can see. No unusual discharge or odor.",
    "exposure": "I'm sexually active. No new partners recently. No vaginal discharge. Last period was 10 days ago, normal.",
    "immunization": "I'm up to date on everything. HPV vaccine too.",
    "family_history": "My mom gets UTIs sometimes. Nothing else relevant.",
    "caregiver_concern": "I just want it to stop burning. It's been 2 days and it's not getting better on its own. I figured I should come in before it gets worse.",
    "review_of_systems": "Burning with urination, frequency, suprapubic pressure. No fever, no back pain, no vaginal discharge. No nausea or vomiting. Otherwise feeling fine.",
    "unknown": "I'm not sure what you mean. Can you ask that a different way?"
}

# CASE 18: Ear pain, 11-year-old, GCS 15 -> standard caregiver
new_responses[18] = {
    "vitals": "HR 90, RR 16, SpO2 99%, Temp 38.0\u00b0C, BP 104/62, cap refill 2s, GCS 15.",
    "appearance": "Alert, well-appearing child with mild discomfort. Tugging at right ear.",
    "respiratory": "No respiratory distress. Lungs clear.",
    "neuro": "Alert and oriented. GCS 15. No facial asymmetry. Neurologically intact.",
    "skin": "No rash. Oropharynx mildly erythematous, no exudates.",
    "cardiac": "Regular rate and rhythm. Heart rate 90. Well-perfused.",
    "abdominal": "No abdominal complaints. No post-auricular tenderness or swelling.",
    "hpi": "His right ear has been hurting for 3 days, getting worse each day. The hearing on that side sounds muffled to him. He had a cold for about 5 days before the ear pain started. No drainage from the ear. We've been giving ibuprofen which takes the edge off but doesn't fix it. Low-grade fever today.",
    "onset": "The ear pain started 3 days ago. He had a cold for about 5 days before that with a runny nose and cough, and then the ear pain came on.",
    "pmh": "He had one ear infection about 2 years ago that cleared up with antibiotics. No ear tubes. No hearing problems. No ear surgery.",
    "medications": "He doesn't take any daily medications. We've been giving him ibuprofen for the pain, about every 6 hours.",
    "allergies": "No known allergies.",
    "pain": "He says it's about a 5 out of 10. Constant ache in his right ear. It gets worse when he lies down. The ibuprofen helps bring it down to about a 3.",
    "interventions": "Just ibuprofen at home \u2014 200mg every 6 hours. We tried warm compresses on the ear too. That helped a little temporarily.",
    "hydration": "He's been drinking fine. Water, juice. No problems with fluids.",
    "fever_history": "He had a very low fever today \u2014 37.9 at home. First day of any fever. No fever for the first 2 days of ear pain.",
    "behavior": "He's been a little grumpy from the pain but otherwise acting normally. He went to school yesterday. Today he stayed home because of the fever.",
    "feeding": "Normal appetite. He's eating fine. No pain with swallowing, just the ear hurting.",
    "urinary": "Normal. No concerns.",
    "exposure": "He had a cold \u2014 probably from school. No one at home is sick. No recent swimming or water in the ear.",
    "immunization": "He's fully vaccinated. Up to date on everything.",
    "family_history": "His younger sister gets ear infections a lot but he usually doesn't. No hearing problems in the family.",
    "caregiver_concern": "It's been 3 days and it's not getting better. The muffled hearing concerns me. I just want him checked and probably needs antibiotics at this point.",
    "review_of_systems": "Right ear pain for 3 days, muffled hearing right side, low-grade fever today. Had a cold before this. No dizziness, no ear drainage, no facial drooping. No vomiting.",
    "unknown": "Sorry, I'm not sure what you're asking about. Can you ask that another way?"
}

# CASE 19: Abrasion, 5-year-old, GCS 15 -> standard caregiver
new_responses[19] = {
    "vitals": "HR 92, RR 18, SpO2 99%, Temp 36.7\u00b0C, BP 96/58, cap refill 2s, GCS 15.",
    "appearance": "Alert, interactive child running around the triage area. In no distress.",
    "respiratory": "No respiratory distress. Lungs clear.",
    "neuro": "Alert, interactive, and playful. GCS 15. No signs of head injury.",
    "skin": "4x3cm superficial gravel abrasion on right knee. Bleeding has stopped. No deep tissue involvement. No foreign body visible.",
    "cardiac": "Regular rate and rhythm. Well-perfused. Heart rate 92.",
    "abdominal": "No abdominal concerns. Full range of motion at right knee. No bony tenderness.",
    "hpi": "He fell off his bike on a gravel path about 30 minutes ago. Scraped up his knee. He wasn't wearing a helmet but he didn't hit his head \u2014 just landed on his knees and hands. We rinsed it off with water at home. He got up and walked right over to us afterward. He's asking for a sticker, so I think he's fine.",
    "onset": "About 30 minutes ago. He was riding his bike in front of our house, hit some gravel, and tipped over.",
    "pmh": "He's a healthy kid. No medical problems. No bleeding disorders. Fully vaccinated \u2014 his tetanus is up to date, he got his DTaP at age 4.",
    "medications": "He's not on any medications.",
    "allergies": "No known allergies.",
    "pain": "He said it's a 2 out of 10. He cried when it happened but he's over it now. He's running around the waiting room.",
    "interventions": "We washed it off with water at home and put a paper towel on it. The bleeding stopped on its own. No bandage yet.",
    "hydration": "He's been drinking water. He's totally fine.",
    "fever_history": "No fever. Completely healthy.",
    "behavior": "Totally himself. Running around, chatting, asking for stickers. He's not bothered at all.",
    "feeding": "He had a snack before riding his bike. Normal appetite. He's already asked if he can have a popsicle.",
    "urinary": "Normal. No issues.",
    "exposure": "He fell on a gravel path in front of our house. No glass or anything unusual in the gravel. Just a regular scrape.",
    "immunization": "He's fully up to date. He got his DTaP booster at his 4-year checkup last year.",
    "family_history": "No bleeding disorders or anything like that in the family.",
    "caregiver_concern": "Honestly, I mainly wanted to make sure it was clean enough and didn't need stitches. It looks pretty superficial to me. He's acting completely normal.",
    "review_of_systems": "Just the scraped knee. No head injury, no headache, no vomiting, no dizziness. He's running around. Completely fine otherwise.",
    "unknown": "I'm not sure what you're asking about. Can you say that a different way?"
}

# CASE 20: Med refill, 13-year-old, GCS 15 -> patient-as-speaker
new_responses[20] = {
    "vitals": "HR 84, RR 16, SpO2 99%, Temp 36.8\u00b0C, BP 108/64, cap refill 2s, GCS 15.",
    "appearance": "Alert, pleasant, talkative adolescent. No acute distress.",
    "respiratory": "No respiratory distress. Lungs clear.",
    "neuro": "Alert, oriented. Normal neurological exam. No signs of psychiatric decompensation or agitation.",
    "skin": "No rash. No marks or wounds. Skin normal.",
    "cardiac": "Regular rate and rhythm. No tachycardia. No hypertension.",
    "abdominal": "Abdomen soft, non-tender. No complaints.",
    "hpi": "I ran out of my Concerta 2 days ago and my psychiatrist is on vacation for another 10 days. I have an appointment when she gets back. I just need a refill to get me through. I'm having a harder time focusing in school without it.",
    "onset": "I ran out 2 days ago. I've been on it since I was 8. I usually get refills from my psychiatrist but she's out of town.",
    "pmh": "I have ADHD \u2014 combined type. I was diagnosed when I was 8. That's my only diagnosis. No hospitalizations. No psychiatric emergencies or anything like that.",
    "medications": "Concerta \u2014 methylphenidate extended-release, 27 milligrams. I take it every morning. That's my only medication.",
    "allergies": "No allergies.",
    "pain": "No pain. I feel fine physically.",
    "interventions": "Nothing. I just came in to get the prescription. My mom called the psychiatrist's office but they can't do anything until she's back.",
    "hydration": "I'm drinking fine. No issues.",
    "fever_history": "No fever. I'm not sick.",
    "behavior": "My parents say I've been more distracted and impulsive the last 2 days without the medication. I can tell the difference too \u2014 it's harder to sit still in class and I keep zoning out. But it's not dangerous or anything.",
    "feeding": "My appetite has actually been better the last 2 days \u2014 which makes sense because the medication usually suppresses it. I've been eating more.",
    "urinary": "Normal. No problems.",
    "exposure": "No drug use, no alcohol, no vaping. I'm not using anything else to try to compensate for not having my medication.",
    "immunization": "I'm up to date on everything.",
    "family_history": "My dad has ADHD too. My mom has anxiety. No other psychiatric history in the family.",
    "caregiver_concern": "I'm not in any crisis. I just need my medication refilled so I can function at school. I have a test next week and I can't focus without it.",
    "review_of_systems": "No physical complaints at all. Just more distracted and impulsive without the medication. No suicidal thoughts, no depression, no anxiety crisis. I feel fine.",
    "unknown": "I'm not sure what you're asking. Can you rephrase that?"
}

def main():
    with open(CASES_FILE) as f:
        cases = json.load(f)

    for case in cases:
        case['chat_responses'] = new_responses[case['id']]

    with open(CASES_FILE, 'w') as f:
        json.dump(cases, f, indent=2, ensure_ascii=False)

    # Verify
    for case in cases:
        keys = set(case['chat_responses'].keys())
        status = "OK" if len(keys) == 25 else "WARN"
        print(f"Case {case['id']}: {len(keys)} keys {status}")

    print("\nDone.")

if __name__ == "__main__":
    main()
