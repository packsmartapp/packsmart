// Packy's booking buttons (D57), shared by /api/ask (which picks one per answer, in offerFor) and /api/email-chat
// (which puts the same buttons in the emailed chat). The AI never picks or writes these; only this list does.
// The leading underscore keeps this file from becoming an API route.
// Itinerary and "plan my trip" questions (owner, 26 Nov): Packy gives a starting route, then this button opens the
// trip planner on the home page with Japan filled in (it builds the day-by-day plan for the reader's dates and group).
export const ITINQ = /itin[ea]r|iten[ae]r|itenar|\b(?:make|build|create|give|suggest|draw up|help me with)\b.{0,25}\b(?:plan|route|schedule)\b(?!.{0,15}\b(?:data|esim|sim|insurance)\b)|\bplan\b.{0,25}\b(?:for japan|in japan|my japan|japan trip|trip|holiday|vacation|visit)\b|plan (?:my|our|a|the) (?:\w+ )?(?:trip|holiday|vacation|route|visit)|\b\d{1,2}[ -]?(?:days?|nights?|weeks?)\b|where (?:should|to|can) (?:i|we) go|what (?:should|to) (?:i|we) (?:see|visit)|things to do in japan|first (?:trip|time|visit) (?:to|in) japan/;
// Whole-trip budget questions (27 Nov, a tester: "total cost for a family of 4 ... 10 days ... all included"): Packy gives
// the checked costs it has, asks a few questions, and this button opens the trip planner, which estimates a budget.
export const BUDGETQ = /total (?:cost|budget|price|spend)|\bbudget\b|how much (?:will|would|does|do|should) (?:it|the trip|a trip|our trip|my trip|we|i) (?:cost|need|spend|budget)|how much (?:money|cash) (?:will|would|should|do) (?:i|we) (?:need|bring|budget)|(?:trip|holiday|vacation) (?:cost|costs|budget)|cost (?:of|for) (?:the|a|our|my) (?:trip|holiday|vacation)|likely (?:total|cost)|overall cost|all included|all-inclusive|estimate (?:the |our |my )?(?:cost|budget)/;
// 27 Nov 2026: the airport transfer, eSIM and bag storage buttons use Packy's own Travelpayouts links (Sub IDs
// packy-transfer, packy-esim, packy-bags-tokyo/-osaka/-kyoto), so Packy's sales show up separately from the site's.
export const OFFERS = [
  // the budget calculator; ask.js adds what the reader said (people, nights, Disney days) to the link
  { id: 'budget', rx: BUDGETQ, label: 'Work out your trip budget', url: '/japan-budget?src=packy', partner: false },
  // guided multi-day tours: off (see TOURS_ON in tools/w86_japan_budget.py) until TourRadar confirms
  { id: 'multitour', off: true, rx: /package (?:tour|holiday|trip)|tour package|holiday package|multi-?day tours?|guided (?:trip|holiday|tour of japan)|group tours?|organi[sz]ed tours?|escorted tours?|all[- ]inclusive|someone (?:else )?(?:to )?(?:handle|organi[sz]e|arrange|book) (?:it|everything)|(?:easier|simpler|better) (?:with|to (?:take|book|join)) a tour|join a tour/, label: 'Compare guided multi-day Japan tours', url: 'https://www.tourradar.com/d/japan?utm_source=partner-traveller-1471305&utm_medium=ambassador&utm_campaign=packy-tours', partner: true },
  { id: 'plan', rx: ITINQ, not: /\bpass\b|ticket|valid|visa|stay (?:up to|for)|lockers?|bus\b/, label: 'Build a day-by-day Japan plan', url: '/?dest=Japan&src=packy#plan', partner: false },
  { id: 'skyliner', rx: /skyliner|keisei|ueno.{0,40}narita|narita.{0,40}ueno|nippori/, regions: ['tokyo', ''], label: 'Book Skyliner tickets online', url: 'https://klook.tpx.li/gIYih1CY', partner: true },
  { id: 'nex', rx: /narita express|\bn'?ex\b/, regions: ['tokyo', ''], label: 'Book Narita Express tickets online', url: 'https://klook.tpx.li/tX4jclRv', partner: true },
  { id: 'limousine', rx: /limousine/, regions: ['tokyo', ''], label: 'Book an airport limousine bus online', url: 'https://klook.tpx.li/SISnlOYP', partner: true },
  // the nationwide pass only: not for the Hokkaido or area passes (no partner sells those through us)
  { id: 'jrpass', rx: /japan rail pass|\bjr pass\b/, not: /hokkaido rail pass|area pass|hokkaido pass/, regions: ['tokyo', 'kansai', ''], label: 'Book a Japan Rail Pass online', url: 'https://klook.tpx.li/vRbZKSsT', partner: true },
  { id: 'shinkansen', rx: /shinkansen|bullet train|nozomi|hikari|kodama/, regions: ['tokyo', 'kansai', ''], label: 'Book Shinkansen tickets online', url: 'https://www.japan-bullettrain.com/?via=packsmart', partner: true },
  { id: 'transfer', rx: /\btransfer\b|private car|pick ?up|taxi from|door.to.door/, regions: ['tokyo', 'kansai', 'hokkaido', ''], label: 'Book a private airport transfer', url: 'https://tpo.lu/5TSGg9Tf', partner: true },
  { id: 'car', rx: /rent(al)?[ -]?a?[ -]?car|car (hire|rental)|\bdrive\b|driving/, regions: ['hokkaido', 'tokyo', 'kansai', ''], by: {
      hokkaido: ['Compare car hire in our guide', '/blog/new-chitose-airport-guide#transfer-car', false],
      tokyo: ['Compare car hire in our guide', '/blog/ueno-station-guide#car-rental', false] }, label: 'Compare car hire in our guide', url: '/blog/new-chitose-airport-guide#transfer-car', partner: false },
  { id: 'esim', rx: /\besim\b|\bsim\b|mobile data|internet|wi-?fi|phone data|roaming/, regions: ['tokyo', 'kansai', 'hokkaido', ''], label: 'See eSIM data plans for Japan', url: 'https://airalo.tpo.lu/ndZAMVI0', partner: true },
  { id: 'insurance', rx: /insurance|hospital|doctor|medical/, regions: ['tokyo', 'kansai', 'hokkaido', ''], label: 'Get a SafetyWing travel medical insurance quote', url: 'https://www.safetywing.com/nomad-insurance?referenceID=26492686&utm_source=26492686&utm_medium=Ambassador', partner: true },
  // bag storage partner covers Tokyo, Kyoto and Osaka only; in Hokkaido point to our locker sections instead
  { id: 'bags', rx: /luggage|\bbags?\b|suitcase|locker/, regions: ['tokyo', 'kansai', 'hokkaido'], by: {
      tokyo: ['Store your bags in Tokyo', 'https://radicalstorage.tpo.lu/hEstntUb', true],
      kansai: ['Store your bags in Osaka', 'https://radicalstorage.tpo.lu/1S7khUHA', true],
      kyoto: ['Store your bags in Kyoto', 'https://radicalstorage.tpo.lu/FNuz9B3L', true],
      hokkaido: ['Lockers and luggage at Sapporo Station', '/blog/sapporo-station-guide#luggage', false],
      'hokkaido-airport': ['Lockers and bag delivery at New Chitose', '/blog/new-chitose-airport-guide#luggage', false] } },
  { id: 'hotel', rx: /hotel|\bstay\b|accommodation|where to sleep/, regions: ['hokkaido'], label: 'Hotels by Sapporo Station', url: '/blog/sapporo-station-guide#hotels', partner: false },
  { id: 'tour', rx: /\btours?\b|day trip|guided|excursion|ski (lesson|tour|pass)|lift ticket/, regions: ['tokyo', 'kansai', 'hokkaido', ''], partner: true, gyg: true },
];
export const TOUR_PLACES = ['niseko', 'otaru', 'noboribetsu', 'furano', 'biei', 'asahikawa', 'sapporo', 'hakodate', 'kyoto', 'osaka', 'nara', 'tokyo', 'hakone', 'fuji', 'nikko', 'hiroshima'];

// The emailed chat may show only buttons from this list (the email form is public, so it must not carry other links).
const GYG = /^https:\/\/www\.getyourguide\.com\/s\/\?q=[a-z0-9%]+&partner_id=D7IXONS&cmp=ps-packy-[a-z]+$/;
export function knownOffer(o) {
  if (!o || typeof o.url !== 'string') return null;
  if (/^\/japan-budget\?src=packy(?:&(?:ad|tn|ch|in|nt|nk|no|nh|dn)=\d{1,2})*$/.test(o.url)) return { label: 'Work out your trip budget', url: o.url, partner: false };
  if (GYG.test(o.url)) {
    const label = String(o.label || '');
    return /^Compare [a-z ]{3,60}$/i.test(label) ? { label, url: o.url, partner: true } : null;
  }
  for (const x of OFFERS) {
    if (x.off) continue;
    if (x.url === o.url && x.label) return { label: x.label, url: x.url, partner: !!x.partner };
    for (const k in (x.by || {})) { const b = x.by[k]; if (b[1] === o.url) return { label: b[0], url: b[1], partner: b[2] }; }
  }
  return null;
}
