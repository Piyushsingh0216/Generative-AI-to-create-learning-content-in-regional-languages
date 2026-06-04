import bengaliAssistant from "../assets/characters/bengali-assistant.svg";
import bhojpuriAssistant from "../assets/characters/bhojpuri-assistant.svg";
import hindiAssistant from "../assets/characters/hindi-assistant.svg";
import tamilAssistant from "../assets/characters/tamil-assistant.svg";

const CHARACTER_PROFILES = {
  hi: {
    name: "Asha",
    outfitLabel: "North Indian style",
    voiceLang: "hi-IN",
    image: hindiAssistant,
  },
  ta: {
    name: "Kavin",
    outfitLabel: "South Indian style",
    voiceLang: "ta-IN",
    image: tamilAssistant,
  },
  bn: {
    name: "Mili",
    outfitLabel: "Bengali traditional style",
    voiceLang: "bn-IN",
    image: bengaliAssistant,
  },
  bho: {
    name: "Gopal",
    outfitLabel: "Rural North Indian style",
    voiceLang: "hi-IN",
    image: bhojpuriAssistant,
  },
  default: {
    name: "Mitra",
    outfitLabel: "Learning companion",
    voiceLang: "hi-IN",
    image: hindiAssistant,
  },
};

export default CHARACTER_PROFILES;
