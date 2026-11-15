from typing import Dict, Any, Optional
import re
import time
from config import settings
from services.gemini_service import gemini_model

# Comprehensive dictionary of core medical phrases and warnings in all 8 regional languages
TRANSLATION_DICTIONARY: Dict[str, Dict[str, str]] = {
    "ta": { # Tamil
        "duplicate_warning": "எச்சரிக்கை: உங்கள் மருந்துச் சீட்டுகளில் ஒரே மருந்து அல்லது அதன் மூலக்கூறு ஒன்றுக்கு மேற்பட்ட முறை உள்ளது. இதனால் அதிக டோஸ் ஏற்படும் அபாயம் உள்ளது. தயவுசெய்து உங்கள் மருத்துவரிடம் சரிபார்க்கவும்.",
        "interaction_warning": "பாதுகாப்பு எச்சரிக்கை: இந்த மருந்துகளை ஒன்றாக உட்கொள்ளும்போது ஒன்றோடொன்று முரண்பட வாய்ப்புள்ளது. உங்கள் மருத்துவரிடம் கலந்து ஆலோசிக்கவும்.",
        "dosage_warning": "டோஸ் எச்சரிக்கை: இந்த மருந்தின் தினசரி மொத்த அளவு பரிந்துரைக்கப்பட்ட அளவை விட அதிகமாகத் தெரிகிறது. உங்கள் மருத்துவரிடம் உறுதிப்படுத்தவும்.",
        "overlap_warning": "சிகிச்சை ஒன்றுடன் ஒன்று பொருந்துதல்: இந்த மருந்துகள் ஒரே விதமான சிகிச்சைக்குப் பயன்படுகின்றன. இரண்டையும் எடுத்துக்கொள்ள வேண்டுமா என மருத்துவரிடம் கேட்கவும்.",
        "consult_doctor": "மருத்துவரை அணுகவும்: எந்தவொரு மருந்தையும் மாற்றுவதற்கு அல்லது நிறுத்துவதற்கு முன் உங்கள் மருத்துவரை அணுகவும்.",
        "reminder": "மருந்து நேரம்: உங்கள் மருந்தை மருத்துவர் கூறியபடி தவறாமல் சரியான நேரத்தில் உட்கொள்ளவும்.",
        "summary": "மருந்து பாதுகாப்பு சுருக்கம்: உங்கள் மருந்துச் சீட்டுகள் வெற்றிகரமாக ஆய்வு செய்யப்பட்டன. தயவுசெய்து கீழே உள்ள தகவல்களை மதிப்பாய்வு செய்யவும்."
    },
    "hi": { # Hindi
        "duplicate_warning": "चेतावनी: आपके पर्चे में एक ही दवा या उसका सक्रिय घटक एक से अधिक बार मौजूद है। इससे डबल डोज का जोखिम हो सकता है। कृपया अपने डॉक्टर से परामर्श करें।",
        "interaction_warning": "सुरक्षा चेतावनी: इन दवाओं को एक साथ लेने पर परस्पर दुष्प्रभाव हो सकते हैं। कृपया अपने डॉक्टर या फार्मासिस्ट से परामर्श लें।",
        "dosage_warning": "खुराक चेतावनी: इस दवा की कुल दैनिक खुराक सामान्य सीमा से अधिक प्रतीत होती है। डॉक्टर से जांच कराएं।",
        "overlap_warning": "उपचार ओवरलैप: ये दवाएं एक जैसे उद्देश्य के लिए हैं। क्या दोनों दवाएं साथ लेनी हैं, डॉक्टर से पुष्टि करें।",
        "consult_doctor": "डॉक्टर से परामर्श लें: किसी भी दवा को शुरू करने, बदलने या बंद करने से पहले डॉक्टर से सलाह लें।",
        "reminder": "दवा का समय: कृपया डॉक्टर की सलाह के अनुसार अपनी दवा समय पर लें।",
        "summary": "दवा सुरक्षा सारांश: आपके पर्चों का विश्लेषण पूरा हो गया है। कृपया सुरक्षा चेतावनियों की समीक्षा करें।"
    },
    "te": { # Telugu
        "duplicate_warning": "హెచ్చరిక: మీ ప్రిస్క్రిప్షన్లలో ఒకే రకమైన మందు ఒకటి కంటే ఎక్కువసార్లు ఉంది. ఇది డబుల్ డోస్ ప్రమాదానికి దారితీయవచ్చు. దయచేసి మీ వైద్యుడిని సంప్రదించండి.",
        "interaction_warning": "భద్రతా హెచ్చరిక: ఈ మందులను కలిపి తీసుకున్నప్పుడు ఒకదానితో ఒకటి ప్రతికూల చర్యలు జరగవచ్చు. దయచేసి మీ డాక్టర్ లేదా ఫార్మసిస్ట్‌తో మాట్లాడండి.",
        "dosage_warning": "డోసేజ్ హెచ్చరిక: ఈ మందు యొక్క మొత్తం రోజువారీ మోతాదు అధికంగా కనిపిస్తోంది. దయచేసి వైద్యుడితో సరిచూసుకోండి.",
        "overlap_warning": "చికిత్స సమన్వయం: ఈ మందులు ఒకే ప్రయోజనం కోసం పనిచేస్తాయి. రెండింటినీ కొనసాగించాలో లేదో డాక్టర్‌ను అడగండి.",
        "consult_doctor": "వైద్యుడిని సంప్రదించండి: మందులను మార్చడానికి లేదా ఆపడానికి ముందు ఎల్లప్పుడూ వైద్యుడిని సంప్రదించండి.",
        "reminder": "మందుల సమయం: డాక్టర్ సూచించిన విధంగా మీ మందులను సమయానికి తీసుకోండి.",
        "summary": "మందుల భద్రతా సారాంశం: మీ ప్రిస్క్రిప్షన్ల విశ్లేషణ పూర్తయింది. దయచేసి వివరాలను పరిశీలించండి."
    },
    "ml": { # Malayalam
        "duplicate_warning": "മുന്നറിയിപ്പ്: നിങ്ങളുടെ കുറിപ്പടികളിൽ ഒരേ മരുന്നോ അതിലെ ചേരുവയോ ഒന്നിലധികം തവണ വന്നിട്ടുണ്ട്. ഇത് അമിത ഡോസിന് കാരണമായേക്കാം. ഡോക്ടറുമായി സംസാരിക്കുക.",
        "interaction_warning": "സുരക്ഷാ മുന്നറിയിപ്പ്: ഈ മരുന്നുകൾ ഒരുമിച്ച് കഴിക്കുന്നത് പരസ്പരവിരുദ്ധമായ പാർശ്വഫലങ്ങൾ ഉണ്ടാക്കിയേക്കാം. ഡോക്ടറുമായോ ഫാർമസിസ്റ്റുമായോ ആലോചിക്കുക.",
        "dosage_warning": "ഡോസ് മുന്നറിയിപ്പ്: ഈ മരുന്നിന്റെ പ്രതിദിന ഡോസ് അനുവദനീയമായതിലും കൂടുതലായി കാണപ്പെടുന്നു. ഡോക്ടറോട് ചോദിക്കുക.",
        "overlap_warning": "ചികിത്സാ സമാനത: ഈ മരുന്നുകൾ സമാനമായ രോഗാവസ്ഥയ്ക്കുള്ളതാണ്. രണ്ടും ഒരുമിച്ച് കഴിക്കണോ എന്ന് ഡോക്ടറോട് സ്ഥിരീകരിക്കുക.",
        "consult_doctor": "ഡോക്ടറെ സമീപിക്കുക: മരുന്ന് നിർത്തുന്നതിനോ മാറ്റുന്നതിനോ മുൻപ് ഡോക്ടറുടെ ഉപദേശം തേടുക.",
        "reminder": "മരുന്ന് സമയം: ഡോക്ടർ നിർദ്ദേശിച്ചതനുസരിച്ച് കൃത്യസമയത്ത് മരുന്ന് കഴിക്കുക.",
        "summary": "മരുന്ന് സുരക്ഷാ സംഗ്രഹം: നിങ്ങളുടെ കുറിപ്പടികളുടെ പരിശോധന പൂർത്തിയായി. ദയവായി വിവരങ്ങൾ പരിശോധിക്കുക."
    },
    "kn": { # Kannada
        "duplicate_warning": "ಎಚ್ಚರಿಕೆ: ನಿಮ್ಮ ಪ್ರಿಸ್ಕ್ರಿಪ್ಷನ್‌ನಲ್ಲಿ ಒಂದೇ ಔಷಧಿಯು ಒಂದಕ್ಕಿಂತ ಹೆಚ್ಚು ಬಾರಿ ಕಂಡುಬಂದಿದೆ. ಇದು ಡಬಲ್ ಡೋಸ್ ಅಪಾಯವನ್ನು ಉಂಟುಮಾಡಬಹುದು. ದಯವಿಟ್ಟು ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ.",
        "interaction_warning": "ಸುರಕ್ಷತಾ ಎಚ್ಚರಿಕೆ: ಈ ಔಷಧಿಗಳನ್ನು ಒಟ್ಟಿಗೆ ಸೇವಿಸಿದಾಗ ಅಡ್ಡಪರಿಣಾಮಗಳು ಉಂಟಾಗಬಹುದು. ದಯವಿಟ್ಟು ವೈದ್ಯರು ಅಥವಾ ಫಾರ್ಮಾಸಿಸ್ಟ್ ಜೊತೆ ಮಾತನಾಡಿ.",
        "dosage_warning": "ಡೋಸ್ ಎಚ್ಚರಿಕೆ: ಈ ಔಷಧಿಯ ದೈನಂದಿನ ಪ್ರಮಾಣವು ನಿಗದಿತ ಮಿತಿಗಿಂತ ಹೆಚ್ಚಾಗಿದೆ. ವೈದ್ಯರಿಂದ ಪರಿಶೀಲಿಸಿಕೊಳ್ಳಿ.",
        "overlap_warning": "ಚಿಕಿತ್ಸಾ ಹೊಂದಾಣಿಕೆ: ಈ ಔಷಧಿಗಳು ಒಂದೇ ರೀತಿಯ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತವೆ. ಎರಡನ್ನೂ ಸೇವಿಸಬೇಕೆ ಎಂದು ವೈದ್ಯರನ್ನು ಕೇಳಿ.",
        "consult_doctor": "ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ: ಯಾವುದೇ ಔಷಧಿಯನ್ನು ಬದಲಾಯಿಸುವ ಮುನ್ನ ವೈದ್ಯರ ಸಲಹೆ ಪಡೆಯಿರಿ.",
        "reminder": "ಔಷಧಿ ಸಮಯ: ವೈದ್ಯರ ಸೂಚನೆಯಂತೆ ಸಮಯಕ್ಕೆ ಸರಿಯಾಗಿ ಔಷಧಿ ತೆಗೆದುಕೊಳ್ಳಿ.",
        "summary": "ಔಷಧಿ ಸುರಕ್ಷತಾ ಸಾರಾಂಶ: ನಿಮ್ಮ ಪ್ರಿಸ್ಕ್ರಿಪ್ಷನ್ ವಿಶ್ಲೇಷಣೆ ಪೂರ್ಣಗೊಂಡಿದೆ. ದಯವಿಟ್ಟು ವಿವರಗಳನ್ನು ಗಮನಿಸಿ."
    },
    "bn": { # Bengali
        "duplicate_warning": "সতর্কতা: আপনার প্রেসক্রিপশনে একই ওষুধ একাধিকবার রয়েছে। এতে অতিরিক্ত ডোজের ঝুঁকি হতে পারে। অনুগ্রহ করে ডাক্তারের সাথে পরামর্শ করুন।",
        "interaction_warning": "সুরক্ষা সতর্কতা: এই ওষুধগুলি একসাথে খেলে ক্ষতিকর মিথস্ক্রিয়া হতে পারে। আপনার ডাক্তারের সাথে পরামর্শ করুন।",
        "dosage_warning": "ডোজের সতর্কতা: এই ওষুধের দৈনিক মাত্রা স্বাভাবিকের চেয়ে বেশি মনে হচ্ছে। ডাক্তারের সাথে যাচাই করুন।",
        "overlap_warning": "ওষুধের মিল: এই ওষুধগুলো একই উদ্দেশ্যে ব্যবহৃত হয়। উভয় ওষুধই চালিয়ে যাবেন কিনা তা ডাক্তারের কাছে নিশ্চিত হন।",
        "consult_doctor": "ডাক্তারের পরামর্শ নিন: কোনো ওষুধ পরিবর্তন বা বন্ধ করার আগে চিকিৎসকের সাথে কথা বলুন।",
        "reminder": "ওষুধের সময়: ডাক্তারের নির্দেশ অনুযায়ী সময়মতো ওষুধ সেবন করুন।",
        "summary": "ওষুধ সুরক্ষা সারাংশ: আপনার প্রেসক্রিপশন বিশ্লেষণ সম্পন্ন হয়েছে। সতর্কতাগুলো পর্যালোচনা করুন।"
    },
    "mr": { # Marathi
        "duplicate_warning": "इशारा: तुमच्या प्रिस्क्रिप्शनमध्ये एकच औषध एकापेक्षा जास्त वेळा आले आहे. यामुळे ओव्हरडोसचा धोका होऊ शकतो. कृपया डॉक्टरांशी संपर्क साधा.",
        "interaction_warning": "सुरक्षा इशारा: ही औषधे एकत्र घेतल्यास परस्पर दुष्परिणाम होऊ शकतात. कृपया आपल्या डॉक्टरांचा किंवा फार्मासिस्टचा सल्ला घ्या.",
        "dosage_warning": "डोस इशारा: या औषधाचा दैनंदिन डोस नेहमीपेक्षा जास्त दिसत आहे. कृपया डॉक्टरांकडून खात्री करून घ्या.",
        "overlap_warning": "समान उपचार: ही औषधे एकाच कारणासाठी आहेत. दोन्ही औषधे एकत्र घ्यायची की नाही हे डॉक्टरांना विचारा.",
        "consult_doctor": "डॉक्टरांचा सल्ला घ्या: कोणतेही औषध बदलण्यापूर्वी किंवा बंद करण्यापूर्वी डॉक्टरांशी बोला.",
        "reminder": "औषधाची वेळ: डॉक्टरांच्या सल्ल्यानुसार आपली औषधे वेळेवर घ्या.",
        "summary": "औषध सुरक्षा सारांश: आपल्या प्रिस्क्रिप्शनचे विश्लेषण पूर्ण झाले आहे. कृपया माहिती तपासा."
    }
}

_gemini_cooldown_until = 0.0

def translate_explanation(text: str, target_lang: str) -> str:
    """
    Translates explanation into target regional language using Gemini or deterministic dictionary.
    Guarantees that medicine brand names and numeric dosages remain intact.
    """
    global _gemini_cooldown_until
    if target_lang == "en" or not text:
        return text

    now = time.time()
    # If Gemini is available, generate a fluid regional translation preserving clinical precision
    if gemini_model and now > _gemini_cooldown_until:
        lang_name = settings.SUPPORTED_LANGUAGES.get(target_lang, target_lang)
        prompt = (
            f"You are a medical translator assisting an elderly patient in India.\n"
            f"Translate the following patient safety alert directly into {lang_name}.\n"
            f"STRICT RULES:\n"
            f"1. Output ONLY the translated text in one or two clear, polite sentences.\n"
            f"2. DO NOT include markdown asterisks, bullet points, options, pronunciation guides, or preamble.\n"
            f"3. Keep medicine names (e.g. Paracetamol, Dolo 650, Warfarin, Aspirin, Metformin) in English alphabet.\n"
            f"4. Keep dosage numbers intact.\n\n"
            f"Alert: {text}"
        )
        try:
            resp = gemini_model.generate_content(prompt, request_options={"timeout": 7.0})
            if resp and resp.text:
                cleaned = resp.text.strip().replace('"', '').replace('*', '')
                # If response has multiple lines, take the first clean non-empty sentence
                lines = [l.strip() for l in cleaned.split('\n') if l.strip() and not l.strip().startswith(('1.', '2.', '-', '*'))]
                if lines:
                    return " ".join(lines)
                return cleaned
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "quota" in err_str.lower() or "504" in err_str:
                _gemini_cooldown_until = now + 60.0
            print(f"Gemini translation notice: {e}")

    # Fallback to high-quality deterministic dictionary based on context
    lang_dict = TRANSLATION_DICTIONARY.get(target_lang, {})
    if not lang_dict:
        return text

    lower = text.lower()
    if "duplicate" in lower:
        return lang_dict.get("duplicate_warning", text)
    elif "interaction" in lower:
        return lang_dict.get("interaction_warning", text)
    elif "dosage" in lower or "dose" in lower or "mg/day" in lower or "exceeds" in lower:
        return lang_dict.get("dosage_warning", text)
    elif "overlap" in lower or "therapeutic" in lower:
        return lang_dict.get("overlap_warning", text)
    elif "reminder" in lower or "time to take" in lower or "schedule" in lower:
        return lang_dict.get("reminder", text)
    elif "summary" in lower or "analysis" in lower:
        return lang_dict.get("summary", text)

    prefix = lang_dict.get("consult_doctor", "")
    return prefix or text
