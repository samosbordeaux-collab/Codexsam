#!/usr/bin/env python3
"""SamWord - Jeu de lettres inspiré du scrabble, en français."""

from __future__ import annotations

import random
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

BOARD_SIZE = 15
RACK_SIZE = 7
CENTER = (7, 7)
MAX_CONSECUTIVE_PASSES = 6

LETTER_POINTS: Dict[str, int] = {
    "A": 1,
    "B": 3,
    "C": 3,
    "D": 2,
    "E": 1,
    "F": 4,
    "G": 2,
    "H": 4,
    "I": 1,
    "J": 8,
    "K": 10,
    "L": 1,
    "M": 2,
    "N": 1,
    "O": 1,
    "P": 3,
    "Q": 8,
    "R": 1,
    "S": 1,
    "T": 1,
    "U": 1,
    "V": 4,
    "W": 10,
    "X": 10,
    "Y": 10,
    "Z": 10,
    "?": 0,
}

# Distribution proche de la version francophone classique (ajustée pour SamWord)
TILE_DISTRIBUTION: Dict[str, int] = {
    "A": 9,
    "B": 2,
    "C": 2,
    "D": 3,
    "E": 15,
    "F": 2,
    "G": 2,
    "H": 2,
    "I": 8,
    "J": 1,
    "K": 1,
    "L": 5,
    "M": 3,
    "N": 6,
    "O": 6,
    "P": 2,
    "Q": 1,
    "R": 6,
    "S": 6,
    "T": 6,
    "U": 6,
    "V": 2,
    "W": 1,
    "X": 1,
    "Y": 1,
    "Z": 1,
    "?": 2,
}

WORD_MULTIPLIER_COORDS: Dict[Tuple[int, int], int] = {
    (0, 0): 3, (0, 7): 3, (0, 14): 3,
    (7, 0): 3, (7, 14): 3,
    (14, 0): 3, (14, 7): 3, (14, 14): 3,
    (1, 1): 2, (2, 2): 2, (3, 3): 2, (4, 4): 2,
    (10, 10): 2, (11, 11): 2, (12, 12): 2, (13, 13): 2,
    (1, 13): 2, (2, 12): 2, (3, 11): 2, (4, 10): 2,
    (10, 4): 2, (11, 3): 2, (12, 2): 2, (13, 1): 2,
    CENTER: 2,
}

LETTER_MULTIPLIER_COORDS: Dict[Tuple[int, int], int] = {
    (1, 5): 3, (1, 9): 3, (5, 1): 3, (5, 5): 3, (5, 9): 3, (5, 13): 3,
    (9, 1): 3, (9, 5): 3, (9, 9): 3, (9, 13): 3, (13, 5): 3, (13, 9): 3,
    (0, 3): 2, (0, 11): 2, (2, 6): 2, (2, 8): 2,
    (3, 0): 2, (3, 7): 2, (3, 14): 2,
    (6, 2): 2, (6, 6): 2, (6, 8): 2, (6, 12): 2,
    (7, 3): 2, (7, 11): 2,
    (8, 2): 2, (8, 6): 2, (8, 8): 2, (8, 12): 2,
    (11, 0): 2, (11, 7): 2, (11, 14): 2,
    (12, 6): 2, (12, 8): 2, (14, 3): 2, (14, 11): 2,
}


def normalize_word(word: str) -> str:
    word = unicodedata.normalize("NFD", word.strip().upper())
    letters = [ch for ch in word if unicodedata.category(ch) != "Mn"]
    return "".join(letters)


@dataclass
class MoveResult:
    success: bool
    message: str
    score: int = 0
    words_formed: List[str] = field(default_factory=list)


class TileBag:
    def __init__(self) -> None:
        self.tiles: List[str] = []
        for letter, count in TILE_DISTRIBUTION.items():
            self.tiles.extend([letter] * count)
        random.shuffle(self.tiles)

    def draw(self, count: int) -> List[str]:
        picked = self.tiles[:count]
        self.tiles = self.tiles[count:]
        return picked

    def add(self, tiles: Sequence[str]) -> None:
        self.tiles.extend(tiles)
        random.shuffle(self.tiles)

    def remaining(self) -> int:
        return len(self.tiles)


@dataclass
class Player:
    name: str
    rack: List[str] = field(default_factory=list)
    score: int = 0

    def rack_string(self) -> str:
        return " ".join(sorted(self.rack))


class SamWordGame:
    def __init__(self, players: Sequence[str], dictionary_path: str = "words_fr.txt") -> None:
        self.players: List[Player] = [Player(name=p.strip()) for p in players]
        self.board: List[List[Optional[Tuple[str, bool]]]] = [[None] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.bag = TileBag()
        self.turn_index = 0
        self.consecutive_passes = 0
        self.dictionary: Set[str] = self.load_dictionary(dictionary_path)

        for p in self.players:
            p.rack.extend(self.bag.draw(RACK_SIZE))

    @staticmethod
    def load_dictionary(path: str) -> Set[str]:
        full = Path(path)
        if not full.exists():
            raise FileNotFoundError(f"Dictionnaire introuvable: {full}")
        words = set()
        for line in full.read_text(encoding="utf-8").splitlines():
            w = normalize_word(line)
            if len(w) >= 2 and all(c.isalpha() for c in w):
                words.add(w)
        if not words:
            raise ValueError("Le dictionnaire est vide.")
        return words

    def current_player(self) -> Player:
        return self.players[self.turn_index]

    def advance_turn(self) -> None:
        self.turn_index = (self.turn_index + 1) % len(self.players)

    def is_first_move(self) -> bool:
        return all(cell is None for row in self.board for cell in row)

    def display_board(self) -> str:
        header = "    " + " ".join(f"{i:02}" for i in range(BOARD_SIZE))
        lines = [header]
        for r in range(BOARD_SIZE):
            row_cells = []
            for c in range(BOARD_SIZE):
                cell = self.board[r][c]
                if cell:
                    letter, is_blank = cell
                    row_cells.append(letter.lower() if is_blank else letter)
                elif (r, c) == CENTER:
                    row_cells.append("★")
                elif WORD_MULTIPLIER_COORDS.get((r, c)) == 3:
                    row_cells.append("M")
                elif WORD_MULTIPLIER_COORDS.get((r, c)) == 2:
                    row_cells.append("m")
                elif LETTER_MULTIPLIER_COORDS.get((r, c)) == 3:
                    row_cells.append("L")
                elif LETTER_MULTIPLIER_COORDS.get((r, c)) == 2:
                    row_cells.append("l")
                else:
                    row_cells.append(".")
            lines.append(f"{r:02} | " + " ".join(row_cells))
        return "\n".join(lines)

    def play_move(self, word: str, row: int, col: int, direction: str) -> MoveResult:
        direction = direction.upper()
        if direction not in {"H", "V"}:
            return MoveResult(False, "Direction invalide: utilisez H (horizontal) ou V (vertical).")

        normalized = normalize_word(word)
        if len(normalized) < 2 or not normalized.isalpha():
            return MoveResult(False, "Mot invalide. Entrez un mot français d'au moins 2 lettres.")

        dr, dc = (0, 1) if direction == "H" else (1, 0)
        positions = [(row + i * dr, col + i * dc) for i in range(len(normalized))]
        if any(not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE) for r, c in positions):
            return MoveResult(False, "Le mot sort du plateau.")

        player = self.current_player()
        rack_copy = player.rack.copy()
        placed_tiles: List[Tuple[int, int, str, bool]] = []
        touches_existing = False

        for (r, c), letter in zip(positions, normalized):
            existing = self.board[r][c]
            if existing:
                existing_letter, _ = existing
                if existing_letter != letter:
                    return MoveResult(False, f"Conflit sur la case ({r},{c}).")
                touches_existing = True
            else:
                if letter in rack_copy:
                    rack_copy.remove(letter)
                    is_blank = False
                elif "?" in rack_copy:
                    rack_copy.remove("?")
                    is_blank = True
                else:
                    return MoveResult(False, f"Lettre manquante dans le chevalet: {letter}.")
                placed_tiles.append((r, c, letter, is_blank))

        if not placed_tiles:
            return MoveResult(False, "Vous devez poser au moins une nouvelle lettre.")

        if self.is_first_move():
            if CENTER not in [(r, c) for r, c, _, _ in placed_tiles]:
                return MoveResult(False, "Le premier mot doit couvrir la case centrale ★.")
        elif not touches_existing and not self._touches_adjacent(placed_tiles):
            return MoveResult(False, "Le mot doit se connecter à un mot existant.")

        candidate_board = [row_data[:] for row_data in self.board]
        for r, c, letter, is_blank in placed_tiles:
            candidate_board[r][c] = (letter, is_blank)

        words = self._extract_words(candidate_board, positions, direction)
        invalid = [w for w in words if len(w) > 1 and w not in self.dictionary]
        if invalid:
            return MoveResult(False, f"Mot(s) absent(s) du dictionnaire: {', '.join(invalid)}")

        score = self._calculate_score(positions, placed_tiles, direction, candidate_board)
        if len(placed_tiles) == RACK_SIZE:
            score += 50

        self.board = candidate_board
        player.rack = rack_copy
        player.score += score
        player.rack.extend(self.bag.draw(RACK_SIZE - len(player.rack)))

        self.consecutive_passes = 0
        self.advance_turn()

        return MoveResult(True, "Coup validé.", score, sorted(set(words)))

    def _touches_adjacent(self, placed_tiles: Sequence[Tuple[int, int, str, bool]]) -> bool:
        for r, c, _, _ in placed_tiles:
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                rr, cc = r + dr, c + dc
                if 0 <= rr < BOARD_SIZE and 0 <= cc < BOARD_SIZE and self.board[rr][cc]:
                    return True
        return False

    def _extract_words(
        self,
        board: List[List[Optional[Tuple[str, bool]]]],
        main_positions: Sequence[Tuple[int, int]],
        direction: str,
    ) -> List[str]:
        words: List[str] = []

        def collect_from(r: int, c: int, dr: int, dc: int) -> str:
            while 0 <= r - dr < BOARD_SIZE and 0 <= c - dc < BOARD_SIZE and board[r - dr][c - dc]:
                r -= dr
                c -= dc
            chars = []
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c]:
                chars.append(board[r][c][0])
                r += dr
                c += dc
            return "".join(chars)

        dr, dc = (0, 1) if direction == "H" else (1, 0)
        perp_dr, perp_dc = (1, 0) if direction == "H" else (0, 1)

        main_word = collect_from(main_positions[0][0], main_positions[0][1], dr, dc)
        words.append(main_word)

        for r, c in main_positions:
            if self.board[r][c] is None:
                cross_word = collect_from(r, c, perp_dr, perp_dc)
                if len(cross_word) > 1:
                    words.append(cross_word)

        return words

    def _calculate_score(
        self,
        positions: Sequence[Tuple[int, int]],
        placed_tiles: Sequence[Tuple[int, int, str, bool]],
        direction: str,
        board: List[List[Optional[Tuple[str, bool]]]],
    ) -> int:
        placed_set = {(r, c): (letter, is_blank) for r, c, letter, is_blank in placed_tiles}

        def score_word(start_r: int, start_c: int, dr: int, dc: int) -> int:
            while 0 <= start_r - dr < BOARD_SIZE and 0 <= start_c - dc < BOARD_SIZE and board[start_r - dr][start_c - dc]:
                start_r -= dr
                start_c -= dc

            total = 0
            word_mult = 1
            r, c = start_r, start_c
            length = 0
            while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c]:
                letter, is_blank = board[r][c]
                base = 0 if is_blank else LETTER_POINTS[letter]
                if (r, c) in placed_set:
                    base *= LETTER_MULTIPLIER_COORDS.get((r, c), 1)
                    word_mult *= WORD_MULTIPLIER_COORDS.get((r, c), 1)
                total += base
                length += 1
                r += dr
                c += dc
            return total * word_mult if length > 1 else 0

        dr, dc = (0, 1) if direction == "H" else (1, 0)
        perp_dr, perp_dc = (1, 0) if direction == "H" else (0, 1)

        score = score_word(positions[0][0], positions[0][1], dr, dc)
        for r, c, _, _ in placed_tiles:
            cross = score_word(r, c, perp_dr, perp_dc)
            if cross:
                score += cross
        return score

    def exchange_tiles(self, letters: str) -> MoveResult:
        letters = normalize_word(letters)
        player = self.current_player()
        if self.bag.remaining() < len(letters):
            return MoveResult(False, "Pas assez de lettres dans le sac pour un échange.")

        rack_copy = player.rack.copy()
        for ch in letters:
            if ch in rack_copy:
                rack_copy.remove(ch)
            elif ch == "?" and "?" in rack_copy:
                rack_copy.remove("?")
            else:
                return MoveResult(False, f"Vous ne possédez pas la lettre: {ch}")

        removed = list(letters)
        player.rack = rack_copy
        player.rack.extend(self.bag.draw(len(removed)))
        self.bag.add(removed)

        self.consecutive_passes += 1
        self.advance_turn()
        return MoveResult(True, "Échange effectué.")

    def pass_turn(self) -> None:
        self.consecutive_passes += 1
        self.advance_turn()

    def is_game_over(self) -> bool:
        if self.consecutive_passes >= MAX_CONSECUTIVE_PASSES:
            return True
        if self.bag.remaining() == 0 and any(len(p.rack) == 0 for p in self.players):
            return True
        return False

    def apply_endgame_bonus(self) -> None:
        emptied = [p for p in self.players if len(p.rack) == 0]
        if not emptied:
            for p in self.players:
                p.score -= sum(LETTER_POINTS[ch] for ch in p.rack)
            return

        finisher = emptied[0]
        for p in self.players:
            if p is finisher:
                continue
            malus = sum(LETTER_POINTS[ch] for ch in p.rack)
            p.score -= malus
            finisher.score += malus

    def ranking(self) -> List[Player]:
        return sorted(self.players, key=lambda p: p.score, reverse=True)


def print_help() -> None:
    print(
        """
Commandes:
  JOUER <mot> <ligne> <colonne> <H|V>    Exemple: JOUER MAISON 7 4 H
  ECHANGER <lettres>                      Exemple: ECHANGER AE?
  PASSER
  PLATEAU
  CHEVALET
  SCORES
  AIDE
  QUITTER

Notes:
- Toutes les commandes et tous les mots sont traités en français.
- Les accents sont acceptés (é, à, ç...) puis normalisés automatiquement.
- Le joker '?' remplace n'importe quelle lettre et vaut 0 point.
        """.strip()
    )


def main() -> None:
    print("=== SamWord (jeu de lettres en français) ===")
    print("Entrez le nombre de joueurs (2 à 4).")

    while True:
        try:
            count = int(input("> ").strip())
            if 2 <= count <= 4:
                break
            print("Veuillez choisir entre 2 et 4 joueurs.")
        except ValueError:
            print("Entrez un nombre valide.")

    names = []
    for i in range(1, count + 1):
        while True:
            name = input(f"Nom du joueur {i}: ").strip()
            if name:
                names.append(name)
                break
            print("Le nom ne peut pas être vide.")

    game = SamWordGame(names)
    print_help()

    while not game.is_game_over():
        player = game.current_player()
        print("\n" + "=" * 64)
        print(game.display_board())
        print(f"\nTour de {player.name} | Score: {player.score} | Sac: {game.bag.remaining()} lettres")
        print(f"Chevalet: {player.rack_string()}")
        cmd = input("Commande > ").strip()
        if not cmd:
            continue

        parts = cmd.split()
        action = normalize_word(parts[0])

        if action == "AIDE":
            print_help()
        elif action == "PLATEAU":
            print(game.display_board())
        elif action == "CHEVALET":
            print(f"Chevalet: {player.rack_string()}")
        elif action == "SCORES":
            for p in game.players:
                print(f"- {p.name}: {p.score}")
        elif action == "PASSER":
            game.pass_turn()
            print("Tour passé.")
        elif action == "ECHANGER":
            if len(parts) != 2:
                print("Usage: ECHANGER <lettres>")
                continue
            result = game.exchange_tiles(parts[1])
            print(result.message)
        elif action == "JOUER":
            if len(parts) != 5:
                print("Usage: JOUER <mot> <ligne> <colonne> <H|V>")
                continue
            mot = parts[1]
            try:
                row = int(parts[2])
                col = int(parts[3])
            except ValueError:
                print("Ligne/colonne invalides.")
                continue
            result = game.play_move(mot, row, col, parts[4])
            if result.success:
                print(f"+{result.score} points | Mots: {', '.join(result.words_formed)}")
            else:
                print(f"Coup refusé: {result.message}")
        elif action == "QUITTER":
            print("Partie arrêtée.")
            return
        else:
            print("Commande inconnue. Tapez AIDE pour la liste.")

    print("\n=== Fin de partie ===")
    game.apply_endgame_bonus()
    for idx, p in enumerate(game.ranking(), start=1):
        print(f"{idx}. {p.name}: {p.score} points")


if __name__ == "__main__":
    main()
