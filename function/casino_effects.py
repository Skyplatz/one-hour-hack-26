"""Word effects and balance settings for WHACK Casino. Percentages are points."""

from dataclasses import dataclass

MAX_SLEEP = 8
PROJECT_GOAL = 100
MAX_FREE_SPINS = 5
MAX_BUFFS = 3
MAX_SHIELDS = 1
# Tuned for roughly 40% losses when playing until completion or zero sleep.
PROGRESS_MULTIPLIER = 0.76

# Multipliers boost positive project progress, never setbacks.
MATCH_MULTIPLIERS = {
    "standard": 1,
    "separated_pair": 1.25,
    "adjacent_pair": 1.5,
    "jackpot": 2,
}


@dataclass(frozen=True)
class WordEffect:
    description: str
    progress: int = 0
    sleep: int = 0
    free_spins: int = 0
    focus: int = 0
    shields: int = 0
    jackpot_refill: bool = False


# These are game effects, rather than claims about the named organisations.
WORD_EFFECTS = {
    "whack": WordEffect("Hackathon inspiration", progress=7),
    "hack": WordEffect("Build a useful shortcut", progress=6),
    "duck": WordEffect("A lucky duck grants a free spin", free_spins=1),
    "quack": WordEffect("Duck encouragement boosts your next spin", focus=1),
    "goose": WordEffect("A goose steals your work", progress=-5),
    "honk": WordEffect("A noisy interruption breaks your flow", progress=-2),
    "bug": WordEffect("A bug needs fixing", progress=-4),
    "feature": WordEffect("Finish a feature", progress=8),
    "warwick": WordEffect("Campus inspiration", progress=5),
    "oculus": WordEffect("Find a quiet place to focus", focus=1),
    "compsoc": WordEffect("A coding tip moves you forward", progress=6),
    "marshall": WordEffect("A mentor helps with the design", progress=5),
    "wace": WordEffect("A fresh perspective unlocks an idea", focus=1),
    "brevan": WordEffect("Plan your next steps", focus=1),
    "howard": WordEffect("A useful review catches future mistakes", shields=1),
    "capital": WordEffect("Extra resources buy a free spin", free_spins=1),
    "one": WordEffect("One more chance", free_spins=1),
    "bloomberg": WordEffect("Useful data improves the project", progress=6),
    "netcraft": WordEffect("A security review protects your work", shields=1),
    "incident": WordEffect("An incident interrupts development", progress=-6),
    "io": WordEffect("Wire up the input and output", progress=4),
    "pizza": WordEffect("Food restores an hour of energy", sleep=1),
    "coffee": WordEffect("Coffee restores an hour of energy", sleep=1, jackpot_refill=True),
    "sleep": WordEffect("A power nap restores two hours of energy", sleep=2, jackpot_refill=True),
    "deploy": WordEffect("Deploy a working build", progress=9),
    "merge": WordEffect("Merge a finished branch", progress=7),
    "conflict": WordEffect("A merge conflict needs untangling", progress=-4),
    "commit": WordEffect("Save a solid piece of work", progress=5),
    "push": WordEffect("Push your changes", progress=4),
    "prod": WordEffect("Your production check passes", progress=8),
    "segfault": WordEffect("A crash costs development time", progress=-7),
    "null": WordEffect("Missing data blocks a feature", progress=-3),
    "pointer": WordEffect("A helpful pointer solves a problem", progress=5),
    "stack": WordEffect("Set up your project stack", progress=5),
    "overflow": WordEffect("Too many tasks cause a setback", progress=-4),
    "semicolon": WordEffect("Fix that tiny syntax error", progress=3),
    "rubber": WordEffect("Rubber-duck debugging prevents a setback", shields=1),
    "demo": WordEffect("Get the demo working", progress=10),
    "pitch": WordEffect("Polish your project pitch", progress=7),
    "prize": WordEffect("Win a bonus spin", free_spins=1),
    "midnight": WordEffect("Time slips away", sleep=-1),
    "wifi": WordEffect("A stable connection speeds up the next spin", focus=1),
}


@dataclass
class GameState:
    sleep_hours: int = MAX_SLEEP
    progress: int = 0
    free_spins: int = 0
    focus: int = 0
    shields: int = 0


def apply_spin(state: GameState, symbols: list[str], tier: str) -> list[str]:
    """Resolve rewards before checking whether sleep has run out.

    Focus doubles positive progress on the next spin. A shield blocks one
    harmful symbol. Buffs earned this spin become available next spin.
    """
    messages = []
    focused = state.focus > 0
    if focused:
        state.focus -= 1
        messages.append("Focus used: double positive project progress!")

    positive_progress = 0
    setbacks = 0
    sleep_change = 0
    free_spins = 0
    new_focus = 0
    new_shields = 0

    for word in symbols:
        effect = WORD_EFFECTS[word]
        if (effect.progress < 0 or effect.sleep < 0) and state.shields > 0:
            state.shields -= 1
            messages.append(f"{word}: shield blocked the setback!")
            continue

        messages.append(f"{word}: {effect.description}.")
        positive_progress += max(0, effect.progress)
        setbacks += min(0, effect.progress)
        sleep_change += effect.sleep
        free_spins += effect.free_spins
        new_focus += effect.focus
        new_shields += effect.shields

    gain = round(positive_progress * PROGRESS_MULTIPLIER * MATCH_MULTIPLIERS[tier] * (2 if focused else 1))
    old_progress = state.progress
    state.progress = max(0, min(PROJECT_GOAL, state.progress + gain + setbacks))
    state.sleep_hours = max(0, min(MAX_SLEEP, state.sleep_hours + sleep_change))
    state.free_spins = min(MAX_FREE_SPINS, state.free_spins + free_spins)
    state.focus = min(MAX_BUFFS, state.focus + new_focus)
    state.shields = min(MAX_SHIELDS, state.shields + new_shields)

    if tier == "jackpot" and WORD_EFFECTS[symbols[0]].jackpot_refill:
        state.sleep_hours = MAX_SLEEP
        messages.append(f"Triple {symbols[0]}! Sleep fully restored to {MAX_SLEEP}h.")

    messages.append(f"Project change: {state.progress - old_progress:+d} percentage points.")
    return messages
