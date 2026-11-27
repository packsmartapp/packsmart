// Fuku's emailed lessons (the MailerLite gift emails, 26 Nov 2026) and the hub's "Hear Fuku say it" card on /japan.
// One list for both: each phrase in an email links to /japan?say=<lesson>-<phrase>, which opens that lesson's card
// and lets the reader play it with the device's own Japanese voice (the voice reads the Japanese, not the romaji).
// tools/w73_japan_hub.py reads the object below as JSON, so keep it plain JSON: [romaji, Japanese, meaning].
// The phrases still need a native speaker's check before the lessons are promoted.
export const LESSONS = {
  "1": {"title": "At the station", "phrases": [
    ["Deguchi wa doko desu ka?", "出口はどこですか？", "Where is the exit?"],
    ["Kaisatsu wa doko desu ka?", "改札はどこですか？", "Where is the ticket gate?"],
    ["Nanban hoomu desu ka?", "何番ホームですか？", "Which platform is it?"],
    ["Kore wa Shinjuku ni ikimasu ka?", "これは新宿に行きますか？", "Does this go to Shinjuku? (Swap in any station.)"],
    ["Shuuden wa nanji desu ka?", "終電は何時ですか？", "What time is the last train?"]]},
  "2": {"title": "Eating out", "phrases": [
    ["Futari desu.", "ふたりです。", "Two people. (One person: hitori desu.)"],
    ["Eigo no menyuu wa arimasu ka?", "英語のメニューはありますか？", "Do you have an English menu?"],
    ["Omizu o kudasai.", "お水をください。", "Water, please."],
    ["Shokumotsu arerugii ga arimasu.", "食物アレルギーがあります。", "I have a food allergy."],
    ["Okaikei o onegai shimasu.", "お会計をお願いします。", "The bill, please."]]},
  "3": {"title": "At the konbini", "phrases": [
    ["Atatamete kudasai.", "温めてください。", "Please heat it up."],
    ["Fukuro wa irimasen.", "袋はいりません。", "I don't need a bag."],
    ["Kaado wa tsukaemasu ka?", "カードは使えますか？", "Can I pay by card?"],
    ["Reshiito o kudasai.", "レシートをください。", "A receipt, please."],
    ["Menzei de kaemasu ka?", "免税で買えますか？", "Can I buy this tax-free?"]]},
  "4": {"title": "When you don't understand", "phrases": [
    ["Wakarimasen.", "わかりません。", "I don't understand."],
    ["Yukkuri onegai shimasu.", "ゆっくりお願いします。", "Slowly, please."],
    ["Mou ichido onegai shimasu.", "もう一度お願いします。", "Once more, please."],
    ["Kaite kudasai.", "書いてください。", "Please write it down."],
    ["Chotto matte kudasai.", "ちょっと待ってください。", "One moment, please."]]},
  "5": {"title": "On the train", "phrases": [
    ["Sumimasen, orimasu.", "すみません、降ります。", "Excuse me, I'm getting off."],
    ["Kono seki, aite imasu ka?", "この席、空いていますか？", "Is this seat free?"],
    ["Douzo.", "どうぞ。", "Please, go ahead. (Offering your seat.)"],
    ["Tsugi no eki wa nan desu ka?", "次の駅は何ですか？", "What's the next station?"],
    ["Doko de norikaemasu ka?", "どこで乗り換えますか？", "Where do I change trains?"]]},
  "6": {"title": "Tickets and IC cards", "phrases": [
    ["Kippu wa doko de kaemasu ka?", "切符はどこで買えますか？", "Where can I buy a ticket?"],
    ["Chaaji shitai desu.", "チャージしたいです。", "I'd like to top up my card."],
    ["Seisanki wa doko desu ka?", "精算機はどこですか？", "Where is the fare adjustment machine?"],
    ["Kaado ga tsukaemasen.", "カードが使えません。", "My card isn't working."],
    ["Kono basu wa eki ni ikimasu ka?", "このバスは駅に行きますか？", "Does this bus go to the station?"]]},
  "7": {"title": "Small talk about the weather", "phrases": [
    ["Ii tenki desu ne.", "いい天気ですね。", "Lovely weather, isn't it?"],
    ["Kyou wa atsui desu ne.", "今日は暑いですね。", "Hot today, isn't it?"],
    ["Samui desu ne.", "寒いですね。", "Cold, isn't it?"],
    ["Ame ga furisou desu ne.", "雨が降りそうですね。", "Looks like rain."],
    ["Kasa wa arimasu ka?", "傘はありますか？", "Do you sell umbrellas?"]]},
  "8": {"title": "Asking for help", "phrases": [
    ["Tasukete!", "助けて！", "Help!"],
    ["Kouban wa doko desu ka?", "交番はどこですか？", "Where is the police box?"],
    ["Saifu o nakushimashita.", "財布をなくしました。", "I lost my wallet."],
    ["Byouin wa doko desu ka?", "病院はどこですか？", "Where is a hospital?"],
    ["Kyuukyuusha o yonde kudasai.", "救急車を呼んでください。", "Please call an ambulance."]]}
};
