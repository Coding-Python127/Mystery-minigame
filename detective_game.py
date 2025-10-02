import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
import random
import textwrap

# ---------------------
# Config
# ---------------------
START_CREDIBILITY = 10
MAX_TURNS = 50
WINDOW_TITLE = "The Deductionist: Case File"

LOCATIONS = [
    "Victim's Penthouse", "Industrial Dock", "Grand Hotel Lobby",
    "Office Tower", "Local Dive Bar", "City Park",
    "Security Office", "Rooftop Garden"
]

SUSPECT_NAMES = [
    "Avery Collins", "Jordan Blake", "Riley Park",
    "Morgan Hale", "Casey Lin", "Elias Vance"
]

MOTIVES = [
    "Financial", "Revenge", "Jealousy", "Political Cover-Up", "Power Struggle"
]

CLUE_TYPES = [
    ("Fingerprint", "links person to a location"),
    ("Receipt", "shows a recent purchase or expense"),
    ("Message", "a threatening or revealing text/email"),
    ("Witness", "eye witness statement placing someone at the scene"),
    ("Weapon Trace", "residue or tool mark"),
    ("Photo", "visual evidence or security footage snippet")
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
        # Tracks which Clue IDs have been used in a successful presentation against this suspect.
        self.presented_clues = set()

    def summary(self):
        return f"{self.name} | Motive: {self.motive} | Alibi: {self.alibi}"

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
    # Use 4 random locations
    locations = {name: Location(name) for name in locs[:4]}

    # Use 5 random suspects
    suspects_list = random.sample(SUSPECT_NAMES, 5)
    culprit_name = random.choice(suspects_list)

    suspects = {}
    for name in suspects_list:
        motive = random.choice(MOTIVES)
        alibi = random.choice(list(locations.keys()))
        tags = [name.split()[0].lower(), motive.lower().replace(' ', '-')]
        suspects[name] = Suspect(name, motive, alibi, tags)

    culprit = suspects[culprit_name]
    linking_tag = culprit.tags.intersection({t.split()[0].lower() for t in SUSPECT_NAMES}).pop()

    # Generate "strong" clues linked to the culprit (3-4 clues)
    clue_pool = []
    clue_id = 1
    
    num_culprit_clues = random.randint(3, 4)
    culprit_clues = random.sample(CLUE_TYPES, num_culprit_clues)
    
    for tname, tdesc in culprit_clues:
        c = Clue(clue_id, tname, f"{tdesc} clearly connected to {linking_tag}", {linking_tag, tname.lower()})
        clue_pool.append(c)
        clue_id += 1

    # Generate "filler" clues (4-6 clues)
    num_filler_clues = random.randint(4, 6)
    all_other_suspects = [s for name, s in suspects.items() if name != culprit_name]
    
    for _ in range(num_filler_clues):
        tname, tdesc = random.choice(CLUE_TYPES)
        # Link filler clues to other suspects or generic tags
        filler_tag = random.choice(all_other_suspects).tags.pop() if all_other_suspects and random.random() < 0.5 else random.choice(MOTIVES).lower().replace(' ', '-')
        tags = {filler_tag, tname.lower()}
        c = Clue(clue_id, tname, f"Generic {tdesc} related to {filler_tag}", tags)
        clue_pool.append(c)
        clue_id += 1

    # Distribute clues across locations
    loc_names = list(locations.keys())
    for c in clue_pool:
        chosen = random.choice(loc_names)
        locations[chosen].clues.append(c)

    return {
        "locations": locations,
        "suspects": suspects,
        "culprit": culprit_name,
        "linking_tag": linking_tag
    }

def generate_tutorial_case():
    locations = {
        "Victim's Penthouse": Location("Victim's Penthouse"),
        "Local Dive Bar": Location("Local Dive Bar"),
        "Office Tower": Location("Office Tower"),
        "Rooftop Garden": Location("Rooftop Garden")
    }
    suspects_list = ["Avery Collins", "Jordan Blake", "Riley Park", "Morgan Hale"]
    culprit = "Avery Collins"
    suspects = {}
    for name in suspects_list:
        motive = "Jealousy" if "Avery" in name else random.choice(MOTIVES)
        alibi = "Local Dive Bar" if name != "Avery Collins" else "Victim's Penthouse"
        tags = [name.split()[0].lower(), motive.lower()]
        suspects[name] = Suspect(name, motive, alibi, tags)

    # Clues linking to Avery
    c1 = Clue(1, "Photo", "A crumpled photo of the victim defaced with the name 'Avery' on the back", {"avery", "photo"})
    c2 = Clue(2, "Message", "A threatening text referencing a 'financial deal gone sour' sent by a number traced to the Office Tower.", {"avery", "message"})
    # Distraction clue
    c3 = Clue(3, "Receipt", "A late-night receipt from a convenience store for someone with an alibi.", {"distraction", "receipt"})
    # Strongest linking clue
    c4 = Clue(4, "Fingerprint", "A clear fingerprint match for Avery found on the murder weapon (a broken statue).", {"avery", "fingerprint"})


    locations["Victim's Penthouse"].clues.extend([c1, c4])
    locations["Office Tower"].clues.append(c2)
    locations["Rooftop Garden"].clues.append(c3)

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
        
        # Apply a basic style configuration
        self.bg_color = "#2c3e50" # Dark Blue/Grey
        self.fg_color = "#ecf0f1" # Light Grey
        self.accent_color = "#3498db" # Blue
        self.button_color = "#34495e" # Darker Grey

        self.root.configure(bg=self.bg_color)
        
        default_font = ("Consolas", 10)
        heading_font = ("Consolas", 12, "bold")

        # --- Top frame: controls and status ---
        top = tk.Frame(root, bg=self.bg_color)
        top.pack(fill="x", padx=10, pady=10)

        self.cred_label = tk.Label(top, text="Credibility: -", bg=self.bg_color, fg=self.fg_color, font=heading_font)
        self.cred_label.pack(side="left", padx=(0, 20))

        self.turn_label = tk.Label(top, text="Turns: -", bg=self.bg_color, fg=self.fg_color, font=heading_font)
        self.turn_label.pack(side="left", padx=(0, 20))

        # Buttons on the right
        btn_frame = tk.Frame(top, bg=self.bg_color)
        btn_frame.pack(side="right")
        
        start_btn = tk.Button(btn_frame, text="Start New Case", command=self.start_case, bg=self.accent_color, fg="white", font=default_font)
        start_btn.pack(side="right", padx=4)
        tut_btn = tk.Button(btn_frame, text="Tutorial Case", command=self.start_tutorial, bg=self.button_color, fg=self.fg_color, font=default_font)
        tut_btn.pack(side="right", padx=4)

        # --- Main content area ---
        main_content = tk.Frame(root, bg=self.bg_color)
        main_content.pack(fill="both", expand=True, padx=10, pady=5)

        # Left frame: locations
        left = tk.LabelFrame(main_content, text="Locations", padx=6, pady=6, bg=self.bg_color, fg=self.fg_color, font=heading_font)
        left.pack(side="left", fill="y", padx=(0, 10))

        self.location_buttons = {}
        for i in range(4):
            b = tk.Button(left, text=f"Location {i+1}", width=20, bg=self.button_color, fg=self.fg_color, font=default_font, activebackground=self.accent_color)
            b.pack(pady=4)
            self.location_buttons[f"loc{i}"] = b

        # Right frame: suspects
        right = tk.LabelFrame(main_content, text="Suspects", padx=6, pady=6, bg=self.bg_color, fg=self.fg_color, font=heading_font)
        right.pack(side="right", fill="y", padx=(10, 0))
        
        self.suspect_listbox = tk.Listbox(right, width=40, height=10, bg=self.button_color, fg=self.fg_color, selectbackground=self.accent_color, font=default_font)
        self.suspect_listbox.pack(padx=4, pady=4)
        
        self.suspect_info = tk.Label(right, text="Select a suspect for details.", wraplength=300, justify="left", bg=self.bg_color, fg=self.fg_color, font=default_font)
        self.suspect_info.pack(padx=4, pady=4)

        # Bind selection update
        self.suspect_listbox.bind("<<ListboxSelect>>", self.on_suspect_select)
        
        # Middle frame: actions and output
        mid = tk.Frame(main_content, bg=self.bg_color)
        mid.pack(side="left", fill="both", expand=True)

        actions = tk.LabelFrame(mid, text="Available Actions", padx=6, pady=6, bg=self.bg_color, fg=self.fg_color, font=heading_font)
        actions.pack(fill="x", pady=(0, 8))

        # Action Buttons Layout (using grid for uniform size)
        action_buttons = [
            ("Examine Scene (0 cost)", self.examine),
            ("Search/Collect (-1 cred)", self.search_prompt),
            ("Interrogate (-1 cred)", self.interrogate_prompt),
            ("Present Evidence (-1 cred)", self.present_prompt),
            ("Accuse (End Case)", self.accuse_prompt),
            ("Notebook (Clues/Info)", self.show_notebook)
        ]
        
        for i, (text, command) in enumerate(action_buttons):
            b = tk.Button(actions, text=text, command=command, bg=self.accent_color, fg="white", font=default_font, padx=5, pady=5)
            b.grid(row=0, column=i, padx=4, pady=4, sticky="ew")

        actions.grid_columnconfigure(5, weight=1) # Ensure Notebook stretches slightly

        # Output area
        out_frame = tk.LabelFrame(mid, text="Investigative Log", padx=6, pady=6, bg=self.bg_color, fg=self.fg_color, font=heading_font)
        out_frame.pack(fill="both", expand=True)
        self.log = scrolledtext.ScrolledText(out_frame, height=18, state="disabled", wrap="word", bg="#1b2c3a", fg="#d3d9df", font=default_font)
        self.log.pack(fill="both", expand=True)

        # initialize disabled state
        self.disable_game_ui()
        self.log_write("Welcome, Detective. The clock is ticking. Click Tutorial or Start New Case to begin your investigation.")

    # ---------------------
    # UI helpers
    # ---------------------
    def log_write(self, text, style='info'):
        self.log.configure(state="normal")
        
        tag_name = style
        if tag_name not in self.log.tag_names():
            if style == 'error':
                self.log.tag_config(tag_name, foreground="#e74c3c", font=("Consolas", 10, "bold"))
            elif style == 'win':
                self.log.tag_config(tag_name, foreground="#2ecc71", font=("Consolas", 10, "bold"))
            elif style == 'action':
                self.log.tag_config(tag_name, foreground="#f39c12", font=("Consolas", 10, "italic"))
            else: # info
                self.log.tag_config(tag_name, foreground="#ecf0f1")
        
        
        self.log.insert("end", textwrap.fill(text, 80) + "\n\n", tag_name)
        self.log.see("end")
        self.log.configure(state="disabled")

    def enable_game_ui(self):
        for b in self.location_buttons.values():
            b.configure(state="normal")
        # Other action buttons remain enabled/disabled via their initial setup, 
        # but the core location/suspect interaction must be enabled.
        self.suspect_listbox.configure(state="normal")

    def disable_game_ui(self):
        for b in self.location_buttons.values():
            b.configure(state="disabled")
        self.suspect_listbox.configure(state="disabled")

    def update_status(self):
        cs = self.case_state
        self.cred_label.config(text=f"Credibility: {max(0, cs['credibility'])}")
        self.turn_label.config(text=f"Turns: {cs['turns']}/{MAX_TURNS}")
        
        if cs['credibility'] <= 0 or cs['turns'] >= MAX_TURNS:
            self.disable_game_ui()
            # If the game is already over due to accusation, don't re-log the loss conditions.

    def refresh_locations(self):
        loc_names = list(self.case_state['locations'].keys())
        btns = list(self.location_buttons.values())
        for i in range(4):
            name = loc_names[i]
            btn = btns[i]
            
            # Show number of visible clues
            clue_count = len(self.case_state['locations'][name].clues)
            clue_indicator = f" ({clue_count})" if clue_count > 0 else ""
            
            btn.config(text=name + clue_indicator, command=lambda n=name: self.move_to(n))
            
            # highlight current location
            if name == self.case_state['current_location']:
                btn.config(relief="sunken", bg=self.accent_color)
            else:
                btn.config(relief="raised", bg=self.button_color)

    def refresh_suspects(self):
        self.suspect_listbox.delete(0, "end")
        for s in self.case_state['suspects'].values():
            pres = self.case_state['presented'].get(s.name, "none")
            
            # Show if interrogated and if evidence was strong
            int_mark = " (I)" if s.interrogated else ""
            pres_mark = ""
            if pres == "strong":
                pres_mark = " [STRONG EVIDENCE]"
            elif pres == "weak":
                pres_mark = " [WEAK]"
            
            self.suspect_listbox.insert("end", f"{s.name}{int_mark} | {s.alibi}{pres_mark}")

    def current_location_obj(self):
        return self.case_state['locations'][self.case_state['current_location']]

    # ---------------------
    # Game lifecycle
    # ---------------------
    def start_case(self):
        case = generate_case()
        self.setup_case(case)
        self.log_write("CASE START: A high-profile murder has been committed. The police commissioner has given you a limited budget and only 50 hours of investigation time. Find the culprit and present a watertight case.", style='win')
        self.log_write("Suspects identified:")
        for s in self.case_state['suspects'].values():
            self.log_write(f"- {s.summary()}")
        self.refresh_ui_after_change()

    def start_tutorial(self):
        case = generate_tutorial_case()
        self.setup_case(case)
        self.log_write("TUTORIAL CASE LOADED. Welcome to the case of the Defaced Photo. Start by clicking EXAMINE SCENE.", style='win')
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
            
        # Cost is only applied if moving to a *new* location
        if loc_name != self.case_state['current_location']:
            self.apply_credibility(1)
            self.case_state['current_location'] = loc_name
            self.log_write(f"You travel to {loc_name}. (-1 Credibility)", style='action')
        else:
            self.log_write(f"You are already at {loc_name}.")

        self.refresh_ui_after_change()

    def examine(self):
        if self.case_state is None:
            return
        
        # Examine is a free action
        loc = self.current_location_obj()
        if not loc.clues:
            self.log_write("You see nothing of obvious interest in this area.")
        else:
            self.log_write(f"Visible items and clues at {loc.name}:")
            for c in loc.clues:
                self.log_write(f" • id {c.id}: {c.brief()}")
        
        # tutorial guidance
        if self.case_state.get('tutorial_step') == 1:
            self.log_write("Tutorial hint: Click Search/Collect and enter clue ID 1 to secure this piece of evidence. This costs 1 Credibility.", style='win')
            self.case_state['tutorial_step'] = 2

    def search_prompt(self):
        if self.case_state is None or self.case_state['credibility'] <= 0: return
        
        loc = self.current_location_obj()
        if not loc.clues:
            messagebox.showinfo("Search", "No loose clues here to collect.")
            return

        ids = [str(c.id) for c in loc.clues]
        default = ids[0]
        
        val = simpledialog.askstring("Search / Collect Evidence", 
                                     f"Enter the ID of the clue you wish to collect (visible IDs: {', '.join(ids)})", 
                                     initialvalue=default)
        if val is None:
            return
        
        try:
            cid = int(val.strip())
        except ValueError:
            messagebox.showerror("Search", "Clue ID must be a number.")
            return
        
        found = next((c for c in loc.clues if c.id == cid), None)

        if not found:
            messagebox.showinfo("Search", "No such clue here.")
            return

        # Perform the action and apply cost
        self.apply_credibility(1)
        found.found = True
        self.case_state['found_clues'].append(found)
        loc.clues.remove(found)
        
        self.log_write(f"You collected the evidence: {found.brief()} (-1 Credibility)", style='action')
        
        # tutorial guidance
        if self.case_state.get('tutorial_step') == 2:
            self.log_write("Tutorial hint: Open your Notebook to see the collected clue and its tags. Then, select a suspect (e.g., Avery Collins) and click Interrogate.", style='win')
            self.case_state['tutorial_step'] = 3
        
        self.refresh_ui_after_change()

    def interrogate_prompt(self):
        if self.case_state is None or self.case_state['credibility'] <= 0: return
        
        sel = self.get_selected_suspect_name()
        if sel is None:
            messagebox.showinfo("Interrogate", "Select a suspect from the list first.")
            return
        
        suspect = self.case_state['suspects'][sel]
        
        # Only pay cost if not already interrogated
        cost = 0
        if not suspect.interrogated:
            cost = 1
            self.apply_credibility(cost)
            suspect.interrogated = True
            
            self.log_write(f"You interrogate {suspect.name}. (-{cost} Credibility)", style='action')
        else:
            self.log_write(f"You re-interrogate {suspect.name}. The suspect is cooperative but offers no new information.")
            return

        # Reveal a lead if matching tags exist in uncollected clues (20% chance if tags match)
        reveal = False
        for locname, loc in self.case_state['locations'].items():
            for c in loc.clues:
                if suspect.tags & c.tags and random.random() < 0.2:
                    self.log_write(f"During questioning, {suspect.name} mentions a detail that points to a lead at: {locname}")
                    reveal = True
                    break
            if reveal:
                break
                
        if not reveal:
            self.log_write(f"{suspect.name} maintains their alibi: {suspect.alibi}. They don't budge.")
            
        # tutorial guidance
        if self.case_state.get('tutorial_step') == 3:
            self.log_write("Tutorial hint: Did you notice the clue you found was linked to 'avery'? Now try to Present Evidence against 'Avery Collins'.", style='win')
            self.case_state['tutorial_step'] = 4
            
        self.refresh_ui_after_change()

    def present_prompt(self):
        if self.case_state is None or self.case_state['credibility'] <= 0: return
        
        sel = self.get_selected_suspect_name()
        if sel is None:
            messagebox.showinfo("Present", "Select a suspect from the list first.")
            return
        
        self.apply_credibility(1) # Apply cost regardless of outcome
        self.log_write(f"Preparing to present evidence against {sel}...", style='action')
        self.present_evidence(sel)
        
        # tutorial guidance
        if self.case_state.get('tutorial_step') == 4:
            self.log_write("Tutorial hint: You gained credibility! Use Accuse to close the case on 'Avery Collins'.", style='win')
            self.case_state['tutorial_step'] = 5
            
        self.refresh_ui_after_change()

    def accuse_prompt(self):
        if self.case_state is None or self.case_state['credibility'] <= 0: return
        
        sel = self.get_selected_suspect_name()
        if sel is None:
            messagebox.showinfo("Accuse", "Select a suspect from the list first.")
            return
            
        # Accusation uses a turn but has a higher failure cost
        self.apply_credibility(1) 
        
        # Check if the game is over due to max turns or 0 cred, before proceeding with the accusation check
        if self.case_state['credibility'] <= 0 or self.case_state['turns'] >= MAX_TURNS:
            return

        correct = self.check_win(sel)
        
        if correct:
            messagebox.showinfo("Case Closed", f"Congratulations! You secured a conviction against {sel}.")
            self.disable_game_ui()
        else:
            if self.case_state['credibility'] <= 0:
                # Game over message handled by apply_credibility
                pass
            else:
                messagebox.showinfo("Accuse Failed", "Your accusation was too weak or misplaced. Public trust is severely damaged.")
        
        self.refresh_ui_after_change()

    def show_notebook(self):
        if self.case_state is None:
            return
        dlg = tk.Toplevel(self.root, bg=self.bg_color)
        dlg.title("Notebook")
        
        txt = scrolledtext.ScrolledText(dlg, width=80, height=25, wrap="word", bg="#1b2c3a", fg="#d3d9df", font=("Consolas", 10))
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        
        txt.insert("end", "--- Collected Evidence ---\n\n", ("Consolas", 12, "bold"))
        if not self.case_state['found_clues']:
            txt.insert("end", "- No evidence collected yet.\n\n")
        else:
            for c in self.case_state['found_clues']:
                txt.insert("end", f"• ID {c.id}: {c.brief()}\n")
                txt.insert("end", f"   Tags: {', '.join(c.tags)}\n\n")

        txt.insert("end", "\n--- Suspect Details ---\n\n", ("Consolas", 12, "bold"))
        for s in self.case_state['suspects'].values():
            pres_status = self.case_state['presented'].get(s.name, "none")
            
            txt.insert("end", f"• {s.name}\n")
            txt.insert("end", f"   Motive: {s.motive}\n")
            txt.insert("end", f"   Alibi Location: {s.alibi}\n")
            txt.insert("end", f"   Interrogated: {'Yes' if s.interrogated else 'No'}\n")
            txt.insert("end", f"   Presentation Status: {pres_status.upper()}\n\n")
            
        txt.configure(state="disabled")

    # ---------------------
    # Core logic helpers
    # ---------------------
    def apply_credibility(self, cost=1):
        # Always check if the game is already ending before applying the cost
        if self.case_state['credibility'] <= 0 or self.case_state['turns'] >= MAX_TURNS:
            return
            
        if cost > 0:
            self.case_state['credibility'] -= cost
            
        self.case_state['turns'] += 1
        
        if self.case_state['credibility'] <= 0:
            self.log_write("Your credibility has reached zero. The case has been reassigned. GAME OVER.", style='error')
            self.log_write(f"The investigation revealed the true culprit was: {self.case_state['culprit']}", style='error')
            self.disable_game_ui()
            
        if self.case_state['turns'] >= MAX_TURNS:
            self.log_write("You ran out of allowed turns (time limit exceeded). The case is cold. GAME OVER.", style='error')
            self.log_write(f"The investigation revealed the true culprit was: {self.case_state['culprit']}", style='error')
            self.disable_game_ui()
        
        self.update_status()

    def get_selected_suspect_name(self):
        sel = self.suspect_listbox.curselection()
        if not sel:
            return None
        line = self.suspect_listbox.get(sel[0])
        # Name is before ' (I) ' or ' |'
        name = line.split(" |")[0].split(" (I)")[0].strip()
        return name

    def on_suspect_select(self, event=None):
        name = self.get_selected_suspect_name()
        if name is None:
            self.suspect_info.config(text="Select a suspect for details.")
            return
            
        s = self.case_state['suspects'].get(name)
        if not s: return

        pres = self.case_state['presented'].get(name, "none")
        info = (f"{s.name}\nMotive: {s.motive}\nAlibi: {s.alibi}\n"
                f"Interrogated: {'Yes' if s.interrogated else 'No'}\n"
                f"Presentation Status: {pres.upper()}")
        self.suspect_info.config(text=info)

    def present_evidence(self, suspect_name):
        suspect = self.case_state['suspects'].get(suspect_name)
        if not suspect: 
            self.log_write("Error: No such suspect.", style='error')
            return
            
        # --- FIX: Prevent Credibility Spamming ---
        current_status = self.case_state['presented'].get(suspect_name)
        if current_status == "strong":
            self.log_write(f"You have already made a strong presentation against {suspect_name}. Further attempts with the current evidence are redundant (0 Credibility change).")
            return
        
        found_clues = self.case_state['found_clues']
        linking_clues = []
        
        # Calculate score using ONLY evidence not previously used for this suspect
        for c in found_clues:
            if c.id not in suspect.presented_clues and len(suspect.tags & c.tags) > 0:
                linking_clues.append(c)

        score = len(linking_clues)
        
        if score >= 2:
            self.log_write(f"You present {score} new pieces of strong, linking evidence against {suspect.name}. Credibility +2.", style='win')
            self.case_state['credibility'] = min(START_CREDIBILITY, self.case_state['credibility'] + 2) # Cap credibility
            self.case_state['presented'][suspect.name] = "strong"
            # Mark the clues as used for scoring against this suspect
            for c in linking_clues:
                suspect.presented_clues.add(c.id)
                
        elif score == 1:
            self.log_write(f"Your evidence is suggestive but circumstantial ({score} clue link). Credibility unchanged.")
            self.case_state['presented'][suspect.name] = "weak"
        else:
            self.log_write("No clear or new evidence links this suspect to the crime. You lose 2 credibility for a weak presentation.", style='error')
            self.case_state['credibility'] -= 2
            self.case_state['presented'][suspect.name] = "none"


    def check_win(self, accused_name):
        culprit = self.case_state['culprit']
        
        if accused_name == culprit:
            # Win condition: Accuse the right person AND have at least 2 key clues (linking_tag clues)
            strong_evidence_count = 0
            for c in self.case_state['found_clues']:
                if self.case_state['linking_tag'] in c.tags:
                    strong_evidence_count += 1
                    
            if strong_evidence_count >= 2:
                self.log_write(f"Accusation successful! You proved {accused_name}'s guilt with {strong_evidence_count} key pieces of evidence. Case closed. (+3 Credibility Bonus)", style='win')
                self.case_state['credibility'] = min(START_CREDIBILITY, self.case_state['credibility'] + 3)
                return True
            else:
                self.log_write(f"You accused the right person ({accused_name}) but only had {strong_evidence_count} key pieces of evidence. The case is dismissed for lack of proof. You lose 2 Credibility.", style='error')
                self.case_state['credibility'] -= 2
                return False
        else:
            self.log_write(f"Accusation failed. {accused_name} is innocent. Public trust plummets. You lose 5 credibility.", style='error')
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

    try:
        root = tk.Tk()
        app = DetectiveGameUI(root)
        root.mainloop()
    except Exception as e:
        # Fallback in case of environment issues
        print(f"An error occurred: {e}")
       
tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
import random
import textwrap

# ---------------------
# Config
# ---------------------
START_CREDIBILITY = 10
MAX_TURNS = 50
WINDOW_TITLE = "The Deductionist: Case File"

LOCATIONS = [
    "Victim's Penthouse", "Industrial Dock", "Grand Hotel Lobby",
    "Office Tower", "Local Dive Bar", "City Park",
    "Security Office", "Rooftop Garden"
]

SUSPECT_NAMES = [
    "Avery Collins", "Jordan Blake", "Riley Park",
    "Morgan Hale", "Casey Lin", "Elias Vance"
]

MOTIVES = [
    "Financial", "Revenge", "Jealousy", "Political Cover-Up", "Power Struggle"
]

CLUE_TYPES = [
    ("Fingerprint", "links person to a location"),
    ("Receipt", "shows a recent purchase or expense"),
    ("Message", "a threatening or revealing text/email"),
    ("Witness", "eye witness statement placing someone at the scene"),
    ("Weapon Trace", "residue or tool mark"),
    ("Photo", "visual evidence or security footage snippet")
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
        # Tracks which Clue IDs have been used in a successful presentation against this suspect.
        self.presented_clues = set()

    def summary(self):
        return f"{self.name} | Motive: {self.motive} | Alibi: {self.alibi}"

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
    # Use 4 random locations
    locations = {name: Location(name) for name in locs[:4]}

    # Use 5 random suspects
    suspects_list = random.sample(SUSPECT_NAMES, 5)
    culprit_name = random.choice(suspects_list)

    suspects = {}
    for name in suspects_list:
        motive = random.choice(MOTIVES)
        alibi = random.choice(list(locations.keys()))
        tags = [name.split()[0].lower(), motive.lower().replace(' ', '-')]
        suspects[name] = Suspect(name, motive, alibi, tags)

    culprit = suspects[culprit_name]
    linking_tag = culprit.tags.intersection({t.split()[0].lower() for t in SUSPECT_NAMES}).pop()

    # Generate "strong" clues linked to the culprit (3-4 clues)
    clue_pool = []
    clue_id = 1
    
    num_culprit_clues = random.randint(3, 4)
    culprit_clues = random.sample(CLUE_TYPES, num_culprit_clues)
    
    for tname, tdesc in culprit_clues:
        c = Clue(clue_id, tname, f"{tdesc} clearly connected to {linking_tag}", {linking_tag, tname.lower()})
        clue_pool.append(c)
        clue_id += 1

    # Generate "filler" clues (4-6 clues)
    num_filler_clues = random.randint(4, 6)
    all_other_suspects = [s for name, s in suspects.items() if name != culprit_name]
    
    for _ in range(num_filler_clues):
        tname, tdesc = random.choice(CLUE_TYPES)
        # Link filler clues to other suspects or generic tags
        filler_tag = random.choice(all_other_suspects).tags.pop() if all_other_suspects and random.random() < 0.5 else random.choice(MOTIVES).lower().replace(' ', '-')
        tags = {filler_tag, tname.lower()}
        c = Clue(clue_id, tname, f"Generic {tdesc} related to {filler_tag}", tags)
        clue_pool.append(c)
        clue_id += 1

    # Distribute clues across locations
    loc_names = list(locations.keys())
    for c in clue_pool:
        chosen = random.choice(loc_names)
        locations[chosen].clues.append(c)

    return {
        "locations": locations,
        "suspects": suspects,
        "culprit": culprit_name,
        "linking_tag": linking_tag
    }

def generate_tutorial_case():
    locations = {
        "Victim's Penthouse": Location("Victim's Penthouse"),
        "Local Dive Bar": Location("Local Dive Bar"),
        "Office Tower": Location("Office Tower"),
        "Rooftop Garden": Location("Rooftop Garden")
    }
    suspects_list = ["Avery Collins", "Jordan Blake", "Riley Park", "Morgan Hale"]
    culprit = "Avery Collins"
    suspects = {}
    for name in suspects_list:
        motive = "Jealousy" if "Avery" in name else random.choice(MOTIVES)
        alibi = "Local Dive Bar" if name != "Avery Collins" else "Victim's Penthouse"
        tags = [name.split()[0].lower(), motive.lower()]
        suspects[name] = Suspect(name, motive, alibi, tags)

    # Clues linking to Avery
    c1 = Clue(1, "Photo", "A crumpled photo of the victim defaced with the name 'Avery' on the back", {"avery", "photo"})
    c2 = Clue(2, "Message", "A threatening text referencing a 'financial deal gone sour' sent by a number traced to the Office Tower.", {"avery", "message"})
    # Distraction clue
    c3 = Clue(3, "Receipt", "A late-night receipt from a convenience store for someone with an alibi.", {"distraction", "receipt"})
    # Strongest linking clue
    c4 = Clue(4, "Fingerprint", "A clear fingerprint match for Avery found on the murder weapon (a broken statue).", {"avery", "fingerprint"})


    locations["Victim's Penthouse"].clues.extend([c1, c4])
    locations["Office Tower"].clues.append(c2)
    locations["Rooftop Garden"].clues.append(c3)

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
        
        # Apply a basic style configuration
        self.bg_color = "#2c3e50" # Dark Blue/Grey
        self.fg_color = "#ecf0f1" # Light Grey
        self.accent_color = "#3498db" # Blue
        self.button_color = "#34495e" # Darker Grey

        self.root.configure(bg=self.bg_color)
        
        default_font = ("Consolas", 10)
        heading_font = ("Consolas", 12, "bold")

        # --- Top frame: controls and status ---
        top = tk.Frame(root, bg=self.bg_color)
        top.pack(fill="x", padx=10, pady=10)

        self.cred_label = tk.Label(top, text="Credibility: -", bg=self.bg_color, fg=self.fg_color, font=heading_font)
        self.cred_label.pack(side="left", padx=(0, 20))

        self.turn_label = tk.Label(top, text="Turns: -", bg=self.bg_color, fg=self.fg_color, font=heading_font)
        self.turn_label.pack(side="left", padx=(0, 20))

        # Buttons on the right
        btn_frame = tk.Frame(top, bg=self.bg_color)
        btn_frame.pack(side="right")
        
        start_btn = tk.Button(btn_frame, text="Start New Case", command=self.start_case, bg=self.accent_color, fg="white", font=default_font)
        start_btn.pack(side="right", padx=4)
        tut_btn = tk.Button(btn_frame, text="Tutorial Case", command=self.start_tutorial, bg=self.button_color, fg=self.fg_color, font=default_font)
        tut_btn.pack(side="right", padx=4)

        # --- Main content area ---
        main_content = tk.Frame(root, bg=self.bg_color)
        main_content.pack(fill="both", expand=True, padx=10, pady=5)

        # Left frame: locations
        left = tk.LabelFrame(main_content, text="Locations", padx=6, pady=6, bg=self.bg_color, fg=self.fg_color, font=heading_font)
        left.pack(side="left", fill="y", padx=(0, 10))

        self.location_buttons = {}
        for i in range(4):
            b = tk.Button(left, text=f"Location {i+1}", width=20, bg=self.button_color, fg=self.fg_color, font=default_font, activebackground=self.accent_color)
            b.pack(pady=4)
            self.location_buttons[f"loc{i}"] = b

        # Right frame: suspects
        right = tk.LabelFrame(main_content, text="Suspects", padx=6, pady=6, bg=self.bg_color, fg=self.fg_color, font=heading_font)
        right.pack(side="right", fill="y", padx=(10, 0))
        
        self.suspect_listbox = tk.Listbox(right, width=40, height=10, bg=self.button_color, fg=self.fg_color, selectbackground=self.accent_color, font=default_font)
        self.suspect_listbox.pack(padx=4, pady=4)
        
        self.suspect_info = tk.Label(right, text="Select a suspect for details.", wraplength=300, justify="left", bg=self.bg_color, fg=self.fg_color, font=default_font)
        self.suspect_info.pack(padx=4, pady=4)

        # Bind selection update
        self.suspect_listbox.bind("<<ListboxSelect>>", self.on_suspect_select)
        
        # Middle frame: actions and output
        mid = tk.Frame(main_content, bg=self.bg_color)
        mid.pack(side="left", fill="both", expand=True)

        actions = tk.LabelFrame(mid, text="Available Actions", padx=6, pady=6, bg=self.bg_color, fg=self.fg_color, font=heading_font)
        actions.pack(fill="x", pady=(0, 8))

        # Action Buttons Layout (using grid for uniform size)
        action_buttons = [
            ("Examine Scene (0 cost)", self.examine),
            ("Search/Collect (-1 cred)", self.search_prompt),
            ("Interrogate (-1 cred)", self.interrogate_prompt),
            ("Present Evidence (-1 cred)", self.present_prompt),
            ("Accuse (End Case)", self.accuse_prompt),
            ("Notebook (Clues/Info)", self.show_notebook)
        ]
        
        for i, (text, command) in enumerate(action_buttons):
            b = tk.Button(actions, text=text, command=command, bg=self.accent_color, fg="white", font=default_font, padx=5, pady=5)
            b.grid(row=0, column=i, padx=4, pady=4, sticky="ew")

        actions.grid_columnconfigure(5, weight=1) # Ensure Notebook stretches slightly

        # Output area
        out_frame = tk.LabelFrame(mid, text="Investigative Log", padx=6, pady=6, bg=self.bg_color, fg=self.fg_color, font=heading_font)
        out_frame.pack(fill="both", expand=True)
        self.log = scrolledtext.ScrolledText(out_frame, height=18, state="disabled", wrap="word", bg="#1b2c3a", fg="#d3d9df", font=default_font)
        self.log.pack(fill="both", expand=True)

        # initialize disabled state
        self.disable_game_ui()
        self.log_write("Welcome, Detective. The clock is ticking. Click Tutorial or Start New Case to begin your investigation.")

    # ---------------------
    # UI helpers
    # ---------------------
    def log_write(self, text, style='info'):
        self.log.configure(state="normal")
        
        tag_name = style
        if tag_name not in self.log.tag_names():
            if style == 'error':
                self.log.tag_config(tag_name, foreground="#e74c3c", font=("Consolas", 10, "bold"))
            elif style == 'win':
                self.log.tag_config(tag_name, foreground="#2ecc71", font=("Consolas", 10, "bold"))
            elif style == 'action':
                self.log.tag_config(tag_name, foreground="#f39c12", font=("Consolas", 10, "italic"))
            else: # info
                self.log.tag_config(tag_name, foreground="#ecf0f1")
        
        
        self.log.insert("end", textwrap.fill(text, 80) + "\n\n", tag_name)
        self.log.see("end")
        self.log.configure(state="disabled")

    def enable_game_ui(self):
        for b in self.location_buttons.values():
            b.configure(state="normal")
        # Other action buttons remain enabled/disabled via their initial setup, 
        # but the core location/suspect interaction must be enabled.
        self.suspect_listbox.configure(state="normal")

    def disable_game_ui(self):
        for b in self.location_buttons.values():
            b.configure(state="disabled")
        self.suspect_listbox.configure(state="disabled")

    def update_status(self):
        cs = self.case_state
        self.cred_label.config(text=f"Credibility: {max(0, cs['credibility'])}")
        self.turn_label.config(text=f"Turns: {cs['turns']}/{MAX_TURNS}")
        
        if cs['credibility'] <= 0 or cs['turns'] >= MAX_TURNS:
            self.disable_game_ui()
            # If the game is already over due to accusation, don't re-log the loss conditions.

    def refresh_locations(self):
        loc_names = list(self.case_state['locations'].keys())
        btns = list(self.location_buttons.values())
        for i in range(4):
            name = loc_names[i]
            btn = btns[i]
            
            # Show number of visible clues
            clue_count = len(self.case_state['locations'][name].clues)
            clue_indicator = f" ({clue_count})" if clue_count > 0 else ""
            
            btn.config(text=name + clue_indicator, command=lambda n=name: self.move_to(n))
            
            # highlight current location
            if name == self.case_state['current_location']:
                btn.config(relief="sunken", bg=self.accent_color)
            else:
                btn.config(relief="raised", bg=self.button_color)

    def refresh_suspects(self):
        self.suspect_listbox.delete(0, "end")
        for s in self.case_state['suspects'].values():
            pres = self.case_state['presented'].get(s.name, "none")
            
            # Show if interrogated and if evidence was strong
            int_mark = " (I)" if s.interrogated else ""
            pres_mark = ""
            if pres == "strong":
                pres_mark = " [STRONG EVIDENCE]"
            elif pres == "weak":
                pres_mark = " [WEAK]"
            
            self.suspect_listbox.insert("end", f"{s.name}{int_mark} | {s.alibi}{pres_mark}")

    def current_location_obj(self):
        return self.case_state['locations'][self.case_state['current_location']]

    # ---------------------
    # Game lifecycle
    # ---------------------
    def start_case(self):
        case = generate_case()
        self.setup_case(case)
        self.log_write("CASE START: A high-profile murder has been committed. The police commissioner has given you a limited budget and only 50 hours of investigation time. Find the culprit and present a watertight case.", style='win')
        self.log_write("Suspects identified:")
        for s in self.case_state['suspects'].values():
            self.log_write(f"- {s.summary()}")
        self.refresh_ui_after_change()

    def start_tutorial(self):
        case = generate_tutorial_case()
        self.setup_case(case)
        self.log_write("TUTORIAL CASE LOADED. Welcome to the case of the Defaced Photo. Start by clicking EXAMINE SCENE.", style='win')
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
            
        # Cost is only applied if moving to a *new* location
        if loc_name != self.case_state['current_location']:
            self.apply_credibility(1)
            self.case_state['current_location'] = loc_name
            self.log_write(f"You travel to {loc_name}. (-1 Credibility)", style='action')
        else:
            self.log_write(f"You are already at {loc_name}.")

        self.refresh_ui_after_change()

    def examine(self):
        if self.case_state is None:
            return
        
        # Examine is a free action
        loc = self.current_location_obj()
        if not loc.clues:
            self.log_write("You see nothing of obvious interest in this area.")
        else:
            self.log_write(f"Visible items and clues at {loc.name}:")
            for c in loc.clues:
                self.log_write(f" • id {c.id}: {c.brief()}")
        
        # tutorial guidance
        if self.case_state.get('tutorial_step') == 1:
            self.log_write("Tutorial hint: Click Search/Collect and enter clue ID 1 to secure this piece of evidence. This costs 1 Credibility.", style='win')
            self.case_state['tutorial_step'] = 2

    def search_prompt(self):
        if self.case_state is None or self.case_state['credibility'] <= 0: return
        
        loc = self.current_location_obj()
        if not loc.clues:
            messagebox.showinfo("Search", "No loose clues here to collect.")
            return

        ids = [str(c.id) for c in loc.clues]
        default = ids[0]
        
        val = simpledialog.askstring("Search / Collect Evidence", 
                                     f"Enter the ID of the clue you wish to collect (visible IDs: {', '.join(ids)})", 
                                     initialvalue=default)
        if val is None:
            return
        
        try:
            cid = int(val.strip())
        except ValueError:
            messagebox.showerror("Search", "Clue ID must be a number.")
            return
        
        found = next((c for c in loc.clues if c.id == cid), None)

        if not found:
            messagebox.showinfo("Search", "No such clue here.")
            return

        # Perform the action and apply cost
        self.apply_credibility(1)
        found.found = True
        self.case_state['found_clues'].append(found)
        loc.clues.remove(found)
        
        self.log_write(f"You collected the evidence: {found.brief()} (-1 Credibility)", style='action')
        
        # tutorial guidance
        if self.case_state.get('tutorial_step') == 2:
            self.log_write("Tutorial hint: Open your Notebook to see the collected clue and its tags. Then, select a suspect (e.g., Avery Collins) and click Interrogate.", style='win')
            self.case_state['tutorial_step'] = 3
        
        self.refresh_ui_after_change()

    def interrogate_prompt(self):
        if self.case_state is None or self.case_state['credibility'] <= 0: return
        
        sel = self.get_selected_suspect_name()
        if sel is None:
            messagebox.showinfo("Interrogate", "Select a suspect from the list first.")
            return
        
        suspect = self.case_state['suspects'][sel]
        
        # Only pay cost if not already interrogated
        cost = 0
        if not suspect.interrogated:
            cost = 1
            self.apply_credibility(cost)
            suspect.interrogated = True
            
            self.log_write(f"You interrogate {suspect.name}. (-{cost} Credibility)", style='action')
        else:
            self.log_write(f"You re-interrogate {suspect.name}. The suspect is cooperative but offers no new information.")
            return

        # Reveal a lead if matching tags exist in uncollected clues (20% chance if tags match)
        reveal = False
        for locname, loc in self.case_state['locations'].items():
            for c in loc.clues:
                if suspect.tags & c.tags and random.random() < 0.2:
                    self.log_write(f"During questioning, {suspect.name} mentions a detail that points to a lead at: {locname}")
                    reveal = True
                    break
            if reveal:
                break
                
        if not reveal:
            self.log_write(f"{suspect.name} maintains their alibi: {suspect.alibi}. They don't budge.")
            
        # tutorial guidance
        if self.case_state.get('tutorial_step') == 3:
            self.log_write("Tutorial hint: Did you notice the clue you found was linked to 'avery'? Now try to Present Evidence against 'Avery Collins'.", style='win')
            self.case_state['tutorial_step'] = 4
            
        self.refresh_ui_after_change()

    def present_prompt(self):
        if self.case_state is None or self.case_state['credibility'] <= 0: return
        
        sel = self.get_selected_suspect_name()
        if sel is None:
            messagebox.showinfo("Present", "Select a suspect from the list first.")
            return
        
        self.apply_credibility(1) # Apply cost regardless of outcome
        self.log_write(f"Preparing to present evidence against {sel}...", style='action')
        self.present_evidence(sel)
        
        # tutorial guidance
        if self.case_state.get('tutorial_step') == 4:
            self.log_write("Tutorial hint: You gained credibility! Use Accuse to close the case on 'Avery Collins'.", style='win')
            self.case_state['tutorial_step'] = 5
            
        self.refresh_ui_after_change()

    def accuse_prompt(self):
        if self.case_state is None or self.case_state['credibility'] <= 0: return
        
        sel = self.get_selected_suspect_name()
        if sel is None:
            messagebox.showinfo("Accuse", "Select a suspect from the list first.")
            return
            
        # Accusation uses a turn but has a higher failure cost
        self.apply_credibility(1) 
        
        # Check if the game is over due to max turns or 0 cred, before proceeding with the accusation check
        if self.case_state['credibility'] <= 0 or self.case_state['turns'] >= MAX_TURNS:
            return

        correct = self.check_win(sel)
        
        if correct:
            messagebox.showinfo("Case Closed", f"Congratulations! You secured a conviction against {sel}.")
            self.disable_game_ui()
        else:
            if self.case_state['credibility'] <= 0:
                # Game over message handled by apply_credibility
                pass
            else:
                messagebox.showinfo("Accuse Failed", "Your accusation was too weak or misplaced. Public trust is severely damaged.")
        
        self.refresh_ui_after_change()

    def show_notebook(self):
        if self.case_state is None:
            return
        dlg = tk.Toplevel(self.root, bg=self.bg_color)
        dlg.title("Notebook")
        
        txt = scrolledtext.ScrolledText(dlg, width=80, height=25, wrap="word", bg="#1b2c3a", fg="#d3d9df", font=("Consolas", 10))
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        
        txt.insert("end", "--- Collected Evidence ---\n\n", ("Consolas", 12, "bold"))
        if not self.case_state['found_clues']:
            txt.insert("end", "- No evidence collected yet.\n\n")
        else:
            for c in self.case_state['found_clues']:
                txt.insert("end", f"• ID {c.id}: {c.brief()}\n")
                txt.insert("end", f"   Tags: {', '.join(c.tags)}\n\n")

        txt.insert("end", "\n--- Suspect Details ---\n\n", ("Consolas", 12, "bold"))
        for s in self.case_state['suspects'].values():
            pres_status = self.case_state['presented'].get(s.name, "none")
            
            txt.insert("end", f"• {s.name}\n")
            txt.insert("end", f"   Motive: {s.motive}\n")
            txt.insert("end", f"   Alibi Location: {s.alibi}\n")
            txt.insert("end", f"   Interrogated: {'Yes' if s.interrogated else 'No'}\n")
            txt.insert("end", f"   Presentation Status: {pres_status.upper()}\n\n")
            
        txt.configure(state="disabled")

    # ---------------------
    # Core logic helpers
    # ---------------------
    def apply_credibility(self, cost=1):
        # Always check if the game is already ending before applying the cost
        if self.case_state['credibility'] <= 0 or self.case_state['turns'] >= MAX_TURNS:
            return
            
        if cost > 0:
            self.case_state['credibility'] -= cost
            
        self.case_state['turns'] += 1
        
        if self.case_state['credibility'] <= 0:
            self.log_write("Your credibility has reached zero. The case has been reassigned. GAME OVER.", style='error')
            self.log_write(f"The investigation revealed the true culprit was: {self.case_state['culprit']}", style='error')
            self.disable_game_ui()
            
        if self.case_state['turns'] >= MAX_TURNS:
            self.log_write("You ran out of allowed turns (time limit exceeded). The case is cold. GAME OVER.", style='error')
            self.log_write(f"The investigation revealed the true culprit was: {self.case_state['culprit']}", style='error')
            self.disable_game_ui()
        
        self.update_status()

    def get_selected_suspect_name(self):
        sel = self.suspect_listbox.curselection()
        if not sel:
            return None
        line = self.suspect_listbox.get(sel[0])
        # Name is before ' (I) ' or ' |'
        name = line.split(" |")[0].split(" (I)")[0].strip()
        return name

    def on_suspect_select(self, event=None):
        name = self.get_selected_suspect_name()
        if name is None:
            self.suspect_info.config(text="Select a suspect for details.")
            return
            
        s = self.case_state['suspects'].get(name)
        if not s: return

        pres = self.case_state['presented'].get(name, "none")
        info = (f"{s.name}\nMotive: {s.motive}\nAlibi: {s.alibi}\n"
                f"Interrogated: {'Yes' if s.interrogated else 'No'}\n"
                f"Presentation Status: {pres.upper()}")
        self.suspect_info.config(text=info)

    def present_evidence(self, suspect_name):
        suspect = self.case_state['suspects'].get(suspect_name)
        if not suspect: 
            self.log_write("Error: No such suspect.", style='error')
            return
            
        # --- FIX: Prevent Credibility Spamming ---
        current_status = self.case_state['presented'].get(suspect_name)
        if current_status == "strong":
            self.log_write(f"You have already made a strong presentation against {suspect_name}. Further attempts with the current evidence are redundant (0 Credibility change).")
            return
        
        found_clues = self.case_state['found_clues']
        linking_clues = []
        
        # Calculate score using ONLY evidence not previously used for this suspect
        for c in found_clues:
            if c.id not in suspect.presented_clues and len(suspect.tags & c.tags) > 0:
                linking_clues.append(c)

        score = len(linking_clues)
        
        if score >= 2:
            self.log_write(f"You present {score} new pieces of strong, linking evidence against {suspect.name}. Credibility +2.", style='win')
            self.case_state['credibility'] = min(START_CREDIBILITY, self.case_state['credibility'] + 2) # Cap credibility
            self.case_state['presented'][suspect.name] = "strong"
            # Mark the clues as used for scoring against this suspect
            for c in linking_clues:
                suspect.presented_clues.add(c.id)
                
        elif score == 1:
            self.log_write(f"Your evidence is suggestive but circumstantial ({score} clue link). Credibility unchanged.")
            self.case_state['presented'][suspect.name] = "weak"
        else:
            self.log_write("No clear or new evidence links this suspect to the crime. You lose 2 credibility for a weak presentation.", style='error')
            self.case_state['credibility'] -= 2
            self.case_state['presented'][suspect.name] = "none"


    def check_win(self, accused_name):
        culprit = self.case_state['culprit']
        
        if accused_name == culprit:
            # Win condition: Accuse the right person AND have at least 2 key clues (linking_tag clues)
            strong_evidence_count = 0
            for c in self.case_state['found_clues']:
                if self.case_state['linking_tag'] in c.tags:
                    strong_evidence_count += 1
                    
            if strong_evidence_count >= 2:
                self.log_write(f"Accusation successful! You proved {accused_name}'s guilt with {strong_evidence_count} key pieces of evidence. Case closed. (+3 Credibility Bonus)", style='win')
                self.case_state['credibility'] = min(START_CREDIBILITY, self.case_state['credibility'] + 3)
                return True
            else:
                self.log_write(f"You accused the right person ({accused_name}) but only had {strong_evidence_count} key pieces of evidence. The case is dismissed for lack of proof. You lose 2 Credibility.", style='error')
                self.case_state['credibility'] -= 2
                return False
        else:
            self.log_write(f"Accusation failed. {accused_name} is innocent. Public trust plummets. You lose 5 credibility.", style='error')
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

    try:
        root = tk.Tk()
        app = DetectiveGameUI(root)
        root.mainloop()
    except Exception as e:
        # Fallback in case of environment issues
        print(f"An error occurred: {e}")