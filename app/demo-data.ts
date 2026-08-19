export type DemoRecord = {
  id: string;
  type: string;
  mr: { query: string; answer: string; passage: string };
  en: { query: string; answer: string; passage: string };
};

// Exact records sampled from the official ai4bharat/MSMARCO-XI Marathi
// validation parquet. The backend/ ingestion pipeline handles a requested full split.
export const demoRecords: DemoRecord[] = [
  {
    id: "1102432", type: "DESCRIPTION",
    mr: { query: "कॉर्पोरेशन म्हणजे काय?", answer: "कॉर्पोरेशन ही एक कंपनी किंवा लोकांचा समूह आहे ज्याला एकल संस्था म्हणून काम करण्याचा अधिकार आहे आणि ज्याला कायद्यानुसार मान्यता प्राप्त आहे.", passage: "मॅकडोनाल्ड कॉर्पोरेशन ही जगातील सर्वात ओळखली जाणारी कॉर्पोरेशन आहे. कॉर्पोरेशन म्हणजे एक कंपनी किंवा लोकांचा समूह ज्याला एकल संस्था म्हणून काम करण्याचा अधिकार आहे आणि कायद्यानुसार त्याला मान्यता दिली आहे." },
    en: { query: "what is a corporation?", answer: "A corporation is a company or group of people authorized to act as a single entity and recognized as such in law.", passage: "McDonald's Corporation is one of the most recognizable corporations in the world. A corporation is a company or group of people authorized to act as a single entity (legally a person) and recognized as such in law." },
  },
  {
    id: "1102431", type: "DESCRIPTION",
    mr: { query: "रॅचेल कार्सनने द ऑब्लिगेशन टू एन्ड्युअर का लिहिले?", answer: "रेचल कार्सनने हे लिहिले कारण नको असलेले कीटक आणि तण काढून टाकण्याच्या मानवी प्रयत्नांमुळे पर्यावरण प्रदूषित होऊन अधिक समस्या निर्माण होतात, असा तिचा विश्वास होता.", passage: "रॅचेल कार्सनचा 'दि ऑब्लिगेशन टू एन्ड्युअर' हा रसायने, कीटकनाशके, तणनाशके आणि खतांच्या पर्यावरणावरील हानिकारक उपयोगांबद्दलचा युक्तिवाद आहे." },
    en: { query: "why did Rachel Carson write an obligation to endure?", answer: "Rachel Carson wrote The Obligation to Endure because she believed that attempts to eliminate unwanted insects and weeds were creating more problems by polluting the environment.", passage: "Rachel Carson's essay The Obligation to Endure is a convincing argument about the harmful uses of chemicals, pesticides, herbicides, and fertilizers on the environment." },
  },
  {
    id: "300122", type: "NUMERIC",
    mr: { query: "फ्रँक गिफर्डने किती स्त्रियांशी लग्न केले?", answer: "फ्रँक गिफर्डने तीन स्त्रियांशी लग्न केले.", passage: "फ्रँक गिफर्डचे लग्न कॅथी ली गिफर्ड, अ‍ॅस्ट्रिड गिफर्ड आणि मॅक्सिन एव्हिस एव्हर्ट यांच्याशी झाले होते." },
    en: { query: "how many women did Frank Gifford marry?", answer: "Frank Gifford married three women.", passage: "Frank Gifford was married to Kathie Lee Gifford, Astrid Gifford and Maxine Avis Ewart." },
  },
  {
    id: "233826", type: "NUMERIC",
    mr: { query: "गरुड किती वेगाने प्रवास करतो?", answer: "गरुड साधारण ३० ते ५५ मैल प्रति तास वेगाने उडतो.", passage: "गरुड ३० ते ५५ मैल प्रति तास वेगाने उडतात आणि १०० मैल प्रति तासापेक्षा जास्त वेगाने सूर मारतात. गरुड उष्ण हवेच्या प्रवाहांवर तासांच्या तासांसाठी उडू शकतात." },
    en: { query: "how fast does an eagle travel?", answer: "Eagles fly at roughly 30 to 55 mph.", passage: "Eagles fly 30 to 55 mph and dive at over 100 mph. Eagles can soar for hours on warm air currents, which conserves energy during long migrations." },
  },
  {
    id: "260880", type: "NUMERIC",
    mr: { query: "कॅन्टालूप परिपक्व होण्यासाठी किती वेळ लागतो?", answer: "कॅन्टालूपला बियापासून पिकलेल्या फळापर्यंत साधारण ९० दिवस लागतात.", passage: "कॅन्टालूपला परागित फुलांपासून विकसित होण्यासाठी ३५ ते ४५ दिवस लागतात. वेलींना बियांपासून पिकलेल्या फळापर्यंत वाढण्यासाठी साधारण ९० दिवस लागतात." },
    en: { query: "how long does cantaloupe take to mature?", answer: "Cantaloupe normally takes about 90 days to grow from seed to ripe fruit.", passage: "Cantaloupes take 35 to 45 days to ripen after pollination. Cantaloupe vines normally take 90 days to grow from seed to ripe fruit." },
  },
  {
    id: "116898", type: "DESCRIPTION",
    mr: { query: "मनमानी या शब्दाची व्याख्या काय?", answer: "कारण किंवा निर्णयावर आधारित नसलेली आणि नियम किंवा मानकांचा विचार न करता वैयक्तिक इच्छेवर आधारित कृती किंवा निर्णय म्हणजे मनमानी.", passage: "स्वेच्छाधीन म्हणजे कारण किंवा निर्णयावर आधारित नसून नियम किंवा मानकांचा विचार न करता वैयक्तिक इच्छा किंवा विवेकावर आधारित कृती किंवा निर्णय." },
    en: { query: "what is the definition of arbitrary?", answer: "Arbitrary describes an action or decision based on personal will rather than reason, rules, or standards.", passage: "The term arbitrary describes a course of action or a decision that is not based on reason or judgment but on personal will or discretion without regard to rules or standards." },
  },
  {
    id: "1090353", type: "DESCRIPTION",
    mr: { query: "हवामान आणि वातावरण यात काय फरक आहे?", answer: "वातावरण ही प्रदेशातील दैनंदिन स्थिती आणि अल्पकालीन बदल आहेत, तर हवामान ही विशिष्ट ठिकाणच्या दीर्घ कालावधीतील वातावरणाची सांख्यिकीय माहिती आहे.", passage: "वातावरण ही एखाद्या प्रदेशातील दैनंदिन स्थिती आणि त्यातील अल्पकालीन फरक आहेत, तर हवामान विशिष्ट ठिकाणी वातावरणातील फरकांचे दीर्घकालीन सांख्यिकीय वर्णन करते." },
    en: { query: "what is the difference between weather and climate?", answer: "Weather is the day-to-day state of the atmosphere, while climate statistically describes weather variation over a specified interval.", passage: "Weather is the day-to-day state of the atmosphere in a region and its short-term variations, whereas climate is statistical weather information for a given place over a specified interval." },
  },
  {
    id: "113570", type: "DESCRIPTION",
    mr: { query: "संस्कृतीचे समाजशास्त्र म्हणजे काय?", answer: "समाजातील सदस्यांनी वापरलेल्या प्रतीकात्मक संकेतांचा संच म्हणून समजल्या जाणाऱ्या संस्कृतीचे पद्धतशीर विश्लेषण म्हणजे संस्कृतीचे समाजशास्त्र.", passage: "संस्कृतीचे समाजशास्त्र हे संस्कृतीचे पद्धतशीर विश्लेषण आहे, जी समाजातील सदस्यांनी वापरलेल्या प्रतीकात्मक संकेतांचा समूह म्हणून समजली जाते." },
    en: { query: "what is the sociology of culture?", answer: "It is the systematic analysis of culture as the ensemble of symbolic codes used by members of a society.", passage: "The sociology of culture concerns the systematic analysis of culture, usually understood as the ensemble of symbolic codes used by members of a society." },
  },
  {
    id: "126172", type: "DESCRIPTION",
    mr: { query: "रॅडिकल नेक डिसेक्शन म्हणजे काय?", answer: "डोके किंवा मानेतील कर्करोगाचे ऊती किंवा वाढ काढून टाकण्यासाठी वापरली जाणारी ही शस्त्रक्रिया आहे.", passage: "रॅडिकल नेक डिसेक्शन ही डोके किंवा मानेतील कर्करोगाचे ऊती किंवा वाढ काढून टाकण्यासाठी वापरली जाणारी शस्त्रक्रिया आहे." },
    en: { query: "what is a radical neck dissection?", answer: "It is a surgical procedure used to remove cancerous tissues or growths in the head or neck.", passage: "A radical neck dissection is a surgical procedure that is used to remove cancerous tissues or growths in the head or neck." },
  },
  {
    id: "267380", type: "NUMERIC",
    mr: { query: "कार्ब सायकल किती काळ करावी?", answer: "कार्ब सायकल साधारण दोन ते आठ आठवडे करावी.", passage: "शरीरातील सुरुवातीच्या चरबीच्या प्रमाणानुसार कार्ब-सायकलिंग दोन ते आठ आठवड्यांच्या दरम्यान असावे. हे अल्पकालीन साधन आहे." },
    en: { query: "how long should you carb cycle?", answer: "Carb cycling should generally last between two and eight weeks.", passage: "It should be somewhere between two and eight weeks depending on initial body fat. Carb-cycling is a short-term tool." },
  },
  {
    id: "1090352", type: "DESCRIPTION",
    mr: { query: "डोळ्यावर रांजणवाडी कशामुळे होते?", answer: "पापणीतील तेल ग्रंथींच्या संसर्गामुळे, बहुतेकदा स्टॅफिलोकोकस जीवाणूमुळे रांजणवाडी होते.", passage: "रांजणवाडी सहसा पापण्यांतील तेल ग्रंथींच्या संसर्गामुळे होते. बर्‍याचदा ते स्टॅफिलोकोकस जीवाणूंनी संक्रमित होतात." },
    en: { query: "what causes a stye?", answer: "Styes are caused by infections of the eyelid's oil glands, commonly involving Staphylococcus bacteria.", passage: "Styes are usually caused by infections of the oil glands in the eyelid, most commonly involving Staphylococcus bacteria." },
  },
  {
    id: "202891", type: "NUMERIC",
    mr: { query: "रेडिंग कॅलिफोर्नियातील सर्वोच्च तापमान किती?", answer: "रेडिंग, कॅलिफोर्नियामध्ये अधिकृतपणे नोंदवलेले सर्वोच्च तापमान ११८ फॅरेनहाइट आहे.", passage: "२० जुलै १९८८ रोजी रेडिंग, कॅलिफोर्नियामध्ये नोंदवलेले सर्वाधिक अधिकृत तापमान ११८ फॅरेनहाइट होते." },
    en: { query: "what is the highest recorded temperature in Redding California?", answer: "The highest official recorded temperature in Redding, California was 118°F.", passage: "The highest official recorded temperature in Redding, California was 118°F on July 20, 1988." },
  },
];
