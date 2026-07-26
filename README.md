# لعبة القنابل والجائزة

لعبة محلية بسيطة لشخصين بالتناوب، مبنية باستخدام Python وPygame. يضع كل
لاعب سرًا 3 قنابل وجائزة واحدة في لوحة 6×6. يفوز اللاعب الذي يعثر على جائزة
خصمه، ويخسر اللاعب الذي يكتشف ثلاث قنابل.

لا تحتاج اللعبة إلى اتصال بالإنترنت أثناء التشغيل، ولا تستخدم صورًا أو أصواتًا
أو قاعدة بيانات.

## المتطلبات

- Python 3.9 أو أحدث.
- Windows 10/11 في النسخة الحالية.
- يمكن تنزيل Python من <https://www.python.org/downloads/>. أثناء التثبيت على
  Windows فعّل خيار **Add Python to PATH**.

## التثبيت على Windows

افتح PowerShell أو Command Prompt داخل مجلد المشروع، ثم أنشئ بيئة افتراضية:

```bash
python -m venv venv
```

فعّل البيئة:

```bat
venv\Scripts\activate
```

ثبّت المكتبات:

```bash
pip install -r requirements.txt
```

يستخدم ملف المتطلبات Pygame الرسمي مع Python 3.9–3.13. ولأن Pygame الرسمي
لا يوفر حاليًا حزمة Windows جاهزة لـ Python 3.14، يختار الملف تلقائيًا
`pygame-ce` لهذا الإصدار الأحدث؛ وهو يوفر واجهة `pygame` نفسها التي يستخدمها
المشروع.

## تشغيل اللعبة

```bash
python main.py
```

استخدم الفأرة للأزرار واختيار المربعات. في شاشة الأسماء يمكن استخدام Tab
للتنقل، وBackspace للحذف، وEnter للمتابعة. يعيد Escape الشاشة الحالية إلى
القائمة الرئيسية.

## تشغيل نسخة الويب والهاتف

ثبّت أداة بناء الويب:

```bash
pip install -r requirements-web.txt
```

من المجلد الذي يحتوي مجلد المشروع شغّل:

```bash
python -m pygbag bomb_prize_game
```

ثم افتح `http://localhost:8000` في المتصفح. تدعم نسخة الويب لمس الأزرار
والمربعات، وعند لمس حقل اسم على الهاتف تظهر لوحة المفاتيح الخاصة بالنظام.

لإنشاء حزمة قابلة للرفع:

```bash
python -m pygbag --archive main.py
```

ستظهر الحزمة في `build/web.zip`.

## تشغيل الاختبارات

الاختبارات تتحقق من منطق اللعبة فقط ولا تفتح نافذة Pygame:

```bash
pytest
```

يمكن أيضًا التحقق من جميع ملفات Python:

```bash
python -m compileall .
```

## Raspberry Pi 3

الكود لا يعتمد على ميزات خاصة بـ Windows، ولذلك يمكن نقله لاحقًا إلى
Raspberry Pi OS. استخدم إصدار Raspberry Pi OS حديثًا مع Python 3، ثم نفّذ:

```bash
sudo apt update
sudo apt install python3-pygame python3-pytest
python3 main.py
```

أو أنشئ بيئة افتراضية وثبّت `requirements.txt` باستخدام `pip` إذا كانت حزم
Pygame المناسبة متاحة لإصدار Raspberry Pi OS المستخدم. دقة النافذة الحالية
900×700 ويمكن تغييرها مع بقية الثوابت في `game/settings.py`.

## تنظيم المشروع

```text
.
├── main.py
├── requirements.txt
├── README.md
├── game/
│   ├── board.py
│   ├── button.py
│   ├── game_manager.py
│   ├── player.py
│   └── settings.py
├── screens/
│   ├── common.py
│   ├── gameplay_screen.py
│   ├── main_menu.py
│   ├── names_screen.py
│   ├── pass_screen.py
│   ├── result_screen.py
│   └── setup_screen.py
└── tests/
    └── test_game_logic.py
```
