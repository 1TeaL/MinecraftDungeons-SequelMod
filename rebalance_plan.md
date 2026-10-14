# Sequel Mod - Enchantment Rebalance Plan

The master list of enchantments and decisions lives in `Enchantment_Rebalance.xlsx`
(fill the yellow Verdict / Your change columns, e.g. in Google Sheets).

Rebuild the sheet from game data with:

    python -c "$(cat tools/build_sheet.py)" tools/game_en.json enchant_dump.txt Enchantment_Rebalance.xlsx

(Store Python can't open files under AppData, hence the `-c "$(cat ...)"` form.)

Editable column:
- pak     - numbers are in the blueprint, editable with a .pak mod
- partial - only a minor value is in the blueprint; the core number is native
- native  - compiled into the exe, needs UE4SS (runtime) to change
