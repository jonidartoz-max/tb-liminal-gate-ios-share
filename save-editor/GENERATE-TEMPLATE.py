# -*- coding: utf-8 -*-
"""Generate TEMPLATE-bootstrap-state.json dari save yang JELAS-JELAS jalan.

Template = satu akun bersih (4 char tutorial-complete) dalam bentuk FILE SAVE
lengkap (bukan cuma userdata), ditulis dgn .0 utk double, dan lolos VALIDASI
boot server. Jangan karang manual — generate dari sini.
"""
import json, sys, tempfile, subprocess
from pathlib import Path

S = Path(r'D:\Ai Agent\Terra Battle - Liminal Gate\TB-SHARE - Liminal Gate\save-editor')
LIVE = Path(r'D:\Ai Agent\temp\st_now.json')

live = json.loads(LIVE.read_text(encoding='utf-8'))

# ambil chrdata 4-char yg sudah terbukti jalan (pilih akun editor lama)
src_acc = live['accounts']['5C34785D7E6CEAFC36D4DE51363D66DF']
src_ud = src_acc['userdata']
print('sumber chrdata: 5C34785D (4 char) [3, 25, 64, 63]')

AID = 'migrated-template'
acc = {
    'userdata': {
        'chrdata': json.loads(json.dumps(src_ud['chrdata'])),
        'teamMembers': list(src_ud['teamMembers']) if len(src_ud.get('teamMembers', [])) == 90 else None,
        'teamMembers_VS': list(src_ud.get('teamMembers_VS', [0]*18)),
        'teamBuddies_VS': list(src_ud.get('teamBuddies_VS', [0]*18)),
        'itemList': list(src_ud.get('itemList', [0]*181)),
        'summonList': list(src_ud.get('summonList', [0]*16)),
        'progressCode': 16777345, 'coins': 218, 'freeEnergy': 50,
        'lastupdate': 1.0, 'lastUpdate': 0.0,
        'refillStartTime': 0.0, 'metalZoneUnlockTime': 9999999999.0,
        'multipleFlags': {}, 'questClearDate': {},
        'worldMapNo': 0, 'summonId': 1, 'teamNo': 1, 'teamNo_VS': 1,
        'countryId': 0, 'countryCode': '', 'bonusStamina': 0,
        'loginDays': 1, 'consecutiveLoginDays': 1,
        'birthyear': 0, 'birthmonth': 0, 'changeUsernameDate': 0.0,
        'achivementFlags': [], 'achivementReadFlags': [],
    },
    'tutorial_phase': 'free_roam',
    'tutorial_requests': {}, 'initial_userdata_served': True,
    'tutorial_starter_character_id': 1,
    'active_generic_story': None, 'active_hunt': None,
    'active_hunt_ticket_spent': None, 'active_world_map_special': None,
    'claimed_achievements': [], 'achievement_requests': {},
    'messages': {}, 'chapter_milestones_issued': [], 'message_requests': {},
    'migration_grants': {}, 'username': 'Player',
}
if acc['userdata']['teamMembers'] is None:
    raise SystemExit('sumber teamMembers rusak, batal')

# chapter/section dari progressCode
pc = acc['userdata']['progressCode']
acc['userdata']['chapter'] = max(1, (pc >> 6) & 0x3FF)
acc['userdata']['section'] = pc & 0x3F
v = {'coins': acc['userdata']['coins'], 'freeEnergy': acc['userdata']['freeEnergy'],
     'energy': 0, 'energyAndApp': 0, 'energyAppStore': 0, 'energyGooglePlay': 0}
acc['userdata']['valuables'] = v

tpl = {'active_account_id': AID, 'accounts': {AID: acc},
       'tokens': {}, 'client_hosts': {}, 'account_aliases': {}}

(S / 'TEMPLATE-bootstrap-state.json').write_text(
    json.dumps(tpl, ensure_ascii=False, indent=1), encoding='utf-8')
print('ditulis TEMPLATE-bootstrap-state.json (sumber otomatis, bukan karangan)')
