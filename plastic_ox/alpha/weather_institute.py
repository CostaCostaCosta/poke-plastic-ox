#!/usr/bin/env python3
"""Project Equilibrium: the Weather Institute / Route 119 story beat.

Writes the authored scripts to data/scripts/plastic_ox_weather_institute.inc
and places the event's objects and research-file signs on Route119 and both
Institute floors. Run from the repository root; --check reports drift without
writing. See plastic_ox/story/locations/route119.md for the design.

State machine (all persistent, no new key item):

  trial 1  TRAINER_PLASTIC_OX_WEATHER_DEVON  defeated  (FLAG_POX_TRAINER_WEATHER_DEVON)
  trial 2  TRAINER_PLASTIC_OX_WEATHER        defeated  (ordinary trainer flag, 0x4AF)
  done     FLAG_POX_STORY_WEATHER  set by the Director once both trials are won

FLAG_POX_STORY_WEATHER is the flag the Route 119 -> Fortree crossing, Fortree's
arrival script and Winona already require, so nothing downstream changes.
"""
from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INC = ROOT / "data/scripts/plastic_ox_weather_institute.inc"
WIDTH = 32          # characters per text-box line, matching build_story.speech
DEVON = "TRAINER_PLASTIC_OX_WEATHER_DEVON"
SILPH = "TRAINER_PLASTIC_OX_WEATHER"
DONE = "FLAG_POX_STORY_WEATHER"

out: list[str] = []


def boxes(paragraph: str) -> list[str]:
    """One paragraph per text box, Gen 3 style: the first two lines fill the
    box (\\n) and any further lines scroll it up (\\l), so a paragraph never
    leaves a lone orphan line on a box of its own."""
    lines = textwrap.wrap(paragraph, WIDTH)
    assert lines, paragraph
    return [lines[0] + "".join(("\\n" if i == 1 else "\\l") + line
                               for i, line in enumerate(lines[1:], 1))]


def string(label: str, text: str) -> None:
    """'|' starts a new text box; each box holds two wrapped lines."""
    pages = [box for paragraph in text.split("|") for box in boxes(paragraph)]
    out.append(f'{label}::\n\t.string "' + "\\p".join(pages) + '$"\n')


def script(body: str) -> None:
    out.append(textwrap.dedent(body).strip("\n") + "\n")


# --------------------------------------------------------------------------
# Route 119 crossing: Silph research engineer.
# --------------------------------------------------------------------------
script("""
    Pox_WI_Engineer::
    	goto_if_unset FLAG_POX_TRIGGERS_ENABLED, Pox_End
    	lock
    	faceplayer
    	msgbox Pox_Text_WI_Engineer, MSGBOX_DEFAULT
    	release
    	end
    """)
string("Pox_Text_WI_Engineer",
       "Sorry! The crossing is temporarily closed.|"
       "We're running a joint research project with DEVON and the WEATHER INSTITUTE.|"
       "DEVON's sensors are reading this whole stretch of the gorge, and our model is "
       "checking itself against them live.|"
       "Our team inside needs a skilled POKéMON TRAINER for the final battle trials.|"
       "The INSTITUTE is back down the trail. Once we're finished, we'll reopen the crossing.")
# Shown by PoxRegion_route119_fortree_a when the crossing refuses passage.
string("Pox_Text_WI_CrossingClosed",
       "ENGINEER: Hold it! The crossing's closed while the trials run.|"
       "The team at the WEATHER INSTITUTE needs a TRAINER. It's back down the trail.")

# After completion the engineer is off the route and back inside on 1F.
script("""
    Pox_WI_EngineerInside::
    	lock
    	faceplayer
    	msgbox Pox_Text_WI_EngineerInside, MSGBOX_DEFAULT
    	release
    	end
    """)
string("Pox_Text_WI_EngineerInside",
       "The trials are finished, so I pulled our sensor line off the crossing myself.|"
       "FORTREE CITY is open. The instruments stay up, though. This gorge keeps giving us "
       "readings worth having.")

# --------------------------------------------------------------------------
# 1F: Institute Director.
# --------------------------------------------------------------------------
script(f"""
    Pox_WI_Director::
    	goto_if_unset FLAG_POX_TRIGGERS_ENABLED, Pox_End
    	lock
    	faceplayer
    	goto_if_set {DONE}, Pox_WI_Director_After
    	goto_if_not_defeated {DEVON}, Pox_WI_Director_Intro
    	goto_if_not_defeated {SILPH}, Pox_WI_Director_Halfway
    	msgbox Pox_Text_WI_DirectorConclude, MSGBOX_DEFAULT
    	setflag {DONE}
    	release
    	end

    Pox_WI_Director_Intro::
    	msgbox Pox_Text_WI_DirectorIntro, MSGBOX_DEFAULT
    	release
    	end

    Pox_WI_Director_Halfway::
    	msgbox Pox_Text_WI_DirectorHalfway, MSGBOX_DEFAULT
    	release
    	end

    Pox_WI_Director_After::
    	goto_if_set FLAG_POX_STORY_SPACE_CENTER, Pox_WI_Director_Mossdeep
    	msgbox Pox_Text_WI_DirectorAfter, MSGBOX_DEFAULT
    	release
    	end

    Pox_WI_Director_Mossdeep::
    	msgbox Pox_Text_WI_DirectorMossdeep, MSGBOX_DEFAULT
    	release
    	end
    """)
string("Pox_Text_WI_DirectorIntro",
       "Welcome to the WEATHER INSTITUTE. You've walked into PROJECT EQUILIBRIUM.|"
       "DEVON brought the instruments. SILPH brought the computers. We brought decades of "
       "weather observations.|"
       "Between the three of us, we thought we'd have some answers by now.|"
       "Mostly, we have better questions.|"
       "Our final battle trials are upstairs. DEVON's field researcher goes first.")
string("Pox_Text_WI_DirectorHalfway",
       "DEVON's readings are in. Good.|"
       "SILPH's researcher is upstairs, waiting to test the model against a second battle.")
string("Pox_Text_WI_DirectorConclude",
       "Excellent work! We've collected enough data to conclude today's experiments.|"
       "SILPH will keep analyzing the results at their head office in SAFFRON.|"
       "I'll let our engineers know they can reopen the crossing.|"
       "You should be able to reach FORTREE CITY now.")
string("Pox_Text_WI_DirectorAfter",
       "The habitat lines on our survey maps have moved twice this month.|"
       "Each time, the POKéMON along them turned up somewhere that suited them.|"
       "The world hasn't finished changing. It just keeps landing on its feet.|"
       "We record it. We don't explain it. Not yet.")
string("Pox_Text_WI_DirectorMossdeep",
       "MOSSDEEP ran our survey against the whole region. It held everywhere.|"
       "They confirmed it. I'd rather they hadn't.")

# --------------------------------------------------------------------------
# 2F: Devon field researcher, trial 1.
# --------------------------------------------------------------------------
script(f"""
    Pox_WI_Devon::
    	goto_if_unset FLAG_POX_TRIGGERS_ENABLED, Pox_End
    	goto_if_set {DONE}, Pox_WI_Devon_After
    	goto_if_unset FLAG_BADGE03_GET, Pox_NotReady
    	trainerbattle_single {DEVON}, Pox_Text_WI_DevonIntro, Pox_Text_WI_DevonDefeat, Pox_WI_Devon_Won
    	goto Pox_WI_Devon_Won
    Pox_WI_Devon_Won::
    	msgbox Pox_Text_WI_DevonPost, MSGBOX_DEFAULT
    	release
    	end

    Pox_WI_Devon_After::
    	lock
    	faceplayer
    	msgbox Pox_Text_WI_DevonAfter, MSGBOX_DEFAULT
    	release
    	end
    """)
string("Pox_Text_WI_DevonIntro",
       "I'm LINDEN, DEVON field research.|"
       "We need to measure how POKéMON influence atmospheric conditions during a real "
       "battle.|"
       "Don't hold back. Accurate results require realistic conditions!")
string("Pox_Text_WI_DevonDefeat",
       "Excellent! Those readings were even better than we expected.")
string("Pox_Text_WI_DevonPost",
       "POKéMON don't simply live in their environments. They actively shape them.|"
       "Understanding that relationship is an important part of our research.|"
       "SILPH's researcher runs the next trial. By the far window.")
string("Pox_Text_WI_DevonAfter",
       "When the world changed, we expected POKéMON populations to struggle.|"
       "Instead, many species found suitable habitats almost immediately.|"
       "POKéMON may be far more adaptable than we ever realized.")

# --------------------------------------------------------------------------
# 2F: Silph systems researcher, trial 2. Recurring character: VALE.
# --------------------------------------------------------------------------
script(f"""
    Pox_WI_Vale::
    	goto_if_unset FLAG_POX_TRIGGERS_ENABLED, Pox_End
    	goto_if_set {DONE}, Pox_WI_Vale_After
    	goto_if_not_defeated {DEVON}, Pox_WI_Vale_Wait
    	trainerbattle_single {SILPH}, Pox_Text_WI_ValeIntro, Pox_Text_WI_ValeDefeat, Pox_WI_Vale_Won
    	goto Pox_WI_Vale_Won
    Pox_WI_Vale_Won::
    	msgbox Pox_Text_WI_ValePost, MSGBOX_DEFAULT
    	goto Pox_WI_Vale_Scope

    @ VALE lends the SILPH SCOPE (identifies the POKéMON TOWER's ghosts; the
    @ battle engine checks the bag). A key item cannot be discarded, so the bag
    @ itself is the record; saves that finished the trials before this gift
    @ get it the next time they talk to VALE.
    Pox_WI_Vale_Scope::
    	checkitem ITEM_SILPH_SCOPE
    	goto_if_eq VAR_RESULT, TRUE, Pox_WI_Vale_ScopeHeld
    	msgbox Pox_Text_WI_ValeScope, MSGBOX_DEFAULT
    	giveitem ITEM_SILPH_SCOPE
    	msgbox Pox_Text_WI_ValeScopeAfter, MSGBOX_DEFAULT
    Pox_WI_Vale_ScopeHeld::
    	release
    	end

    Pox_WI_Vale_Wait::
    	lock
    	faceplayer
    	msgbox Pox_Text_WI_ValeWait, MSGBOX_DEFAULT
    	release
    	end

    Pox_WI_Vale_After::
    	lock
    	faceplayer
    	msgbox Pox_Text_WI_ValeAfter, MSGBOX_DEFAULT
    	goto Pox_WI_Vale_Scope
    """)
string("Pox_Text_WI_ValeWait",
       "VALE, SILPH CO. systems research.|"
       "My model needs DEVON's environmental readings first. LINDEN is running that trial.|"
       "Come back once LINDEN has the numbers.")
string("Pox_Text_WI_ValeIntro",
       "DEVON's experiment gave us the environmental measurements.|"
       "Now I'd like to test whether our model can predict the changes during another "
       "battle.|"
       "Let's see how well our calculations hold up.")
string("Pox_Text_WI_ValeDefeat",
       "Interesting. The results are remarkably consistent with our predictions.")
string("Pox_Text_WI_ValePost",
       "Our model predicted the atmospheric changes during that battle almost perfectly.|"
       "Perhaps the world is more predictable than we realized.|"
       "I'll forward these results to our head office in SAFFRON. The roads there are "
       "closed, but the data lines still run.|"
       "They're investigating something similar. The DIRECTOR will want to see you "
       "downstairs.")
string("Pox_Text_WI_ValeScope",
       "One more thing. SILPH lends these to its field teams: a SILPH SCOPE.|"
       "It separates a signal from the noise around it. Shapes, too.|"
       "The keepers at LAVENDER's POKéMON TOWER say some visitors up there can't be "
       "made out at all. If your road goes that way, take it with you.")
string("Pox_Text_WI_ValeScopeAfter",
       "Keep it in your bag. It works on its own once you're inside the tower.")
string("Pox_Text_WI_ValeAfter",
       "My colleagues at DEVON believe we're witnessing natural adaptation.|"
       "But adaptation takes time.|"
       "Some of the patterns we've observed were present almost immediately.|"
       "That's what interests me.")

# --------------------------------------------------------------------------
# Mossdeep Space Center: reveal-ladder step 11, built on the Institute's survey.
# The report scientist keeps the established label and flag; VALE is optional.
# --------------------------------------------------------------------------
SPACE = "FLAG_POX_STORY_SPACE_CENTER"
script(f"""
    Pox_SpaceReport::
    	goto_if_unset FLAG_POX_TRIGGERS_ENABLED, Pox_End
    	lock
    	faceplayer
    	goto_if_unset FLAG_BADGE06_GET, Pox_NotReady
    	goto_if_set {SPACE}, Pox_SC_Report_After
    	msgbox Pox_Text_SC_ReportSurvey, MSGBOX_DEFAULT
    	closemessage
    	turnobject VAR_LAST_TALKED, DIR_NORTH
    	delay 48
    	turnobject VAR_LAST_TALKED, DIR_SOUTH
    	delay 16
    	msgbox Pox_Text_SC_ReportSaffron, MSGBOX_DEFAULT
    	setflag {SPACE}
    	release
    	end

    Pox_SC_Report_After::
    	msgbox Pox_Text_SC_ReportAfter, MSGBOX_DEFAULT
    	release
    	end

    Pox_SC_Vale::
    	goto_if_unset FLAG_POX_TRIGGERS_ENABLED, Pox_End
    	lock
    	faceplayer
    	goto_if_set {SPACE}, Pox_SC_Vale_After
    	msgbox Pox_Text_SC_Vale, MSGBOX_DEFAULT
    	release
    	end

    Pox_SC_Vale_After::
    	msgbox Pox_Text_SC_ValeAfter, MSGBOX_DEFAULT
    	release
    	end
    """)
string("Pox_Text_SC_ReportSurvey",
       "The WEATHER INSTITUTE sent us their survey. Their habitat lines kept moving, "
       "and kept landing somewhere suitable.|"
       "We wanted to know if that held at a larger scale. It does.|"
       "The region is not arranged randomly. Habitats and strong TRAINERS have become "
       "easier to reach.|"
       "It looks like an environment arranged for training.")
string("Pox_Text_SC_ReportSaffron",
       "One more thing. The data lines into SAFFRON are carrying far more than anyone's "
       "results.|"
       "Transfer traffic is converging on SAFFRON, at SILPH CO. We cannot identify its "
       "source.")
string("Pox_Text_SC_ReportAfter",
       "The traffic into SAFFRON hasn't slowed. We log it every launch window.|"
       "The roads into the city should be open to you now.")
string("Pox_Text_SC_Vale",
       "VALE, SILPH CO. We met at the WEATHER INSTITUTE.|"
       "I brought our model here. It was most accurate where TRAINERS battle most often.|"
       "Up here, it's accurate almost everywhere.|"
       "The chief has the readings. They should come from the SPACE CENTER, not from me.")
string("Pox_Text_SC_ValeAfter",
       "I've sent everything to head office. The lines into SAFFRON are busier than they "
       "should be.|"
       "At the INSTITUTE I called that interesting. I'm not sure that's the word anymore.")

# --------------------------------------------------------------------------
# Optional research files. (map, label, tiles, title, body)
# --------------------------------------------------------------------------
FILES = [
    ("Route119_WeatherInstitute_2F", "001", [(5, 2), (6, 2), (7, 2)],
     "ATMOSPHERIC SURVEY",
     "Weather patterns across formerly disconnected regions show unexpected "
     "correlations.|"
     "A rain front over this gorge now tracks conditions over coasts that used to be "
     "a sea away.|"
     "Conventional atmospheric models cannot fully explain these observations."),
    ("Route119_WeatherInstitute_1F", "002", [(9, 2), (10, 2), (11, 2), (12, 2)],
     "HABITAT DISTRIBUTION",
     "Initial surveys predicted severe disruption to POKéMON populations.|"
     "Instead, most observed populations occupy stable, suitable habitats.|"
     "Stake line C shifted overnight on the 14th. Every species logged along it was "
     "found again, in suitable cover.|"
     "The speed of this adjustment remains unexplained."),
    ("Route119_WeatherInstitute_2F", "003", [(8, 3), (9, 3), (8, 4), (9, 4), (8, 5), (9, 5)],
     "SIGNAL INTERFERENCE",
     "Monitoring equipment detects brief electromagnetic signals during atmospheric "
     "disturbances.|"
     "SILPH engineers note that the pattern resembles data traffic more than "
     "lightning.|"
     "Further investigation is required."),
    ("Route119_WeatherInstitute_2F", "004", [(10, 2), (11, 2), (12, 2), (13, 2), (14, 2)],
     "PREDICTIVE MODELING",
     "SILPH's experimental model shows unexpected accuracy when predicting certain "
     "environmental changes.|"
     "Accuracy is highest where TRAINERS battle most often.|"
     "The mechanisms underlying these predictions remain poorly understood."),
    ("Route119_WeatherInstitute_1F", "005", [(13, 1), (14, 1)],
     "GEOLOGICAL OBSERVATIONS",
     "DEVON reports unusual energy signatures beneath several distant sites, among "
     "them the deep seafloor and the root of an old volcano.|"
     "No definitive relationship between these observations has been established."),
    ("Route119_WeatherInstitute_1F", "006", [(16, 4), (17, 4), (16, 5), (17, 5), (16, 6), (17, 6)],
     "EXTERNAL CORRESPONDENCE",
     "The MOSSDEEP SPACE CENTER has asked to run large-scale observations.|"
     "Copies of the current findings go to its scientific staff by courier, and to "
     "SILPH's head office by data line."),
    ("MossdeepCity_SpaceCenter_1F", "007", [(3, 1), (4, 1), (5, 1)],
     "REGIONAL SCALE",
     "Received from the WEATHER INSTITUTE: survey data and SILPH's model.|"
     "Run against orbital imagery, the model's accuracy holds across every observed "
     "region.|"
     "Recommendation: compare against network load at SAFFRON."),
]
for map_name, number, tiles, title, body in FILES:
    label = f"Pox_WI_File{number}"
    script(f"""
        {label}::
        	msgbox Pox_Text_WI_File{number}, MSGBOX_SIGN
        	end
        """)
    # Header box first, then the body; each body box is two wrapped lines.
    header = f"PROJECT EQUILIBRIUM\\nFILE {number}: {title}"
    assert len(f"FILE {number}: {title}") <= 36, title
    pages = [header]
    pages.extend(box for paragraph in body.split("|") for box in boxes(paragraph))
    out.append(f'Pox_Text_WI_File{number}::\n\t.string "' + "\\p".join(pages) + '$"\n')

INC_TEXT = ("@ Generated by plastic_ox/alpha/weather_institute.py. Edit the source there.\n\n"
            + "\n".join(out))


# --------------------------------------------------------------------------
# Map events.
# --------------------------------------------------------------------------
def obj(gfx, x, y, script_name, flag, facing="MOVEMENT_TYPE_FACE_DOWN"):
    return {"graphics_id": gfx, "x": x, "y": y, "elevation": 3,
            "movement_type": facing, "movement_range_x": 0, "movement_range_y": 0,
            "trainer_type": "TRAINER_TYPE_NONE", "trainer_sight_or_berry_tree_id": "0",
            "script": script_name, "flag": flag}


def place(data: dict, new_objs: list[dict], new_signs: list[dict]) -> dict:
    ours = {o["script"] for o in new_objs}
    data["object_events"] = [o for o in data["object_events"] if o["script"] not in ours]
    data["object_events"] += new_objs
    data["bg_events"] = [b for b in data["bg_events"]
                         if not b.get("script", "").startswith("Pox_WI_File")] + new_signs
    return data


def signs(map_name: str) -> list[dict]:
    return [{"type": "sign", "x": x, "y": y, "elevation": 0,
             "player_facing_dir": "BG_EVENT_PLAYER_FACING_ANY",
             "script": f"Pox_WI_File{number}"}
            for m, number, tiles, *_ in FILES if m == map_name for x, y in tiles]


maps: dict[str, dict] = {}


def load(name: str) -> dict:
    maps[name] = json.loads((ROOT / f"data/maps/{name}/map.json").read_text())
    return maps[name]


# Route 119: the engineer stands beside the crossing at (39,8) and leaves for
# good once the Director concludes the trials.
place(load("Route119"),
      [obj("OBJ_EVENT_GFX_WORKER_M", 38, 7, "Pox_WI_Engineer", DONE)], [])

# 1F: the Director by the centre desk; the engineer reappears indoors after the
# event (hidden by FLAG_TEMP_1 until FLAG_POX_STORY_WEATHER, see OnTransition).
place(load("Route119_WeatherInstitute_1F"),
      [obj("OBJ_EVENT_GFX_SCIENTIST_1", 10, 5, "Pox_WI_Director", "FLAG_POX_HIDE_STORY_NPCS"),
       obj("OBJ_EVENT_GFX_WORKER_M", 1, 11, "Pox_WI_EngineerInside", "FLAG_TEMP_1",
           "MOVEMENT_TYPE_FACE_RIGHT")],
      signs("Route119_WeatherInstitute_1F"))

# 2F: Vale reuses the old duty-scientist object; Bryony joins mid-floor.
second = load("Route119_WeatherInstitute_2F")
for o in second["object_events"]:
    if o["script"] in ("Pox_Weather", "Pox_WI_Vale"):
        o.update(graphics_id="OBJ_EVENT_GFX_SCIENTIST", x=18, y=6,
                 movement_type="MOVEMENT_TYPE_FACE_LEFT", movement_range_x=0,
                 movement_range_y=0, script="Pox_WI_Vale", flag="FLAG_POX_HIDE_STORY_NPCS")
        break
else:
    raise SystemExit("2F duty-scientist object not found")
place(second,
      [obj("OBJ_EVENT_GFX_DEVON_EMPLOYEE", 11, 6, "Pox_WI_Devon", "FLAG_POX_HIDE_STORY_NPCS")],
      signs("Route119_WeatherInstitute_2F"))

# Space Center 1F: VALE at the consoles, file 007 on the console row.
place(load("MossdeepCity_SpaceCenter_1F"),
      [obj("OBJ_EVENT_GFX_SCIENTIST", 4, 3, "Pox_SC_Vale", "FLAG_POX_HIDE_STORY_NPCS",
           "MOVEMENT_TYPE_FACE_UP")],
      signs("MossdeepCity_SpaceCenter_1F"))

FIRST_FLOOR_SCRIPTS = """\
Route119_WeatherInstitute_1F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Route119_WeatherInstitute_1F_OnTransition
	.byte 0

@ Project Equilibrium: the crossing engineer works indoors once the trials end.
Route119_WeatherInstitute_1F_OnTransition:
	goto_if_set FLAG_POX_STORY_WEATHER, Pox_End
	setflag FLAG_TEMP_1
	end
"""


def main() -> int:
    writes = {INC: INC_TEXT}
    for name, data in maps.items():
        writes[ROOT / f"data/maps/{name}/map.json"] = json.dumps(data, indent=2) + "\n"
    script_path = ROOT / "data/maps/Route119_WeatherInstitute_1F/scripts.inc"
    text = script_path.read_text()
    head, sep, rest = text.partition("Route119_WeatherInstitute_1F_EventScript_SetLittleBoyPos::")
    writes[script_path] = FIRST_FLOOR_SCRIPTS + "\n" + sep + rest
    stale = [str(p.relative_to(ROOT)) for p, t in writes.items()
             if not p.exists() or p.read_text() != t]
    if "--check" in sys.argv:
        for p in stale:
            print("stale:", p)
        return 1 if stale else 0
    for p, t in writes.items():
        p.write_text(t)
    print("wrote", ", ".join(stale) or "nothing (up to date)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
