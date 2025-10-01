import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
import random
import textwrap

# ---------------------
# Config
# ---------------------
START_CREDIBILITY = 10
MAX_TURNS = 50
WINDOW_TITLE = "Detective CLI -> GUI Prototype"

LOCATIONS = [
    "Victim's Apartment", "Back Alley", "Rooftop Garden",
    "Office", "Local Bar", "Park"
]

SUSPECT_NAMES = [
    "Avery Collins", "Jordan Blake", "Riley Park",
    "Morgan Hale", "Casey Lin"
]

MOTIVES = [
    "money", "revenge", "jealousy", "cover-up", "power"
]

CLUE_TYPES = [
    ("fingerprint", "links person to a location"),
    ("receipt", "shows a recent purchase"),
    ("text", "message mentioning the victim"),
    ("witness", "eye witness statement"),
    ("rope", "possible murder weapon"),
    ("photo", "visual evidence")
]

# ---------------------
# Core data classes
# ---------------------
class Clue:
    def __init__(self, id, type_name, desc, tags):
        self.id = id
        self.type_name = type_name
        self.desc = desc
        self.tags = set(tags)
        self.found = False

    def brief(self):
        return f"[{self.type_name}] {self.desc}"

class Suspect:
    def __init__(self, name, motive, alibi, tags):
        self.name = name
        self.motive = motive
        self.alibi = alibi
        self.tags = set(tags)
        self.interrogated = False

    def summary(self):
        return f"{self.name} -- motive: {self.motive}; alibi: {self.alibi}"

class Location:
    def __init__(self, name):
        self.name = name
        self.clues = []

# ---------------------
# Case generation
# ---------------------
def generate_case():
    locs = LOCATIONS[:]
    random.shuffle(locs)
    locations = {name: Location(name) for name in locs[:4]}

    suspects_list = random.sample(SUSPECT_NAMES, 4)
    culprit = random.choice(suspects_list)

    suspects = {}
    for name in suspects_list:
        motive = random.choice(MOTIVES)
        alibi = random.choice(list(locations.keys()))
        tags = [name.split()[0].lower(), motive]
        suspects[name] = Suspect(name, motive, alibi, tags)

    clue_pool = []
    clue_id = 1
    linking_tag = culprit.split()[0].lower()
    for tname, tdesc in random.sample(CLUE_TYPES, 3):
        c = Clue(clue_id, tname, f"{tdesc} related to {linking_tag}", [linking_tag, tname])
        clue_pool.append(c)
        clue_id += 1

    for _ in range(6):
        tname, tdesc = random.choice(CLUE_TYPES)
        tags = [random.choice(MOTIVES), tname]
        c = Clue(clue_id, tname, tdesc, tags)
        clue_pool.append(c)
        clue_id += 1

    loc_names = list(locations.keys())
    for c in clue_pool:
        chosen = random.choice(loc_names)
        locations[chosen].clues.append(c)

    return {
        "locations": locations,
        "suspects": suspects,
        "culprit": culprit,
        "linking_tag": linking_tag
    }

def generate_tutorial_case():
    locations = {
        "Victim's Apartment": Location("Victim's Apartment"),
        "Local Bar": Location("Local Bar"),
        "Office": Location("Office"),
        "Park": Location("Park")
    }
    suspects_list = ["Avery Collins", "Jordan Blake", "Riley Park", "Morgan Hale"]
    culprit = "Avery Collins"
    suspects = {}
    for name in suspects_list:
        motive = "jealousy" if "Avery" in name else random.choice(MOTIVES)
        alibi = "Local Bar" if name != "Avery Collins" else "Office"
        tags = [name.split()[0].lower(), motive]
        suspects[name] = Suspect(name, motive, alibi, tags)

    c1 = Clue(1, "photo", "a photo with a partial name 'Avery' on the back", ["avery", "photo"])
    c2 = Clue(2, "text", "a threatening text referencing the victim", ["avery", "text"])
    c3 = Clue(3, "receipt", "a bar receipt timestamped near time of crime", ["bar", "receipt"])
    locations["Victim's Apartment"].clues.append(c1)
    locations["Office"].clues.append(c2)
    locations["Local Bar"].clues.append(c3)

    return {
        "locations": locations,
        "suspects": suspects,
        "culprit": culprit,
        "linking_tag": "avery"
    }

# ---------------------
# Game controller and UI
# ---------------------
class DetectiveGameUI:
    def __init__(self, root):
        self.root = root
        root.title(WINDOW_TITLE)
        self.case_state = None

        # Top frame: controls and status
        top = tk.Frame(root)
        top.pack(fill="x", padx=8, pady=6)

        self.cred_label = tk.Label(top, text="Credibility: -")
        self.cred_label.pack(side="left", padx=(0,10))

        self.turn_label = tk.Label(top, text="Turns: -")
        self.turn_label.pack(side="left", padx=(0,10))

        start_btn = tk.Button(top, text="Start Case", command=self.start_case)
        start_btn.pack(side="right", padx=4)
        tut_btn = tk.Button(top, text="Tutorial", command=self.start_tutorial)
        tut_btn.pack(side="right", padx=4)

        # Left frame: locations
        left = tk.LabelFrame(root, text="Locations", padx=6, pady=6)
        left.pack(side="left", fill="y", padx=8, pady=6)

        self.location_buttons = {}
        for i in range(4):
            b = tk.Button(left, text=f"Location {i+1}", width=20, command=lambda name=None: None)
            b.pack(pady=4)
            self.location_buttons[f"loc{i}"] = b

        # Middle frame: actions and output
        mid = tk.Frame(root)
        mid.pack(side="left", fill="both", expand=True, padx=8, pady=6)

        actions = tk.LabelFrame(mid, text="Actions", padx=6, pady=6)
        actions.pack(fill="x")

        btn_examine = tk.Button(actions, text="Examine", command=self.examine)
        btn_examine.grid(row=0, column=0, padx=4, pady=4)
        btn_search = tk.Button(actions, text="Search / Collect", command=self.search_prompt)
        btn_search.grid(row=0, column=1, padx=4, pady=4)
        btn_interrogate = tk.Button(actions, text="Interrogate", command=self.interrogate_prompt)
        btn_interrogate.grid(row=0, column=2, padx=4, pady=4)
        btn_present = tk.Button(actions, text="Present Evidence", command=self.present_prompt)
        btn_present.grid(row=0, column=3, padx=4, pady=4)
        btn_accuse = tk.Button(actions, text="Accuse", command=self.accuse_prompt)
        btn_accuse.grid(row=0, column=4, padx=4, pady=4)
        btn_notebook = tk.Button(actions, text="Notebook", command=self.show_notebook)
        btn_notebook.grid(row=0, column=5, padx=4, pady=4)

        # Output area
        out_frame = tk.LabelFrame(mid, text="Investigative Log", padx=6, pady=6)
        out_frame.pack(fill="both", expand=True, pady=(8,0))
        self.log = scrolledtext.ScrolledText(out_frame, height=18, state="disabled", wrap="word")
        self.log.pack(fill="both", expand=True)

        # Right frame: suspects
        right = tk.LabelFrame(root, text="Suspects", padx=6, pady=6)
        right.pack(side="right", fill="y", padx=8, pady=6)
        self.suspect_listbox = tk.Listbox(right, width=36, height=12)
        self.suspect_listbox.pack(padx=4, pady=4)
        self.suspect_info = tk.Label(right, text="Select a suspect and click Interrogate or Present", wraplength=260, justify="left")
        self.suspect_info.pack(padx=4, pady=4)

        # Bind selection update
        self.suspect_listbox.bind("<<ListboxSelect>>", self.on_suspect_select)

        # initialize disabled state
        self.disable_game_ui()
        self.log_write("Welcome. Click Tutorial or Start Case to begin.")

    # ---------------------
    # UI helpers
    # ---------------------
    def log_write(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", textwrap.fill(text, 80) + "\n\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def enable_game_ui(self):
        for b in self.location_buttons.values():
            b.configure(state="normal")
        self.suspect_listbox.configure(state="normal")

    def disable_game_ui(self):
        for b in self.location_buttons.values():
            b.configure(state="disabled")
        self.suspect_listbox.configure(state="disabled")

    def update_status(self):
        cs = self.case_state
        self.cred_label.config(text=f"Credibility: {cs['credibility']}")
        self.turn_label.config(text=f"Turns: {cs['turns']}/{MAX_TURNS}")

    def refresh_locations(self):
        # show first 4 locations as buttons
        loc_names = list(self.case_state['locations'].keys())
        btns = list(self.location_buttons.values())
        for i in range(4):
            name = loc_names[i] if i < len(loc_names) else "N/A"
            btn = btns[i]
            btn.config(text=name, command=lambda n=name: self.move_to(n))
            # highlight current
            if name == self.case_state['current_location']:
                btn.config(relief="sunken")
            else:
                btn.config(relief="raised")

    def refresh_suspects(self):
        self.suspect_listbox.delete(0, "end")
        for s in self.case_state['suspects'].values():
            pres = self.case_state.get('presented', {}).get(s.name, "not presented")
            self.suspect_listbox.insert("end", f"{s.name} | alibi: {s.alibi} | {pres}")

    def current_location_obj(self):
        return self.case_state['locations'][self.case_state['current_location']]

    # ---------------------
    # Game lifecycle
    # ---------------------
    def start_case(self):
        case = generate_case()
        self.setup_case(case)
        self.log_write("New randomized case started.")
        self.log_write("Suspects:")
        for s in self.case_state['suspects'].values():
            self.log_write(f"- {s.summary()}")
        self.refresh_ui_after_change()

    def start_tutorial(self):
        case = generate_tutorial_case()
        self.setup_case(case)
        self.log_write("Tutorial case loaded. Click Examine to begin the guided walkthrough.")
        self.case_state['tutorial_step'] = 1
        self.refresh_ui_after_change()

    def setup_case(self, case):
        self.case_state = {
            "locations": case['locations'],
            "suspects": case['suspects'],
            "culprit": case['culprit'],
            "linking_tag": case['linking_tag'],
            "current_location": list(case['locations'].keys())[0],
            "credibility": START_CREDIBILITY,
            "turns": 0,
            "found_clues": [],
            "presented": {}
        }
        self.enable_game_ui()
        self.refresh_ui_after_change()

    # ---------------------
    # Action handlers
    # ---------------------
    def move_to(self, loc_name):
        if self.case_state is None:
            return
        if loc_name not in self.case_state['locations']:
            messagebox.showinfo("Move", "Unknown location.")
            return
        self.case_state['current_location'] = loc_name
        self.apply_credibility(1)
        self.log_write(f"You move to {loc_name}.")
        self.refresh_ui_after_change()

    def examine(self):
        if self.case_state is None:
            return
        loc = self.current_location_obj()
        if not loc.clues:
            self.log_write("You see nothing of obvious interest.")
        else:
            self.log_write("Visible items and clues:")
            for c in loc.clues:
                self.log_write(f"  id {c.id}: {c.brief()}")
        # tutorial guidance
        if self.case_state.get('tutorial_step') == 1:
            self.log_write("Tutorial hint: click Search / Collect to collect clue id 1.")
            self.case_state['tutorial_step'] = 2

    def search_prompt(self):
        if self.case_state is None:
            return
        loc = self.current_location_obj()
        if not loc.clues:
            messagebox.showinfo("Search", "No clues here to collect.")
            return
        ids = [str(c.id) for c in loc.clues]
        default = ids[0]
        val = simpledialog.askstring("Search", f"Enter clue id to collect (visible: {', '.join(ids)})", initialvalue=default)
        if val is None:
            return
        try:
            cid = int(val.strip())
        except Exception:
            messagebox.showerror("Search", "Clue id must be a number.")
            return
        found = None
        for c in loc.clues:
            if c.id == cid:
                found = c
                break
        if not found:
            messagebox.showinfo("Search", "No such clue here.")
            return
        if found.found:
            messagebox.showinfo("Search", "You already collected that clue.")
            return
        found.found = True
        self.case_state['found_clues'].append(found)
        loc.clues.remove(found)
        self.apply_credibility(1)
        self.log_write("You collected the clue: " + found.brief())
        # tutorial guidance
        if self.case_state.get('tutorial_step') == 2:
            self.log_write("Tutorial hint: open Notebook to review the clue and suspect list.")
            self.case_state['tutorial_step'] = 3
        self.refresh_ui_after_change()

    def interrogate_prompt(self):
        if self.case_state is None:
            return
        sel = self.get_selected_suspect_name()
        if sel is None:
            messagebox.showinfo("Interrogate", "Select a suspect from the list first.")
            return
        suspect = self.case_state['suspects'][sel]
        suspect.interrogated = True
        self.apply_credibility(1)
        # reveal a lead if matching tags exist in uncollected clues
        reveal = False
        for locname, loc in self.case_state['locations'].items():
            for c in loc.clues:
                if suspect.tags & c.tags:
                    self.log_write(f"During questioning you learn of a lead at: {locname}")
                    reveal = True
                    break
            if reveal:
                break
        if not reveal:
            self.log_write(f"The suspect maintains their alibi: {suspect.alibi}")
        # tutorial guidance
        if self.case_state.get('tutorial_step') == 3:
            self.log_write("Tutorial hint: follow the lead to Local Bar by clicking its location button, then Search to collect a linking clue.")
            self.case_state['tutorial_step'] = 4
        self.refresh_ui_after_change()

    def present_prompt(self):
        if self.case_state is None:
            return
        sel = self.get_selected_suspect_name()
        if sel is None:
            messagebox.showinfo("Present", "Select a suspect from the list first.")
            return
        self.apply_credibility(1)
        self.present_evidence(sel)
        # tutorial guidance
        if self.case_state.get('tutorial_step') == 4:
            self.log_write("Tutorial hint: if evidence is strong, use Accuse to close the case.")
            self.case_state['tutorial_step'] = 5
        self.refresh_ui_after_change()

    def accuse_prompt(self):
        if self.case_state is None:
            return
        sel = self.get_selected_suspect_name()
        if sel is None:
            messagebox.showinfo("Accuse", "Select a suspect from the list first.")
            return
        self.apply_credibility(0)  # accusation is evaluated without extra automatic deduction
        correct = self.check_win(sel)
        if correct:
            messagebox.showinfo("Case Closed", "You accused correctly and provided strong evidence. You win.")
            self.disable_game_ui()
        else:
            if self.case_state['credibility'] <= 0:
                messagebox.showinfo("Game Over", f"Your credibility hit zero. The real culprit was: {self.case_state['culprit']}")
                self.disable_game_ui()
            else:
                messagebox.showinfo("Accuse", "Accusation failed. Continue investigating if you have credibility left.")
        self.refresh_ui_after_change()

    def show_notebook(self):
        if self.case_state is None:
            return
        dlg = tk.Toplevel(self.root)
        dlg.title("Notebook")
        txt = scrolledtext.ScrolledText(dlg, width=80, height=20, wrap="word")
        txt.pack(fill="both", expand=True)
        txt.insert("end", "Collected clues:\n\n")
        if not self.case_state['found_clues']:
            txt.insert("end", "- none\n\n")
        else:
            for c in self.case_state['found_clues']:
                txt.insert("end", f"- id {c.id}: {c.brief()} | tags: {', '.join(c.tags)}\n")
            txt.insert("end", "\n")
        txt.insert("end", "Suspect summaries:\n\n")
        for s in self.case_state['suspects'].values():
            pres = self.case_state.get('presented', {}).get(s.name, "not presented")
            txt.insert("end", f"- {s.name} | alibi: {s.alibi} | presented: {pres}\n")
        txt.configure(state="disabled")

    # ---------------------
    # Core logic helpers
    # ---------------------
    def apply_credibility(self, cost=1):
        if cost > 0:
            self.case_state['credibility'] -= cost
        self.case_state['turns'] += 1
        if self.case_state['credibility'] <= 0:
            self.log_write("Your credibility has reached zero. You have been removed from the case. GAME OVER.")
            self.log_write(f"The real culprit was: {self.case_state['culprit']}")
            self.disable_game_ui()
        if self.case_state['turns'] >= MAX_TURNS:
            self.log_write("You ran out of allowed turns. GAME OVER.")
            self.log_write(f"The real culprit was: {self.case_state['culprit']}")
            self.disable_game_ui()

    def get_selected_suspect_name(self):
        sel = self.suspect_listbox.curselection()
        if not sel:
            return None
        line = self.suspect_listbox.get(sel[0])
        # name is before ' |'
        name = line.split(" |")[0].strip()
        return name

    def on_suspect_select(self, event=None):
        name = self.get_selected_suspect_name()
        if name is None:
            self.suspect_info.config(text="Select a suspect and click Interrogate or Present")
            return
        s = self.case_state['suspects'][name]
        info = f"{s.name}\nMotive: {s.motive}\nAlibi: {s.alibi}\nInterrogated: {'Yes' if s.interrogated else 'No'}"
        self.suspect_info.config(text=info)

    def present_evidence(self, suspect_name):
        suspect = self.case_state['suspects'].get(suspect_name)
        if not suspect:
            self.log_write("No such suspect.")
            return
        found = self.case_state['found_clues']
        score = 0
        for c in found:
            if len(suspect.tags & c.tags) > 0:
                score += 1
        if score >= 2:
            self.log_write(f"You present a convincing chain of evidence linking {suspect.name} to the crime. Credibility +2.")
            self.case_state['credibility'] += 2
            self.case_state['presented'][suspect.name] = "strong"
        elif score == 1:
            self.log_write(f"Your evidence is suggestive but circumstantial. Credibility unchanged.")
            self.case_state['presented'][suspect.name] = "weak"
        else:
            self.log_write("No clear evidence links this suspect to the crime. You lose 2 credibility for a weak presentation.")
            self.case_state['credibility'] -= 2
            self.case_state['presented'][suspect.name] = "none"

    def check_win(self, accused_name):
        culprit = self.case_state['culprit']
        if accused_name == culprit:
            strong = 0
            for c in self.case_state['found_clues']:
                if self.case_state['linking_tag'] in c.tags:
                    strong += 1
            if strong >= 2:
                self.log_write("You accused the culprit and provided strong evidence. Case closed. You win.")
                return True
            else:
                self.log_write("You accused the right person but lacked supporting evidence. The case is dismissed for lack of proof.")
                return False
        else:
            self.log_write("You accused the wrong person. Public trust plummets. You lose 5 credibility.")
            self.case_state['credibility'] -= 5
            return False

    # ---------------------
    # UI refresh wrapper
    # ---------------------
    def refresh_ui_after_change(self):
        if self.case_state is None:
            return
        self.update_status()
        self.refresh_locations()
        self.refresh_suspects()

# ---------------------
# Entrypoint
# ---------------------
if __name__ == "__main__":
    random.seed()
    root = tk.Tk()
    app = DetectiveGameUI(root)
    root.mainloop()
