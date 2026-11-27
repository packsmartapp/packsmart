// Packy search check (26 Nov 2026): real traveller questions, each with the note that should answer it.
// It loads the search() from api/ask.js and the notes from api/_japan_kb.js, and reports whether a matching note is in
// the top N that Packy hands the model. No network, no AI call.
// Run from the repo root:  node tools/packy_eval.mjs        (add -v to list the top notes for every question)
// Add a question whenever a reader's question gets a weak answer, so the fix stays fixed.
import fs from 'fs';

const src = fs.readFileSync('api/ask.js', 'utf8');
const kbMod = await import(process.cwd() + '/api/_japan_kb.js');
const KB = kbMod.KB || kbMod.default;
const { ITINQ, BUDGETQ } = await import(process.cwd() + '/api/_offers.js');
// rebuild search() exactly as ask.js defines it (same words, stemming, aliases and weights)
const stopLine = src.match(/const STOP = new Set\([^\n]*\n/)[0];
const start = src.indexOf('const words = s =>');
const end = src.indexOf('\n}\n', src.indexOf('function search(')) + 3;
const twm = src.match(/const TOPIC_WORDS = \{[^\n]*\n/)[0];
const { search, TOPIC_WORDS } = new Function('KB', 'ITINQ', 'BUDGETQ', stopLine + src.slice(start, end) + twm + 'return {search, TOPIC_WORDS};')(KB, ITINQ, BUDGETQ);

const N = 9;   // what ask.js passes to the model
// [question, page topic ('' = the hub or a general page), what a right note contains (regex on title + text),
//  optionally a regex on note titles that must NOT be among the notes handed to the model]
const CASES = [
  ['What should I do if I need a doctor in Tokyo?', '', /visitor hotline|119/i],
  ['emergency number in Japan', '', /119/],
  ['I feel sick, who can I call?', '', /visitor hotline|119/i],
  ['I lost my wallet, what should I do?', '', /\b110\b|police|lost/i],
  ['How do I get from Narita to Shinjuku?', '', /narita express|n'ex/i],
  ['Haneda airport to Shibuya by train', '', /haneda/i],
  ['How do I get from Kansai Airport to Kyoto?', '', /haruka|kyoto/i],
  ['New Chitose Airport to Sapporo', '', /rapid|new chitose/i],
  ['How do I top up a Suica card?', '', /suica/i],
  ['Is tipping expected in Japan?', '', /tip/i],
  ['Do I need a visa for Japan?', '', /visa/i],
  ['Where can I withdraw cash at Shinjuku station?', 'shinjuku', /atm/i],
  ['What plug do I need in Japan?', '', /plug|volt/i],
  ['When is cherry blossom season?', '', /cherry|sakura/i],
  ['How long is the Shinkansen from Tokyo to Kyoto?', '', /kyoto/i],
  ['Is the Japan Rail Pass worth it?', '', /rail pass/i],
  ['Where can I store my luggage at Ueno?', 'ueno', /locker|baggage|luggage/i],
  ['Can I pay by credit card in Japan?', '', /card/i],
  ['How cold is Sapporo in winter?', '', /snow|winter|°c|degrees/i],
  ['Is there a ski bus to Niseko?', '', /niseko/i],
  ['How does tax-free shopping work?', '', /tax-free|tax free/i],
  ['What is the etiquette on trains?', '', /etiquette|quiet|phone/i],
  ['How much is a taxi from Haneda?', '', /taxi/i],
  ['Where can I buy a SIM card at Narita?', '', /sim/i],
  ['Is the tap water safe to drink?', '', /tap water/i],
  ['How do I get from Osaka to Kyoto?', '', /kyoto/i],
  ['Where is the Skyliner at Ueno?', 'ueno', /skyliner/i],
  ['Can I bring medicine into Japan?', '', /medicine/i],
  ['What exit should I use at Shinjuku?', 'shinjuku', /exit/i],
  ['Do I need travel insurance for Japan?', '', /travel insurance/i],
  ['Can I buy travel insurance after I arrive in Japan?', '', /after you enter japan|after entering japan/i],
  ['How expensive is a hospital in Japan for tourists?', '', /million yen|10,000,000/i],
  ['Where can I buy medicine for a cold?', '', /pharmacy|drugstore/i],
  ['How do I call an ambulance?', '', /119/],
  ['Is there a helpline in English?', '', /visitor hotline/i],
  ['How do I find an English-speaking doctor in Osaka?', '', /search medical institutions|medical institutions where consultations/i],
  ['Does travel insurance cover pregnancy care?', '', /perinatal/i],
  ['Where can I buy alcohol in Tokyo?', 'tokyo', /sakaya|convenience stores/i],
  ['Can I drink beer in a park in Japan?', '', /drinking outside/i],
  ['Do I need to carry my passport in Japan?', '', /carry your passport/i],
  ['Can I go to an onsen with tattoos?', '', /tattoo/i],
  ['Can I smoke on the street in Tokyo?', '', /smoking/i],
  ['Is CBD or cannabis legal in Japan?', '', /cannabis/i],
  ['Do we have to be naked in an onsen?', '', /naked/i],
  ['Can I wear a swimsuit in an onsen?', '', /swimsuit|naked/i],
  ['What do I do with my towel at the hot spring?', '', /towel/i],
  ['What is the drinking age in Japan?', '', /under the age of 20|remain at 20/i],
  ['Is there an onsen at New Chitose Airport?', '', /onsen and hotel, both conveniently located within the airport/i],
  ['can you plan an itenerary for 10 days, and for family of 4.', '', /tokyo to kyoto|kyoto/i],
  ['can you make a plan for me for Japan?', '', /kyoto|tokai|kansai/i],
  ['What should we see on a first trip to Japan?', '', /kyoto|tokai|kansai/i],
  ['I am 19, can I drink beer in Japan?', '', /under the age of 20|remain at 20/i],
  ['How much is a ticket to Tokyo Disneyland?', '', /1-Day Passport/],
  ['Ueno Zoo entrance fee for kids', 'ueno', /Ueno Zoo admission/],
  // 27 Nov, a tester: a Tokyo family budget got Asahiyama Zoo and Sapporo fares
  ['Can you give me the total cost, for a family of 4, from Singapore, for 10 days, 4 star hotels, and mostly in Tokyo, theme park, zoos, temple visits, taxi etc all included... what is the likely total cost? Planning in Feb 2027.', '', /tokyo subway ticket|departure tax|taxi in tokyo/i, /^sapporo|new chitose|hokkaido/i],
  ['How much budget do we need for a week in Tokyo?', '', /tokyo subway ticket|departure tax|taxi in tokyo/i, /^sapporo|new chitose|hokkaido/i],
  ['What will our Kyoto and Osaka trip cost?', '', /kyoto|osaka|kansai|departure tax/i, /^sapporo|new chitose|hokkaido/i],
];
const verbose = process.argv.includes('-v');
let hit = 0;
for (const [q, topic, rx, notRx] of CASES) {
  const top = search(q, N, TOPIC_WORDS[topic] || []);
  const rank = top.findIndex(p => rx.test(p.t + ' ' + p.x)) + 1;
  const bad = notRx ? top.find(p => notRx.test(p.t)) : null;   // by the note's title: a shared note (e.g. city transport) may mention both
  if (rank && rank <= 5 && !bad) hit++;
  console.log((bad ? 'BAD ' : rank && rank <= 5 ? 'ok  ' : rank ? 'low ' : 'MISS') + ' #' + (rank || '-') + '  ' + q.slice(0, 110) + (bad ? '   (has: ' + bad.t.slice(0, 60) + ')' : ''));
  if (verbose || !rank || rank > 5) top.slice(0, 5).forEach((p, i) => console.log('        ' + (i + 1) + ' ' + p.t.split(' > ').slice(-2).join(' > ').slice(0, 90)));
}
console.log('\n' + hit + '/' + CASES.length + ' questions have a right note in the top 5');
