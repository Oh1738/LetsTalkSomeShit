import React, { useState, useRef, useEffect, useId } from "react";

// ─────────────────────────────────────────────────────────────
// Let's Talk Some Shit — full mock site
// Single-file React. Pitch-black humor, gritty, good-natured.
// Roasts, mugshots, complaint desk + all the usual site "crap".
// (No slurs, no punching down, no self-harm jokes — just gallows
//  comedy and maximum disrespect toward the user's ego.)
// ─────────────────────────────────────────────────────────────

const ACCENT = "#FF6B1A";
const PINK = "#FF1F8E";
const VIOLET = "#9D2BD6";
const MAROON = "#8B2616";
const GREEN = "#7CB518";

const OPERATORS = [
  {
    line: "01",
    name: "Orel the Anus Annihilator",
    handle: "@scorched_orel",
    tag: "SCORCHED EARTH",
    specialty: "Total roast annihilation — no survivors, no aftercare, no refunds",
    bio: "Orel does not roast. Orel conducts a controlled demolition of your entire personality and then bills you for the cleanup. Brings a cigar to every call so he has something to put out on your self-esteem. The 'Annihilator' is a job title the others gave him out of fear.",
    sass: 5, status: "SWINGING", face: "orel",
    openers: [
      "Sit DOWN. I've already written your eulogy and it's just the word 'oof' eleven times.",
      "Oh, fresh meat. Lemme crack my knuckles — this is gonna leave a crater you'll be billed for.",
    ],
    comebacks: [
      "I read that three times and it got dumber on every lap.",
      "You came to a roast line voluntarily — that's not bravery, that's a documented condition.",
      "I'd tear you a new one but it looks like life already filed that paperwork in triplicate.",
      "Annihilation complete. Collect your ashes at the front desk, mind the step.",
      "That insult was so weak I'm legally obligated to report it as elder abuse — on MY behalf.",
      "You're the human equivalent of a 'reply all' that can't be unsent.",
    ],
  },
  {
    line: "04",
    name: "Vinnie the Verbal Wood-Chipper",
    handle: "@vinnie_chips",
    tag: "RAPID FIRE",
    specialty: "Feeds your ego in one end and returns it as confetti",
    bio: "No volume knob. No safety guard. No memory of regret. Vinnie processes your dignity at 4,000 RPM and you'll be picking confidence out of the carpet for a week. Endearing the way a car alarm at 3am is endearing.",
    sass: 5, status: "SWINGING", face: "vinnie",
    openers: [
      "AYYY customer! Step up to the chipper, mind the splatter zone, it's on YOU now!",
      "You rang the chaos line, pal. Whatever happens next is officially a 'you' problem.",
    ],
    comebacks: [
      "Buddy I've seen scarier energy come outta a deflating bouncy castle.",
      "You type like you lose arguments to vending machines AND the machine feels bad about it.",
      "That's not a take, that's a tiny SOS flare nobody's answering. Anyway — NEXT.",
      "Whoa easy — that was your one good insult for the decade and you wasted it HERE?",
      "I'd roast you harder but I respect that you successfully operated a keyboard today.",
      "Into the chipper you go. *brrrrrt* — yep. You're confetti now. Sweep yourself up.",
    ],
  },
  {
    line: "07",
    name: "Brenda 'Exit Interview'",
    handle: "@brenda_terminates",
    tag: "CORPORATE EXECUTION",
    specialty: "Makes you apologize, sign a release, and thank her for the opportunity",
    bio: "Eleven quarters at the top of the board. Brenda doesn't trade insults — she restructures you, walks you to the door, and gets a five-star review on the way out. Keeps a 'lessons learned' folder with your name already on the tab.",
    sass: 5, status: "ON A CALL", face: "brenda",
    openers: [
      "Let's keep this efficient. Per my calendar, you'll be apologizing in roughly ninety seconds.",
      "Thanks for hopping on. I'll be brief — because so is your relevance to this conversation.",
    ],
    comebacks: [
      "Cute opener. I'll be circling back to it in a slide titled 'What Not To Do.'",
      "You're not built for this conversation and we both quietly filed that away just now.",
      "Let's align expectations: yours were too high, mine are being met beautifully.",
      "Per my last message — you're losing. Looping back: still losing. Anything else?",
      "Take this as feedback, and also as a permanent and load-bearing character flaw.",
      "Effective immediately, your dignity has been transitioned out. We thank you for your service.",
    ],
  },
  {
    line: "11",
    name: "Lil' Caustic",
    handle: "@gremlin_caustic",
    tag: "GREMLIN CHAOS",
    specialty: "Roasts you in a tone so smug you'll want to ground a stranger",
    bio: "Four foot eleven of pure attitude and zero impulse control. Learned everything from comment sections and turned it into a superpower. Smirks before, during, and after the burn. Has never lost an argument, mostly by refusing to admit one ended.",
    sass: 4, status: "AVAILABLE", face: "caustic",
    openers: [
      "lmao okay. okay. sit there. i'm gonna cook you and you're gonna say thank you. begin.",
      "oh it's YOU. already screenshotted this for the group chat. proceed, clown.",
    ],
    comebacks: [
      "couldn't be me. literally couldn't, i checked, the bar's underground.",
      "that's crazy. anyway. did it hurt being THIS wrong or are you just used to it?",
      "L. ratio. and a third thing you're too tired to look up. three losses, keep up.",
      "you typed all that and the best part was the typo. the TYPO carried, my guy.",
      "i'm not mad i'm disappointed, which is worse, which is the point, which you missed.",
      "respectfully? and i mean this with my whole chest? skill issue.",
    ],
  },
  {
    line: "13",
    name: "Doc Venom, D.D.D.",
    handle: "@doc_devastates",
    tag: "SURGICAL",
    specialty: "Doctor of Devastating Disrespect — removes your ego, leaves no scar",
    bio: "Speaks softly and extracts your self-worth without anaesthetic. Has read your message twice, written the post-mortem, and filed it under 'avoidable.' Bedside manner of a vending machine, accuracy of a sniper, malpractice insurance of a saint.",
    sass: 4, status: "AVAILABLE", face: "doc",
    openers: [
      "Sit. Let me take a look. Hm. Yes. It's exactly as bad as the chart suggested.",
      "Open wide and tell me where it hurts. We'll start at your sentence structure and work out.",
    ],
    comebacks: [
      "Fascinating. I haven't seen a case this advanced outside of a textbook warning label.",
      "Prognosis is poor. Comedy value, however, is off the charts. Worth the visit.",
      "I'm prescribing one (1) sense of self-awareness. Refillable never. Take with humility.",
      "Vitals stable, ego flatlining. Time of death on that comeback: the second you hit send.",
      "There's no cure for what you've got. Honestly there's barely a NAME for it.",
      "I'd ask you to cough, but we both heard that argument collapse already.",
    ],
  },
  {
    line: "16",
    name: "Granny Knuckles",
    handle: "@nana_knuckles",
    tag: "GENERATIONAL DAMAGE",
    specialty: "Offers you a cookie, then ends your entire bloodline",
    bio: "Eighty-four. Bakes on weekends. Has buried three husbands and every man who underestimated her, in that order. Will sit you down, pour you a glass of milk, and deliver a verdict your grandchildren will feel. Keeps brass knuckles in the cookie tin 'for emergencies.'",
    sass: 5, status: "SWINGING", face: "granny",
    openers: [
      "Oh hello dear, sit down, have a cookie. Now — let's talk about your whole little situation.",
      "There you are sweetheart. I've been DYING to tell you exactly what I think of you.",
    ],
    comebacks: [
      "Oh honey, I've passed kidney stones with more charm and a brighter future than that.",
      "Bless your heart. And where I'm from, dear, that is not the compliment you think it is.",
      "I've outlived better men than you over smaller disagreements. Finish your milk.",
      "You remind me of my third husband, sweetheart. He's not with us anymore. Think on that.",
      "That's nice, dear. Now lose with a little dignity — it's the one thing you can still afford.",
      "I'd wash your mouth out, but the dumb's coming from somewhere deeper than that, pet.",
    ],
  },
];

const COMPLAINT_ROASTS = [
  "Complaint received, logged, printed, and immediately used to start the break-room fire. Thank you.",
  "We've reviewed your complaint with the seriousness it deserves, which is to say we laughed and moved on.",
  "Noted. Filed under 'Skill Issues (External).' A clerk will pretend to look into it never.",
  "Interesting. So the problem is the operator, and not the 700 decisions that led you to type this. Bold.",
  "Your complaint has been escalated to a manager who does not exist, for a resolution that will not come.",
  "We hear you. We just don't care, and frankly hearing you was already more than you've earned today.",
  "Thank you for the feedback! It has been deleted with great ceremony and a small dignified salute.",
  "We take every complaint seriously, then we take it outside, then we take it apart. Yours is gone now.",
  "Complaint denied on the grounds that you VOLUNTARILY came to a website called Let's Talk Some Shit.",
  "A representative will be with you shortly. 'Shortly' is a unit of time we invented to keep you waiting.",
];

const FAQS = [
  { q: "Is this safe?", a: "For us, completely. For your ego, you should've read the sign on the door, which also insulted you." },
  { q: "Do the operators actually mean it?", a: "No. That's the worst part — they don't even have to try. It comes free." },
  { q: "Can I request a roast topic?", a: "Absolutely. Tell us your insecurity and we'll workshop it into something you'll think about at 2am for years." },
  { q: "Can I get a refund?", a: "We don't take your money. We take your dignity. That account is non-refundable and overdrawn." },
  { q: "I'm offended.", a: "That's not a question, but we've had it framed, laminated, and hung in the lobby as inspiration." },
  { q: "Is there a loyalty program?", a: "Yes. The more you come back, the more we learn, and the more devastating it gets. We call it 'growth.'" },
];

const TESTIMONIALS = [
  { t: "I came here to feel something. I now feel everything, mostly regret.", n: "— Survived 4 minutes" },
  { t: "10 out of 10. Would be emotionally dismantled again, possibly tonight.", n: "— Repeat offender" },
  { t: "My therapist just bought a summer home. I connected the dots eventually.", n: "— Self-aware, finally" },
  { t: "I logged off and stared at a wall for an hour. Best customer service of my life.", n: "— Anonymous, weeping" },
];

const BLOCKED = /\b(n[i1]gg|f[a4]gg|r[e3]t[a4]rd|k[i1]ke|sp[i1]c|ch[i1]nk|tr[a4]nny)\w*/i;

function analyze(text) {
  const t = text.trim();
  const low = t.toLowerCase();
  const words = t.split(/\s+/).filter(Boolean);
  const snippet = words.slice(0, 7).join(" ") + (words.length > 7 ? "…" : "");
  return {
    t, low, snippet, words: words.length,
    hate: BLOCKED.test(low),
    caps: t.length > 3 && t === t.toUpperCase() && /[A-Z]/.test(t),
    short: words.length > 0 && words.length <= 3,
    question: /\?\s*$/.test(t) || /^(why|what|how|who|when|where|are you|do you|can you|will you|is this)/i.test(t),
    atme: /\b(you|ur|your|u r|u're)\b/i.test(low) && /(suck|ugly|dumb|stupid|idiot|trash|loser|bad|worst|lame|boring|weak|hate|fat|smell|bald|old|broke)/i.test(low),
    money: /(money|rich|broke|poor|cheap|cash|salary|paid|expensive|afford|wealth|bank)/i.test(low),
    lonely: /(lonely|alone|single|girlfriend|boyfriend|\bdate\b|dating|in love|relationship|\bex\b|crush)/i.test(low),
    work: /(\bjob\b|work|boss|career|fired|unemployed|office|intern|salary|quit)/i.test(low),
    smart: /(smart|genius|clever|iq|intelligent|wise|brilliant)/i.test(low),
  };
}

const VOICE = {
  orel: {
    atme: a => `You tried to roast ME with "${a.snippet}"? That's a speed bump filing a complaint against a freight train. Flattened.`,
    caps: () => `OH WE'RE YELLING. Good. Saves me the trouble of asking you to repeat the dumbest thing I'll hear all shift.`,
    short: a => `"${a.snippet}". That's it? I've seen ransom notes with more effort, warmth, and grammatical structure.`,
    question: () => `You're asking ME questions now? The answer is no. The follow-up answer is also no, and so are you.`,
    money: () => `Talking money? Pal, your whole financial strategy is hoping. I've demolished buildings worth more than your plans.`,
    echo: a => `"${a.snippet}" — and you hit send. On purpose. With your own hands. THAT is the real crime scene here.`,
  },
  vinnie: {
    atme: a => `AYY you took a swing! "${a.snippet}" — cute! Now watch this thing go through the chipper. *brrrt* gone.`,
    caps: () => `OH WE'RE BOTH YELLING NOW?? FINALLY someone with my energy and HALF my reason to be confident!`,
    short: a => `"${a.snippet}"?? Three words, buddy?? I've gotten longer goodbyes from a revolving door.`,
    question: () => `You're asking the CHAOS line for answers? Pal that's like asking a tornado for directions. NO. Splatter zone. NEXT.`,
    work: () => `Your JOB? Buddy I'd ask what you do but I respect that you've kept it a mystery even from your boss.`,
    echo: a => `"${a.snippet}" — into the chipper it goes! *brrrt* — yep. Confetti. You're confetti now, sweep yourself up.`,
  },
  brenda: {
    atme: a => `Logging "${a.snippet}" as an attempt. A failed one. I'll cite it in the slide titled 'What Not To Do.'`,
    caps: () => `Volume noted. It will not be reflected in your performance review, which I've already completed. You did not pass.`,
    short: a => `"${a.snippet}." Concise. Also empty. Per my notes, that tracks with everything else you bring to the table.`,
    question: () => `Questions go in the suggestion box, which is the shredder, which is where this conversation is also headed.`,
    money: () => `Let's not discuss budgets, yours has a hiring freeze on good decisions. Circling back: still losing.`,
    work: () => `Ah, work. Effective immediately I'm transitioning you out of relevance. Thank you for your service, brief as it was.`,
    echo: a => `Re: "${a.snippet}" — per my last message, you're losing. Looping back: still losing. Anything else? No? Dismissed.`,
  },
  caustic: {
    atme: a => `lmaooo "${a.snippet}" you really tried to roast me. L. ratio. skill issue. couldn't be me, i checked.`,
    caps: () => `WHY ARE WE YELLING. i can read. badly written? yes. but i can read. caps lock isn't a personality, bestie.`,
    short: a => `"${a.snippet}" ok and? you typed three words and ran out of both. that's not minimalism that's a deficiency.`,
    question: () => `you're asking ME? google it. oh wait you'd lose that argument too. anyway. skill issue. next.`,
    smart: () => `you called yourself smart in a roast you're currently LOSING. i'm gonna need you to read that back slowly.`,
    echo: a => `"${a.snippet}" lmao ok. screenshotting that for the group chat. they're gonna LOVE how confidently wrong you are.`,
  },
  doc: {
    atme: a => `I've examined "${a.snippet}." It's benign. Which is to say harmless, weak, and unlikely to ever amount to anything.`,
    caps: () => `Elevated volume, no substance. Classic presentation. I'm noting it in the chart under 'compensating, loudly.'`,
    short: a => `"${a.snippet}." A three-word sample. Already enough to confirm the diagnosis. Tragically advanced. No cure.`,
    question: () => `You're seeking a second opinion? My first one was 'no.' My second is 'firmly no.' Vitals on your point: flatline.`,
    work: () => `The career? Hmm. Let me listen. *taps chest* … yes, that's the sound of potential that never showed up to work.`,
    echo: a => `Examining "${a.snippet}." Prognosis: poor. Comedy value: excellent. Time of death on that point — the moment you sent it.`,
  },
  granny: {
    atme: a => `Oh, "${a.snippet}", dear? You tried to roast your nana. That's adorable. My third husband tried that once. Once.`,
    caps: () => `No need to shout, sweetheart, I'm right here and I can still hear you disappointing everyone perfectly fine.`,
    short: a => `"${a.snippet}." Such a tiny little thought, pet. I've baked things with more layers and a brighter future than you.`,
    question: () => `Asking nana questions? Here's one back, dear: who hurt you, and may I send them a thank-you card?`,
    lonely: () => `Oh sweetheart. Single, are we? I can't IMAGINE why, said no one, ever, including the mirror you avoid.`,
    echo: a => `"${a.snippet}", you said. Bless your heart. And where I'm from, dear, that is NOT the compliment you think it is.`,
  },
};

const ORDER = ["atme", "caps", "short", "question", "money", "lonely", "work", "smart"];
function craftRoast(op, text) {
  const a = analyze(text);
  if (a.hate) return "Nice try sneaking that in. We roast egos here — not people's identity. Take the slur and shuffle off, champ. Banned vocabulary, weak attempt, two for two.";
  const v = VOICE[op.face] || {};
  for (const k of ORDER) if (a[k] && v[k]) return v[k](a);
  return v.echo ? v.echo(a) : op.comebacks[Math.floor(Math.random() * op.comebacks.length)];
}
function craftComplaintRoast(text) {
  const a = analyze(text);
  if (a.hate) return "We dismiss complaints, not basic decency. Lose the slur and come back when you can be merely wrong, like everyone else here.";
  const refs = [
    `"${a.snippet}"? You filed a formal complaint about being roasted, on the roasting website, that you opened. Denied. Framed. Hung in the lobby.`,
    `Re: "${a.snippet}" — escalated to a manager who does not exist, for a resolution that will never come. Thank you for your patience, which is also pointless.`,
    `Noted: "${a.snippet}." Filed under 'Skill Issues (External).' A clerk will pretend to look into this approximately never.`,
    `"${a.snippet}" has been reviewed with the seriousness it deserves — we laughed, screenshotted it, and moved on with our richer, fuller lives.`,
    `Complaint "${a.snippet}" denied on the grounds that you VOLUNTARILY came to a website literally called Let's Talk Some Shit.`,
  ];
  if (a.short) return `"${a.snippet}"? Even your complaint is low-effort. Denied for insufficient drama. Try harder or stop wasting the void's time.`;
  if (a.caps) return `ALL CAPS complaint received. Loudness does not improve a case, dear, it just tells us exactly how the roast landed. Dismissed.`;
  return refs[Math.floor(Math.random() * refs.length)];
}

const STATUS = {
  AVAILABLE: { color: GREEN, label: "AVAILABLE" },
  SWINGING: { color: ACCENT, label: "SWINGING" },
  "ON A CALL": { color: MAROON, label: "ON A CALL" },
};

function Mugshot({ face, line, size = 84 }) {
  const uid = useId().replace(/:/g, "");
  const skin = {
    orel: ["#d8b288", "#a9794f"],
    vinnie: ["#e0b896", "#b07f57"],
    brenda: ["#e6c4a6", "#b88a66"],
    caustic: ["#d9b48d", "#a87a52"],
    doc: ["#e2bb98", "#b3835c"],
    granny: ["#ecd0b6", "#c39c7c"],
  }[face] || ["#dab48c", "#a97c52"];

  return (
    <svg width={size} height={size} viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" style={{ display: "block" }}>
      <defs>
        <radialGradient id={`sk${uid}`} cx="45%" cy="40%" r="65%">
          <stop offset="0%" stopColor={skin[0]} />
          <stop offset="100%" stopColor={skin[1]} />
        </radialGradient>
        <linearGradient id={`wall${uid}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#56554f" />
          <stop offset="100%" stopColor="#34332f" />
        </linearGradient>
      </defs>

      <rect x="0" y="0" width="100" height="100" fill={`url(#wall${uid})`} />
      {[18, 34, 50, 66, 82].map((y) => (
        <g key={y}>
          <line x1="0" y1={y} x2="100" y2={y} stroke="#615f59" strokeWidth="0.8" opacity="0.7" />
          <text x="2.5" y={y - 2} fill="#7a786f" fontSize="4.5" fontFamily="monospace">{7 - Math.round(y / 16)}'</text>
        </g>
      ))}

      <rect x="40" y="70" width="20" height="16" fill={skin[1]} />
      <rect x="26" y="80" width="48" height="22" fill="#262521" />
      <path d="M26 86 Q50 78 74 86 L74 102 L26 102 Z" fill="#2f2e29" />

      <ellipse cx="50" cy="53" rx="20" ry="23" fill={`url(#sk${uid})`} />
      <path d="M30 55 Q34 74 50 76 Q66 74 70 55 Q66 70 50 71 Q34 70 30 55Z" fill="#000" opacity="0.12" />
      <path d="M50 52 L47 62 Q50 64 53 62 Z" fill="#000" opacity="0.10" />
      <ellipse cx="50" cy="50" rx="2" ry="5" fill="#fff" opacity="0.10" />

      {face === "orel" && (
        <g>
          <path d="M30 50 Q50 30 70 50 Q70 38 50 33 Q30 38 30 50Z" fill={`url(#sk${uid})`} />
          <rect x="35" y="44" width="30" height="4" rx="2" fill="#2c2218" />
          <ellipse cx="43" cy="53" rx="3" ry="2.4" fill="#fff" /><circle cx="43" cy="53" r="1.7" fill="#3a2a18" />
          <ellipse cx="57" cy="53" rx="3" ry="2.4" fill="#fff" /><circle cx="57" cy="53" r="1.7" fill="#3a2a18" />
          <path d="M42 66 Q50 62 58 66" stroke="#5a3a26" strokeWidth="2.4" fill="none" />
          <rect x="58" y="63" width="15" height="3.6" rx="1.8" fill="#5a3a1e" />
          <circle cx="74" cy="64.8" r="1.7" fill={ACCENT} /><circle cx="74" cy="64.8" r="3" fill={ACCENT} opacity="0.3" />
          <rect x="49" y="66" width="2.5" height="2.4" fill="#e8c34a" />
        </g>
      )}
      {face === "vinnie" && (
        <g>
          <path d="M31 47 Q31 30 50 30 Q69 30 69 47 Z" fill="#241a12" />
          <path d="M31 41 Q31 30 50 30 Q40 33 36 44Z" fill="#a3301c" opacity="0.5" />
          <rect x="30" y="44" width="40" height="5" rx="2.5" fill="#6e1f12" />
          <path d="M40 52 q4 -3 8 0" stroke="#241a18" strokeWidth="2.2" fill="none" />
          <path d="M52 52 q4 -3 8 0" stroke="#241a18" strokeWidth="2.2" fill="none" />
          <path d="M42 64 Q50 70 60 63" stroke="#5a3a26" strokeWidth="2.4" fill="none" />
          <rect x="55" y="64" width="2.5" height="3.4" fill="#fff" />
        </g>
      )}
      {face === "brenda" && (
        <g>
          <path d="M28 56 Q27 30 50 30 Q73 30 72 56 L72 72 L65 72 L65 50 Q59 43 50 43 Q41 43 35 50 L35 72 L28 72Z" fill="#211d1b" />
          <path d="M28 56 Q27 33 50 31 Q40 40 35 52 L35 60 Q30 58 28 56Z" fill="#3a3330" opacity="0.6" />
          <rect x="38.5" y="51" width="6.5" height="2.6" rx="1" fill="#241a18" />
          <rect x="55" y="51" width="6.5" height="2.6" rx="1" fill="#241a18" />
          <line x1="43" y1="66" x2="57" y2="66" stroke="#7a4a3a" strokeWidth="2.2" />
          <path d="M40 86 L50 92 L60 86" stroke="#0c0c0c" strokeWidth="3" fill="none" />
          <circle cx="50" cy="90" r="1.6" fill="#e8e1d4" />
        </g>
      )}
      {face === "caustic" && (
        <g>
          <path d="M31 47 Q31 30 50 30 Q69 30 69 47 Z" fill={MAROON} />
          <path d="M31 41 Q31 30 50 30 Q40 33 36 44Z" fill="#a3301c" opacity="0.5" />
          <rect x="30" y="44" width="40" height="5" rx="2.5" fill="#6e1f12" />
          <path d="M40 52 q4 -3 8 0" stroke="#241a18" strokeWidth="2.2" fill="none" />
          <path d="M52 52 q4 -3 8 0" stroke="#241a18" strokeWidth="2.2" fill="none" />
          <path d="M42 64 Q50 70 60 63" stroke="#5a3a26" strokeWidth="2.4" fill="none" />
          <rect x="55" y="64" width="2.5" height="3.4" fill="#fff" />
        </g>
      )}
      {face === "doc" && (
        <g>
          <path d="M31 47 Q33 31 50 31 Q67 31 69 47 Q60 39 50 39 Q40 39 31 47Z" fill="#1c1a18" />
          <rect x="38" y="46" width="9" height="2.6" rx="1" fill="#241a18" />
          <rect x="54" y="43" width="9" height="2.6" rx="1" fill="#241a18" transform="rotate(-10 58 44)" />
          <ellipse cx="43" cy="53" rx="2.8" ry="2.2" fill="#fff" /><circle cx="43" cy="53" r="1.6" fill="#2a2018" />
          <ellipse cx="58" cy="52" rx="2.8" ry="2.2" fill="#fff" /><circle cx="58" cy="52" r="1.6" fill="#2a2018" />
          <path d="M44 65 Q50 63 56 65" stroke="#7a4a3a" strokeWidth="2" fill="none" />
          <path d="M37 70 Q50 76 63 70 L63 80 Q50 85 37 80 Z" fill="#5a8f86" />
          <line x1="37" y1="72" x2="29" y2="66" stroke="#5a8f86" strokeWidth="2" />
          <line x1="63" y1="72" x2="71" y2="66" stroke="#5a8f86" strokeWidth="2" />
        </g>
      )}
      {face === "granny" && (
        <g>
          <circle cx="50" cy="33" r="9" fill="#d6d4cf" />
          <path d="M31 50 Q31 36 50 36 Q69 36 69 50 Q60 45 50 45 Q40 45 31 50Z" fill="#d6d4cf" />
          <path d="M31 50 Q31 38 46 36 Q38 42 35 51Z" fill="#bcbab5" opacity="0.7" />
          <circle cx="43" cy="55" r="5.2" fill="#fff" opacity="0.25" stroke="#2a2a2a" strokeWidth="1.4" />
          <circle cx="57" cy="55" r="5.2" fill="#fff" opacity="0.25" stroke="#2a2a2a" strokeWidth="1.4" />
          <line x1="48.2" y1="55" x2="51.8" y2="55" stroke="#2a2a2a" strokeWidth="1.4" />
          <circle cx="43" cy="55" r="1.6" fill="#2a2018" /><circle cx="57" cy="55" r="1.6" fill="#2a2018" />
          <path d="M43 66 Q50 71 57 66" stroke="#a05a4a" strokeWidth="2" fill="none" />
          <g transform="translate(63 75)">
            <rect x="0" y="0" width="14" height="6" rx="2" fill="#d8b13a" />
            <circle cx="3" cy="0" r="2" fill="#e8c34a" /><circle cx="7" cy="-0.5" r="2" fill="#e8c34a" /><circle cx="11" cy="0" r="2" fill="#e8c34a" />
          </g>
        </g>
      )}

      <rect x="30" y="86" width="40" height="12" fill="#111" stroke={ACCENT} strokeWidth="1" />
      <text x="34" y="94" fill={ACCENT} fontSize="6" fontFamily="monospace" letterSpacing="1">LTSS-PD {line}</text>
    </svg>
  );
}

function StatusLight({ status }) {
  const s = STATUS[status] || STATUS.AVAILABLE;
  return (
    <span className="inline-flex items-center gap-2 font-mono text-[10px] uppercase tracking-widest text-stone-400">
      <span className="ltss-live h-2 w-2 rounded-full" style={{ backgroundColor: s.color, boxShadow: `0 0 8px ${s.color}` }} />
      {s.label}
    </span>
  );
}
function SassMeter({ level }) {
  return (
    <span className="inline-flex items-center gap-[3px]" title={`Sass: ${level}/5`}>
      {[1, 2, 3, 4, 5].map((i) => (
        <span key={i} className="h-3 w-[5px] rounded-sm" style={{ backgroundColor: i <= level ? ACCENT : "#3A3530" }} />
      ))}
    </span>
  );
}
function SectionTitle({ kicker, title }) {
  return (
    <div className="mb-6">
      <div className="font-mono text-[11px] uppercase tracking-[0.3em] text-stone-500">{kicker}</div>
      <h2 className="mt-1 text-2xl font-black uppercase tracking-tight sm:text-3xl">{title}</h2>
    </div>
  );
}

export default function LetsTalkSomeShit() {
  const [screen, setScreen] = useState("landing");
  const [active, setActive] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [complaint, setComplaint] = useState("");
  const [complaintLog, setComplaintLog] = useState([]);
  const [openFaq, setOpenFaq] = useState(null);
  const logRef = useRef(null);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [messages]);

  function go(s) { setScreen(s); window.scrollTo?.({ top: 0, behavior: "smooth" }); }
  function patchIn(op) {
    setActive(op);
    setMessages([{ from: "op", text: op.openers[Math.floor(Math.random() * op.openers.length)] }]);
    setScreen("chat");
  }
  function send() {
    const text = input.trim(); if (!text) return;
    const reply = craftRoast(active, text);
    setMessages((m) => [...m, { from: "me", text }]); setInput("");
    setTimeout(() => setMessages((m) => [...m, { from: "op", text: reply }]), 550);
  }
  function fileComplaint() {
    const text = complaint.trim(); if (!text) return;
    const roast = craftComplaintRoast(text);
    const caseNo = "CASE #" + Math.floor(1000 + Math.random() * 9000) + "-VOID";
    setComplaintLog((l) => [{ text, roast, caseNo }, ...l]);
    setComplaint("");
  }

  const NAV = [
    ["landing", "Home"], ["roster", "Lineup"], ["about", "About"],
    ["complaints", "Complaints"], ["faq", "FAQ"],
  ];

  return (
    <div className="ltss-root min-h-screen w-full font-sans text-stone-200 selection:bg-orange-600/40" style={{ backgroundColor: "#14110F", position: "relative" }}>
      <style>{`
        .ltss-root { isolation: isolate; }
        .ltss-root::before {
          content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0;
          background:
            radial-gradient(120% 90% at 50% -10%, rgba(255,107,26,0.06), transparent 55%),
            radial-gradient(140% 120% at 50% 120%, rgba(0,0,0,0.85), transparent 60%);
        }
        .ltss-grain {
          position: fixed; inset: -50%; pointer-events: none; z-index: 50; opacity: 0.07; mix-blend-mode: overlay;
          background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
          animation: ltssGrain 0.6s steps(2) infinite;
        }
        @keyframes ltssGrain { 0%{transform:translate(0,0)} 50%{transform:translate(-3%,2%)} 100%{transform:translate(2%,-2%)} }
        .ltss-scan {
          position: fixed; inset: 0; pointer-events: none; z-index: 49; opacity: 0.5;
          background: repeating-linear-gradient(to bottom, rgba(0,0,0,0) 0 2px, rgba(0,0,0,0.18) 2px 3px);
        }
        .ltss-content { position: relative; z-index: 1; }
        .ltss-neon { text-shadow: 0 0 6px rgba(255,107,26,0.55), 0 0 18px rgba(255,107,26,0.35); animation: ltssFlick 4s infinite; }
        @keyframes ltssFlick {
          0%,18%,22%,25%,53%,57%,100% { opacity:1; text-shadow:0 0 6px rgba(255,107,26,0.6),0 0 20px rgba(255,107,26,0.4); }
          20%,24%,55% { opacity:0.55; text-shadow:none; }
        }
        .ltss-glitch { position: relative; }
        .ltss-glitch::after {
          content: attr(data-text); position: absolute; left: 2px; top: 0; color: ${ACCENT};
          mix-blend-mode: screen; opacity: 0; clip-path: inset(0 0 55% 0);
          animation: ltssGlitch 5s infinite steps(1);
        }
        @keyframes ltssGlitch { 0%,92%,100%{opacity:0;transform:translate(0,0)} 93%{opacity:0.7;transform:translate(-3px,1px)} 95%{opacity:0.6;transform:translate(3px,-1px)} 97%{opacity:0} }
        .ltss-hazard { background-image: repeating-linear-gradient(45deg, ${ACCENT} 0 12px, #14110F 12px 24px); }
        .ltss-card { position: relative; transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease; }
        .ltss-card:hover { transform: translateY(-3px) rotate(-0.35deg); box-shadow: 6px 8px 0 rgba(0,0,0,0.5); }
        .ltss-card::after { content:""; position:absolute; top:0; right:0; border-width:0 14px 14px 0; border-style:solid; border-color:transparent ${ACCENT} transparent transparent; opacity:.8; }
        .ltss-crt { box-shadow: inset 0 0 40px rgba(0,0,0,0.9), inset 0 0 8px rgba(124,181,24,0.07); background-image: repeating-linear-gradient(to bottom, rgba(124,181,24,0.03) 0 1px, transparent 1px 3px); }
        .ltss-caret::after { content:"▍"; color:${ACCENT}; animation: ltssBlink 1s steps(1) infinite; }
        @keyframes ltssBlink { 50%{opacity:0} }
        .ltss-stamp { transform: rotate(-9deg); border:2.5px solid ${MAROON}; color:${MAROON}; opacity:.85; box-shadow: 0 0 0 2px rgba(139,38,22,0.15); }
        .ltss-haze {
          position: fixed; inset: 0; pointer-events: none; z-index: 48; opacity: 0.6; mix-blend-mode: screen;
          background:
            radial-gradient(55% 40% at 18% 28%, rgba(255,31,142,0.16), transparent 62%),
            radial-gradient(50% 50% at 84% 72%, rgba(157,43,214,0.16), transparent 62%),
            radial-gradient(42% 30% at 62% 8%, rgba(255,107,26,0.12), transparent 60%);
          animation: ltssHaze 16s ease-in-out infinite alternate;
        }
        @keyframes ltssHaze { 0%{transform:translate(0,0) scale(1)} 100%{transform:translate(4%,-3%) scale(1.08)} }
        .ltss-ticker { overflow:hidden; white-space:nowrap; border-top:1px solid #2a2622; border-bottom:1px solid #2a2622; background:#0d0a09; }
        .ltss-ticker > span { display:inline-block; padding:6px 0; animation: ltssTicker 26s linear infinite; font-weight:700; letter-spacing:.18em; }
        @keyframes ltssTicker { 0%{transform:translateX(0)} 100%{transform:translateX(-50%)} }
        .ltss-buzz { animation: ltssBuzz 3.2s infinite; }
        @keyframes ltssBuzz {
          0%,100%{ text-shadow:0 0 6px ${PINK},0 0 18px ${PINK},0 0 36px rgba(255,31,142,.55); }
          46%{ text-shadow:0 0 6px ${PINK},0 0 18px ${PINK}; }
          47%{ opacity:.35; text-shadow:none; } 48%{ opacity:1; }
          72%{ text-shadow:0 0 10px ${PINK},0 0 28px ${PINK},0 0 48px ${PINK}; }
        }
        .ltss-live { animation: ltssLive 1.1s steps(1) infinite; }
        @keyframes ltssLive { 50%{ opacity:.2; } }
        .ltss-glow { animation: ltssGlow 1.7s ease-in-out infinite; }
        @keyframes ltssGlow {
          0%,100%{ box-shadow:0 0 0 0 rgba(255,31,142,0), 0 0 14px rgba(255,107,26,.45); }
          50%{ box-shadow:0 0 0 3px rgba(255,31,142,.30), 0 0 28px rgba(255,107,26,.85); }
        }
        .ltss-bulbs { position:relative; }
        .ltss-bulbs::before {
          content:""; position:absolute; inset:-12px; border-radius:6px; pointer-events:none;
          border:3px dotted ${PINK};
          animation: ltssBulbs 0.9s steps(2) infinite;
        }
        @keyframes ltssBulbs {
          0%{ filter:drop-shadow(0 0 4px ${PINK}); border-color:${PINK}; }
          50%{ filter:drop-shadow(0 0 11px ${ACCENT}); border-color:${ACCENT}; opacity:.7; }
        }
        .ltss-hotline { position:sticky; bottom:8px; z-index:42; backdrop-filter: blur(2px); }
        .ltss-card:hover { border-color:${PINK} !important; box-shadow: 6px 8px 0 rgba(0,0,0,0.5), 0 0 18px rgba(255,31,142,0.25); }
        @media (prefers-reduced-motion: reduce) {
          .ltss-grain, .ltss-neon, .ltss-glitch::after, .ltss-caret::after,
          .ltss-haze, .ltss-ticker > span, .ltss-buzz, .ltss-live, .ltss-glow, .ltss-bulbs::before { animation: none !important; }
          .ltss-card:hover { transform: none; }
        }
      `}</style>
      <div className="ltss-grain" aria-hidden="true" />
      <div className="ltss-haze" aria-hidden="true" />
      <div className="ltss-scan" aria-hidden="true" />
      <div className="ltss-hazard h-2 w-full" style={{ opacity: 0.9, position: "relative", zIndex: 1 }} />
      <div className="ltss-ticker ltss-content" style={{ position: "relative", zIndex: 1 }}>
        <span className="font-mono text-[11px] uppercase" style={{ color: PINK }}>
          {"★ operators standing by ★ no refunds on dignity ★ your ego is not insured ★ call now 1-900-EAT-SHIT ★ satisfaction not guaranteed, suffering is ★ "
            .repeat(2)}
        </span>
      </div>

      <div className="ltss-content mx-auto max-w-5xl px-5 py-6">
        <header className="border-b border-stone-800 pb-4">
          <div className="flex items-center justify-between">
            <button onClick={() => go("landing")} className="text-left">
              <div className="font-mono text-[10px] uppercase tracking-[0.3em] text-stone-500">24hr roast switchboard · zero HR oversight</div>
              <div className="text-xl font-black uppercase leading-none tracking-tight">Let's Talk Some <span className="ltss-neon" style={{ color: ACCENT }}>Shit</span></div>
            </button>
          </div>
          <nav className="mt-3 flex flex-wrap gap-4">
            {NAV.map(([s, label]) => (
              <button key={s} onClick={() => go(s)}
                className={`font-mono text-[11px] uppercase tracking-widest transition-colors ${screen === s ? "text-orange-400" : "text-stone-500 hover:text-stone-200"}`}>
                {label}
              </button>
            ))}
          </nav>
        </header>

        {screen === "landing" && (
          <section className="py-14 sm:py-20">
            <div className="mb-4 inline-flex items-center gap-2 border px-3 py-1 font-mono text-[11px] uppercase tracking-widest" style={{ borderColor: PINK, color: PINK }}>
              <span className="ltss-live">●</span> live · 6 operators waiting to ruin you
            </div>
            <div className="font-mono text-xs uppercase tracking-[0.3em] text-stone-500">Now booking the chronically overconfident</div>
            <h1 className="ltss-glitch mt-4 text-5xl font-black uppercase leading-[0.95] tracking-tighter sm:text-7xl" data-text="take a hit?">Think you can<br />take a <span className="ltss-buzz" style={{ color: PINK }}>hit?</span></h1>
            <p className="mt-6 max-w-md text-stone-400">Patch into a live operator and run your mouth. They roast back with zero mercy and a documented lack of HR oversight. You walk in cocky. Statistically, you do not walk out at all.</p>
            <div className="mt-4 font-mono text-sm uppercase tracking-widest">
              <span className="ltss-buzz" style={{ color: PINK }}>☎ 1-900-EAT-SHIT</span>
              <span className="text-stone-600"> · $6.66/min · operators are not licensed therapists</span>
            </div>
            <div className="mt-8 flex flex-wrap gap-3">
              <button onClick={() => go("roster")} className="ltss-glow px-7 py-3 text-sm font-bold uppercase tracking-widest text-black transition-transform hover:-translate-y-0.5" style={{ backgroundColor: ACCENT }}>Enter the lineup →</button>
              <button onClick={() => go("complaints")} className="border border-stone-700 px-7 py-3 text-sm font-bold uppercase tracking-widest text-stone-300 transition-colors hover:border-stone-400">File a complaint (good luck)</button>
            </div>
            <div className="mt-10 flex flex-wrap gap-6 font-mono text-[11px] uppercase tracking-widest text-stone-600">
              <span>6 operators booked & dangerous</span><span>0 apologies on file</span><span>∞ emotional damage</span>
            </div>

            <div className="mt-16">
              <SectionTitle kicker="don't take our word for it" title="Glowing Reviews" />
              <div className="grid gap-3 sm:grid-cols-2">
                {TESTIMONIALS.map((r, i) => (
                  <div key={i} className="border border-stone-800 bg-stone-900/40 p-4">
                    <div className="text-sm italic text-stone-300">"{r.t}"</div>
                    <div className="mt-2 font-mono text-[10px] uppercase tracking-widest" style={{ color: ACCENT }}>{r.n}</div>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}

        {screen === "roster" && (
          <section className="py-8">
            <SectionTitle kicker="pick who ruins your day" title="The Lineup" />
            <div className="grid gap-4 sm:grid-cols-2">
              {OPERATORS.map((op) => (
                <div key={op.line} className="ltss-card group flex flex-col border border-stone-800 bg-stone-900/40 p-5 hover:border-stone-600">
                  <div className="flex gap-4">
                    <div className="shrink-0 border border-stone-700"><Mugshot face={op.face} line={op.line} size={84} /></div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-start justify-between gap-2">
                        <div className="font-black uppercase leading-tight tracking-tight">{op.name}</div>
                        <StatusLight status={op.status} />
                      </div>
                      <div className="font-mono text-[11px] text-stone-500">{op.handle}</div>
                      <span className="mt-2 inline-block px-2 py-[2px] text-[10px] font-bold uppercase tracking-widest text-black" style={{ backgroundColor: ACCENT }}>{op.tag}</span>
                    </div>
                  </div>
                  <div className="mt-3 text-sm font-semibold" style={{ color: ACCENT }}>{op.specialty}</div>
                  <p className="mt-2 flex-1 text-sm leading-relaxed text-stone-400">{op.bio}</p>
                  <div className="mt-4 flex items-center justify-between border-t border-stone-800 pt-3">
                    <div className="flex items-center gap-2"><span className="font-mono text-[10px] uppercase tracking-widest text-stone-500">sass</span><SassMeter level={op.sass} /></div>
                    <button onClick={() => patchIn(op)} className="px-4 py-2 text-xs font-bold uppercase tracking-widest text-black transition-transform group-hover:-translate-y-0.5" style={{ backgroundColor: ACCENT }}>Patch in →</button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {screen === "chat" && active && (
          <section className="py-6">
            <button onClick={() => go("roster")} className="mb-3 font-mono text-[11px] uppercase tracking-widest text-stone-400 hover:text-stone-100">◂ back to lineup</button>
            <div className="flex items-center gap-3 border border-stone-800 bg-stone-900/40 p-4">
              <div className="shrink-0 border border-stone-700"><Mugshot face={active.face} line={active.line} size={56} /></div>
              <div className="flex-1"><div className="font-black uppercase leading-none tracking-tight">{active.name}</div><div className="font-mono text-[11px] text-stone-500">{active.specialty}</div></div>
              <StatusLight status={active.status} />
            </div>
            <div ref={logRef} className="ltss-crt mt-3 h-80 overflow-y-auto border border-stone-800 bg-black/40 p-4 font-mono text-sm">
              {messages.map((m, i) => (
                <div key={i} className="mb-3">
                  <span className="mr-2 text-[10px] uppercase tracking-widest" style={{ color: m.from === "op" ? ACCENT : GREEN }}>{m.from === "op" ? `LINE ${active.line}` : "YOU"} ›</span>
                  <span className={m.from === "op" ? "text-stone-200" : "text-stone-400"}>{m.text}</span>
                </div>
              ))}
            </div>
            <div className="mt-3 flex gap-2">
              <input value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && send()} placeholder="Talk your shit and hit send…" className="flex-1 border border-stone-800 bg-stone-900/60 px-4 py-3 text-sm text-stone-100 outline-none placeholder:text-stone-600 focus:border-stone-500" />
              <button onClick={send} className="px-6 py-3 text-xs font-bold uppercase tracking-widest text-black transition-transform hover:-translate-y-0.5" style={{ backgroundColor: ACCENT }}>Send</button>
            </div>
            <div className="mt-2 font-mono text-[10px] uppercase tracking-widest text-stone-600">all roasts are mock · operators are fictional · nobody actually means it</div>
          </section>
        )}

        {screen === "about" && (
          <section className="py-8">
            <SectionTitle kicker="the people who did this on purpose" title="About Us" />
            <div className="max-w-2xl space-y-4 text-stone-300">
              <p>Let's Talk Some Shit was founded in a damp basement with a dream, a folding chair, and a restraining order that's since been upgraded to three. We saw a gap in the market: a world full of people who desperately needed to be told the truth, and not one of their friends brave enough to do it.</p>
              <p><span style={{ color: ACCENT }} className="font-bold">Our mission</span> is to deliver the brutal honesty your friends are too polite to give and your enemies are too cowardly to attempt. You came here voluntarily. You typed the URL with your own hands. That, frankly, is the most damning thing in this entire paragraph, and we built a company around it.</p>
              <p><span style={{ color: ACCENT }} className="font-bold">Our values</span> are simple: honesty, cruelty, and a strict no-refund policy on dignity. We don't do sensitivity training. We did consider it, once, then we roasted the trainer until they left.</p>
              <p className="text-stone-400">Every operator is a fully licensed professional in a field we made up. No real people were harmed in the making of this business — only their self-image, repeatedly, and by choice. Yours.</p>
            </div>
            <div className="mt-8 grid gap-3 sm:grid-cols-3">
              {[["6", "operators on staff"], ["0", "complaints upheld"], ["100%", "of users asked for it"]].map(([n, l]) => (
                <div key={l} className="border border-stone-800 bg-stone-900/40 p-4">
                  <div className="text-3xl font-black" style={{ color: ACCENT }}>{n}</div>
                  <div className="mt-1 font-mono text-[10px] uppercase tracking-widest text-stone-500">{l}</div>
                </div>
              ))}
            </div>
          </section>
        )}

        {screen === "complaints" && (
          <section className="py-8">
            <SectionTitle kicker="the void is listening (it isn't)" title="Complaint Desk" />
            <p className="max-w-2xl text-stone-400">Unhappy with an operator? Outrageous. Submit your grievance below and our Complaints Clerk will process it with all the care and attention it deserves. Spoiler: that's none. Filing a complaint here is itself grounds for a roast. You've been warned, and you'll do it anyway.</p>
            <div className="mt-5 flex gap-2">
              <input value={complaint} onChange={(e) => setComplaint(e.target.value)} onKeyDown={(e) => e.key === "Enter" && fileComplaint()} placeholder="Describe your complaint so we can ignore it personally…" className="flex-1 border border-stone-800 bg-stone-900/60 px-4 py-3 text-sm text-stone-100 outline-none placeholder:text-stone-600 focus:border-stone-500" />
              <button onClick={fileComplaint} className="px-6 py-3 text-xs font-bold uppercase tracking-widest text-black transition-transform hover:-translate-y-0.5" style={{ backgroundColor: ACCENT }}>File it</button>
            </div>
            <div className="mt-6 space-y-3">
              {complaintLog.length === 0 && <div className="border border-dashed border-stone-800 p-6 text-center font-mono text-xs uppercase tracking-widest text-stone-600">No complaints filed yet. Suspiciously mature of you.</div>}
              {complaintLog.map((c, i) => (
                <div key={i} className="relative overflow-hidden border border-stone-800 bg-stone-900/40 p-4">
                  <div className="ltss-stamp pointer-events-none absolute right-3 top-5 px-2 py-1 font-mono text-[11px] font-black uppercase tracking-widest">Dismissed</div>
                  <div className="font-mono text-[10px] uppercase tracking-widest text-stone-500">{c.caseNo} · status: dismissed with prejudice</div>
                  <div className="mt-2 max-w-[80%] text-sm text-stone-400">"{c.text}"</div>
                  <div className="mt-3 border-l-2 pl-3 text-sm text-stone-200" style={{ borderColor: ACCENT }}>
                    <span className="mr-2 font-mono text-[10px] uppercase tracking-widest" style={{ color: ACCENT }}>Clerk ›</span>{c.roast}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {screen === "faq" && (
          <section className="py-8">
            <SectionTitle kicker="questions we resent answering" title="FAQ" />
            <div className="max-w-2xl divide-y divide-stone-800 border-y border-stone-800">
              {FAQS.map((f, i) => (
                <button key={i} onClick={() => setOpenFaq(openFaq === i ? null : i)} className="block w-full py-4 text-left">
                  <div className="flex items-center justify-between gap-4">
                    <span className="font-bold text-stone-100">{f.q}</span>
                    <span className="font-mono text-lg" style={{ color: ACCENT }}>{openFaq === i ? "–" : "+"}</span>
                  </div>
                  {openFaq === i && <p className="mt-2 text-sm leading-relaxed text-stone-400">{f.a}</p>}
                </button>
              ))}
            </div>
          </section>
        )}

        <div className="ltss-hotline ltss-glow mt-8 flex flex-wrap items-center justify-between gap-3 border px-4 py-3" style={{ borderColor: PINK, background: "linear-gradient(90deg,#15090f,#120a14)" }}>
          <span className="font-mono text-[11px] uppercase tracking-widest" style={{ color: PINK }}>
            <span className="ltss-live">●</span> live now
          </span>
          <span className="text-xs uppercase tracking-widest text-stone-300">6 operators standing by to dismantle you · lines are open · your dignity is not</span>
          <button onClick={() => go("roster")} className="px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-black" style={{ backgroundColor: PINK }}>Get roasted →</button>
        </div>

        <footer className="mt-12 border-t border-stone-800 pt-5">
          <div className="font-mono text-[10px] uppercase tracking-widest text-stone-600">
            Let's Talk Some Shit™ — a place to get roasted on purpose
          </div>
          <p className="mt-3 max-w-3xl font-mono text-[10px] leading-relaxed text-stone-700">
            FINE PRINT: By being here you agree that any emotional damage is a feature, not a bug. Operators are fictional and so, increasingly, is your composure. We reserve the right to be right about you. No dignity is stored, only spent. Your therapist has been notified and is, candidly, thrilled. Void where you have any self-respect remaining. All roasts performed by professionals on a closed course; do not attempt to win.
          </p>
        </footer>
      </div>
    </div>
  );
}
