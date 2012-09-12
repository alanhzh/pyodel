# -*- coding: utf-8 -*-
DATA = """TABLE auth_user
auth_user.id,auth_user.first_name,auth_user.last_name,auth_user.email,auth_user.password,auth_user.registration_key,auth_user.reset_password_key,auth_user.registration_id
1,Doctor,Vogeler,drvogeler@example.com,"pbkdf2(1000,20,sha512)$8cb58a96c0735950$006073203dc23268ddf52a5b964282a00e510f76",,,


TABLE auth_group
auth_group.id,auth_group.role,auth_group.description
1,user_1,Group uniquely assigned to user 1
2,wiki_editor,<NULL>
3,manager,Managers group


TABLE auth_membership
auth_membership.id,auth_membership.user_id,auth_membership.group_id
1,1,1
2,1,2
3,1,3


TABLE auth_permission


TABLE auth_event
auth_event.id,auth_event.time_stamp,auth_event.client_ip,auth_event.user_id,auth_event.origin,auth_event.description
1,2012-09-09 17:53:37,127.0.0.1,1,auth,User 1 Logged-out
2,2012-09-09 17:54:16,127.0.0.1,<NULL>,auth,Group 1 created
3,2012-09-09 17:54:16,127.0.0.1,1,auth,User 1 Registered


TABLE auth_cas


TABLE wiki_media


TABLE wiki_tag
wiki_tag.id,wiki_tag.name,wiki_tag.wiki_page,wiki_tag.is_active,wiki_tag.created_on,wiki_tag.created_by,wiki_tag.modified_on,wiki_tag.modified_by
1,more,1,True,2012-09-09 18:08:45,1,2012-09-09 18:08:45,1
2,yodeling,1,True,2012-09-09 18:08:45,1,2012-09-09 18:08:45,1
3,early,2,True,2012-09-09 18:09:50,1,2012-09-09 18:09:50,1
4,days,2,True,2012-09-09 18:09:50,1,2012-09-09 18:09:50,1
5,yodeling,2,True,2012-09-09 18:09:50,1,2012-09-09 18:09:50,1
6,yodel,3,True,2012-09-09 18:11:17,1,2012-09-09 18:11:17,1
7,gorilla,3,True,2012-09-09 18:11:17,1,2012-09-09 18:11:17,1
8,yodel,4,True,2012-09-09 18:12:22,1,2012-09-09 18:12:22,1
9,definition,4,True,2012-09-09 18:12:22,1,2012-09-09 18:12:22,1


TABLE wiki_page
wiki_page.id,wiki_page.slug,wiki_page.title,wiki_page.body,wiki_page.tags,wiki_page.can_read,wiki_page.can_edit,wiki_page.changelog,wiki_page.html,wiki_page.is_active,wiki_page.created_on,wiki_page.created_by,wiki_page.modified_on,wiki_page.modified_by
1,more-on-yodeling,More On Yodeling,"## More On Yodeling

[[http://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Swiss_yodelers.jpg/305px-Swiss_yodelers.jpg  200px]]

All human voices are considered to have at least two distinct vocal registers, called the ""head"" and ""chest"" voices, which result from different ways that the tone is produced.[20] Most people can sing tones within a certain range of lower pitch in their chest voices and tones within a certain range of higher pitch in their head voices and spring into their falsetto (an ""unsupported"" register forcing vocal cords in a higher pitch without any head or chest voice air support). In untrained or inexperienced singers, a gap between these ranges often exists, although more experienced singers can control their voices at the point where these ranges overlap and can easily switch between them to produce high-quality tones in either. Yodelling is a particular application of this technique, wherein a singer might switch between these registers several times in only a few seconds and at a high volume. Repeated alternation between registers at a singer's passaggio pitch range produces a very distinctive sound.

For example, in the famous ""Yodel - Ay - EEE - Oooo"", the ""EEE"" is sung in the head voice while all other syllables are in the chest voice.

The best places for Alpine-style yodelling are those with an echo.[citation needed] Ideal natural locations include not only mountain ranges but lakes, rocky gorges or shorelines, and high or open areas with one or more distant rock faces.

### (photo and text source: Wikipedia)",|more|yodeling|,|everybody|,|user_1|,,"<h2>More On Yodeling</h2><p><a href=""200px""><img src=""http://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Swiss_yodelers.jpg/305px-Swiss_yodelers.jpg"" style=""max-width:100%""/></a></p><p>All human voices are considered to have at least two distinct vocal registers, called the ""head"" and ""chest"" voices, which result from different ways that the tone is produced.[20] Most people can sing tones within a certain range of lower pitch in their chest voices and tones within a certain range of higher pitch in their head voices and spring into their falsetto (an ""unsupported"" register forcing vocal cords in a higher pitch without any head or chest voice air support). In untrained or inexperienced singers, a gap between these ranges often exists, although more experienced singers can control their voices at the point where these ranges overlap and can easily switch between them to produce high-quality tones in either. Yodelling is a particular application of this technique, wherein a singer might switch between these registers several times in only a few seconds and at a high volume. Repeated alternation between registers at a singer's passaggio pitch range produces a very distinctive sound.</p><p>For example, in the famous ""Yodel - Ay - EEE - Oooo"", the ""EEE"" is sung in the head voice while all other syllables are in the chest voice.</p><p>The best places for Alpine-style yodelling are those with an echo.[citation needed] Ideal natural locations include not only mountain ranges but lakes, rocky gorges or shorelines, and high or open areas with one or more distant rock faces.</p><h3>(photo and text source: Wikipedia)</h3><div class=""w2p_wiki_tags""><a href=""/pyodel/plugin_pyodel/wiki/_search?q=more"">more</a><a href=""/pyodel/plugin_pyodel/wiki/_search?q=yodeling"">yodeling</a></div>",True,2012-09-09 18:08:45,1,2012-09-09 18:08:45,1
2,early-days-of-yodeling,Early Days Of Yodeling,"## Early Days Of Yodeling

Early years

[[http://upload.wikimedia.org/wikipedia/commons/7/7c/Dezurik_sisters.jpg 200px]]

Most music historians say that the first country music record to include yodeling was ""Rock All Our Babies to Sleep"" sung by Riley Puckett, a blind singer from Georgia. In 1924 in country music, his recording was one of the top hits of that year. Another early yodeler was Emmett Miller, a minstrel show performer, also from Georgia. Miller is little-remembered today, however in the 1920s he recorded the song, ""Lovesick Blues"" which was later a major hit for country singer Hank Williams. Bob Wills, the King of Western Swing, was also influenced by Miller (see the sound file above with Will's singer Tommy Duncan singing ""Blue Yodel No. 1"" in 1937)[21] In the early 1920s African American Winston Holmes started a record label, Merritt Records, and was a performer himself. His vocals included bird calls, train whistles and yodels. He managed and made some songs with blues singer Lottie Kimbrough in the twenties.[22]

Although most historians credit white singer Riley Puckett with the first recorded yodeling record, in 1923 and 1924 black performer Charles Anderson recorded eight sides for the Okeh label which gave a summary account of his vaudeville repertoire during the previous decade. Five of the recorded songs are yodels - ""Sleep, Baby, Sleep"", ""Comic Yodle Song"", ""Coo Coo"" (J K Emmett's Cuckoo Song, adapted for Anderson's famous 60-second sustained soprano note), ""Laughing Yodel"" and ""Roll On Silver Moon"", a sentimental ballad, similar to Jimmie Rodgers' various Southern ballad recordings.[23]

### Source: Wikipedia",|early|days|yodeling|,|everybody|,|user_1|,,"<h2>Early Days Of Yodeling</h2><p>Early years</p><p><a href=""200px""><img src=""http://upload.wikimedia.org/wikipedia/commons/7/7c/Dezurik_sisters.jpg"" style=""max-width:100%""/></a></p><p>Most music historians say that the first country music record to include yodeling was ""Rock All Our Babies to Sleep"" sung by Riley Puckett, a blind singer from Georgia. In 1924 in country music, his recording was one of the top hits of that year. Another early yodeler was Emmett Miller, a minstrel show performer, also from Georgia. Miller is little-remembered today, however in the 1920s he recorded the song, ""Lovesick Blues"" which was later a major hit for country singer Hank Williams. Bob Wills, the King of Western Swing, was also influenced by Miller (see the sound file above with Will's singer Tommy Duncan singing ""Blue Yodel No. 1"" in 1937)[21] In the early 1920s African American Winston Holmes started a record label, Merritt Records, and was a performer himself. His vocals included bird calls, train whistles and yodels. He managed and made some songs with blues singer Lottie Kimbrough in the twenties.[22]</p><p>Although most historians credit white singer Riley Puckett with the first recorded yodeling record, in 1923 and 1924 black performer Charles Anderson recorded eight sides for the Okeh label which gave a summary account of his vaudeville repertoire during the previous decade. Five of the recorded songs are yodels - ""Sleep, Baby, Sleep"", ""Comic Yodle Song"", ""Coo Coo"" (J K Emmett's Cuckoo Song, adapted for Anderson's famous 60-second sustained soprano note), ""Laughing Yodel"" and ""Roll On Silver Moon"", a sentimental ballad, similar to Jimmie Rodgers' various Southern ballad recordings.[23]</p><h3>Source: Wikipedia</h3><div class=""w2p_wiki_tags""><a href=""/pyodel/plugin_pyodel/wiki/_search?q=early"">early</a><a href=""/pyodel/plugin_pyodel/wiki/_search?q=days"">days</a><a href=""/pyodel/plugin_pyodel/wiki/_search?q=yodeling"">yodeling</a></div>",True,2012-09-09 18:09:50,1,2012-09-09 18:09:50,1
3,yodel,Yodel,"## Yodel

### From Nookipedia, the Animal Crossing wiki.

- Yodel
[[http://nookipedia.com/w/images/a/af/Yodel.gif 100px]]
- Gender Male
- Personality Lazy
- SpeciesGorilla
- Initial phrase ""yodellay""
- Initial clothes Blue Aloha Shirt
- Appearances Dōbutsu no Mori +,
- Animal Crossing,
- Dōbutsu no Mori e+

Yodel (ヨーデル) is a lazy gorilla islander. He only appeared in Dōbutsu no Mori +, Animal Crossing, and Dōbutsu no Mori e+, two of which are Japanese-exclusive.
[edit] Appearance

Yodel is a grey gorilla who appears to dress as a warm-clothed hiker, which is also where his name ""Yodel"" originated from, for yodel is usually what is thought hikers would do up on the mountain peaks. He initially wears the blue aloha shirt. If you look closely, he also has a white bushy mustache and warm winter hat.
[edit] Personality

Below is a brief description of the lazy personality. For more information, click here.

Yodel has a lazy personality, which means he will enoy eating and sleeping. He won't get along with jock villagers due to their diffirent lifestyles, one always excersising and eating healthy while the other is never excersisng and eats junk food most of the time. Yodel also won't get along with snooty villagers due to him not caring about his physical appearance. Cranky villagers will admire their laid-back lifestyle. When wearing one of your desgins he may ask you to design him a shirt with a picture of food on it.
[edit] Fruit Allergy

As an islander, Yodel has a favorite fruit and a fruit that he is allergic to. Feeding him the allergy fruit will reduce the likelihood of him dropping money bags. Yodel is allergic to cherries and loves apples. 

(source: http://nookipedia.com/wiki/Yodel)",|yodel|gorilla|,|everybody|,|user_1|,,"<h2>Yodel</h2><h3>From Nookipedia, the Animal Crossing wiki.</h3><ul><li>Yodel</li></ul><p><a href=""100px""><img src=""http://nookipedia.com/w/images/a/af/Yodel.gif"" style=""max-width:100%""/></a></p><ul><li>Gender Male</li><li>Personality Lazy</li><li>SpeciesGorilla</li><li>Initial phrase ""yodellay""</li><li>Initial clothes Blue Aloha Shirt</li><li>Appearances Dōbutsu no Mori +,</li><li>Animal Crossing,</li><li>Dōbutsu no Mori e+</li></ul><p>Yodel (ヨーデル) is a lazy gorilla islander. He only appeared in Dōbutsu no Mori +, Animal Crossing, and Dōbutsu no Mori e+, two of which are Japanese-exclusive. [edit] Appearance</p><p>Yodel is a grey gorilla who appears to dress as a warm-clothed hiker, which is also where his name ""Yodel"" originated from, for yodel is usually what is thought hikers would do up on the mountain peaks. He initially wears the blue aloha shirt. If you look closely, he also has a white bushy mustache and warm winter hat. [edit] Personality</p><p>Below is a brief description of the lazy personality. For more information, click here.</p><p>Yodel has a lazy personality, which means he will enoy eating and sleeping. He won't get along with jock villagers due to their diffirent lifestyles, one always excersising and eating healthy while the other is never excersisng and eats junk food most of the time. Yodel also won't get along with snooty villagers due to him not caring about his physical appearance. Cranky villagers will admire their laid-back lifestyle. When wearing one of your desgins he may ask you to design him a shirt with a picture of food on it. [edit] Fruit Allergy</p><p>As an islander, Yodel has a favorite fruit and a fruit that he is allergic to. Feeding him the allergy fruit will reduce the likelihood of him dropping money bags. Yodel is allergic to cherries and loves apples.</p><p>(source: <a href=""http://nookipedia.com/wiki/Yodel"">http://nookipedia.com/wiki/Yodel</a>)</p><div class=""w2p_wiki_tags""><a href=""/pyodel/plugin_pyodel/wiki/_search?q=yodel"">yodel</a><a href=""/pyodel/plugin_pyodel/wiki/_search?q=gorilla"">gorilla</a></div>",True,2012-09-09 18:11:17,1,2012-09-09 18:11:17,1
4,yodel-definition,Yodel Definition,"## Yodel Definition

yodel,  type of singing in which high falsetto and low chest notes are rapidly alternated; its production is helped by the enunciation of open and closed vowels on the low and high notes of wide intervals. Yodeling is also used as a means of communicating over moderate distances by the inhabitants of mountainous regions. It is associated with the Alpine peoples of Switzerland and the Austrian Tirol. But it is found also in other mountain regions (e.g., in China and the Americas) and among the Pygmies of Africa and the Aboriginal peoples of Australia.

In Alpine folk singing, yodeling—frequently mixed with nonsense syllables—occurs in passages called Jodlers, which occur at the beginning, middle, or end of a song. The origin of yodeling is buried in antiquity. It has been suggested that it originated as an imitation of the music of the alpenhorn (alphorn), but this point is uncertain

(source: http://www.britannica.com/EBchecked/topic/653399/yodel)",|yodel|definition|,|everybody|,|user_1|,,"<h2>Yodel Definition</h2><p>yodel,  type of singing in which high falsetto and low chest notes are rapidly alternated; its production is helped by the enunciation of open and closed vowels on the low and high notes of wide intervals. Yodeling is also used as a means of communicating over moderate distances by the inhabitants of mountainous regions. It is associated with the Alpine peoples of Switzerland and the Austrian Tirol. But it is found also in other mountain regions (e.g., in China and the Americas) and among the Pygmies of Africa and the Aboriginal peoples of Australia.</p><p>In Alpine folk singing, yodeling—frequently mixed with nonsense syllables—occurs in passages called Jodlers, which occur at the beginning, middle, or end of a song. The origin of yodeling is buried in antiquity. It has been suggested that it originated as an imitation of the music of the alpenhorn (alphorn), but this point is uncertain</p><p>(source: <a href=""http://www.britannica.com/EBchecked/topic/653399/yodel"">http://www.britannica.com/EBchecked/topic/653399/yodel</a>)</p><div class=""w2p_wiki_tags""><a href=""/pyodel/plugin_pyodel/wiki/_search?q=yodel"">yodel</a><a href=""/pyodel/plugin_pyodel/wiki/_search?q=definition"">definition</a></div>",True,2012-09-09 18:12:22,1,2012-09-09 18:12:22,1


TABLE plugin_pyodel_stream
plugin_pyodel_stream.id,plugin_pyodel_stream.live,plugin_pyodel_stream.name,plugin_pyodel_stream.body,plugin_pyodel_stream.html,plugin_pyodel_stream.starts,plugin_pyodel_stream.ends,plugin_pyodel_stream.tags
1,False,Einen Jodler,Franzl Lang sings  ''Einen Jodler hör i gern '',"<iframe width=""640"" height=""360"" src=""https://www.youtube.com/embed/67rc96joOz8?feature=player_detailpage"" frameborder=""0"" allowfullscreen></iframe>",2012-09-09 18:14:12,<NULL>,|franzl lang|yodel|
2,False,Auf und auf voll Lebenslust,Franzl Lang sings for Lebenslust,"<iframe width=""640"" height=""360"" src=""https://www.youtube.com/embed/bXvoe7U1nwo?feature=player_detailpage"" frameborder=""0"" allowfullscreen></iframe>
",2012-09-09 18:15:20,<NULL>,|franzl lang|yodel|
3,False,Vogeler teaches yodeling,The now classic Yodel course from professor Vogeler,"<iframe width=""420"" height=""315"" src=""http://www.youtube.com/embed/lliHC7QSiG8?rel=0"" frameborder=""0"" allowfullscreen></iframe>",2012-09-09 18:14:12,<NULL>,|professor|vogeler|yodel|teachings|


TABLE plugin_pyodel_course
plugin_pyodel_course.id,plugin_pyodel_course.subject,plugin_pyodel_course.active,plugin_pyodel_course.template,plugin_pyodel_course.code,plugin_pyodel_course.abbreviation,plugin_pyodel_course.name,plugin_pyodel_course.description,plugin_pyodel_course.streams,plugin_pyodel_course.body,plugin_pyodel_course.by,plugin_pyodel_course.starts,plugin_pyodel_course.documents,plugin_pyodel_course.ends,plugin_pyodel_course.tags,plugin_pyodel_course.cost
1,Yodel,True,False,Pyodel-demo,Ydl-I,A primer course on Yodeling,"### Professor Vogeler's institute first course on Yodeling

# Yodeling with Yodeling diploma

- ``With a **degree** in ''Yodeling''``:gray
- ``With a **degree** in ''diploma-yodeling''``:green
- ``It'is **different** from yodeling without Yodeling diploma``:red
- ``Thus **diploma** yodeling cannot be compared``:gray
- ``to normal yodeling without **diploma**``:green
- ``Without a **degree** in ''Yodeling''``:red
- ``and degree in ''Yodeling **diploma**''``:gray",|3|,"## How to explain the increasing success of the Vogeler Yodeling institute?

Dr Vogeler personally founded the Vogeler institute, the Institute Of Modern Yodeling.

``Professional yodeling training is not reserved for men only
All people a housewife with children should have a completed vocational training.
When the time comes and your grown-up children move away, or if anything unexpected happens, then one receives a Yodeling Diploma after two years in the Yodeling school.
This is our own thing.
And we can be certain to stand on our own two feet.
This is our own thing. Then we have our Yodeling diploma.
We want to do something with a purpose. We are not content with only doing the cooking or anything else.
Our usbands/wives want a genuine partner who develops his own intellectual skills. For the family. For society``:green",|1|,<NULL>,|4|,<NULL>,|yodel|,0.0


TABLE plugin_pyodel_lecture
plugin_pyodel_lecture.id,plugin_pyodel_lecture.template,plugin_pyodel_lecture.chapter,plugin_pyodel_lecture.name,plugin_pyodel_lecture.course,plugin_pyodel_lecture.streams,plugin_pyodel_lecture.description,plugin_pyodel_lecture.body,plugin_pyodel_lecture.by,plugin_pyodel_lecture.documents,plugin_pyodel_lecture.tags
1,False,1,Yodeling stories,1,|2|1|,"# What is Yodel  Yodeling (or yodelling, jodeling) is a form of singing that involves singing an extended note which rapidly and repeatedly changes in pitch from the vocal or chest register (or ""chest voice"") to the falsetto/head register; making a high-low-high-low sound. (source: http://en.wikipedia.org/wiki/Yodeling)","The English word yodel is derived from a German word jodeln (originally Austro-Bavarian language) meaning ""to utter the syllable jo"" (pronounced ""yo"" in English).

This vocal technique is used in many cultures throughout the world.[1] Although traveling minstrels were yodeling in their performances in the United Kingdom and the United States as early as the eighteen-hundreds, most music historians credit the first recording to include yodeling to Riley Puckett in 1924.

In 1928, blending traditional work, blues, hobo and cowboy music, Jimmie Rodgers released his first recording ""Blue Yodel No. 1"", and created an instant national craze for yodeling in the United States. The popularity lasted through the 1940s, but by the 1950s it became rare to hear yodeling in Country or Western music

Source: http://en.wikipedia.org/wiki/Yodeling",|1|,|2|1|,|yodel|stories|
2,False,2,Second lesson on Yodel,1,|2|1|,"# Basic yodel voices

The lesson starts with the classic ''Holleree Dee Doodle Yirh'', ending with the also very well known ''Deeree Deeree Doodle Dirh''
","- Holleree Dee Doodle Yirh
- Excuse me. How do I spell Dee Doodle?
- As Pronounced: Dee Doodle
- Deeree Dee Dee Doodle Dirh
- Doo Dell?
- Dle ... Doo Dle!
- Hollerah Dee Duhdle Doh ... Hollerah Dee Duhdle Doh
- Holleree Doo Dirdle Dee ... Holleree Doo Dirdle Dee
- Deeree Deeree Dirdle Doo ... Deeree Deeree Dirdle Doo
- Let's try to recite the basic motifs of the 'Archduke Johann Jodler' as far as we've got.
- Dr Sudermann, please. Holleree ...
- Er ... Holleree Dee ...
- ... Doodle ...
- ... Doodle ...
- ... Yihr ...
- ... Yihr ...
- Mr. Von Lilienkron! ... Hollerah ...
- Hollerah Dee Duhdle Doh
- Thank You ... Ms Hoppenstedt! ...
- Hollerah Duh Deedl ...
- Holleree!
- Holleree Dee Doodle Doo ...
- Doo Dirdle Dee!
- Um ... Holleree Doo Dirdle Doo
- Doo Dirdle Dee!!
- Repeat whole phrase, please ...
- Hollerirh Dirh Doodle Dirh
- Doo Dirdle Dee!!
- Dirh Doodle Dirh is 2nd future tense at sunrise
- Holleree Doo Deedle Doh
- Dee Doodle Dirh!
- Er ... Doo Dirdle Dee
- Holla Hee
- Holleree
- Holleree Dirh Deedle
- Doo Dirdle!
- Doo Dirdle Dee ...
- And everybody, please!
- Holleree Doo Dirdle Dee
- Deeree Deeree Doodle Dirh!
- Thank You. That's it for today. We meet again next Thursday at 3.30 pm.
",|1|,|2|1|3|,|yodel|early|lesson|


TABLE plugin_pyodel_attendance


TABLE plugin_pyodel_task


TABLE plugin_pyodel_answer


TABLE plugin_pyodel_question


TABLE plugin_pyodel_test


TABLE plugin_pyodel_quiz
plugin_pyodel_quiz.id,plugin_pyodel_quiz.body,plugin_pyodel_quiz.name,plugin_pyodel_quiz.description,plugin_pyodel_quiz.tags,plugin_pyodel_quiz.shuffle,plugin_pyodel_quiz.score
1,"q: How do I spell Dee Doodle?
i: I cannot yodel on that
i: Interesting...
c: As Pronounced: Dee Doodle
i: Pass
i: Deeree Doodle, of course

q: Holleree Dee Doodle ...?
i: ... Jahr
i: ... Borg
i: ... bong
c: ... Yihr

q: Hollerah Dee Duhdle ...?
i: ... jahr
c: ... Doh
i: ... borg
i: ... bong
c: ... hoD, but in another order
c: ... What for is the question?
m:

q: Dirh Doodle Dirh is ...
i: A mountain near Swizerland
c: 2nd future tense at sunrise
i: Nah, ... I forgot that
i: a horrible salad
c: What does it matter?, I can not even pronounce it
m:

q: Deeree (...) Doodle Dihr?
i: It's second past continuous, I think
i: That's easy: Hollereeehoooo
c: Deeree, naturally
i: This is the correct one (it says so at least)

q: Diploma Yodeling cannot be compared to ...:
i: with a degree in Yodeling
i: degree in Yodeling diploma
c: normal Yodeling without diploma
i: without a degree in Yodeling
i: Yodeling with Yodeling diploma
i: diploma-Yodeling
i: Yodeling-diploma
i: Doo Dirdle Dee",A simple Yodel test,This Quiz serves as a simple test for measuring the minimal requisites of a first course on Yodel.,|yodel|quiz|simple|,False,100.0


TABLE plugin_pyodel_instance
plugin_pyodel_instance.id,plugin_pyodel_instance.name,plugin_pyodel_instance.abbreviation,plugin_pyodel_instance.ordered,plugin_pyodel_instance.formula,plugin_pyodel_instance.replaces
1,First,FI,A,,<NULL>
2,Second,SI,B,,<NULL>
3,Third,TI,C,,<NULL>
4,Final,NI,D,(FI+SI+TI)/3.0,<NULL>


TABLE plugin_pyodel_evaluation
plugin_pyodel_evaluation.id,plugin_pyodel_evaluation.template,plugin_pyodel_evaluation.name,plugin_pyodel_evaluation.code,plugin_pyodel_evaluation.description,plugin_pyodel_evaluation.instance,plugin_pyodel_evaluation.course,plugin_pyodel_evaluation.lectures,plugin_pyodel_evaluation.starts,plugin_pyodel_evaluation.ends,plugin_pyodel_evaluation.students,plugin_pyodel_evaluation.evaluators,plugin_pyodel_evaluation.tests,plugin_pyodel_evaluation.quizzes,plugin_pyodel_evaluation.score,plugin_pyodel_evaluation.tags,plugin_pyodel_evaluation.tasks
1,True,Pyodel demo evaluation,pde-1234,### A sample evaluation template for the Pyodel demo,1,1,|2|1|,2012-09-09 18:27:20,<NULL>,||,|1|,||,|1|,100.0,|yodel|evaluation|,||


TABLE plugin_pyodel_work


TABLE plugin_pyodel_hourglass


TABLE plugin_pyodel_sandglass


TABLE plugin_pyodel_retort


TABLE plugin_pyodel_gradebook


TABLE plugin_pyodel_grade


END
"""
