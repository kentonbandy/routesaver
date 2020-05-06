
from tkinter import *
import tkinter as tk
from PIL import ImageTk, Image
import numpy as np
import json
from pathlib import Path
import os
import time
import textwrap

'''
TO DO:
- Create initial function that checks viability of database file
'''

root = tk.Tk()
root.title("Work Data App")
root.geometry("500x600")
bgc = "#0b5973"
fgc = "white"
root.configure(background=bgc)

# Open window in the center of the screen
root.withdraw()
root.update_idletasks()
x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2 - 100
y = (root.winfo_screenheight() - root.winfo_reqheight()) / 2 - 200
root.geometry("+%d+%d" % (x, y))
root.deiconify()

#frames
mm_frame = Frame(root, bg=bgc)
error_frame = Frame(root, bg=bgc)
ne_frame = Frame(root, bg=bgc)
review_frame = Frame(root, bg=bgc)
success_frame = Frame(root, bg=bgc)
fail_frame = Frame(root, bg=bgc)
overwrite_frame = Frame(root, bg=bgc)
cs_frame = Frame(root, bg=bgc)
an_frame = Frame(root, bg=bgc)
ve_frame = Frame(root, bg=bgc)
ve_viewer = Frame(root, bg=bgc)
notes_frame = Frame(root, bg=bgc)
de_frame = Frame(root, bg=bgc)

all_frames = [mm_frame, error_frame, ne_frame, cs_frame, an_frame, ve_frame,
              ve_viewer, de_frame, review_frame, success_frame, fail_frame,
              overwrite_frame, notes_frame]

global FOUND
FOUND = None

script_dir = os.path.dirname(__file__)
db_file = Path(f'{script_dir}/workdata_database.json')


def init_db_check():
    '''
    error 1 = file exists but isn't formatted correctly, backups exist
    error 2 = file exists but isn't formatted correctly, no backups
    error 3 = file doesn't exist, backups exist
    error 4 = neither file nor backups exist
    '''
    if Path(f'{script_dir}/workdata_backup/').is_dir() == False:
        new_backup_dir()
    for p, d, files in os.walk(f'{script_dir}/workdata_backup/'):
        if files:
            try:
                testpath = Path(f'{script_dir}/workdata_backup/{files[-1]}')
                backup = json.loads(testpath.read_text())
                x = backup['workdata']
                y = backup['default_salary']
            except KeyError:
                backup = None
        else:
            backup = None
    if db_file.is_file():
        try:
            test = json.loads(db_file.read_text())
        except json.decoder.JSONDecodeError:
            if backup:
                error(1, backup)
            else:
                error(2)
            return
        try:
            x = test['workdata']
            y = test['default_salary']
            get_data()
            change_frame(mm_frame)
        except KeyError:
            if backup:
                error(1, backup)
            else:
                error(2)
    else:
        if backup:
            error(3, backup)
        else:
            error(4)


def get_data():
    global data
    data = json.loads(db_file.read_text())
    create_base_entry()


def error(code, backup=None):
    codedict = {1: {
                    'title': 'Database file corrupted!\nBackup files found!',
                    'bvar1': 'Restore from backup',
                    'bvar2': 'Exit program'
                    },
                2: {
                    'title': 'Database file corrupted!\nBackup files not found!',
                    'bvar1': 'Create new (blank) database file',
                    'bvar2': 'Exit program'
                    },
                3: {
                    'title': 'Database file not found!\nBackup files found!',
                    'bvar1': 'Restore from backup',
                    'bvar2': 'Exit program'
                    },
                4: {
                    'title': 'Database file not found!\nBackup files not found!',
                    'bvar1': 'Create new (blank) database file',
                    'bvar2': 'Exit program'
                    }
                }

    error_title_var.set(codedict[code]['title'])
    eb_1_var.set(codedict[code]['bvar1'])
    eb_2_var.set(codedict[code]['bvar2'])
    error_button_2.config(command=quit)
    if code == 1 or code == 3:
        error_button_1.config(command=lambda: write_to_db(backup))
    else:
        error_button_1.config(command=new_db_file)

    change_frame(error_frame)


def new_db_file():
    empty_db_file = {'workdata': [], 'default_salary': 0}
    with open(f'{script_dir}/workdata_database.json', 'w') as f:
        json.dump(empty_db_file, f, indent=2)
    if Path(f'{script_dir}/workdata_database.json').is_file():
        success_mm_button.config(command=lambda: [get_data(), change_frame(mm_frame)])
        change_frame(success_frame)
    else:
        change_frame(fail_frame)


def new_backup_dir():
    os.mkdir(f'{script_dir}/workdata_backup/')


def backup_db(db):
    try:
        backup_files = os.listdir(path=f'{script_dir}/workdata_backup/')
        if len(backup_files) == 0:
            newnum = 0
        else:
            backup_files.sort(key=len)
            while len(backup_files) > 20:
                os.remove(f'{script_dir}/workdata_backup/{backup_files[0]}')
                backup_files.remove(backup_files[0])
            full_name = backup_files[-1]
            file_name = full_name[:-5]
            name_list = file_name.split('_')
            num = int(name_list[-1])
            newnum = num + 1
    except FileNotFoundError:
        newnum = 0
    newname = f'workdata_backup_{newnum}.json'
    with open(f'{script_dir}/workdata_backup/{newname}', 'w') as f:
        json.dump(db, f, indent=2)

def float_it(ent):
    if ent.get():
        var = float(ent.get())
    else:
        var = None
    return var


def complete_entry():
    # needs to check for problems!
    serial = convert_date(date_.get())
    route = route_.get()
    bt = float_it(bt_)
    et = float_it(et_)
    f3996 = float_it(form_)
    fappr = float_it(form_appr_)
    appr = appr_.get()
    bp = float_it(bp_)
    notes = notes_.get()
    sal = base_entry['Salary']
    hourly = base_entry['Hourly']
    hours = float(np.round((et - bt), 2))
    uaot = None
    if appr == "":
        appr = None
    if notes == "":
        notes = None
    if hours >= 6.00:
        hours = float(np.round((hours - 0.50), 2))
    if hours >= 7.93:
        reg_time = 8.00
    else:
        reg_time = hours
    ot = float(np.round((hours - reg_time), 2))
    if ot <= 0.08:
        ot = 0
    if bp:
        bp = float(bp)
        routetime = float(np.round((hours - bp), 2))
    else:
        routetime = hours
    if fappr:
        if ot <= fappr:
            appr = "3996"
    elif ot == 0:
        appr = "NO OT"
    if appr is None:
        if fappr:
            uaot = float(np.round((ot - fappr), 2))
        else:
            uaot = ot
    payable_reg = float(np.round((reg_time * hourly), 2))
    payable_ot = float(np.round((ot * 1.5 * hourly), 2))
    gross = float(np.round((payable_reg + payable_ot), 2))
    new_entry = {}
    entry_values = [
                    int(serial), int(route), bt, et, f3996, fappr, appr, bp,
                    notes, None, None, hours, reg_time, ot, routetime, uaot, gross
                    ]
    for i in base_entry:
        new_entry[i] = base_entry[i]
        keylist = []
    for i in base_entry.keys():
        keylist.append(i)
    for n in range(17):
        k = keylist[n]
        if k == 'Salary' or k == 'Hourly':
            new_entry[k] = base_entry[k]
        else:
            new_entry[k] = entry_values[n]

    display_entry(new_entry)
    viewer_title_var.set("Data to be saved:")
    viewer_button_1_var.set("Save!")
    viewer_button_1.config(command=lambda: [save_entry(new_entry), clear_entries(ne_frame), viewer_button_2.grid(row=18, column=1, pady=10), viewer_button_4.grid(row=19, column=2, pady=10)])
    viewer_button_3_var.set("Do not save")
    viewer_button_3.config(command=lambda: [clear_entries(ne_frame), change_frame(ne_frame), viewer_button_2.grid(row=18, column=1, pady=10), viewer_button_4.grid(row=19, column=2, pady=10)])
    viewer_button_2_var.set("View Notes")
    viewer_button_2.config(command=lambda: [notestitlevar.set(f"Notes for {convert_date(str(FOUND['Date']))}:"),
                                            notesvar.set(textwrap.fill(new_entry['Notes'], 50)),
                                            change_frame(notes_frame)])
    viewer_button_4.grid_forget()
    change_frame(ve_viewer)


def check_for_duplicate(ent):
    for entry in data['workdata']:
        if ent['Date'] == entry['Date']:
            return entry


def remove_entry(delete_this):
    data['workdata'].remove(delete_this)
    write_to_db(data)

def write_to_db(new_db):
    try:
        backup_db(data)
    except NameError:
        pass
    db_file.write_text(json.dumps(new_db, indent=2))
    check_db(new_db)


def check_db(new_db):
    get_data()
    if new_db == data:
        change_frame(success_frame)
    else:
        change_frame(fail_frame)


def save_entry(ent):

    delete_this = None

    def remove_entry():
        data['workdata'].remove(delete_this)
        append_entry()

    def append_entry():
        data['workdata'].append(ent)
        sort_db()

    def sort_db():
        serials = []
        for e in data['workdata']:
            serials.append(int(e['Date']))
        serials.sort()
        sorted_db = {'workdata': [], 'default_salary': None}
        for serial in serials:
            for e in data['workdata']:
                if int(e['Date']) == serial:
                    sorted_db['workdata'].append(e)
            sorted_db['default_salary'] = data['default_salary']
        write_to_db(sorted_db)

    delete_this = check_for_duplicate(ent)
    if delete_this:
        or_ybutton.config(command=remove_entry)
        change_frame(overwrite_frame)
    else:
        append_entry()



def time_format(input_, ent):
    inp = input_.get()
    inpstrip = remove_char(inp, ".")
    if inpstrip == "":
        input_.set("")
        return
    inpstrip2 = inpstrip[:]
    for n in range(len(inpstrip2)):
        if inpstrip2[n].isdigit() is False:
            inpstrip = inpstrip2[:n] + inpstrip2[n+1:]
    if len(inpstrip) <= 2 and len(inpstrip) > 0:
        input_.set("." + inpstrip)
        root.after_idle(lambda: ent.icursor(len(inp) + 1))
    elif len(inpstrip) >= 3:
        if len(inpstrip) > 4:
            inpstrip = inpstrip[:4]
        inp = inpstrip[:-2] + '.' + inpstrip[-2:]
        input_.set(inp)
        root.after_idle(lambda: ent.icursor(len(inp) + 1))
    else:
        input_.set("")


def convert_date(date):
    if "/" in date:
        converted = date[-4:] + date[:2] + date[3:5]
        return converted
    converted = date[-4:-2] + "/" + date[-2:] + "/" + date[:4]
    return converted


def remove_char(s, c):
    newstring = ""
    for i in s:
        if i != c:
            newstring += i
    return newstring


def add_char(s, c, ind_lst):
    newstring = ""
    for n in range(len(s)):
        if n in ind_lst:
            newstring += s[n] + c
        else:
            newstring += s[n]
    return newstring


def date_format(input_, ent):
    global lastinp
    try:
        len(lastinp)
    except NameError:
        lastinp = ""
    inp = input_.get()
    if len(inp) > 10:
        input_.set(lastinp)
        root.after_idle(lambda: ent.icursor(len(inp) + 1))
        return
    inpstrip = remove_char(inp, "/")
    inpstrip2 = inpstrip[:]
    for n in range(len(inpstrip2)):
        if inpstrip2[n].isdigit() is False:
            inpstrip = inpstrip2[:n] + inpstrip2[n+1:]
            inp = add_char(inpstrip, "/", [1,3])
            input_.set(inp)
            lastinp = inp
            return
    if len(inp) > 1:
        if len(inp) in [2,5]:
            if len(lastinp) > len(inp):
                lastinp = inp[:-1]
                input_.set(lastinp)
                return
        inds = [1, 3]
        inp = add_char(inpstrip, "/", [1,3])
        lastinp = inp[:]
        input_.set(inp)
        root.after_idle(lambda: ent.icursor(len(inp) + 1))
    lastinp = inp


def clear_entries(frame):
    for widget in frame.winfo_children():
        if widget.winfo_class() == 'Entry':
            widget.delete(0, END)



def remove_labels(frame):
    for widget in frame.winfo_children():
        if widget.winfo_class() == "Label":
            widget.destroy()


def remove_all_widgets(frame):
    classes = ["Label", "Entry", "Button"]
    for widget in frame.winfo_children():
        for c in classes:
            if widget.winfo_class() == c:
                widget.destroy()


def find_first_entry(frame):
    for widget in frame.winfo_children():
        if widget.winfo_class() == 'Entry':
            return widget


def change_frame(frame):
    for w in root.winfo_children():
        if w.winfo_class() == 'Frame':
            w.pack_forget()
    if frame == mm_frame:
        mm_sal_var.set(f"Salary set to ${data['default_salary']}")
    frame.pack()


def find_entry(ent):
    ent = convert_date(ent)
    ent = int(ent)
    for e in data['workdata']:
        if e['Date'] == ent:
            viewer_title_var.set("Entry found!")
            FOUND = e
            display_entry(e)
            de_title_var.set(f"Are you sure you want to delete the entry for {convert_date(str(FOUND['Date']))}?")
            de_ybutton.config(command=lambda: [clear_display_labels(), remove_entry(FOUND)])
            viewer_button_2.config(command=lambda: [
                                                    notestitlevar.set(f"Notes for {convert_date(str(FOUND['Date']))}:"),
                                                    notesvar.set(textwrap.fill(FOUND['Notes'], 50)),
                                                    change_frame(notes_frame)
                                                    ])
            return
    viewer_title_var.set("Entry not found!")


def clear_display_labels():
    for sv in labvar_list:
        sv.set("")
    for sv in labvar_list2:
        sv.set("")


def display_entry(ent):
    keys = []
    vals = []
    for k, v in ent.items():
        keys.append(k)
        vals.append(v)
    for n in range(len(labvar_list)):
        labvar_list[n].set(f"{keys[n]}:")
        if keys[n] == 'Date':
            labvar_list2[n].set(convert_date(str(vals[n])))
        elif keys[n] == 'Notes' or keys[n] == 'OT approval method':
            if vals[n]:
                if len(vals[n]) > 125:
                    short_notes = vals[n][:125] + "..."
                    labvar_list2[n].set(textwrap.fill(short_notes, 35))
                else:
                    labvar_list2[n].set(textwrap.fill(vals[n], 35))
            else:
                labvar_list2[n].set(vals[n])
        else:
            labvar_list2[n].set(vals[n])


def create_base_entry():
    empty_entry = {
                   'Date': None,
                   'Route': None,
                   'Begin Tour': None,
                   'End Tour': None,
                   'Morning estimate (3996)': None,
                   'Mgmt approval (3996)': 0.00,
                   'OT approval method': None,
                   'Non-primary route time': None,
                   'Notes': None,
                   'Salary': None,
                   'Hourly': None,
                   'Total work hours': None,
                   'Regular time': None,
                   'Overtime': None,
                   'Primary route time': None,
                   'Unauthorized OT': 0.00,
                   'Gross pay': 0.00,
                   }
    global base_entry
    base_entry = {}
    for key in empty_entry:
        base_entry[key] = empty_entry[key]   
    base_entry['Salary'] = data['default_salary']
    base_entry['Hourly'] = float(np.round((base_entry['Salary'] / 2080.00), 2))


frame_history = []

# mm_frame population

mm_sal_var = StringVar()

title = Label(mm_frame, text="Welcome to the Work Data App!", bg=bgc, fg=fgc)
sal_disp = Label(mm_frame,
                 textvariable=mm_sal_var, bg=bgc, fg=fgc)
entry = Button(mm_frame, text="Create New Entry", command=lambda: change_frame(ne_frame))
change_sal = Button(mm_frame, text="Change Salary Rate")
analytics = Button(mm_frame, text="Analytics Menu")
view_ent = Button(mm_frame, text="View Entry", command=lambda: [
                                                                viewer_title_var.set("Entry found!"),
                                                                viewer_button_1_var.set("New Search"),
                                                                viewer_button_1.config(command=lambda: [clear_display_labels(), clear_entries(ve_frame), change_frame(ve_frame)]),
                                                                viewer_button_2_var.set("View Notes"),
                                                                viewer_button_3_var.set("Delete Entry"),
                                                                viewer_button_3.config(command=lambda: change_frame(de_frame)),
                                                                viewer_button_4_var.set("Main Menu"),
                                                                viewer_button_4.config(command=lambda: [clear_entries(ve_frame), change_frame(mm_frame)]),
                                                                change_frame(ve_frame)
                                                                ])
delete_ent = Button(mm_frame, text="Delete an Entry")
close_pgm = Button(mm_frame, text="Exit the Program", command=quit)

title.pack(pady=20)
sal_disp.pack(pady=20)
entry.pack(pady=5)
change_sal.pack(pady=5)
analytics.pack(pady=5)
view_ent.pack(pady=5)
delete_ent.pack(pady=5)
close_pgm.pack(pady=5)

# ne_frame population
ne_title = Label(ne_frame, text="New Entry", bg=bgc, fg=fgc)
date_l = Label(ne_frame, text="Date (MM/DD/YYYY)*", bg=bgc, fg=fgc)
route_l = Label(ne_frame, text="Route #*", bg=bgc, fg=fgc)
bt_l = Label(ne_frame, text="Begin Tour (HH.UU)*", bg=bgc, fg=fgc)
et_l = Label(ne_frame, text="End Tour (HH.UU)*", bg=bgc, fg=fgc)
form_l = Label(ne_frame, text="3996 Estimate (HH.UU)", bg=bgc, fg=fgc)
form_appr_l = Label(ne_frame, text="3996 Approval (HH.UU)", bg=bgc, fg=fgc)
appr_l = Label(ne_frame, text="Was all OT Approved? List method of approval", bg=bgc, fg=fgc)
bp_l = Label(ne_frame, text="Time spent on other routes (HH.UU)", bg=bgc, fg=fgc)
notes_l = Label(ne_frame, text="Additional Notes", bg=bgc, fg=fgc)

ne_entries = ["date_",
              "route_",
              "bt_",
              "et_",
              "form_",
              "form_appr_",
              "appr_",
              "bp_",
              "notes_"
              ]
date_text = StringVar()
date_ = Entry(ne_frame, width=15, textvariable=date_text)
date_text.trace('w', lambda *args: date_format(date_text, date_))
route_ = Entry(ne_frame, width=15)
bt_text = StringVar()
bt_ = Entry(ne_frame, width=15, textvariable=bt_text)
bt_text.trace('w', lambda *args: time_format(bt_text, bt_))
et_text = StringVar()
et_ = Entry(ne_frame, width=15, textvariable=et_text)
et_text.trace('w', lambda *args: time_format(et_text, et_))
form_text = StringVar()
form_ = Entry(ne_frame, width=15, textvariable=form_text)
form_text.trace('w', lambda *args: time_format(form_text, form_))
form_appr_text = StringVar()
form_appr_ = Entry(ne_frame, width=15, textvariable=form_appr_text)
form_appr_text.trace('w', lambda *args: time_format(form_appr_text, form_appr_))
appr_ = Entry(ne_frame, width=15)
bp_text = StringVar()
bp_ = Entry(ne_frame, width=15, textvariable=bp_text)
bp_text.trace('w', lambda *args: time_format(bp_text, bp_))
notes_ = Entry(ne_frame, width=15)

submit = Button(ne_frame, text="Submit Entry", padx=23, state="active", command=complete_entry)
to_main = Button(ne_frame, text="Return to Main Menu", command=lambda: change_frame(mm_frame))

req = Label(ne_frame, bg=bgc, fg=fgc, text="* = Field required.\nIf no asterisk, only fill in if the field is applicable.")

ne_title.grid(row=0, column=0, columnspan=2, pady=20)
date_l.grid(row=1, column=0, pady=5)
route_l.grid(row=2, column=0, pady=5)
bt_l.grid(row=3, column=0, pady=5)
et_l.grid(row=4, column=0, pady=5)
form_l.grid(row=5, column=0, pady=5)
form_appr_l.grid(row=6, column=0, pady=5)
appr_l.grid(row=7, column=0, pady=5, padx=5)
bp_l.grid(row=8, column=0, pady=5)
notes_l.grid(row=9, column=0, pady=5)
date_.grid(row=1, column=1, pady=5)
route_.grid(row=2, column=1, pady=5)
bt_.grid(row=3, column=1, pady=5)
et_.grid(row=4, column=1, pady=5)
form_.grid(row=5, column=1, pady=5)
form_appr_.grid(row=6, column=1, pady=5)
appr_.grid(row=7, column=1, pady=5)
bp_.grid(row=8, column=1, pady=5)
notes_.grid(row=9, column=1, pady=5)
submit.grid(row=10, column=0, columnspan=2, pady=10)
to_main.grid(row=11, column=0, columnspan=2, pady=5)
req.grid(row=12, column=0, columnspan=2, pady=5)

# view entry frame population
ve_title = Label(ve_frame, text="View Entry", bg=bgc, fg=fgc)
ve_label = Label(ve_frame, text="Enter the date of the entry you would like to view.", bg=bgc, fg=fgc)
ve_text = StringVar()
ve_entry = Entry(ve_frame, width=15, textvariable=ve_text)
ve_text.trace('w', lambda *args: date_format(ve_text, ve_entry))
ve_button = Button(ve_frame, text="Search", command=lambda: [
                                                             find_entry(ve_text.get()),
                                                             change_frame(ve_viewer),
                                                             clear_entries(ve_frame)
                                                             ])
ve_mm_button = Button(ve_frame, text="Main Menu", command=lambda: [change_frame(mm_frame), clear_entries(ve_frame)])

ve_title.pack(pady=10)
ve_label.pack(pady=10)
ve_entry.pack()
ve_button.pack(pady=15)
ve_mm_button.pack()

# ve_viewer frame population
viewer_title_var = StringVar()
viewer_button_1_var = StringVar()
viewer_button_2_var = StringVar()
viewer_button_3_var = StringVar()
viewer_button_4_var = StringVar()
viewer_title = Label(ve_viewer, textvariable=viewer_title_var, bg=bgc, fg=fgc)
viewer_button_1 = Button(ve_viewer, textvariable=viewer_button_1_var)
viewer_button_2 = Button(ve_viewer, textvariable=viewer_button_2_var)
viewer_button_3 = Button(ve_viewer, textvariable=viewer_button_3_var)
viewer_button_4 = Button(ve_viewer, textvariable=viewer_button_4_var)

lab_1var = StringVar()
lab_2var = StringVar()
lab_3var = StringVar()
lab_4var = StringVar()
lab_5var = StringVar()
lab_6var = StringVar()
lab_7var = StringVar()
lab_8var = StringVar()
lab_9var = StringVar()
lab_10var = StringVar()
lab_11var = StringVar()
lab_12var = StringVar()
lab_13var = StringVar()
lab_14var = StringVar()
lab_15var = StringVar()
lab_16var = StringVar()
lab_17var = StringVar()
lab_18var = StringVar()
lab_19var = StringVar()
lab_20var = StringVar()
lab_21var = StringVar()
lab_22var = StringVar()
lab_23var = StringVar()
lab_24var = StringVar()
lab_25var = StringVar()
lab_26var = StringVar()
lab_27var = StringVar()
lab_28var = StringVar()
lab_29var = StringVar()
lab_30var = StringVar()
lab_31var = StringVar()
lab_32var = StringVar()
lab_33var = StringVar()
lab_34var = StringVar()

labvar_list = [
               lab_1var, lab_2var, lab_3var, lab_4var, lab_5var, lab_6var,
               lab_7var, lab_8var, lab_9var, lab_10var, lab_11var, lab_12var,
               lab_13var, lab_14var, lab_15var, lab_16var, lab_17var
               ]

labvar_list2 = [
               lab_18var, lab_19var, lab_20var, lab_21var, lab_22var, lab_23var,
               lab_24var, lab_25var, lab_26var, lab_27var, lab_28var, lab_29var,
               lab_30var, lab_31var, lab_32var, lab_33var, lab_34var
               ]

lab_1 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_1var)
lab_2 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_2var)
lab_3 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_3var)
lab_4 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_4var)
lab_5 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_5var)
lab_6 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_6var)
lab_7 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_7var)
lab_8 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_8var)
lab_9 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_9var)
lab_10 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_10var)
lab_11 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_11var)
lab_12 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_12var)
lab_13 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_13var)
lab_14 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_14var)
lab_15 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_15var)
lab_16 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_16var)
lab_17 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_17var)
lab_18 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_18var)
lab_19 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_19var)
lab_20 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_20var)
lab_21 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_21var)
lab_22 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_22var)
lab_23 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_23var)
lab_24 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_24var, justify=LEFT)
lab_25 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_25var)
lab_26 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_26var, justify=LEFT)
lab_27 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_27var)
lab_28 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_28var)
lab_29 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_29var)
lab_30 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_30var)
lab_31 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_31var)
lab_32 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_32var)
lab_33 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_33var)
lab_34 = Label(ve_viewer, bg=bgc, fg=fgc, textvariable=lab_34var)

spacer_label1 = Label(ve_viewer, text="........", bg=bgc, fg=fgc)
spacer_label2 = Label(ve_viewer, text="........", bg=bgc, fg=fgc)
spacer_label3 = Label(ve_viewer, text="........", bg=bgc, fg=fgc)
spacer_label4 = Label(ve_viewer, text="........", bg=bgc, fg=fgc)
spacer_label5 = Label(ve_viewer, text="........", bg=bgc, fg=fgc)
spacer_label6 = Label(ve_viewer, text="........", bg=bgc, fg=fgc)
spacer_label7 = Label(ve_viewer, text="........", bg=bgc, fg=fgc)
spacer_label8 = Label(ve_viewer, text="........", bg=bgc, fg=fgc)
spacer_label9 = Label(ve_viewer, text="........", bg=bgc, fg=fgc)
spacer_label10 = Label(ve_viewer, text="........", bg=bgc, fg=fgc)
spacer_label11 = Label(ve_viewer, text="........", bg=bgc, fg=fgc)
spacer_label12 = Label(ve_viewer, text="........", bg=bgc, fg=fgc)
spacer_label13 = Label(ve_viewer, text="........", bg=bgc, fg=fgc)
spacer_label14 = Label(ve_viewer, text="........", bg=bgc, fg=fgc)
spacer_label15 = Label(ve_viewer, text="........", bg=bgc, fg=fgc)
spacer_label16 = Label(ve_viewer, text="........", bg=bgc, fg=fgc)
spacer_label17 = Label(ve_viewer, text="........", bg=bgc, fg=fgc)

spacer_list = [
               spacer_label1, spacer_label2, spacer_label3, spacer_label4,
               spacer_label5, spacer_label6, spacer_label7, spacer_label8,
               spacer_label9, spacer_label10, spacer_label11, spacer_label12,
               spacer_label13, spacer_label14, spacer_label15, spacer_label16,
               spacer_label17
               ]

viewer_title.grid(row=0, column=0, columnspan=3, pady=15)
lab_1.grid(row=1, column=0, sticky=NE)
lab_2.grid(row=2, column=0, sticky=NE)
lab_3.grid(row=3, column=0, sticky=NE)
lab_4.grid(row=4, column=0, sticky=NE)
lab_5.grid(row=5, column=0, sticky=NE)
lab_6.grid(row=6, column=0, sticky=NE)
lab_7.grid(row=7, column=0, sticky=NE)
lab_8.grid(row=8, column=0, sticky=NE)
lab_9.grid(row=9, column=0, sticky=NE)
lab_10.grid(row=10, column=0, sticky=NE)
lab_11.grid(row=11, column=0, sticky=NE)
lab_12.grid(row=12, column=0, sticky=NE)
lab_13.grid(row=13, column=0, sticky=NE)
lab_14.grid(row=14, column=0, sticky=NE)
lab_15.grid(row=15, column=0, sticky=NE)
lab_16.grid(row=16, column=0, sticky=NE)
lab_17.grid(row=17, column=0, sticky=NE)
lab_18.grid(row=1, column=2, sticky=NW)
lab_19.grid(row=2, column=2, sticky=NW)
lab_20.grid(row=3, column=2, sticky=NW)
lab_21.grid(row=4, column=2, sticky=NW)
lab_22.grid(row=5, column=2, sticky=NW)
lab_23.grid(row=6, column=2, sticky=NW)
lab_24.grid(row=7, column=2, sticky=NW)
lab_25.grid(row=8, column=2, sticky=NW)
lab_26.grid(row=9, column=2, sticky=NW)
lab_27.grid(row=10, column=2, sticky=NW)
lab_28.grid(row=11, column=2, sticky=NW)
lab_29.grid(row=12, column=2, sticky=NW)
lab_30.grid(row=13, column=2, sticky=NW)
lab_31.grid(row=14, column=2, sticky=NW)
lab_32.grid(row=15, column=2, sticky=NW)
lab_33.grid(row=16, column=2, sticky=NW)
lab_34.grid(row=17, column=2, sticky=NW)

for n in range(len(spacer_list)):
    spacer_list[n].grid(row=n+1, column=1, sticky=N)

viewer_button_1.grid(row=18, column=0, pady=10)
viewer_button_2.grid(row=19, column=0, pady=10)
viewer_button_3.grid(row=18, column=2, pady=10)
viewer_button_4.grid(row=19, column=2, pady=10)


# overwrite frame population
or_text = "An entry for that date already exists.\nWould you like to overwrite it?\nThis will delete the previous entry!"
or_label = Label(overwrite_frame, text=or_text, bg=bgc, fg=fgc)
or_ybutton = Button(overwrite_frame, text="YES")
or_nbutton = Button(overwrite_frame, text="NO", command=lambda: change_frame(review_frame))
or_label.grid(row=0, column=0, columnspan=2, pady=10)
or_ybutton.grid(row=1, column=0, pady=20)
or_nbutton.grid(row=1, column=1, pady=20)

# success/fail frame population
success_label = Label(success_frame, text="Success!", bg="#24d62a", fg=fgc)
success_mm_button = Button(success_frame, text="Main Menu", command=lambda: change_frame(mm_frame))
fail_label = Label(fail_frame, text="Failure! Something went wrong :/", bg="#d41c1c", fg=fgc)
fail_mm_button = Button(fail_frame, text="Main Menu", command=lambda: change_frame(mm_frame))
success_label.pack(pady=20)
success_mm_button.pack(pady=20)
fail_label.pack(pady=20)
fail_mm_button.pack(pady=20)

# de_frame population
de_title_var = StringVar()
de_title = Label(de_frame, textvariable=de_title_var, bg=bgc, fg=fgc)
de_ybutton = Button(de_frame, text="Yes")
de_nbutton = Button(de_frame, text="No", command=lambda: change_frame(ve_viewer))

de_title.grid(row=0, column=0, columnspan=2, pady=20)
de_ybutton.grid(row=1, column=0)
de_nbutton.grid(row=1, column=1)

# notes_frame population
notestitlevar = StringVar()
notesvar = StringVar()
notes_title = Label(notes_frame, textvariable=notestitlevar, bg=bgc, fg=fgc)
notes_body = Label(notes_frame, textvariable=notesvar, bg=bgc, fg=fgc, justify=LEFT)
notes_button = Button(notes_frame, text="Return", command=lambda: change_frame(ve_viewer))

notes_title.pack(pady=10)
notes_body.pack()
notes_button.pack(pady=15)

# error frame population
error_title_var = StringVar()
eb_1_var = StringVar()
eb_2_var = StringVar()
error_title_label = Label(error_frame, textvariable=error_title_var, bg='red', fg=fgc)
error_button_1 = Button(error_frame, textvariable=eb_1_var)
error_button_2 = Button(error_frame, textvariable=eb_2_var)

error_title_label.grid(row=0, column=0, columnspan=2, pady=20)
error_button_1.grid(row=1, column=0, padx=10)
error_button_2.grid(row=1, column=1)


init_db_check()

root.mainloop()
