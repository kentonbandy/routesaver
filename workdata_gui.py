
from tkinter import *
import tkinter as tk
from PIL import ImageTk, Image
import numpy as np
import json
from pathlib import Path
import os

'''
TO DO:
- Create initial function that checks viability of database file
'''

root = tk.Tk()
root.title("Work Data App")
root.geometry("400x500")
bgc = "#0b5973"
fgc = "white"
root.configure(background=bgc)

error_frame = Frame(root, bg=bgc)
mm_frame = Frame(root, bg=bgc)
ne_frame = Frame(root, bg=bgc)
cs_frame = Frame(root, bg=bgc)
an_frame = Frame(root, bg=bgc)
ve_frame = Frame(root, bg=bgc)
de_frame = Frame(root, bg=bgc)
test_frame = Frame(root, bg=bgc)


def error(error_type):
    error_frame.pack
    no_db = Label(error_frame, bg="red", fg=fgc, text="Database file not found!")
    no_backup = Label(error_frame, bg="red", fg=fgc, text="Backup folder not found!")
    backup_fail = Label(error_frame, bg="red", fg=fgc, text="Backup retrieval failed!\nCreating a new database file.")
    backup_success = Label(error_frame, bg="green", fg=fgc, text="New database file created from backup!")
    new_db_success = Label(error_frame, bg="green", fg=fgc, text="New database file created!")
    backup_button = Button(error_frame, text="Try using latest backup file")
    new_db = Button(error_frame, text="Create new database file")

    if error_type == 1:
        no_db.pack()
        backup_button.pack()
        new_db.pack()


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
    sal = base_entry['salary']
    hourly = base_entry['hourly']
    hours = float(np.round((et - bt), 2))
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
    uaot = None
    if appr is None:
        if fappr:
            uaot = float(np.round((ot - fappr), 2))
        else:
            uaot = ot
    payable_reg = float(np.round((reg_time * hourly), 2))
    payable_ot = float(np.round((ot * 1.5 * hourly), 2))
    gross = float(np.round((payable_reg + payable_ot), 2))
    new_entry = {}
    for i in base_entry:
        new_entry[i] = base_entry[i]
    new_entry['serial'] = serial
    new_entry['route'] = route
    new_entry['bt'] = bt
    new_entry['et'] = et
    new_entry['3996'] = f3996
    new_entry['3996_appr'] = fappr
    new_entry['appr'] = appr
    new_entry['bump/pivot'] = bp
    new_entry['notes'] = notes
    new_entry['total_hours'] = hours
    new_entry['regular time'] = reg_time
    new_entry['overtime'] = ot
    new_entry['routetime'] = routetime
    new_entry['UAOT'] = uaot
    new_entry['gross_pay'] = gross

    output = Label(test_frame, text="Data to be entered:", pady=10, bg=bgc, fg=fgc)
    output.grid(row=0, column=0, columnspan=2)
    r = 1
    for k, v in new_entry.items():
        if v is None:
            v = "None"
        keylabel = Label(test_frame, bg=bgc, fg=fgc, text=f'{k}:')
        vallabel = Label(test_frame, bg=bgc, fg=fgc, text=v)
        keylabel.grid(row=r, column=0)
        vallabel.grid(row=r, column=1)
        r = r + 1

    save = Button(test_frame, text="Save to database", command=lambda: save_entry(new_entry))
    dns = Button(
                 test_frame,
                 text="Do not save",
                 command=lambda: [
                                  change_frame(mm_frame, test_frame),
                                  remove_labels(test_frame)
                                  ]
                 )

    save.grid(row=(r+1), column=0, columnspan=2, pady=10)
    dns.grid(row=(r+2), column=0, columnspan=2, pady=10)
    clear_entries(ne_frame)
    ne_frame.pack_forget()
    test_frame.pack()


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
    labels = []
    for widget in frame.winfo_children():
        if widget.winfo_class() == "Label":
            widget.destroy()


def find_first_entry(frame):
    for widget in frame.winfo_children():
        if widget.winfo_class() == 'Entry':
            return widget


def change_frame(to_, from_=None):
    if from_:
        clear_entries(from_)
        from_.pack_forget()
    to_.pack()
    first = find_first_entry(to_)
    if first:
        first.focus_set()


if Path('c:/Users/thetr_000/Dropbox/workdata_database.json').is_file():
    db_file = Path('c:/Users/thetr_000/Dropbox/workdata_database.json')
    data = json.loads(db_file.read_text())
    try:
        x = data['workdata']
        pass
    except KeyError:
        error(2)
else:
    error(1)

empty_entry = {
               'serial': None,
               'route': None,
               'bt': None,
               'et': None,
               '3996': None,
               '3996_appr': 0.00,
               'appr': None,
               'bump/pivot': None,
               'notes': None,
               'salary': None,
               'hourly': None,
               'total_hours': None,
               'regular time': None,
               'overtime': None,
               'routetime': None,
               'UAOT': 0.00,
               'gross_pay': 0.00,
               }

base_entry = {}
for key in empty_entry:
    base_entry[key] = empty_entry[key]
try:
    base_entry['salary'] = data['workdata'][-1]['salary']
except IndexError:
    base_entry['salary'] = 0
base_entry['hourly'] = float(np.round((base_entry['salary'] / 2080.00), 2))


# mm_frame population
title = Label(mm_frame, text="Welcome to the Work Data App!", bg=bgc, fg=fgc)
sal_disp = Label(mm_frame,
                 text=f"Salary set to ${base_entry['salary']}", bg=bgc, fg=fgc)
entry = Button(mm_frame, text="Create New Entry", command=lambda: change_frame(ne_frame, mm_frame))
change_sal = Button(mm_frame, text="Change Salary Rate")
analytics = Button(mm_frame, text="Analytics Menu")
view_ent = Button(mm_frame, text="View Entry")
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
to_main = Button(ne_frame, text="Return to Main Menu", command=lambda: change_frame(mm_frame, ne_frame))

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

change_frame(mm_frame)

root.mainloop()
