#!/bin/bash
pkill -f "liminal_gate.bootstrap_server" 2>/dev/null
sleep 2
cd /root/project-liminal-gate
exec .venv/bin/python -m liminal_gate.bootstrap_server   --profile /root/project-liminal-gate/profiles/legacy-client-bootstrap.json   --state-file /root/project-liminal-gate/user-data/bootstrap-state.json   --host 0.0.0.0 --port 25686   --event-log /root/project-liminal-gate/user-data/events.jsonl   --resource-root /root/liminal-gate/local-input/resources/data_u2017   --resource-manifest /root/project-liminal-gate/user-data/resources.json   --public-data-root /root/project-liminal-gate/user-data/public_data   --core-story --pacts --hunting --daily-quests --secondary-worlds --jobs --rebirth --status-items --companion-draw --companion-sale --companion-strengthen --companion-evolution --trading-post --drop-eligibility --achievements --summon-skills
