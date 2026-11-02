"""Area-specific replacements for donor import placeholder dialogue."""
import re
LINES = {
'EcruteakCity': ['The KIMONO dancers rehearse while the bells ring across town.', 'The BURNED TOWER still stands. We keep its history alive.', 'MORTY studies GHOST POKéMON. Bring a team that can face them.', 'The west gate leads toward the LEAGUE. The guard checks BADGES there.', 'Our old wooden houses have heard generations of POKéMON stories.', 'At dusk, the tower casts a long shadow across the rooftops.'],
'NationalPark': ['I come here to watch POKéMON move through the tall grass.', 'A quiet walk around the park helps my team unwind.'],
'LavenderTown': ['People come here to remember the POKéMON they loved.', 'Speak softly near the tower. Some visitors are grieving.'],
'SaffronCity': ['The busy streets make the DOJO feel wonderfully quiet.', 'Trainers come from far away to test themselves at the DOJO.'],
'CinnabarIsland': ['The sea is calm today, but this island was shaped by fire.', 'Our researchers study the traces left by ancient POKéMON.'],
'BlackthornCity': ['Dragon training takes patience. Power alone is not enough.', 'The mountain air makes every morning feel sharp and clear.'],
'Route2': ['The trees shelter small POKéMON. Watch the grass as you pass.', 'I always check my supplies before heading into the trees.'],
'Route3': ['Rocky ground can wear your team down. Rest when you can.', 'The mountain draws hikers and curious trainers alike.'],
'Route4': ['After a long cave walk, this open sky feels wonderful.', 'I stop here to let my POKéMON stretch after the tunnels.'],
'Route6': ['Travelers heading toward SAFFRON often stop here for a breather.', 'City noise fades quickly when you walk into the grass.'],
'Route12': ['Fishing takes patience. Watch your line, not the clock.', 'The water brings a cool breeze along this path.'],
'Route14': ['Bird POKéMON ride the breeze above this stretch of road.', 'The tall grass rustles even when the air is still.'],
'Route16': ['Check your bicycle before a long ride. Brakes matter!', 'Cyclists make this road look easy. I prefer walking.'],
'Route21': ['The waves hide as much life as the grass does.', 'Sea winds can change quickly. Keep the shore in sight.'],
'Route25': ['BILL studies how POKéMON are stored and transferred.', 'That little house attracts some very curious trainers.'],
'Route34': ['The DAY CARE gives busy trainers a helping hand.', 'GOLDENROD feels enormous after a quiet walk out here.'],
'Route35': ['The NATIONAL PARK is a welcome break from city crowds.', 'I like to walk here after shopping in GOLDENROD.'],
'Route38': ['The farms and open fields make this a peaceful place to train.', 'The grass here grows thick after the rain.'],
'Gate_AzaleaTown': ['ILEX FOREST is quiet. Please respect the trees and their POKéMON.', 'Pack supplies before heading into the forest.'],
'Gate_SaffronCity': ['Keep the doorway clear so travelers can pass safely.', 'SAFFRON draws visitors from every nearby road.'],
}
def replace(text, name):
    lines=next((v for k,v in LINES.items() if name.startswith(k)),None)
    if not lines: return text
    import textwrap
    i=0
    def sub(m):
        nonlocal i
        words=textwrap.wrap(lines[i%len(lines)],32);i+=1
        return '.string "'+'\\p'.join('\\n'.join(words[j:j+2]) for j in range(0,len(words),2))+'$"'
    return re.sub(r'\.string "Roads keep ending somewhere they\\ndidn\'t used to\.\$"',sub,text)
