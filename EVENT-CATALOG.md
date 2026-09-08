# Event Catalog — Special Quest / Tower / Eidolon / Strikes Back (optional, RECOMMENDED)

The server can advertise and run the game's event content: **Special Quest** (dragon
descents + collaboration archives), **Tower**, **Eidolon**, and full advertisement of
**Strikes Back / Counter Descent**. Without the files below the server still runs fine —
those menu lists just stay empty (base story, hunting, daily quests, Metal Zone, and all
other modes are unaffected).

## Why these files are not bundled

They are derived from YOUR OWN copy of the Android APK (the game's BattleData + character
master data). The share ships no game data — only code — so each operator generates them
once locally. The folder `user-data/` contains a pre-generated set from the APK
`terrabattle-server terrabattle-108.181.4.225.apk`; if you use that same APK you can skip
generation and use them as-is.

## Files involved

    user-data/battledata.json             (stage metadata: stamina/coins per section)
    user-data/character-catalog.json      (character rarities, used by pact draws)
    user-data/event-catalog.json          (the event stages themselves)
    user-data/companion-equipment.json    (companion equip restrictions; REQUIRED for equipping companions)

START-SERVER-WINDOWS.bat already passes the two catalog flags. If a file is missing or
corrupt, the server prints a `[boot] WARNING` and starts anyway (with those lists empty) —
it never refuses to boot over them.

## Quick path (same APK)

1. Keep `event-catalog.json` + `character-catalog.json` inside `user-data/`.
2. Double-click `START-SERVER-WINDOWS.bat` — done.
3. In-game content unlocks by story progress, exactly like the original game:
   Special/Bahamut from ch2, Tower + Eidolon at ch4, Strikes Back from ch6,
   more specials at ch10/13/15/20/30/31/32.

## Regenerating from a different APK

    runtime\python.exe -m liminal_gate.battledata_importer --apk <your.apk> --dummy-dll-dir <Il2CppDumper\DummyDll> --output user-data\battledata.json
    runtime\python.exe -m liminal_gate.character_catalog_importer --apk <your.apk> --dummy-dll-dir <Il2CppDumper\DummyDll> --output user-data\character-catalog.json
    runtime\python.exe -m liminal_gate.event_catalog_generator --battledata user-data\battledata.json --character-catalog user-data\character-catalog.json --output user-data\event-catalog.json --force

`TypeTreeGeneratorAPI` is required for the importers:

    runtime\python.exe -m pip install TypeTreeGeneratorAPI

(DummyDll comes from running Il2CppDumper once on that APK's libil2cpp.so +
global-metadata.dat.)
