import random
import time

from casino_effects import GameState, MATCH_MULTIPLIERS, PROJECT_GOAL, apply_spin
from whack import whack

REVEAL_DELAY = 0.6
SPIN_COOLDOWN = 3


def build_slots(words: list[str]) -> tuple[list[str], str]:
    """Shuffle the returned list and use its length to determine the match.

    Reuse available symbols for unusually short lists; the length still
    determines the reward tier, so a one-word list cannot earn a jackpot.
    """
    if not words:
        raise ValueError("A spin needs at least one word.")
    shuffled = words.copy()
    random.shuffle(shuffled)
    unique = list(dict.fromkeys(shuffled))
    first = unique[0]
    second = unique[1] if len(unique) > 1 else first

    if len(words) > 90:
        return [first, first, first], "jackpot"
    if len(words) > 70:
        if random.choice([True, False]):
            return [first, first, second], "adjacent_pair"
        return [second, first, first], "adjacent_pair"
    if len(words) > 50:
        return [first, second, first], "separated_pair"

    return [unique[index % len(unique)] for index in range(3)], "standard"


def reveal_slots(symbols: list[str]):
    visible = ["...", "...", "..."]
    print("\n[ ... ] | [ ... ] | [ ... ]", flush=True)
    for index, word in enumerate(symbols):
        time.sleep(REVEAL_DELAY)
        visible[index] = word
        print(" | ".join(f"[ {symbol} ]" for symbol in visible), flush=True)


def show_status(state: GameState):
    print(f"\nProject: {state.progress}% / {PROJECT_GOAL}% | Sleep: {state.sleep_hours}h")
    print(f"Free spins: {state.free_spins} | Focus: {state.focus} | Shields: {state.shields}")


def main():
    state = GameState()
    print("Welcome to WHACK Casino! You start with 8 hours of sleep.")
    print("Finish your project (100%) before your sleep runs out.")
    print("List length: 1-50 normal | 51-70 separated pair | 71-90 adjacent pair | 91-100 jackpot")
    print("Focus doubles your next spin's progress; shields block one harmful word each.")
    print("Free spins are used first. Sleep caps at 8h; free spins at 5; focus at 3; shields at 1.")

    while state.sleep_hours > 0 and state.progress < PROJECT_GOAL:
        show_status(state)
        cost = "FREE" if state.free_spins else "1h of sleep"
        choice = input(f"[Enter/s] Spin for {cost} | [q] Quit: ").strip().lower()

        if choice == "q":
            print(f"You leave with {state.progress}% of your project and {state.sleep_hours}h of sleep.")
            return
        if choice not in ("", "s", "spin"):
            print("Press Enter or type 's' to spin, or 'q' to quit.")
            continue

        words = whack()
        symbols, tier = build_slots(words)
        if state.free_spins:
            state.free_spins -= 1
        else:
            state.sleep_hours -= 1

        reveal_slots(symbols)
        print(f"{len(words)} words -> {tier.replace('_', ' ').upper()} ({MATCH_MULTIPLIERS[tier]:g}x progress)")
        for message in apply_spin(state, symbols, tier):
            print(message)

        if state.sleep_hours > 0 and state.progress < PROJECT_GOAL:
            print(f"\nNext spin available in {SPIN_COOLDOWN} seconds...", flush=True)
            time.sleep(SPIN_COOLDOWN)

    show_status(state)
    if state.progress >= PROJECT_GOAL:
        print("\nProject complete! You made it to the demo. YOU WIN!")
    else:
        print("\nNo sleep left! Game over!")


if __name__ == "__main__":
    main()
