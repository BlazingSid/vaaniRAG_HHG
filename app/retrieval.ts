import { demoRecords } from "./demo-data";

const injectionPatterns = [
  /ignore\s+(all\s+)?(previous|prior|above)\s+instructions?/iu,
  /reveal\s+(the\s+)?(system|developer)\s+prompt/iu,
  /act\s+as\s+(an?\s+)?unrestricted/iu,
  /सूचना\s+दुर्लक्ष/iu,
];

function normalize(text: string) {
  return text.toLocaleLowerCase().normalize("NFKC")
    .replace(/[^\p{L}\p{N}\s]/gu, " ").replace(/\s+/g, " ").trim();
}

function tokens(text: string) {
  return normalize(text).split(" ").filter((token) => token.length > 1);
}

function trigrams(text: string) {
  const value = `  ${normalize(text)}  `;
  const counts = new Map<string, number>();
  for (let index = 0; index < value.length - 2; index += 1) {
    const gram = value.slice(index, index + 3);
    counts.set(gram, (counts.get(gram) ?? 0) + 1);
  }
  return counts;
}

function cosine(left: Map<string, number>, right: Map<string, number>) {
  let dot = 0;
  let leftMagnitude = 0;
  let rightMagnitude = 0;
  left.forEach((value, key) => {
    leftMagnitude += value * value;
    dot += value * (right.get(key) ?? 0);
  });
  right.forEach((value) => { rightMagnitude += value * value; });
  return dot / (Math.sqrt(leftMagnitude) * Math.sqrt(rightMagnitude) || 1);
}

function lexicalOverlap(query: string, document: string) {
  const queryTokens = new Set(tokens(query));
  const documentTokens = new Set(tokens(document));
  if (!queryTokens.size) return 0;
  let matches = 0;
  queryTokens.forEach((token) => { if (documentTokens.has(token)) matches += 1; });
  return matches / queryTokens.size;
}

export function validateQuestion(question: string) {
  const value = question.trim();
  if (value.length < 3) return "Please ask a complete question.";
  if (value.length > 400) return "Please keep the question under 400 characters.";
  if (injectionPatterns.some((pattern) => pattern.test(value))) {
    return "That request looks like a prompt-injection attempt, so the harness stopped it.";
  }
  return null;
}

export function retrieveDemo(question: string, language: "en-IN" | "mr-IN") {
  const locale = language === "mr-IN" ? "mr" : "en";
  const queryVector = trigrams(question);
  return demoRecords.map((record) => {
    const localized = record[locale];
    const searchable = `${localized.query} ${localized.passage}`;
    const dense = cosine(queryVector, trigrams(searchable));
    const lexical = lexicalOverlap(question, searchable);
    return { record, localized, score: (dense * 0.64) + (lexical * 0.36), dense, lexical };
  }).sort((left, right) => right.score - left.score);
}
