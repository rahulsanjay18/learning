#!/usr/bin/env python3
"""Write topics/critical-theory/SYLLABUS.md: the professor's syllabus (policies, outcomes, texts, grading, and a
week-by-week schedule with every day's reading). Readings and day counts come from build_plan.py; the prose per course
(descriptions, objectives, seminar questions, essay prompts) lives in META below.

    python3 topics/critical-theory/build_plan.py && python3 topics/critical-theory/build_syllabus.py
"""
import math, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import build_plan as bp  # noqa: E402

ORDER = ["CT100", "CT201", "CT202", "CT203", "CT110", "CT204", "CT130", "CT205", "CT120", "CT206", "CT260",
         "CT207", "CT208", "CT209", "CT210", "CT211", "CT212", "CT290"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
TERM_WEEKS = 15


def tyson_sections(ch):
    """Section headings of Tyson chapter ch, from library/toc (the book's own contents)."""
    lines = (ROOT / "library/toc/dd5a1301fb.md").read_text(encoding="utf-8").splitlines()
    out, on = [], False
    for l in lines:
        m = re.match(r"^- (\d+) ", l)
        if m:
            on = int(m.group(1)) == ch
            continue
        if on and l.startswith("  - "):
            s = re.sub(r"\[\d+\]\([^)]*\)", "", l[4:]).strip()
            if not re.match(r"(For further study|For advanced study|Works cited)", s):
                out.append(s.replace("_", "*"))
    return out or ["whole chapter"]


def chapters(prefix, n, first=1):
    return [f"{prefix}{i}" for i in range(first, first + n)]


SEM_KEYS = {
 'CT100': ['Culler', 'Culler', 'Fitzgerald: ch. 1', ''],
 'CT201': ['Eliot', 'Wimsatt', "The Dead' (second", 'Araby'],
 'CT202': ['Iser', 'Fish', 'Kafka: ch. 9', 'Kafka: ch. 10', ''],
 'CT203': ['Saussure', 'Barthes', 'Shelley: ch. 1', 'Shelley: ch. 24', 'Jakobson', ''],
 'CT110': ['Singer: ch. 4', 'Singer: ch. 6', 'On Truth', 'Tanner: Postlude', ''],
 'CT204': ['Death of the Author', 'Grammatology', 'de Man', 'Frankenstein again', 'Belsey'],
 'CT130': ['Storr: ch. 4', 'Storr: ch. 12', 'Civilization', ''],
 'CT205': ['Some questions', 'Uncanny', 'Shakespeare: Act 5', 'Lacan', ''],
 'CT120': ['Singer, Marx', 'Manifesto', 'Fetishism', 'Weber', 'Aron', 'Mills', ''],
 'CT206': ['Some questions', 'Althusser', 'Yashpal', 'Yashpal, Dada Comrade (part 12', 'Jameson', 'Williams', ''],
 'CT260': ['Bronner', 'Held ch. 1', 'Held ch. 2', 'Culture Industry', 'Benjamin', 'Held ch. 4', 'Held ch. 5', 'Marcuse', 'Habermas', 'Benjamin', 'Held ch. 14', ''],
 'CT207': ['Beauvoir', 'Woolf', 'Woolf, To', "Lighthouse' §11", 'Cixous', 'Chughtai', ''],
 'CT208': ['What Is an Author', 'What Is an Author', 'Greenblatt', 'Backgrounds', 'Stuart Hall', 'Some questions', ''],
 'CT209': ['History of Sexuality', 'Sedgwick', 'Butler', 'Gatsby again', 'Roberts'],
 'CT210': ['Du Bois', 'Ellison: Prologue', 'Ellison: ch. 1', 'Ellison: ch. 6', 'Ellison: ch. 10', 'Ellison: ch. 15', 'Gates', 'Ellison: ch. 23', 'Ellison: ch. 25', 'Ellison: Epilogue', 'Some questions', 'Barbara Smith'],
 'CT211': ['Kennedy', 'Fanon', 'Said', 'Spivak', 'An Image of Africa', 'Achebe: ch. 13', 'Achebe: ch. 25', 'Toba', 'Ngugi', 'Some questions'],
 'CT212': ['Some questions', 'Woolf', 'Haraway'],
 'CT290': ['Tyson ch. 14', 'HoD NCE', 'HoD NCE', 'HoD NCE', 'HoD NCE', 'HoD NCE'],
}

# units a reading is split into, in order (matched by the start of the reading's text)
UNITS = {
    "Culler": ["Ch. 1 What is theory?", "Ch. 2 What is literature?", "Ch. 3 Literature and cultural studies",
               "Ch. 4 Language, meaning, interpretation", "Ch. 5", "Ch. 6", "Ch. 7", "Ch. 8", "Appendix: schools and movements"],
    "Fitzgerald": chapters("ch. ", 9),
    "Singer, Hegel": chapters("ch. ", 6),
    "Tanner": chapters("ch. ", 9) + ["Postlude"],
    "Singer: ch.": chapters("ch. ", 10),
    "Storr": chapters("ch. ", 12),
    "Belsey": chapters("ch. ", 5),
    "Bronner": ["Introduction"] + chapters("ch. ", 10),
    "Gutting": chapters("ch. ", 10),
    "Kennedy": ["Introduction"] + chapters("ch. ", 5),
    "Joyce": ["'Araby'", "'Eveline'", "'The Dead' (first half)", "'The Dead' (second half)"],
    "Kafka": chapters("ch. ", 10),
    "Shelley": ["Letters 1-4"] + chapters("ch. ", 24),
    "Shakespeare": [f"Act {a}" for a in "1 2 3 4 5".split()],
    "Woolf: 'The Window'": [f"'The Window' §{a}-{b}" for a, b in ((1, 5), (6, 10), (11, 15), (16, 19))] +
                 ["'Time Passes' §1-10"] + [f"'The Lighthouse' §{a}-{b}" for a, b in ((1, 5), (6, 10), (11, 14))],
    "Ellison": ["Prologue"] + chapters("ch. ", 25) + ["Epilogue"],
    "Achebe, Things": chapters("ch. ", 25),
}


def units_for(r):
    w = r["what"]
    m = re.match(r"Tyson ch\. (\d+)", w)
    if m:
        return tyson_sections(int(m.group(1)))
    for k, u in UNITS.items():
        if w.startswith(k):
            return u
    return None


def short(w):
    """Short citation for a reading, used in the daily schedule."""
    w = re.sub(r" \(pp\. \d+-\d+\)$", "", w)
    w = re.sub(r"\s*\((whole|selections|from)[^)]*\)", "", w)
    return w


FULL = {}


def slices(r):
    """One label per reading day."""
    d, _ = bp.days(r)
    w = r["what"]
    if "pages" in r:  # split the page span evenly
        n, book = r["pages"]
        m = re.search(r"pp\. (\d+)-(\d+)", w)
        p0 = int(m.group(1)) if m else None
        name = {"norton": "Norton", "held": "Held", "nce": "Norton Critical HoD"}[book]
        if p0 is None:
            return [f"{short(w)} ({i + 1}/{d})" if d > 1 else short(w) for i in range(d)]
        cuts = [p0 + round(i * n / d) for i in range(d + 1)]
        return [f"{short(w)}, pp. {cuts[i]}-{cuts[i + 1]}" if d > 1 else f"{short(w)}, pp. {cuts[0]}-{cuts[1]}"
                for i in range(d)]
    u = units_for(r)
    base = re.split(r"[:,(]", w)[0].strip() if not w.startswith("Tyson") else w.split(":")[0]
    if not u:
        return [f"{short(w)}" + (f" (part {i + 1} of {d})" if d > 1 else "") for i in range(d)]
    if len(u) >= d:  # several units a day
        out = []
        for i in range(d):
            seg = u[math.floor(i * len(u) / d):math.floor((i + 1) * len(u) / d)]
            label = f"{base}: {seg[0] if len(seg) == 1 else seg[0] + ' → ' + seg[-1]}"
            FULL[label] = f"{base}: " + " ; ".join(seg)  # every unit, for matching seminar questions
            out.append(label)
        return out
    idx = [math.floor(i * len(u) / d) for i in range(d)]  # fewer units than days: a unit spans several days
    return [f"{base}: {u[k]}" + (f" (part {idx[:i + 1].count(k)} of {idx.count(k)})" if idx.count(k) > 1 else "")
            for i, k in enumerate(idx)]


# ---------------------------------------------------------------- the professor's prose, per course
META = {
 "CT100": dict(
   desc="What is 'theory', and why do English departments, sociologists and philosophers all argue about it? Culler's short book "
        "maps the questions; Tyson's first chapter shows why a lens changes what you see. You read *The Great Gatsby* alongside, "
        "because it is the novel every lens in this program is first tried on.",
   obj=["say what a 'lens' is and what it is not (a lens selects evidence; it doesn't invent it)",
        "name the main schools and the one question each asks of a text",
        "summarize Gatsby's plot and narrator well enough to test every later reading against it"],
   sem=["Culler says theory is 'a body of thinking and writing whose limits are exceedingly hard to define.' Is that a dodge or a definition?",
        "Is literature a kind of language or a way of using language? Test both answers on the first page of Gatsby.",
        "Nick says he is 'one of the few honest people' he has known. What would it take to believe him?",
        "Open seminar: pick the Gatsby scene you think is most important, and say what made you pick it (that is already a lens)."],
   essay="In ~600 words: what is the most important sentence in *The Great Gatsby*, and why? Then name the assumptions your answer makes about what reading is for."),
 "CT201": dict(
   desc="The New Critics taught the twentieth century to read closely: the text itself, its tensions, ironies and images, not the "
        "author's life or the reader's feelings. Every later lens, even the ones that attack it, still uses its close reading.",
   obj=["explain the intentional and affective fallacies and the 'heresy of paraphrase'",
        "do a close reading: find a tension in a passage and show how imagery resolves or sustains it",
        "say what New Criticism leaves out and why later critics objected"],
   sem=["Eliot: the poet's mind is a catalyst, not a personality. Is that true of any writer you know?",
        "Wimsatt & Beardsley say the author's intention is 'neither available nor desirable' as a standard. Argue the other side.",
        "Brooks says a poem's meaning can't be paraphrased. Try to paraphrase the last paragraph of 'The Dead', then say what was lost.",
        "Open seminar: close reading of the epiphany in 'Araby'."],
   essay="A close reading (~600 words) of one passage from 'The Dead': its central tension, the images that carry it, and how the ending handles it."),
 "CT202": dict(
   desc="Meaning happens when someone reads. Reader-response critics study that event: the gaps a text leaves, the expectations it "
        "builds and breaks, and the communities that teach us how to read. Kafka's *The Trial* is a book built out of gaps.",
   obj=["tell apart transactional, affective, subjective, psychological and social reader-response theory",
        "describe Iser's 'gaps' and Fish's 'interpretive communities' and where they disagree",
        "track your own reading: what you expected, when it broke, what you filled in"],
   sem=["Iser says the reader fills the text's gaps. Where did you fill one in the first chapters of The Trial, and with what?",
        "Fish: there is no text apart from an interpretive community. If so, can a reading ever be wrong?",
        "The parable 'Before the Law' (ch. 9): the priest gives several readings. Which interpretive communities do they belong to?",
        "Your reading log versus the ending: what did The Trial train you to expect?",
        "Open seminar: compare your reading of Gatsby ch. 1 now with your first reading."],
   essay="~600 words: a reader-response account of *The Trial*. Use your own reading log as evidence."),
 "CT203": dict(
   desc="Structuralism looks past single texts to the systems that make meaning possible: Saussure's language, myths, genres, "
        "narratives. You will learn to see a story's grammar. *Frankenstein*'s nested narrators are an ideal specimen.",
   obj=["explain signifier/signified, arbitrariness, and meaning by difference (Saussure)",
        "describe a narrative's structure: frames, narrators, order and the binary oppositions it is built on",
        "read an everyday object as a sign system, as Barthes does in Mythologies"],
   sem=["Saussure: in language there are only differences. Explain with an example from a language you know.",
        "Barthes reads soap powder ads as myth. Do the same with an ad you saw this week.",
        "Draw Frankenstein's frames (Walton → Victor → the creature). Who is speaking to whom, and why does it matter?",
        "Which binary oppositions hold Frankenstein together (creator/creature, nature/science...)? Which is central?",
        "Jakobson's six functions of language: find each in Walton's letters.",
        "Open seminar: is structuralism a science of literature, and should it be?"],
   essay="~600 words: a structuralist account of *Frankenstein*: its narrative frames and its organizing oppositions."),
 "CT110": dict(
   desc="Foundations from philosophy. Most of the lenses argue with Hegel (history, dialectic, the master-slave struggle) or "
        "with Nietzsche (truth as metaphor, genealogy, perspectivism). Read these two now so that Derrida, Marx and Foucault have context.",
   obj=["explain dialectic and the master-slave relation in Hegel",
        "explain Nietzsche's claim that truths are 'illusions of which we have forgotten that they are illusions'",
        "trace one line from each thinker to a lens you will meet later"],
   sem=["Master and slave: why does Hegel think the slave, not the master, ends up with self-consciousness?",
        "Is Hegel's history of freedom progress, or a story told by the winners?",
        "Nietzsche: truths are 'illusions of which we have forgotten that they are illusions.' Is that claim self-refuting?",
        "Perspectivism and lenses: does Nietzsche license 'every reading is as good as any other'? (Hint: he says no.)",
        "Open seminar: which of the two would make the better literary critic?"],
   essay="~600 words: take one idea from Hegel and one from Nietzsche and show what each lets you see in a text you've read so far."),
 "CT204": dict(
   desc="Deconstruction takes structuralism's binaries and shows how every text undoes its own hierarchy. Barthes kills the "
        "author; Derrida reads the margins; de Man finds rhetoric undoing grammar. You return to *Frankenstein* to watch its oppositions come apart.",
   obj=["explain différance, the trace and the undoing of binary oppositions in plain words",
        "deconstruct a passage: find the privileged term, then the place where the text undermines it",
        "explain what 'the death of the author' does and does not claim"],
   sem=["Barthes: 'the birth of the reader must be at the cost of the death of the Author.' What does the reader gain, and lose?",
        "Derrida on speech and writing: why would philosophy prefer speech?",
        "de Man's 'What's the difference?' example: grammar says one thing, rhetoric another. Find one in Frankenstein.",
        "Which of Frankenstein's oppositions (creator/creature, human/monster) collapses first?",
        "Is deconstruction nihilism? Use Tyson and Belsey to answer."],
   essay="~600 words: a deconstructive reading of *Frankenstein*: one opposition the novel sets up and the point where it undoes itself."),
 "CT130": dict(
   desc="Foundations from psychology. Freud's theory of the unconscious, repression, dreams and the Oedipus complex underlies "
        "psychoanalytic criticism and much of Frankfurt School and feminist theory. Read him as a theory of interpretation, not as current clinical science.",
   obj=["explain the unconscious, repression, defenses, and dream-work (condensation, displacement)",
        "say what Freud thinks civilization costs the individual",
        "separate Freud's interpretive method from his clinical claims, with what current psychology accepts and rejects"],
   sem=["Dream-work: condensation and displacement. Find both in a dream you remember (or a scene in Hamlet).",
        "Storr is sympathetic but critical. Which of Freud's claims does he think have survived?",
        "Civilization and Its Discontents: why does civilization make us unhappy, according to Freud?",
        "Open seminar: if psychoanalysis fails as science, can it still work as a method of reading?"],
   essay="~600 words: explain one Freudian concept and use it to read a scene from any text read so far. Say what the concept lets you see that a plain reading missed."),
 "CT205": dict(
   desc="Psychoanalytic criticism reads texts (and characters, and readers) for what they repress. Freud's uncanny, Lacan's "
        "mirror stage, and the most psychoanalyzed play in English, *Hamlet*.",
   obj=["apply core issues and defenses to a character without diagnosing the author",
        "explain the uncanny (das Unheimliche) and Lacan's mirror stage",
        "judge when a psychoanalytic reading is supported by the text and when it is imposed"],
   sem=["Tyson reads Gatsby for fear of intimacy. Which details carry the reading?",
        "Freud's uncanny: the familiar made strange. Where is Hamlet uncanny?",
        "Why does Hamlet delay? List the explanations, then pick the one with the most textual evidence.",
        "Lacan's mirror stage: what does it add to Freud?",
        "Open seminar: is the Oedipal reading of Hamlet a discovery or an imposition?"],
   essay="~600 words: a psychoanalytic reading of *Hamlet* (or of *Frankenstein*'s creature). Use textual evidence; diagnose the text, not the author."),
 "CT120": dict(
   desc="Foundations from social theory. Marx (class, ideology, alienation, the commodity), Weber (the spirit of capitalism, "
        "rationalization) and Durkheim (society as a moral fact) are the starting points of sociology and of Marxist, Frankfurt and cultural criticism. Mills shows how to connect a life to its society.",
   obj=["explain base and superstructure, ideology, alienation and commodity fetishism",
        "explain Weber's thesis on the Protestant ethic and why it challenges a purely economic account",
        "use Mills's 'sociological imagination' to link a character's private trouble to a public issue"],
   sem=["Singer: what is living and what is dead in Marx?",
        "The Manifesto: which predictions failed, which came true, and does that matter for using Marx as a lens?",
        "Commodity fetishism: describe a social relation hidden in a thing you own.",
        "Weber vs. Marx: do ideas drive economic change, or the other way round?",
        "Durkheim: is society more than the people in it?",
        "Mills: private troubles and public issues. Apply it to Jay Gatsby.",
        "Open seminar: Marx, Weber or Durkheim: which would explain your job best?"],
   essay="~600 words: explain one idea from Marx and one from Weber or Durkheim, and use them to read Gatsby's world."),
 "CT206": dict(
   desc="Marxist criticism reads literature as part of history and class struggle: ideology, hegemony, the institutions that "
        "reproduce them, and the 'political unconscious' of form. The application text is *Dada Comrade* (1941), a Hindi novel by a "
        "former revolutionary, which connects to your Indian History major.",
   obj=["explain ideology (Althusser), hegemony (Gramsci) and the political unconscious (Jameson)",
        "read a text for class: who works, who owns, what the story treats as natural",
        "judge whether a text reinforces or questions the ideology it depicts"],
   sem=["Tyson: 'you are what you own' in Gatsby. Strongest piece of evidence?",
        "Althusser's ideological state apparatuses: which ones shaped you?",
        "Gramsci's intellectuals: who are the 'organic intellectuals' in Dada Comrade?",
        "Does Dada Comrade criticize the revolution it depicts, or only the Raj?",
        "Jameson: 'always historicize!' What does that do to a reading of a love story?",
        "Raymond Williams: 'literature' is itself a historical category. So what?",
        "Open seminar: is Marxist criticism still useful after the Cold War?"],
   essay="~800 words: a Marxist reading of *Dada Comrade*: class, ideology, and whether the novel sees past its own."),
 "CT260": dict(
   desc="The Frankfurt School (capital-C Critical Theory): Horkheimer, Adorno, Marcuse, Benjamin, Fromm and later Habermas. Western Marxists "
        "who fled Nazi Germany and asked why the revolution never came: mass culture, authoritarianism, instrumental reason. "
        "Held is the textbook, Bronner the on-ramp, and the Norton gives the classic essays. You end by applying them to culture now.",
   obj=["tell the Institute's history: Weimar, exile in America, return, and why it matters for the ideas",
        "explain the culture industry, instrumental reason and one-dimensionality",
        "contrast Adorno and Benjamin on mass art, and say where Habermas breaks with both"],
   sem=["Bronner: what makes a theory 'critical' rather than 'traditional'?",
        "Held ch. 1: how did exile shape the Institute's research program?",
        "Held ch. 2: why did Critical Theory move from political economy to culture?",
        "The culture industry: 'something is provided for all so that none may escape.' Test it on a streaming service.",
        "Benjamin's aura: does mechanical (or digital) reproduction free art or empty it?",
        "Held ch. 4: why did the Frankfurt School need Freud?",
        "Dialectic of Enlightenment: how can reason become domination?",
        "Marcuse: 'one-dimensional' society absorbs its own opposition. Example from today?",
        "Habermas: the public sphere and its decline. Is social media a public sphere?",
        "Adorno vs. Benjamin: who wins the argument about film?",
        "Held ch. 14: what problems does Held say remain unsolved?",
        "Open seminar: was the Frankfurt School too pessimistic?"],
   essay="~800 words: read one film, game, or feed you use with Adorno and Benjamin. Who explains it better?"),
 "CT207": dict(
   desc="Feminist criticism asks how texts build, enforce and resist gender: Beauvoir's 'woman as Other', Woolf's room and money, "
        "Gilbert & Gubar's madwoman, Cixous's écriture féminine. Applied to Woolf's own *To the Lighthouse* and Chughtai's 'Lihaaf'.",
   obj=["explain patriarchy, the Other (Beauvoir) and traditional gender roles as Tyson defines them",
        "tell apart the waves and the French, multicultural and gender-studies strands",
        "read a text for how it both reproduces and resists its gender ideology"],
   sem=["Beauvoir: 'One is not born, but rather becomes, a woman.' What does 'becomes' do?",
        "Woolf's Shakespeare's sister: what does the thought experiment prove?",
        "Mrs. Ramsay: patriarchy's victim, enforcer, or artist?",
        "Lily Briscoe finishes her painting. What has changed?",
        "Cixous: 'write your self. Your body must be heard.' Does To the Lighthouse do this?",
        "Chughtai calls 'Lihaaf' 'the story that had become a source of torment for me' (her memoir of Manto, in the same volume). Why would it torment its author?",
        "Open seminar: is Tyson's feminist reading of Gatsby fair to Daisy?"],
   essay="~800 words: a feminist reading of *To the Lighthouse* (with 'Lihaaf' as a comparison if you like)."),
 "CT208": dict(
   desc="New historicism reads literature alongside non-literary texts of its moment as one web of power and discourse (Foucault, "
        "Greenblatt); cultural studies widens the canon to all of culture (Hall). *Heart of Darkness* is read with Conrad's own "
        "Congo diary and letters.",
   obj=["explain discourse, power/knowledge and the author-function (Foucault)",
        "do a new historicist reading: put a literary text next to a non-literary one of its time",
        "explain how new historicism differs from old historicism and from Marxism"],
   sem=["Foucault: 'What is an author?' Why does the author-function exist?",
        "Discipline and Punish: the carceral. Where else do you see surveillance producing the people it watches?",
        "Greenblatt: why read a novel next to a diary rather than a 'background' history?",
        "Conrad's Congo Diary against Marlow's narrative: what changed between experience and fiction?",
        "Hall: what is cultural studies for?",
        "Tyson's 'self-made man' discourse in Gatsby: name today's equivalent.",
        "Open seminar: does new historicism leave room for literature to resist power?"],
   essay="~800 words: a new historicist reading of *Heart of Darkness* using at least two of the backgrounds documents."),
 "CT209": dict(
   desc="Lesbian, gay and queer criticism: the history of sexuality as a history of categories (Foucault), the homosocial (Sedgwick), "
        "gender as performance (Butler). Back to Nick Carraway, 'Lihaaf', and Marlow.",
   obj=["explain homosociality, the closet, and gender performativity",
        "tell lesbian, gay and queer criticism apart and say what they share",
        "judge a queer reading's evidence (Tyson's Nick Carraway reading is a good test case)"],
   sem=["Foucault: why does he call the 'repressive hypothesis' into question?",
        "Sedgwick's triangle: two men and a woman. Find one in Gatsby.",
        "Butler: if gender is performative, what is it a performance of?",
        "Tyson's queer Nick: convincing? Which scenes carry it?",
        "Open seminar: Roberts on masculinity in Heart of Darkness."],
   essay="~600 words: assess Tyson's queer reading of Nick Carraway: what it explains, what it strains, and your verdict."),
 "CT210": dict(
   desc="African American criticism and critical race theory: Du Bois, Hughes and Hurston on art and race, Gates on Signifyin', "
        "Barbara Smith on Black feminism, and CRT's tenets as Tyson summarizes them. Applied to Ellison's *Invisible Man*, one of the "
        "major American novels.",
   obj=["explain double consciousness, Signifyin(g) and CRT's main tenets as Tyson presents them",
        "read a text for how race structures its world, its narration and its silences",
        "connect Invisible Man's episodes to the debates in the theory readings"],
   sem=["Du Bois: 'all Art is propaganda.' Hughes and Hurston answer him. Who's right?",
        "The Prologue: why does the narrator live underground with 1,369 light bulbs?",
        "The Battle Royal: what is the scholarship for?",
        "Bledsoe and the college: Tyson's 'internalized racism' or something else?",
        "Liberty Paints ('Optic White'): what is the symbol doing?",
        "The Brotherhood: Ellison's critique of the Left. Fair?",
        "Gates's Signifyin(g): where does Ellison signify on earlier texts?",
        "Rinehart: identity as performance (compare Butler).",
        "The Harlem riot: how does the novel end its plot?",
        "The Epilogue: 'Who knows but that, on the lower frequencies, I speak for you?'",
        "Tyson's 'But where's Harlem?' reading of Gatsby: what does absence show?",
        "Open seminar: Barbara Smith's critique and the women in Invisible Man."],
   essay="~800 words: a reading of *Invisible Man* through one concept from the theory readings."),
 "CT211": dict(
   desc="Postcolonial criticism reads the culture of empire and its aftermath: Fanon on national consciousness, Said's Orientalism, "
        "Spivak's subaltern, Ngũgĩ on the English department, and Achebe's charge that *Heart of Darkness* is racist, which *Things Fall Apart* answers in fiction. "
        "Kennedy's history of decolonization gives the facts.",
   obj=["explain Orientalism, othering, the subaltern, mimicry and hybridity",
        "summarize the history of decolonization (waves, wars, the nation-state) well enough to place a text in it",
        "weigh Achebe's charge against Conrad, and say what Things Fall Apart does in reply"],
   sem=["Kennedy: why does he call decolonization a series of waves?",
        "Fanon: what are 'the pitfalls of national consciousness'?",
        "Said: what is Orientalism, and how is it a discourse in Foucault's sense?",
        "Spivak: 'can the subaltern speak?' What answer does she give, and why?",
        "Achebe on Conrad: is the charge of racism fair? Use the novella.",
        "Okonkwo: tragic hero, or a critique of a masculinity?",
        "The District Commissioner's last paragraph: what does it do?",
        "'Toba Tek Singh': Partition as madness, or sanity?",
        "Ngũgĩ: should the English department be abolished?",
        "Open seminar: Tyson's 'colony within' reading of Gatsby."],
   essay="~800 words: read *Things Fall Apart* as an answer to *Heart of Darkness*."),
 "CT212": dict(
   desc="Ecocriticism reads literature for its relation to the nonhuman world: deep ecology, eco-Marxism, ecofeminism, environmental "
        "justice, and Haraway's cyborg blurring nature and machine. Short course; re-reads earlier texts.",
   obj=["tell apart deep ecology, eco-Marxism, ecofeminism and environmental justice",
        "read a text's landscape as more than setting"],
   sem=["Tyson's 'real snow, our snow' reading of Gatsby: what does nature mean in the novel?",
        "'Time Passes': a chapter where nature is the protagonist?",
        "Haraway's cyborg and Frankenstein's creature: allies?"],
   essay="~600 words: an ecocritical re-reading of one text you've already read."),
 "CT290": dict(
   desc="The capstone of Level I. One short novel, a century of criticism. You read ten published essays on *Heart of Darkness*, "
        "name the lens each one uses, judge which readings are best supported, and write your own.",
   obj=["identify the lens (or mix of lenses) behind a published critical essay",
        "judge competing readings by their textual evidence and say what each one sees and misses",
        "write a sustained argument that uses two or more lenses together"],
   sem=["Tyson ch. 14: do the lenses add up to one picture, or do they really disagree?",
        "Guerard's 'journey within' and Watt's impressionism: which lenses?",
        "Brantlinger vs. Hawkins on racism and imperialism",
        "Torgovnick and Hawthorn: the women of Heart of Darkness",
        "Said and Armstrong: reading the other",
        "Miller: should we read Heart of Darkness? Your verdict, with reasons."],
   essay="Final essay (~1,500 words): your reading of *Heart of Darkness*, using at least two lenses and answering at least two of the published critics."),
}


def schedule():
    """Each course starts on a Monday. Every week: Mon-Thu reading days, Fri seminar; the course's last Friday is its lens
    essay. A short last week fills its empty weekdays with catch-up. Returns (weeks, {cid: (first_week, last_week)}, days)."""
    by = {c["id"]: c for c in bp.COURSES}
    weeks, info = [], {}
    for cid in ORDER:
        c, m = by[cid], META[cid]
        reads = [s for part in ("theory", "apply") for r in c.get(part, []) for s in slices(r)]
        nw = math.ceil(len(reads) / bp.SEM)
        used = set()
        first = len(weeks) + 1
        for w in range(nw):
            chunk = reads[w * bp.SEM:(w + 1) * bp.SEM]
            wk = [(cid, "read", r) for r in chunk]
            wk += [(cid, "catch", "Catch-up, or start drafting the lens essay")] * (bp.SEM - len(chunk))
            if w == nw - 1:  # last Friday: the essay, plus the best question still open
                done = " | ".join(reads)
                done = " | ".join(FULL.get(r, r) for r in reads)
                left = [q for k, q in zip(SEM_KEYS[cid], m["sem"]) if q not in used and k and k in done]
                left += [q for k, q in zip(SEM_KEYS[cid], m["sem"]) if q not in used and q not in left]
                extra = (" *Questions left over from the unit (think about them while drafting; answer one if you like):* "
                         + " / ".join(left)) if left else ""
                wk.append((cid, "essay", m["essay"] + extra))
            else:  # the next unused question whose reading (key) has been assigned by now
                done = " | ".join(FULL.get(r, r) for r in reads[:(w + 1) * bp.SEM])
                week = " | ".join(FULL.get(r, r) for r in chunk)
                pairs = [(k, q) for k, q in zip(SEM_KEYS[cid], m["sem"]) if q not in used]
                q = (next((q for k, q in pairs if k and k in week), None)        # about this week's reading
                     or next((q for k, q in pairs if k and k in done), None)     # about an earlier one
                     or (next((q for k, q in pairs if not k), None) if w >= nw - 2 else None))  # a general one, late
                used.add(q)
                wk.append((cid, "seminar", q or f"This week's reading ({re.split(r'[:,(]', chunk[0])[0].strip()}): state its main claim in two sentences, then the part you'd push back on."))
            weeks.append(wk)
        info[cid] = (first, len(weeks))
    days = [d for wk in weeks for d in wk]
    return weeks, info, days


def main():
    by = {c["id"]: c for c in bp.COURSES}
    bp.build()  # refresh day counts
    weeks, info, days = schedule()
    nread = sum(1 for d in days if d[1] == "read")
    nsit = 1 + sum(1 for d in days if d[1] != "catch")
    L = []
    L += ["# Critical Theory, Level I: syllabus",
          "",
          "*Generated by `build_syllabus.py` (readings from `build_plan.py`); edit those, not this file. Drafted 2026-10-08. "
          "Parked: a planned major, not scheduled yet (`programs.json`).*",
          "",
          "| | |", "|---|---|",
          "| **Program** | Critical Theory (a self-directed major; Level I ≈ an undergraduate concentration) |",
          "| **Instructor** | Claude, in your learning sessions (\"office hours\": ask anything, any session) |",
          "| **Meets** | Five sittings a week of ~25 minutes: four reading days, then a seminar day |",
          f"| **Length** | {len(weeks)} weeks ({nread} reading days, {len(weeks)} seminars/essays) ≈ {len(weeks) / TERM_WEEKS:.1f} fifteen-week terms, or ≈ {len(weeks) * 5 / 7 / 4.345:.0f} months if you read every day |",
          "| **Prerequisites** | None. Curiosity, and patience with difficult prose |",
          "",
          "## Course description",
          "Every reading of a text rests on assumptions about language, minds, society, gender, race, power and history. Critical theory "
          "makes those assumptions explicit and turns each one into a **lens**: a set of questions you can bring to any text. This "
          "program teaches twelve lenses, the way most undergraduate theory courses do, and the background each one stands on, which "
          "comes from outside English departments: philosophy (Hegel, Nietzsche), social theory (Marx, Weber, Durkheim), psychology "
          "(Freud), linguistics (Saussure), and history (the Frankfurt School's exile, decolonization). For each lens you read three "
          "things: a clear textbook chapter (Tyson), the theorists themselves (the *Norton Anthology of Theory and Criticism*), and a "
          "literary work to apply it to. Several novels come back under different lenses, because the point is that the same "
          "text reads differently through each one.",
          "",
          "## Learning outcomes",
          "By the end of Level I you can:",
          "1. **Explain** each lens in plain words: its key concepts, its founders, the questions it asks, and what it tends to miss.",
          "2. **Trace** each lens to its intellectual background in philosophy, social theory, psychology, linguistics or history.",
          "3. **Apply** any lens to a text you haven't seen before and write a reading supported by textual evidence.",
          "4. **Judge** published criticism: name the lens it uses, test its evidence, and say which of two readings is better supported.",
          "5. **Read difficult theory**: get the argument out of a primary text (Adorno, Derrida, Spivak) without a summary to lean on.",
          "",
          "## Required texts (all in your library, grade A)",
          "| Book | Role | id |", "|---|---|---|",
          "| Lois Tyson, *Critical Theory Today: A User-Friendly Guide*, 4th ed. (Routledge, 2023) | the textbook: one chapter per lens, each ending with a model reading of *Gatsby* | dd5a1301fb |",
          "| Vincent B. Leitch et al. (eds.), *The Norton Anthology of Theory and Criticism*, 2nd ed. (2010) | the theorists' own words | face941c2e |",
          "| Jonathan Culler, *Literary Theory: A Very Short Introduction* | orientation | 68dc21333b |",
          "| David Held, *Introduction to Critical Theory: Horkheimer to Habermas* (1980) | the Frankfurt School | b6f3f5f15a |",
          "| Stephen Eric Bronner, *Critical Theory: A Very Short Introduction* | the Frankfurt School on-ramp | 4eb171370b |",
          "| Robert C. Tucker (ed.), *The Marx-Engels Reader*, 2nd ed.; Max Weber, *The Protestant Ethic*; Raymond Aron, *Main Currents in Sociological Thought* vol. 2; C. Wright Mills, *The Sociological Imagination* | social theory | b01fb90f16, 4c885b6657, 0b7173c20a, 7fd3ab615b |",
          "| VSIs: Hegel (Singer), Nietzsche (Tanner), Marx (Singer), Freud (Storr), Poststructuralism (Belsey), Foucault (Gutting), Decolonization (Kennedy) | background | see READING-PLAN.md |",
          "| Simone de Beauvoir, *The Second Sex*; Herbert Marcuse, *One-Dimensional Man* | primary sources | d004f50be2, c1cf685a4d |",
          "| **Literature:** Fitzgerald, *The Great Gatsby* · Joyce, *Dubliners* · Kafka, *The Trial* · Shelley, *Frankenstein* · Shakespeare, *Hamlet* · Yashpal, *Dada Comrade* · Woolf, *To the Lighthouse* · Chughtai, 'Lihaaf' and Manto, 'Toba Tek Singh' · Conrad, *Heart of Darkness* (Norton Critical Ed., with its criticism) · Ellison, *Invisible Man* · Achebe, *Things Fall Apart* | the texts the lenses are applied to | see READING-PLAN.md |",
          "",
          "**Book to supply:** Freud, *Civilization and Its Discontents* (CT130). Level II needs more (PROGRAM.md, \"Books needed\").",
          "**Optional video:** Paul Fry's Yale course *ENGL 300: Introduction to Theory of Literature* (26 free lectures, Open Yale Courses). "
          "The lecture numbers for each unit are listed below. Watch them on a day you have extra time; nothing depends on them.",
          "",
          "## How the course works",
          "- **Reading days (Mon–Thu).** One ~25-minute slice, listed in the schedule. Each slice comes with 2–3 reading-guide questions. "
          "Answering them in your head is enough. Typing a line is optional, but it gives me something to grade. If the slice runs long, "
          "**stop at 25 minutes and mark your place**. The schedule absorbs it.",
          "- **Seminar day (Fri).** A real lesson page: a recap of the week, the hard ideas explained, a few recall questions that feed "
          "your daily review, and **one seminar question** (listed in the schedule) that you answer in ~150–200 words. This is the class discussion.",
          "- **Course check (the last day of each unit).** A short **lens essay** (600–800 words; 1,500 for the final). It is the unit's exam.",
          "- **Order.** Lenses follow Tyson's logic: formal lenses first, then the lenses that argue with them. Each foundations course "
          "comes **just before** the lenses that need it (philosophy before deconstruction, Freud before psychoanalytic criticism, "
          "Marx/Weber/Durkheim before Marxism and the Frankfurt School), not all at the front.",
          "",
          "## Assessment",
          "Mastery, not points (TEACHING-LOG rule 20). Each unit lists 2–3 objectives, and I grade each one **Got it / Not yet**. "
          "A unit is passed when every objective is Got it. A Not yet gets a short re-teach and a second try, never a penalty.",
          "",
          "| Work | Counts toward | Weight in my judgment of an objective |", "|---|---|---|",
          "| Reading-guide lines (optional) | nothing on their own; they show me where you are | — |",
          "| Seminar recall questions | the concept objectives (\"explain…\") | supporting |",
          "| Seminar paragraph | the application objectives (\"read a text for…\") | main evidence |",
          "| Lens essay | every objective in the unit | decisive |",
          "",
          "**Lens-essay rubric** (each 1–4; pass = no score below 2, mean ≥ 3):",
          "1. **Claim**: a specific, arguable thesis about the text, not about the lens.",
          "2. **Lens accuracy**: the concepts are used the way the theorists use them.",
          "3. **Evidence**: quotation and close reading carry the argument, and the reading doesn't skip over contrary evidence.",
          "4. **Counter-reading**: at least one other reading (another lens, or a published critic) considered and answered.",
          "5. **Clarity**: plain prose; jargon only where it does work.",
          "",
          "## Policies",
          "- **Late work.** There is no such thing. Missed days slide the schedule; the only rule is to finish the day's plan across all majors before going deeper on one (CLAUDE.md).",
          "- **Summaries.** Read the text before any summary (SparkNotes, Wikipedia, or me). Summaries are fine afterward to check your reading.",
          "- **Your own words first.** Write the seminar paragraph or the essay draft before asking me about the question. Then ask anything.",
          "- **Disagree with me.** If a reading guide, a grade or a lens seems wrong, argue it, with the text. If you're right, I'll concede and log the fix (TEACHING-LOG).",
          "- **Accommodations.** Readings are cut into 25-minute slices with guides, so they work for ADHD-style attention. Any slice can be split further. Ask.",
          "- **Content.** Several texts deal with racism, colonial violence, sexual violence and madness. The theory exists to analyze those things, not to endorse them.",
          "",
          "## Schedule",
          "Week numbers count from whenever the major starts. **R** = reading day, **S** = seminar, **E** = lens essay due (the unit's last Friday), – = catch-up.",
          ""]
    L += ["### Week 0", "", "#### CT000 Placement",
          "One sitting, whenever you start. A short pretest (name the lens behind six short critical passages, define eight terms, one "
          "paragraph on a Gatsby passage) so you can skip what you already know. It doesn't feed review (TEACHING-LOG rule 28).", ""]
    term = 0
    cur_course = None
    for wi, wk in enumerate(weeks, 1):
        t = (wi - 1) // TERM_WEEKS + 1
        if t != term:
            term = t
            L += [f"### Term {t} (weeks {(t - 1) * TERM_WEEKS + 1}–{min(t * TERM_WEEKS, len(weeks))})", ""]
        cid = wk[0][0]
        if cid != cur_course:
            cur_course = cid
            c, m = by[cid], META[cid]
            fry = f" · optional video: Yale ENGL 300 lectures {', '.join(map(str, c['fry']))}" if c.get("fry") else ""
            a, b = info[cid]
            L += [f"#### {cid} {c['title']}",
                  f"*Weeks {a}–{b} ({b - a + 1} weeks){fry}*", "",
                  m["desc"], "", "**Objectives.** You can: " + "; ".join(m["obj"]) + ".", ""]
        L.append(f"**Week {wi}**")
        L.append("")
        for di, (_, kind, text) in enumerate(wk):
            tag = {"read": "R", "seminar": "**S**", "essay": "**E**", "catch": "–"}[kind]
            body = {"read": text, "catch": text, "seminar": f"Seminar: {text}", "essay": f"Lens essay due: {text}"}[kind]
            L.append(f"- {DAYS[di]} · {tag} · {body}")
        L.append("")
    L += ["## After Level I",
          "Optional extras (breadth: hermeneutics, the theory wars, postmodernism, criticism before theory; electives: Indian fiction "
          "through the lenses, lenses on film and games, the long novels; a capstone essay; an end-of-level conversation) and the "
          "opt-in Level II seminars (whole primary books: *Dialectic of Enlightenment*, *One-Dimensional Man*, *Illuminations*, "
          "*The Second Sex*, *Discipline and Punish*, *Orientalism*, *The Political Unconscious*, *Gender Trouble*, *Capital*, the "
          "public sphere) are described in `PROGRAM.md` and mapped in `curriculum.json`.",
          "",
          "## Sources",
          "1. Lois Tyson, *Critical Theory Today*, 4th ed. (Routledge, 2023), Preface: chapters \"sequenced for a specific pedagogical "
          "purpose\" yet each \"written to stand on its own\"; usable \"as a precursor to (or in tandem with) critical theory anthologies\". In collection (dd5a1301fb).",
          "2. *The Norton Anthology of Theory and Criticism*, 2nd ed. (2010): contents pages (page ranges above). In collection (face941c2e).",
          "3. Paul Fry, *ENGL 300: Introduction to Theory of Literature*, Open Yale Courses (spring 2009): 26 lectures, from formalism "
          "to queer theory; required text Richter, *The Critical Tradition*. https://oyc.yale.edu/english/engl-300",
          "4. Columbia College, *Contemporary Civilization* (Core Curriculum): Marx, Freud, Du Bois and Fanon among the required "
          "authors. https://bulletin.columbia.edu/columbia-college/core-curriculum/contemporary-civilization",
          "5. University of Chicago, *Self, Culture and Society* (Social Sciences Core), as described by its former chair Moishe Postone: "
          "Smith, Marx and Weber; Durkheim; then Freud, Marcuse, Beauvoir and Fanon. https://thepointmag.com/dialogue/critical-attempts-moishe-postone-general-education/",
          "6. Reading-day sizes and the schedule: computed by `build_plan.py` / `build_syllabus.py` from library word counts and contents pages.",
          ""]
    (HERE / "SYLLABUS.md").write_text("\n".join(L), encoding="utf-8")
    print(f"SYLLABUS.md: {nsit} sittings, {nread} reading days, {len(weeks)} weeks")


if __name__ == "__main__":
    main()
